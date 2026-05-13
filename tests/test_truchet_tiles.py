import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "65-truchet-tiles"
PIECE_DIR = REPO / "pieces" / PIECE_ID
INDEX_HTML = PIECE_DIR / "index.html"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
README = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def _get_entry():
    for entry in _load_pieces():
        if entry["id"] == PIECE_ID:
            return entry
    return None


class TestDirectoryStructure:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert INDEX_HTML.is_file()

    def test_thumbnail_exists(self):
        assert THUMBNAIL.is_file()

    def test_readme_exists(self):
        assert README.is_file()


class TestPiecesJson:
    def test_entry_present(self):
        assert _get_entry() is not None, f"No entry with id={PIECE_ID!r} in pieces.json"

    def test_entry_fields_complete(self):
        entry = _get_entry()
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
        assert required <= entry.keys()

    def test_entry_id_matches_directory_name(self):
        entry = _get_entry()
        assert entry["id"] == PIECE_DIR.name

    def test_entry_path_correct(self):
        entry = _get_entry()
        assert entry["path"] == f"pieces/{PIECE_ID}"

    def test_entry_thumbnail_points_to_svg(self):
        entry = _get_entry()
        assert entry["thumbnail"] == f"pieces/{PIECE_ID}/thumbnail.svg"

    def test_entry_year(self):
        entry = _get_entry()
        assert entry["year"] == 2026

    def test_entry_technique_mentions_truchet(self):
        entry = _get_entry()
        assert "truchet" in entry["technique"].lower()

    def test_no_duplicate_ids(self):
        ids = [e["id"] for e in _load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate IDs in pieces.json"


class TestIndexHtml:
    @pytest.fixture(autouse=True)
    def html(self):
        self._html = INDEX_HTML.read_text()

    def test_has_canvas_element(self):
        assert "<canvas" in self._html

    def test_has_arc_drawing(self):
        assert "ctx.arc(" in self._html

    def test_has_click_handler(self):
        assert "click" in self._html

    def test_has_animation_loop(self):
        assert "requestAnimationFrame" in self._html

    def test_has_background_color(self):
        assert "f5f0e8" in self._html

    def test_has_ink_color(self):
        assert "1a1260" in self._html

    def test_has_30x30_grid(self):
        assert "30" in self._html

    def test_has_hold_duration_constant(self):
        assert "4000" in self._html

    def test_has_both_tile_type_branches(self):
        assert "type === 0" in self._html or "=== 0" in self._html

    def test_uses_global_alpha_for_crossfade(self):
        assert "globalAlpha" in self._html

    def test_is_complete_html_document(self):
        html_lower = self._html.lower()
        assert "<!doctype html>" in html_lower
        assert "</html>" in html_lower


class TestThumbnail:
    def test_thumbnail_is_valid_svg(self):
        content = THUMBNAIL.read_text()
        assert "<svg" in content and "xmlns" in content

    def test_thumbnail_has_arc_paths(self):
        content = THUMBNAIL.read_text()
        assert " A" in content, "Thumbnail should contain SVG arc path commands"

    def test_thumbnail_uses_correct_colors(self):
        content = THUMBNAIL.read_text()
        assert "f5f0e8" in content
        assert "1a1260" in content


class TestReadme:
    @pytest.fixture(autouse=True)
    def text(self):
        self._text = README.read_text()

    def test_not_empty(self):
        assert len(self._text.strip()) > 100

    def test_mentions_smith_variant(self):
        assert "Smith" in self._text

    def test_explains_arc_geometry(self):
        lower = self._text.lower()
        assert "arc" in lower or "quarter" in lower

    def test_explains_randomness(self):
        assert "random" in self._text.lower()

    def test_mentions_color_palette(self):
        has_color = (
            "ivory" in self._text.lower()
            or "indigo" in self._text.lower()
            or "f5f0e8" in self._text
        )
        assert has_color


class TestEdgeCases:
    def test_entry_thumbnail_file_exists_on_disk(self):
        entry = _get_entry()
        thumb = REPO / entry["thumbnail"]
        assert thumb.is_file()

    def test_entry_path_directory_exists_on_disk(self):
        entry = _get_entry()
        piece_path = REPO / entry["path"]
        assert piece_path.is_dir()

    def test_missing_required_field_detected(self):
        entry_without_title = {
            "id": PIECE_ID,
            "tagline": "test",
            "year": 2026,
            "technique": "canvas",
            "path": f"pieces/{PIECE_ID}",
            "thumbnail": f"pieces/{PIECE_ID}/thumbnail.svg",
        }
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
        assert not (required <= entry_without_title.keys())

    def test_wrong_piece_id_not_matched(self):
        entry = _get_entry()
        assert entry["id"] != "64-topographic-contours"

    def test_pieces_json_still_valid_after_addition(self):
        data = _load_pieces()
        assert isinstance(data, list)
        assert len(data) > 0
        for entry in data:
            assert isinstance(entry, dict)
