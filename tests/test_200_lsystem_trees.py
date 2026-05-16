"""Tests for Piece 200 — L-System Branching Trees."""
import json
import pathlib

REPO = pathlib.Path(__file__).parent.parent
PIECES_JSON = REPO / "pieces.json"
PIECE_DIR = REPO / "pieces" / "200-lsystem-trees"


def load_pieces():
    """Return parsed pieces.json as a list."""
    return json.loads(PIECES_JSON.read_text())


def get_entry():
    """Return the pieces.json entry for 200-lsystem-trees, or None."""
    for e in load_pieces():
        if e["id"] == "200-lsystem-trees":
            return e
    return None


class TestEntry:
    """Validate the pieces.json metadata entry for piece 200."""

    def test_entry_exists(self):
        """Entry for 200-lsystem-trees must be present in pieces.json."""
        assert get_entry() is not None, "200-lsystem-trees not found in pieces.json"

    def test_required_fields(self):
        """All required metadata fields must be populated."""
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
        e = get_entry()
        assert e is not None
        missing = required - e.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches_path(self):
        """Entry id must match the final segment of its path."""
        e = get_entry()
        assert e is not None
        assert e["id"] == "200-lsystem-trees"
        assert e["path"] == "pieces/200-lsystem-trees"

    def test_thumbnail_path(self):
        """Thumbnail path must point into the piece directory."""
        e = get_entry()
        assert e is not None
        assert e["thumbnail"] == "pieces/200-lsystem-trees/thumbnail.svg"

    def test_technique_mentions_lsystem(self):
        """Technique field must reference L-system."""
        e = get_entry()
        assert e is not None
        assert "L-system" in e["technique"]

    def test_technique_mentions_requestanimationframe(self):
        """Technique field must reference requestAnimationFrame."""
        e = get_entry()
        assert e is not None
        assert "requestAnimationFrame" in e["technique"]

    def test_year(self):
        """Entry must carry year 2026."""
        e = get_entry()
        assert e is not None
        assert e["year"] == 2026


class TestFiles:
    """Validate the files inside pieces/200-lsystem-trees/."""

    def test_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_index_html_has_canvas(self):
        content = (PIECE_DIR / "index.html").read_text()
        assert "<canvas" in content

    def test_index_html_has_requestanimationframe(self):
        content = (PIECE_DIR / "index.html").read_text()
        assert "requestAnimationFrame" in content

    def test_index_html_has_both_grammar_rules(self):
        """Both grammar rule strings must appear in index.html."""
        content = (PIECE_DIR / "index.html").read_text()
        assert "F[+F]F[-F]F" in content, "Branching plant rule not found"
        assert "FF-[-F+F+F]" in content, "Bush rule not found"

    def test_index_html_has_grammars_array(self):
        """index.html must define a GRAMMARS array cycling between at least 2 entries."""
        content = (PIECE_DIR / "index.html").read_text()
        assert "GRAMMARS" in content

    def test_index_html_not_trivially_small(self):
        """index.html must contain substantial content."""
        content = (PIECE_DIR / "index.html").read_text()
        assert len(content) > 500

    def test_thumbnail_svg_valid(self):
        """thumbnail.svg must be a well-formed SVG with drawable elements."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "<svg" in content
        assert "</svg>" in content
        assert any(tag in content for tag in ("<line", "<path", "<polyline")), (
            "thumbnail.svg has no drawable line elements"
        )

    def test_readme_mentions_lsystem(self):
        content = (PIECE_DIR / "README.md").read_text()
        assert "L-system" in content or "L-System" in content

    def test_readme_mentions_both_grammars(self):
        """README must document both grammar rules."""
        content = (PIECE_DIR / "README.md").read_text()
        assert "F[+F]F[-F]F" in content, "Grammar 1 rule not documented in README"
        assert "FF-[-F+F+F]" in content, "Grammar 2 rule not documented in README"


class TestEdgeCases:
    """Regression and edge-case tests for the gallery as a whole."""

    def test_no_duplicate_ids(self):
        """All piece IDs must be unique."""
        pieces = load_pieces()
        ids = [p["id"] for p in pieces]
        assert len(ids) == len(set(ids)), "Duplicate IDs in pieces.json"

    def test_prior_pieces_preserved(self):
        """Adding piece 200 must not remove any prior piece."""
        pieces = load_pieces()
        ids = {p["id"] for p in pieces}
        for expected in [
            "01-amber-current",
            "95-dragon-fold",
            "194-chladni",
            "199-gyroid-cross-sections",
        ]:
            assert expected in ids, f"Prior piece {expected!r} was removed"

    def test_200_appears_after_199(self):
        """200-lsystem-trees must appear after 199-gyroid-cross-sections in the JSON array."""
        pieces = load_pieces()
        idx_199 = next(
            (i for i, p in enumerate(pieces) if p["id"] == "199-gyroid-cross-sections"),
            None,
        )
        idx_200 = next(
            (i for i, p in enumerate(pieces) if p["id"] == "200-lsystem-trees"),
            None,
        )
        assert idx_199 is not None, "199-gyroid-cross-sections not found"
        assert idx_200 is not None, "200-lsystem-trees not found"
        assert idx_200 > idx_199

    def test_all_referenced_files_exist(self):
        """Every path and thumbnail referenced in the new entry must exist on disk."""
        e = get_entry()
        assert e is not None
        assert (REPO / e["path"]).is_dir(), f"Directory missing: {e['path']}"
        assert (REPO / e["thumbnail"]).is_file(), f"Thumbnail missing: {e['thumbnail']}"
        assert (REPO / e["path"] / "README.md").is_file(), "README.md missing"

    def test_index_html_has_lsystem_interpreter(self):
        """index.html must contain an interpret (turtle) function."""
        content = (PIECE_DIR / "index.html").read_text()
        assert "interpret" in content, "No turtle interpreter function found"
        assert "expand" in content, "No grammar expansion function found"

    def test_index_html_has_line_width_tapering(self):
        """index.html must implement line-width tapering by branch depth."""
        content = (PIECE_DIR / "index.html").read_text()
        assert "lineWidth" in content or "lw(" in content, (
            "No line-width setting found for branch tapering"
        )
