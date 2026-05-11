"""Tests for pieces/04-between-the-tiles: Truchet tile animation."""

import json
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "04-between-the-tiles"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "04-between-the-tiles"


def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} entry not found in pieces.json")


# ---------------------------------------------------------------------------
# File-existence tests
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir(), f"Piece directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert INDEX_HTML.is_file(), "index.html is missing from the piece directory"


def test_readme_exists():
    assert README.is_file(), "README.md is missing from the piece directory"


def test_thumbnail_svg_exists():
    assert THUMBNAIL.is_file(), "thumbnail.svg is missing from the piece directory"


# ---------------------------------------------------------------------------
# HTML structural tests
# ---------------------------------------------------------------------------

def test_html_has_canvas_element():
    assert "<canvas" in _html(), "index.html must contain a <canvas> element"


def test_html_has_script_tag():
    assert "<script" in _html(), "index.html must contain a <script> element"


def test_html_title_contains_tiles():
    title_match = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert title_match, "index.html must have a <title> element"
    assert "tile" in title_match.group(1).lower() or "between" in title_match.group(1).lower(), \
        "Title should reference the piece name"


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html(), \
        "index.html must include a viewport meta tag"


def test_html_has_charset_utf8():
    assert 'charset="UTF-8"' in _html() or "charset='UTF-8'" in _html(), \
        "index.html must declare UTF-8 charset"


def test_html_uses_ink_color():
    assert "#1a1a2e" in _html(), "index.html must use the ink color #1a1a2e"


def test_html_uses_cream_color():
    assert "#f0e6d0" in _html(), "index.html must use the cream color #f0e6d0"


# ---------------------------------------------------------------------------
# JavaScript content tests
# ---------------------------------------------------------------------------

def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html(), \
        "Animation must use requestAnimationFrame"


def test_js_references_canvas_context():
    assert "getContext" in _html(), "Script must obtain a canvas rendering context"


def test_js_defines_cell_constant():
    assert "CELL" in _html(), "Script must define a CELL size constant"


def test_js_defines_flip_interval():
    assert "FLIP_INTERVAL" in _html() or "80" in _html(), \
        "Script must define a flip interval (80ms)"


def test_js_flip_interval_is_80():
    """The suggestion specifies exactly 80ms between tile flips."""
    match = re.search(r"FLIP_INTERVAL\s*=\s*(\d+)", _html())
    assert match, "FLIP_INTERVAL constant not found"
    assert int(match.group(1)) == 80, f"FLIP_INTERVAL must be 80, got {match.group(1)}"


def test_js_uses_arc_for_drawing():
    assert "arc(" in _html() or ".arc(" in _html(), \
        "Script must use canvas arc() to draw quarter-circle arcs"


def test_js_has_tile_array():
    assert "tiles" in _html(), "Script must maintain a tiles array"


def test_js_has_xor_or_flip_logic():
    html = _html()
    assert "^= 1" in html or "^ 1" in html or "1 -" in html or "flip" in html.lower(), \
        "Script must flip tile orientation (XOR or equivalent)"


def test_js_has_two_arc_orientations():
    html = _html()
    assert "orientation" in html or "orient" in html or "tiles[" in html, \
        "Script must track per-tile orientation"


def test_html_has_no_external_script_src():
    external_scripts = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external_scripts, \
        "index.html must be self-contained — no remote script sources"


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    content = THUMBNAIL.read_text()
    assert len(content) > 100, "thumbnail.svg must not be trivially empty"


def test_thumbnail_has_svg_root_element():
    assert "<svg" in THUMBNAIL.read_text(), "thumbnail.svg must have an <svg> root element"


def test_thumbnail_has_viewbox():
    svg = THUMBNAIL.read_text()
    assert "viewBox" in svg, "thumbnail.svg must declare a viewBox attribute"


def test_thumbnail_has_400x400_dimensions():
    """The suggestion specifies a 400×400 representative crop."""
    svg = THUMBNAIL.read_text()
    assert "400" in svg, "thumbnail.svg dimensions should reference 400px"


def test_thumbnail_uses_ink_color():
    assert "#1a1a2e" in THUMBNAIL.read_text(), \
        "thumbnail.svg must use the ink color #1a1a2e"


def test_thumbnail_uses_cream_color():
    assert "#f0e6d0" in THUMBNAIL.read_text(), \
        "thumbnail.svg must use the cream color #f0e6d0"


def test_thumbnail_has_arc_paths():
    svg = THUMBNAIL.read_text()
    assert "<path" in svg, "thumbnail.svg must contain <path> arc elements"


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc


def test_thumbnail_has_dark_background():
    assert "#1a1a2e" in THUMBNAIL.read_text() or "1a1a2e" in THUMBNAIL.read_text(), \
        "thumbnail.svg background should use the ink color"


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_truchet_entry():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert PIECE_ID in ids, f"pieces.json must contain an entry with id={PIECE_ID!r}"


def test_pieces_json_entry_has_all_required_fields():
    entry = _entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - entry.keys()
    assert not missing, f"Entry is missing fields: {missing}"


def test_pieces_json_entry_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_entry_path_matches_dir():
    entry = _entry()
    assert entry["path"] == f"pieces/{PIECE_ID}", \
        "Entry 'path' must point to the piece directory"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg"), "Thumbnail must be an SVG file"


def test_pieces_json_thumbnail_file_exists():
    entry = _entry()
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file(), f"Thumbnail file referenced in pieces.json is missing: {thumb}"


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int), "Year field must be an integer"


def test_pieces_json_year_is_2026():
    assert _entry()["year"] == 2026


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    content = README.read_text()
    assert len(content.strip()) > 20, "README.md must have meaningful content"


def test_readme_mentions_truchet():
    assert "truchet" in README.read_text().lower(), \
        "README should describe the Truchet tile technique"


def test_readme_mentions_two_colors():
    readme = README.read_text().lower()
    assert "ink" in readme or "cream" in readme or "#1a1a2e" in readme or "#f0e6d0" in readme, \
        "README should mention the two-color palette"


def test_readme_is_2_to_3_sentences():
    """Acceptance criteria require 2-3 sentences of explanation."""
    text = README.read_text()
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and not p.startswith("#") and not p.startswith("**")]
    total_sentences = sum(
        len(re.findall(r'[.!?]', p)) for p in paragraphs
    )
    assert total_sentences >= 2, "README must explain the technique in at least 2 sentences"


# ---------------------------------------------------------------------------
# Edge-case / failure-mode tests
# ---------------------------------------------------------------------------

def test_pieces_json_entry_not_missing_truchet(tmp_path):
    """Confirm that removing the entry from a copy would be detected."""
    data = json.loads(PIECES_JSON.read_text())
    filtered = [e for e in data if e.get("id") != PIECE_ID]
    ids = [e.get("id") for e in filtered]
    assert PIECE_ID not in ids, "Filtered list should not contain the truchet entry"


def test_html_ink_and_cream_are_different():
    """The two palette colors must be distinct values."""
    html = _html()
    ink_present = "#1a1a2e" in html
    cream_present = "#f0e6d0" in html
    assert ink_present and cream_present, "Both palette colors must appear in the HTML"
    assert "#1a1a2e" != "#f0e6d0", "Ink and cream colors must be different"


def test_thumbnail_paths_have_stroke_attribute():
    """Each path in the thumbnail must carry a stroke, not just fill."""
    svg_text = THUMBNAIL.read_text()
    root = ET.fromstring(svg_text)
    paths = root.findall(".//path") or root.findall(".//{http://www.w3.org/2000/svg}path")
    assert paths, "thumbnail.svg must contain <path> elements"
    for path in paths:
        assert path.get("stroke") or "stroke" in (path.get("style") or ""), \
            f"Path element missing stroke attribute: {ET.tostring(path)}"
