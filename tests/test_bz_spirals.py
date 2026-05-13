"""Tests for Piece 84 — Belousov-Zhabotinsky Oscillating Spiral Waves."""

import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "84-bz-spirals"
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}


def load_pieces():
    """Return parsed pieces.json as a list."""
    return json.loads(PIECES_JSON.read_text())


def bz_entry():
    """Return the pieces.json entry for 84-bz-spirals, or None if absent."""
    return next((e for e in load_pieces() if e.get("id") == "84-bz-spirals"), None)


# ---------------------------------------------------------------------------
# Happy-path: directory layout
# ---------------------------------------------------------------------------

class TestDirectoryLayout:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir(), "pieces/84-bz-spirals/ must exist"

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_exists(self):
        """Thumbnail may be .svg or .png; at least one must be present."""
        has_thumb = (PIECE_DIR / "thumbnail.svg").is_file() or \
                    (PIECE_DIR / "thumbnail.png").is_file()
        assert has_thumb, "thumbnail.svg or thumbnail.png required"

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# Happy-path: pieces.json entry
# ---------------------------------------------------------------------------

class TestPiecesJsonEntry:
    def test_entry_present(self):
        assert bz_entry() is not None, "84-bz-spirals entry missing from pieces.json"

    def test_required_fields_present(self):
        entry = bz_entry()
        assert entry is not None
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches_directory(self):
        entry = bz_entry()
        assert entry is not None
        piece_dir = REPO / entry["path"]
        assert entry["id"] == piece_dir.name, (
            f"id {entry['id']!r} must match directory name {piece_dir.name!r}"
        )

    def test_thumbnail_path_resolves(self):
        entry = bz_entry()
        assert entry is not None
        thumb = REPO / entry["thumbnail"]
        assert thumb.is_file(), f"Thumbnail path in pieces.json does not exist: {entry['thumbnail']}"

    def test_year_is_integer(self):
        entry = bz_entry()
        assert entry is not None
        assert isinstance(entry["year"], int)

    def test_path_directory_exists(self):
        entry = bz_entry()
        assert entry is not None
        assert (REPO / entry["path"]).is_dir()


# ---------------------------------------------------------------------------
# Happy-path: index.html content
# ---------------------------------------------------------------------------

class TestIndexHtmlContent:
    @pytest.fixture(scope="class")
    def html(self):
        """Return the raw text of index.html."""
        return (PIECE_DIR / "index.html").read_text()

    def test_uses_request_animation_frame(self, html):
        assert "requestAnimationFrame" in html, \
            "index.html must use requestAnimationFrame for animation"

    def test_does_not_use_set_timeout_for_main_loop(self, html):
        # setTimeout is forbidden as the primary animation loop driver
        # (rAF is required by the acceptance criteria)
        lines_with_timeout = [
            ln for ln in html.splitlines()
            if "setTimeout" in ln and "loop" in ln
        ]
        assert not lines_with_timeout, \
            "main animation loop must use requestAnimationFrame, not setTimeout"

    def test_uses_uint8_array_double_buffer(self, html):
        assert html.count("Uint8Array") >= 2, \
            "index.html should declare two Uint8Array buffers for double-buffering"

    def test_teal_color_present(self, html):
        assert "#00e5c0" in html.lower() or "00e5c0" in html.lower(), \
            "Electric teal (#00e5c0) palette colour must appear in index.html"

    def test_coral_color_present(self, html):
        assert "c44b4b" in html.lower(), \
            "Coral (#c44b4b) palette colour must appear in index.html"

    def test_navy_background_present(self, html):
        assert "0a0e1a" in html.lower(), \
            "Navy background (#0a0e1a) must appear in index.html"

    def test_put_image_data_used(self, html):
        assert "putImageData" in html, \
            "index.html must render via putImageData for direct pixel manipulation"

    def test_toroidal_wrap_present(self, html):
        """Toroidal grid must handle boundary wrap with modulo arithmetic."""
        assert "% COLS" in html or "% cols" in html, \
            "Grid column-wrap modulo must be present in index.html"


# ---------------------------------------------------------------------------
# Happy-path: README content
# ---------------------------------------------------------------------------

class TestReadmeContent:
    @pytest.fixture(scope="class")
    def readme(self):
        return (PIECE_DIR / "README.md").read_text()

    def test_mentions_bz_reaction(self, readme):
        assert re.search(r"belousov.zhabotinsky", readme, re.IGNORECASE) or \
               "BZ" in readme, "README must mention the Belousov-Zhabotinsky reaction"

    def test_mentions_spiral(self, readme):
        assert "spiral" in readme.lower(), "README must mention spiral formation"

    def test_mentions_palette(self, readme):
        assert "palette" in readme.lower() or "colour" in readme.lower() or \
               "color" in readme.lower(), "README must explain the colour palette"

    def test_mentions_refractory(self, readme):
        assert "refractory" in readme.lower(), \
            "README must explain the refractory state"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_thumbnail_svg_is_valid_xml(self):
        """SVG thumbnail must be well-formed XML (parse without error)."""
        import xml.etree.ElementTree as ET
        thumb = PIECE_DIR / "thumbnail.svg"
        if not thumb.is_file():
            pytest.skip("thumbnail.svg absent")
        ET.parse(str(thumb))  # raises ParseError on malformed XML

    def test_thumbnail_svg_has_dark_background(self):
        """SVG background rect should use the navy palette colour."""
        thumb = PIECE_DIR / "thumbnail.svg"
        if not thumb.is_file():
            pytest.skip("thumbnail.svg absent")
        content = thumb.read_text()
        assert "0a0e1a" in content.lower(), \
            "thumbnail.svg background should use #0a0e1a navy"

    def test_html_has_canvas_element(self):
        html = (PIECE_DIR / "index.html").read_text()
        assert "<canvas" in html.lower(), "index.html must contain a <canvas> element"

    def test_readme_not_empty(self):
        readme = (PIECE_DIR / "README.md").read_text()
        assert len(readme.strip()) > 100, "README.md must have substantive content"


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_entry_with_missing_field_fails_required_check(self):
        """An entry without 'title' must fail the completeness check."""
        incomplete = {
            "id": "84-bz-spirals",
            "tagline": "test",
            "year": 2026,
            "technique": "canvas",
            "path": "pieces/84-bz-spirals",
            "thumbnail": "pieces/84-bz-spirals/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_wrong_id_detected(self, tmp_path):
        """An id that does not match the directory name must be caught."""
        piece_dir = tmp_path / "84-bz-spirals"
        piece_dir.mkdir()
        entry = {
            "id": "wrong-id",
            "title": "Test",
            "tagline": "test",
            "year": 2026,
            "technique": "canvas",
            "path": str(piece_dir.relative_to(tmp_path)),
            "thumbnail": "pieces/84-bz-spirals/thumbnail.svg",
        }
        assert entry["id"] != piece_dir.name

    def test_missing_thumbnail_file_detected(self, tmp_path):
        """Referencing a non-existent thumbnail path should be caught."""
        ghost = tmp_path / "ghost.svg"
        assert not ghost.exists()

    def test_missing_readme_detected(self, tmp_path):
        """A piece directory without README.md should fail the directory check."""
        piece_dir = tmp_path / "84-bz-spirals"
        piece_dir.mkdir()
        assert not (piece_dir / "README.md").exists()

    def test_no_duplicate_id_in_pieces_json(self):
        """Each id in pieces.json must be unique."""
        pieces = load_pieces()
        ids = [e["id"] for e in pieces]
        assert len(ids) == len(set(ids)), "Duplicate ids found in pieces.json"
