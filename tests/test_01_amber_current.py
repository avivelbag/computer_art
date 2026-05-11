"""Tests for pieces/01-amber-current: Perlin-noise flow-field particle animation."""

import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "01-amber-current"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "01-amber-current"


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


def test_html_canvas_has_id_attribute():
    assert 'id="canvas"' in _html() or "id='canvas'" in _html(), \
        "Canvas element must have an id attribute"


def test_html_has_script_tag():
    assert "<script" in _html(), "index.html must contain a <script> element"


def test_html_title_contains_amber():
    title_match = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert title_match, "index.html must have a <title> element"
    assert "amber" in title_match.group(1).lower(), \
        "Title should reference 'Amber'"


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html(), \
        "index.html must include a viewport meta tag for responsiveness"


def test_html_has_charset_utf8():
    assert 'charset="UTF-8"' in _html() or "charset='UTF-8'" in _html(), \
        "index.html must declare UTF-8 charset"


def test_html_background_is_dark():
    html = _html()
    assert "#0a0500" in html or "0,5,0" in html, \
        "Background should be a near-black dark amber tone"


# ---------------------------------------------------------------------------
# JavaScript content tests
# ---------------------------------------------------------------------------

def test_js_defines_particle_count():
    assert "PARTICLE_COUNT" in _html(), \
        "Script must define a named PARTICLE_COUNT constant"


def test_js_particle_count_is_600():
    match = re.search(r"PARTICLE_COUNT\s*=\s*(\d+)", _html())
    assert match, "PARTICLE_COUNT constant not found"
    assert int(match.group(1)) == 600, \
        f"PARTICLE_COUNT must be 600, got {match.group(1)}"


def test_js_uses_perlin_noise():
    html = _html()
    assert "noise(" in html or "function noise" in html, \
        "Script must contain a Perlin noise function"


def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html(), \
        "Animation must use requestAnimationFrame for the render loop"


def test_js_references_canvas_context():
    html = _html()
    assert "getContext" in html, \
        "Script must obtain a canvas 2D rendering context"


def test_js_has_amber_color_values():
    html = _html()
    amber_patterns = ["255,191,0", "255,153,0", "255,120,30", "255,210,80"]
    found = any(p in html for p in amber_patterns)
    assert found, "Script must define warm amber RGBA colour values"


def test_js_has_flow_field_angle_computation():
    html = _html()
    assert "Math.cos" in html and "Math.sin" in html, \
        "Flow-field movement must use cos/sin to convert angle to velocity"


def test_js_has_particle_array():
    html = _html()
    assert "particles" in html, "Script must maintain a particles collection"


def test_js_particles_wrap_around_edges():
    html = _html()
    assert "< 0" in html or "<0" in html, \
        "Particles should wrap at canvas edges (edge-check detected by '<0')"


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    content = THUMBNAIL.read_text()
    assert len(content) > 50, "thumbnail.svg must not be trivially empty"


def test_thumbnail_has_svg_root_element():
    assert "<svg" in THUMBNAIL.read_text(), \
        "thumbnail.svg must have an <svg> root element"


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text(), \
        "thumbnail.svg must declare a viewBox attribute"


def test_thumbnail_has_amber_fill_colors():
    svg = THUMBNAIL.read_text()
    amber_sigs = ["255,191,0", "255,153,0", "255,120,30", "255,210,80"]
    found = any(sig in svg for sig in amber_sigs)
    assert found, "thumbnail.svg must contain amber-family colour values"


def test_thumbnail_has_dark_background():
    assert "#0a0500" in THUMBNAIL.read_text() or "0a0500" in THUMBNAIL.read_text(), \
        "thumbnail.svg background should match the dark amber background"


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_amber_current_entry():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert PIECE_ID in ids, f"pieces.json must contain an entry with id={PIECE_ID!r}"


def test_pieces_json_entry_has_all_required_fields():
    entry = _entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - entry.keys()
    assert not missing, f"Entry is missing fields: {missing}"


def test_pieces_json_entry_id_is_01_amber_current():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_entry_path_matches_dir():
    entry = _entry()
    assert entry["path"] == f"pieces/{PIECE_ID}", \
        "Entry 'path' must point to the piece directory"


def test_pieces_json_thumbnail_is_svg():
    entry = _entry()
    assert entry["thumbnail"].endswith(".svg"), \
        "Thumbnail must be an SVG file"


def test_pieces_json_thumbnail_file_exists():
    entry = _entry()
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file(), f"Thumbnail file referenced in pieces.json is missing: {thumb}"


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int), "Year field must be an integer"


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    content = README.read_text()
    assert len(content.strip()) > 20, "README.md must have meaningful content"


def test_readme_mentions_flow_field():
    assert "flow" in README.read_text().lower(), \
        "README should describe the flow-field technique"


def test_readme_mentions_amber():
    assert "amber" in README.read_text().lower(), \
        "README should reference the amber palette"


# ---------------------------------------------------------------------------
# Self-containment / edge-case tests
# ---------------------------------------------------------------------------

def test_html_has_no_external_script_src():
    external_scripts = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external_scripts, \
        "index.html must be self-contained — no remote script sources"


def test_thumbnail_svg_is_parseable_xml():
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc
