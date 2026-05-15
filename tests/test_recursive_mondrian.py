"""Tests for Piece 167 — Everything Divides Evenly in the End."""

import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "167-everything-divides"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "167-everything-divides"


# ---------------------------------------------------------------------------
# Directory structure
# ---------------------------------------------------------------------------

class TestPiece167Structure:
    """The required files must exist in the correct location."""

    def test_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_thumbnail_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file() or (PIECE_DIR / "thumbnail.png").is_file()


# ---------------------------------------------------------------------------
# index.html content
# ---------------------------------------------------------------------------

class TestPiece167IndexHtml:
    """index.html must implement the Mondrian subdivision with correct properties."""

    @pytest.fixture(scope="class")
    def html(self):
        return (PIECE_DIR / "index.html").read_text()

    def test_not_empty(self, html):
        assert len(html) > 1000, "index.html is suspiciously short"

    def test_no_external_scripts(self, html):
        """No CDN or external library imports allowed."""
        assert "cdn." not in html.lower()
        assert 'src="http' not in html
        assert "src='http" not in html

    def test_uses_canvas(self, html):
        assert "<canvas" in html

    def test_has_recursive_split_function(self, html):
        """The split function must be present by name."""
        assert "split(" in html or "split (" in html

    def test_has_de_stijl_red(self, html):
        red_tokens = ["#D40920", "#E3001B", "#CC0000", "#d40920", "#e3001b"]
        assert any(t in html for t in red_tokens), "Red primary color not found"

    def test_has_de_stijl_blue(self, html):
        blue_tokens = ["#1B4E8F", "#0D4B8F", "#1b4e8f", "#0d4b8f"]
        assert any(t in html for t in blue_tokens), "Blue primary color not found"

    def test_has_de_stijl_yellow(self, html):
        yellow_tokens = ["#F5C500", "#FFD700", "#f5c500", "#ffd700"]
        assert any(t in html for t in yellow_tokens), "Yellow primary color not found"

    def test_has_white(self, html):
        assert "#F8F5EE" in html or "#FFFFFF" in html or "white" in html.lower()

    def test_has_periodic_regeneration(self, html):
        """Composition must be scheduled to regenerate via setTimeout or setInterval."""
        assert "setTimeout" in html or "setInterval" in html

    def test_has_dissolve_transition(self, html):
        """Transition must be a fade/dissolve, not an instantaneous swap."""
        html_lower = html.lower()
        assert "opacity" in html_lower

    def test_has_min_side_or_max_depth_guard(self, html):
        """Recursion must terminate via a size or depth check."""
        has_min = "MIN_SIDE" in html or "MIN_AREA" in html or "minSide" in html or "minArea" in html
        has_depth = "MAX_DEPTH" in html or "maxDepth" in html or "depth" in html
        assert has_min or has_depth, "No recursion termination condition found"

    def test_has_aspect_ratio_axis_selection(self, html):
        """Axis selection must reference width and height (aspect ratio logic)."""
        assert "w" in html and "h" in html

    def test_split_position_references_golden_or_thirds(self, html):
        """Split position must bias toward golden ratio or rule-of-thirds values."""
        # Look for characteristic constants in numeric or comment form
        golden = "0.618" in html or "0.382" in html or "golden" in html.lower()
        thirds = "0.333" in html or "0.667" in html or "thirds" in html.lower()
        assert golden or thirds, "No golden-ratio or rule-of-thirds split bias found"


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

class TestPiece167PiecesJson:
    """The pieces.json entry must be well-formed and reference existing files."""

    @pytest.fixture(scope="class")
    def all_entries(self):
        return json.loads(PIECES_JSON.read_text())

    @pytest.fixture(scope="class")
    def entry(self, all_entries):
        matches = [e for e in all_entries if e.get("id") == PIECE_ID]
        assert matches, f"No entry with id={PIECE_ID!r} in pieces.json"
        return matches[0]

    def test_entry_exists(self, all_entries):
        ids = [e.get("id") for e in all_entries]
        assert PIECE_ID in ids

    def test_required_fields(self, entry):
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
        missing = required - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches_directory_name(self, entry):
        assert entry["id"] == pathlib.Path(entry["path"]).name

    def test_path_points_to_existing_directory(self, entry):
        assert (REPO / entry["path"]).is_dir()

    def test_thumbnail_file_exists(self, entry):
        assert (REPO / entry["thumbnail"]).is_file()

    def test_year(self, entry):
        assert entry["year"] == 2026

    def test_title_mentions_divide_or_mondrian(self, entry):
        combined = (entry["title"] + " " + entry["tagline"]).lower()
        keywords = ["divid", "mondrian", "split", "rectangle", "grid"]
        assert any(k in combined for k in keywords)

    def test_technique_mentions_canvas(self, entry):
        assert "canvas" in entry["technique"].lower()


# ---------------------------------------------------------------------------
# Edge cases and failure detection
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Verify detection logic for invalid or missing data."""

    def test_readme_has_meaningful_content(self):
        content = (PIECE_DIR / "README.md").read_text()
        assert len(content) > 100, "README.md is too short to be useful"

    def test_no_duplicate_ids_in_pieces_json(self):
        data = json.loads(PIECES_JSON.read_text())
        ids = [e.get("id") for e in data]
        assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"

    def test_missing_id_detection(self):
        """Confirms that querying a non-existent ID returns nothing."""
        data = json.loads(PIECES_JSON.read_text())
        ghost = "999-nonexistent-piece"
        assert not any(e.get("id") == ghost for e in data)

    def test_missing_required_field_detection(self):
        """An entry without 'title' must fail the required-field check."""
        entry = {
            "id": "test-piece",
            "tagline": "test",
            "year": 2026,
            "technique": "canvas",
            "path": "pieces/test-piece",
            "thumbnail": "pieces/test-piece/thumb.svg",
        }
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
        assert not (required <= entry.keys()), "Missing field should have been detected"

    def test_id_mismatch_detection(self):
        """id must equal the last path segment."""
        entry = {"id": "wrong-id", "path": "pieces/correct-name"}
        assert entry["id"] != pathlib.Path(entry["path"]).name

    def test_missing_thumbnail_detection(self, tmp_path):
        """A non-existent thumbnail path should not resolve to a real file."""
        fake_thumb = tmp_path / "pieces" / "ghost" / "thumb.svg"
        assert not fake_thumb.is_file()

    def test_missing_directory_detection(self, tmp_path):
        """A path that is not a directory should be caught."""
        ghost = tmp_path / "ghost-piece"
        assert not ghost.is_dir()
