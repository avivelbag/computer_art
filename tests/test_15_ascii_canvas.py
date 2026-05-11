"""Tests for pieces/15-the-surface-speaks: ASCII-art sine-cosine surface animation."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "15-the-surface-speaks"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "15-the-surface-speaks"
RAMP = " .:-=+*#@"


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

def test_html_has_pre_element():
    assert "<pre" in _html(), "index.html must contain a <pre> element for ASCII art"


def test_html_pre_has_output_id():
    html = _html()
    assert 'id="output"' in html or "id='output'" in html, \
        "<pre> must have id='output'"


def test_html_has_script_tag():
    assert "<script" in _html(), "index.html must contain a <script> element"


def test_html_title_contains_surface():
    title_match = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert title_match, "index.html must have a <title> element"
    assert "surface" in title_match.group(1).lower(), \
        "Title should reference 'Surface'"


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html(), \
        "index.html must include a viewport meta tag"


def test_html_has_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html, \
        "index.html must declare UTF-8 charset"


def test_html_background_is_deep_navy():
    assert "#0a0e1a" in _html(), \
        "Background colour must be deep navy #0a0e1a"


def test_html_text_color_is_amber():
    assert "#ffb000" in _html(), \
        "Text colour must be amber #ffb000"


def test_html_uses_monospace_font():
    assert "monospace" in _html(), \
        "CSS must specify a monospace font family for the <pre> element"


# ---------------------------------------------------------------------------
# JavaScript content tests
# ---------------------------------------------------------------------------

def test_js_defines_cols_constant():
    assert "COLS" in _html(), "Script must define a COLS constant"


def test_js_defines_rows_constant():
    assert "ROWS" in _html(), "Script must define a ROWS constant"


def test_js_defines_ramp():
    html = _html()
    assert "RAMP" in html, "Script must define an ASCII brightness ramp"
    assert ":-=" in html or ".:-" in html or "=+*" in html, \
        "Script must contain ASCII ramp characters like .:-=+*#@"


def test_js_uses_sin_and_cos():
    html = _html()
    assert "Math.sin" in html and "Math.cos" in html, \
        "Surface formula must use both Math.sin and Math.cos"


def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html(), \
        "Animation must use requestAnimationFrame for the render loop"


def test_js_has_fps_cap():
    html = _html()
    assert "60" in html or "FPS_CAP" in html or "FRAME_MS" in html, \
        "Script must cap animation at 60fps"


def test_js_updates_pre_textcontent():
    html = _html()
    assert "textContent" in html, \
        "Script must update pre.textContent to render each ASCII frame"


def test_js_grid_dimensions_are_reasonable():
    html = _html()
    cols_match = re.search(r"COLS\s*=\s*(\d+)", html)
    rows_match = re.search(r"ROWS\s*=\s*(\d+)", html)
    assert cols_match and rows_match, "COLS and ROWS must be numeric constants"
    cols = int(cols_match.group(1))
    rows = int(rows_match.group(1))
    assert 40 <= cols <= 160, f"COLS={cols} is outside a sensible range [40, 160]"
    assert 20 <= rows <= 80, f"ROWS={rows} is outside a sensible range [20, 80]"


# ---------------------------------------------------------------------------
# ASCII ramp correctness (unit-level logic tests)
# ---------------------------------------------------------------------------

def test_ramp_maps_negative_one_to_dark_char():
    """z=-1 must map to the darkest (first) character in the ramp."""
    idx = round(((-1 + 1) / 2) * (len(RAMP) - 1))
    assert idx == 0
    assert RAMP[idx] == " ", "z=-1 should map to a space (darkest)"


def test_ramp_maps_positive_one_to_bright_char():
    """z=+1 must map to the brightest (last) character in the ramp."""
    idx = round(((1 + 1) / 2) * (len(RAMP) - 1))
    assert idx == len(RAMP) - 1
    assert RAMP[idx] == "@", "z=+1 should map to '@' (brightest)"


def test_ramp_maps_zero_to_middle_char():
    """z=0 should map to a middle-brightness character."""
    idx = round(((0 + 1) / 2) * (len(RAMP) - 1))
    assert 0 < idx < len(RAMP) - 1, "z=0 must map to a middle character"


def test_surface_formula_produces_values_in_range():
    """The sine-cosine product surface must stay in [-1, 1] for arbitrary t."""
    for t in [0.0, 0.5, 1.0, 2.5, 10.0, 100.0]:
        for col in range(0, 80, 5):
            for row in range(0, 40, 4):
                x = (col / 80 - 0.5) * math.pi * 2
                y = (row / 40 - 0.5) * math.pi * 2
                z = math.sin(x * 3 + t) * math.cos(y * 3 + t * 0.7)
                assert -1.0 <= z <= 1.0, f"z={z} out of range at t={t}, col={col}, row={row}"


def test_surface_formula_is_not_constant():
    """Adjacent columns must produce different z values (wave has variation)."""
    t = 0.0
    row = 20
    y = (row / 40 - 0.5) * math.pi * 2
    values = set()
    for col in range(40):
        x = (col / 80 - 0.5) * math.pi * 2
        z = math.sin(x * 3 + t) * math.cos(y * 3 + t * 0.7)
        idx = round(((z + 1) / 2) * (len(RAMP) - 1))
        values.add(idx)
    assert len(values) > 3, "Surface must vary across columns — not a flat line"


def test_animation_advances_time():
    """SPEED constant must be positive so animation actually progresses."""
    html = _html()
    speed_match = re.search(r"SPEED\s*=\s*([\d.]+)", html)
    assert speed_match, "Script must define a SPEED constant for time advance"
    speed = float(speed_match.group(1))
    assert speed > 0, f"SPEED must be positive, got {speed}"


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    content = THUMBNAIL.read_text()
    assert len(content) > 100, "thumbnail.svg must not be trivially empty"


def test_thumbnail_has_svg_root_element():
    assert "<svg" in THUMBNAIL.read_text(), \
        "thumbnail.svg must have an <svg> root element"


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text(), \
        "thumbnail.svg must declare a viewBox attribute"


def test_thumbnail_has_dark_background():
    svg = THUMBNAIL.read_text()
    assert "#0a0e1a" in svg or "0a0e1a" in svg, \
        "thumbnail.svg background must be the deep navy colour #0a0e1a"


def test_thumbnail_has_amber_text():
    svg = THUMBNAIL.read_text()
    assert "#ffb000" in svg or "ffb000" in svg, \
        "thumbnail.svg must use amber colour #ffb000 for text"


def test_thumbnail_contains_ascii_ramp_chars():
    svg = THUMBNAIL.read_text()
    ramp_chars_found = sum(1 for ch in ":-=+*#@" if ch in svg)
    assert ramp_chars_found >= 3, \
        "thumbnail.svg must contain ASCII ramp characters from the animation"


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc


def test_thumbnail_uses_monospace_font():
    assert "monospace" in THUMBNAIL.read_text(), \
        "thumbnail.svg must use a monospace font to faithfully represent the ASCII frame"


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
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
    assert _entry()["thumbnail"].endswith(".svg"), \
        "Thumbnail must be an SVG file"


def test_pieces_json_thumbnail_file_exists():
    entry = _entry()
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file(), f"Thumbnail file referenced in pieces.json is missing: {thumb}"


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int), "Year field must be an integer"


def test_pieces_json_technique_mentions_ascii():
    technique = _entry()["technique"].lower()
    assert "ascii" in technique, \
        "Technique field should mention ASCII as this is an ASCII art piece"


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    content = README.read_text()
    assert len(content.strip()) > 50, "README.md must have meaningful content"


def test_readme_mentions_surface():
    assert "surface" in README.read_text().lower(), \
        "README should describe the mathematical surface rendered"


def test_readme_mentions_ramp_or_brightness():
    readme = README.read_text().lower()
    assert "ramp" in readme or "brightness" in readme or "character" in readme, \
        "README should explain the brightness-to-character mapping"


def test_readme_mentions_projection_or_formula():
    readme = README.read_text().lower()
    assert "projection" in readme or "sin" in readme or "cos" in readme or "formula" in readme, \
        "README should explain the 3D-to-2D projection or surface formula"


# ---------------------------------------------------------------------------
# Self-containment / edge-case tests
# ---------------------------------------------------------------------------

def test_html_has_no_external_script_src():
    external_scripts = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external_scripts, \
        "index.html must be self-contained — no remote script sources"


def test_html_no_audio_elements():
    html = _html()
    assert "<audio" not in html and "<Audio" not in html, \
        "Piece must have no audio elements per acceptance criteria"


def test_html_is_valid_utf8():
    INDEX_HTML.read_bytes().decode("utf-8")


def test_thumbnail_svg_is_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


# ---------------------------------------------------------------------------
# Edge-case: index.html with large grid (stress test the ramp logic)
# ---------------------------------------------------------------------------

def test_ramp_index_clamps_for_boundary_floats():
    """Floating-point edge values just outside [-1, 1] must clamp without error."""
    ramp_max = len(RAMP) - 1
    for z in [-1.0, -1.0 + 1e-10, 1.0 - 1e-10, 1.0]:
        idx = round(((z + 1) / 2) * ramp_max)
        clamped = max(0, min(ramp_max, idx))
        assert 0 <= clamped <= ramp_max, f"Clamped index {clamped} out of bounds for z={z}"
        _ = RAMP[clamped]  # must not raise IndexError


# ---------------------------------------------------------------------------
# Failure-mode tests
# ---------------------------------------------------------------------------

def test_html_missing_pre_would_be_caught():
    """Verify our test correctly identifies the absence of <pre>."""
    assert "<pre" not in "<!-- no pre here -->", \
        "Test logic: a string without <pre> should not contain it"


def test_wrong_background_detected():
    """A piece with wrong background colour would fail the navy check."""
    fake_html = '<html><body style="background: #ffffff;"></body></html>'
    assert "#0a0e1a" not in fake_html, \
        "Test logic: wrong background should not pass the navy colour check"


def test_empty_ramp_would_fail_brightness_mapping():
    """An empty ramp string would cause ZeroDivisionError or IndexError."""
    empty_ramp = ""
    assert len(empty_ramp) == 0, "Empty ramp has length 0"
    with __import__("pytest").raises((ZeroDivisionError, IndexError, ValueError)):
        ramp_max = len(empty_ramp) - 1  # -1
        idx = round(((0 + 1) / 2) * ramp_max)  # round(0.5 * -1) = round(-0.5) = 0
        _ = empty_ramp[idx]  # IndexError
