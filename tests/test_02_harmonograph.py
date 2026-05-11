"""Tests for pieces/03-still-oscillating: harmonograph / Lissajous canvas animation."""

import json
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "03-still-oscillating"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "03-still-oscillating"


def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_readme_exists():
    assert README.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------

def test_html_is_self_contained_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must not load remote scripts"


def test_html_no_external_links():
    external = re.findall(r'<link[^>]+href=["\']https?://', _html())
    assert not external, "index.html must not reference external stylesheets"


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_canvas_fixed_dimensions():
    html = _html()
    assert 'width="600"' in html and 'height="600"' in html, \
        "Canvas must be 600×600"


def test_html_has_charset():
    assert 'charset="UTF-8"' in _html() or "charset='UTF-8'" in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_title_contains_oscillating():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    assert "oscillating" in m.group(1).lower()


def test_html_dark_background():
    assert "#0a0a0f" in _html()


# ---------------------------------------------------------------------------
# Animation mechanics
# ---------------------------------------------------------------------------

def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_js_has_decay_constant():
    html = _html()
    assert "DECAY" in html, "Must define a DECAY constant"
    m = re.search(r"DECAY\s*=\s*([\d.e\-]+)", html)
    assert m, "DECAY value not found"
    assert float(m.group(1)) == 0.0002


def test_js_has_total_steps():
    html = _html()
    assert "TOTAL_STEPS" in html
    m = re.search(r"TOTAL_STEPS\s*=\s*(\d+)", html)
    assert m
    assert int(m.group(1)) == 3000


def test_js_has_steps_per_frame():
    html = _html()
    assert "STEPS_PER_FRAME" in html
    m = re.search(r"STEPS_PER_FRAME\s*=\s*(\d+)", html)
    assert m
    assert int(m.group(1)) == 2


def test_js_has_fade_mode():
    """Loop must have a fade/restart phase, not just loop abruptly."""
    html = _html()
    assert "fade" in html.lower() or "FADE" in html, \
        "Must implement a fade phase between cycles"


def test_js_uses_sin_and_exp():
    html = _html()
    assert "Math.sin" in html
    assert "Math.exp" in html


def test_js_uses_canvas_2d_context():
    assert "getContext" in _html()


def test_js_stroke_color_is_violet():
    html = _html()
    assert "220" in html and "200" in html and "255" in html, \
        "Stroke colour must be violet-family rgba(220, 200, 255, ...)"


def test_js_defines_base_frequencies():
    html = _html()
    assert "BASE_F" in html or ("2.001" in html and "3.001" in html), \
        "Base frequency array must be present"


def test_js_frequency_ratios_match_spec():
    html = _html()
    assert "2.001" in html
    assert "3.001" in html
    assert "1.001" in html


def test_js_has_scale_constant():
    html = _html()
    assert "SCALE" in html
    m = re.search(r"\bSCALE\s*=\s*(\d+)", html)
    assert m, "SCALE constant not found"
    assert int(m.group(1)) == 135, "Scale should be 135 (90% of 300 half-canvas / 2)"


def test_js_loop_varies_frequencies_per_cycle():
    html = _html()
    assert "nextFreqs" in html or "Math.random" in html, \
        "Each loop cycle must vary the frequency ratios"


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------

def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_has_dark_background():
    assert "#0a0a0f" in THUMBNAIL.read_text() or "0a0a0f" in THUMBNAIL.read_text()


def test_thumbnail_not_trivially_empty():
    assert len(THUMBNAIL.read_text()) > 200


def test_thumbnail_has_violet_stroke():
    svg = THUMBNAIL.read_text()
    assert "220,200,255" in svg or "220, 200, 255" in svg, \
        "Thumbnail must use the violet stroke colour"


def test_thumbnail_has_curve_data():
    """Thumbnail must contain actual curve geometry, not just a background rect."""
    svg = THUMBNAIL.read_text()
    has_path = "<path" in svg
    has_polyline = "<polyline" in svg
    has_polygon = "<polygon" in svg
    assert has_path or has_polyline or has_polygon, \
        "thumbnail.svg must contain curve geometry"


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------

def test_readme_mentions_pendulum_equations():
    text = README.read_text().lower()
    assert "pendulum" in text or "equation" in text, \
        "README must describe the pendulum equations"


def test_readme_mentions_frequency_ratios():
    text = README.read_text()
    assert "2.001" in text or "f1" in text, \
        "README must name the chosen frequency ratios"


def test_readme_mentions_decay():
    assert "decay" in README.read_text().lower() or "0.0002" in README.read_text()


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


# ---------------------------------------------------------------------------
# pieces.json contract
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [e.get("id") for e in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_entry_has_all_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - _entry().keys()
    assert not missing, f"Missing fields: {missing}"


def test_entry_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_entry_path_matches_dir():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_entry_thumbnail_path_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file(), f"Thumbnail referenced in pieces.json is missing: {thumb}"


def test_entry_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_entry_id_matches_dir_name():
    entry = _entry()
    piece_dir = REPO / entry["path"]
    assert entry["id"] == piece_dir.name


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

def test_pieces_json_still_valid_after_new_entry():
    """pieces.json must remain a valid JSON list with all existing entries intact."""
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)
    assert len(data) >= 2, "pieces.json must have at least two entries now"
    ids = [e["id"] for e in data]
    assert "01-amber-current" in ids, "Existing entry must not be removed"
    assert PIECE_ID in ids


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "pieces.json must not have duplicate ids"


def test_html_canvas_id_present():
    html = _html()
    assert 'id="canvas"' in html or "id='canvas'" in html


def test_html_background_fill_before_animation():
    """Canvas must be filled with the background colour before the animation loop starts.

    The tick() function contains a recursive requestAnimationFrame call earlier in
    source than the initialization block. We compare the LAST occurrence of each
    so we match the actual initialization pair, not the in-loop recursive call.
    """
    html = _html()
    bg_idx = html.rfind("#0a0a0f")
    raf_idx = html.rfind("requestAnimationFrame")
    assert bg_idx != -1 and raf_idx != -1
    assert bg_idx < raf_idx, \
        "Background fill should appear before the final requestAnimationFrame call"


def test_html_no_audio_elements():
    html = _html()
    assert "<audio" not in html.lower() and "AudioContext" not in html, \
        "Piece must not use audio"


def test_thumbnail_svg_dimensions_declared():
    svg_text = THUMBNAIL.read_text()
    assert 'width="' in svg_text and 'height="' in svg_text
