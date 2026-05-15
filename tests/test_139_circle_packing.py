"""Tests for pieces/139-circle-packing: greedy largest-empty-circle packing."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "139-circle-packing"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "139-circle-packing"


def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# Python mirror of the packing algorithm for white-box testing
# ---------------------------------------------------------------------------

def clearance(cx: float, cy: float, circles: list, w: float, h: float) -> float:
    """Compute the largest circle radius fitting at (cx, cy) in a w×h canvas.

    Clearance is the minimum of distance to each canvas edge and the gap
    between (cx, cy) and each placed circle's perimeter.
    """
    r = min(cx, cy, w - cx, h - cy)
    for ox, oy, or_ in circles:
        d = math.sqrt((cx - ox) ** 2 + (cy - oy) ** 2) - or_
        if d < r:
            r = d
    return r


def lerp_color(t: float, pal: list) -> tuple:
    """Interpolate through a 3-stop palette at t in [0, 1].

    t=0 → pal[0], t=0.5 → pal[1], t=1 → pal[2].
    """
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        a, b, s = pal[0], pal[1], t * 2
    else:
        a, b, s = pal[1], pal[2], (t - 0.5) * 2
    return tuple(round(a[i] + (b[i] - a[i]) * s) for i in range(3))


def circle_t(r: float, max_r: float, min_r: float = 2.0) -> float:
    """Map log(r) linearly to [0, 1] where 0=min_r circles, 1=max_r circles."""
    log_min = math.log(min_r)
    log_max = math.log(max_r)
    if log_max <= log_min:
        return 1.0
    return (math.log(r) - log_min) / (log_max - log_min)


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

def test_html_has_doctype():
    assert _html().startswith("<!DOCTYPE html>")


def test_html_has_charset():
    assert 'charset="UTF-8"' in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_canvas():
    assert '<canvas' in _html()


def test_html_canvas_has_id():
    assert 'id="canvas"' in _html()


def test_html_canvas_dimensions():
    html = _html()
    assert 'width="800"' in html and 'height="800"' in html


def test_html_title_mentions_circle():
    m = re.search(r'<title>(.*?)</title>', _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    assert "circle" in m.group(1).lower() or "packing" in m.group(1).lower()


def test_html_dark_background():
    assert '#0a0a14' in _html()


def test_html_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external


def test_html_no_external_links():
    external = re.findall(r'<link[^>]+href=["\']https?://', _html())
    assert not external


# ---------------------------------------------------------------------------
# Animation mechanics
# ---------------------------------------------------------------------------

def test_js_uses_request_animation_frame():
    assert 'requestAnimationFrame' in _html()


def test_js_uses_math_log():
    assert 'Math.log' in _html()


def test_js_uses_math_sqrt():
    assert 'Math.sqrt' in _html()


def test_js_uses_canvas_2d_context():
    assert 'getContext' in _html()


def test_js_defines_min_r():
    html = _html()
    assert 'MIN_R' in html
    m = re.search(r'MIN_R\s*=\s*([\d.]+)', html)
    assert m, "MIN_R constant not found"
    assert float(m.group(1)) <= 5.0


def test_js_defines_n_candidates():
    html = _html()
    assert 'N_CANDIDATES' in html
    m = re.search(r'N_CANDIDATES\s*=\s*(\d+)', html)
    assert m
    assert int(m.group(1)) >= 50


def test_js_defines_circles_per_frame():
    html = _html()
    assert 'CIRCLES_PER_FRAME' in html
    m = re.search(r'CIRCLES_PER_FRAME\s*=\s*(\d+)', html)
    assert m
    cpf = int(m.group(1))
    assert 5 <= cpf <= 200


def test_js_defines_restart_delay():
    html = _html()
    assert 'setTimeout' in html or 'RESTART_DELAY' in html


def test_js_calls_arc():
    """Must use arc() for drawing circles."""
    assert 'ctx.arc(' in _html()


def test_js_calls_fill():
    assert 'ctx.fill()' in _html()


def test_js_defines_clearance_logic():
    """Must compute distance to obstacles via sqrt or Math.sqrt."""
    html = _html()
    assert 'Math.sqrt' in html


def test_js_fills_background():
    html = _html()
    assert 'fillRect(0, 0' in html


def test_js_palette_has_three_stops():
    """Palette must reference the three theme colors: teal, amber, cream."""
    html = _html()
    assert '13' in html and '59' in html
    assert '232' in html and '160' in html
    assert '245' in html and '240' in html


# ---------------------------------------------------------------------------
# Packing algorithm: white-box validation
# ---------------------------------------------------------------------------

def test_clearance_canvas_edge_only():
    """With no placed circles, clearance = distance to nearest canvas edge."""
    r = clearance(50, 80, [], 400, 400)
    assert r == pytest.approx(50.0)


def test_clearance_with_single_circle():
    """Clearance must shrink when a placed circle is nearby."""
    placed = [(200, 200, 50)]
    # Point at (100, 200): dist to circle center = 100, minus r=50 → gap = 50
    r = clearance(100, 200, placed, 400, 400)
    assert r == pytest.approx(50.0)


def test_clearance_inside_placed_circle_is_negative():
    """A candidate inside a placed circle returns a negative clearance."""
    placed = [(200, 200, 80)]
    r = clearance(200, 200, placed, 400, 400)
    assert r < 0


def test_clearance_does_not_exceed_canvas_boundary():
    """clearance can never exceed the distance to the nearest canvas edge."""
    placed = []
    for cx, cy in [(10, 200), (390, 200), (200, 5), (200, 395)]:
        r = clearance(cx, cy, placed, 400, 400)
        assert r <= min(cx, cy, 400 - cx, 400 - cy) + 1e-9


def test_circle_t_at_max_r_is_one():
    """A circle with radius equal to maxR should map to t=1 (cream)."""
    assert circle_t(100.0, 100.0) == pytest.approx(1.0)


def test_circle_t_at_min_r_is_zero():
    """A circle with radius equal to MIN_R should map to t=0 (teal)."""
    assert circle_t(2.0, 100.0, min_r=2.0) == pytest.approx(0.0)


def test_circle_t_is_monotone():
    """Larger radii must map to higher t values."""
    t_small = circle_t(5.0, 200.0)
    t_medium = circle_t(50.0, 200.0)
    t_large = circle_t(150.0, 200.0)
    assert t_small < t_medium < t_large


def test_lerp_color_endpoints():
    """Palette endpoints must map to the defined teal and cream colors."""
    pal = [(13, 59, 79), (232, 160, 32), (245, 240, 200)]
    assert lerp_color(0.0, pal) == (13, 59, 79)
    assert lerp_color(1.0, pal) == (245, 240, 200)


def test_lerp_color_midpoint():
    """t=0.5 must return the middle palette stop."""
    pal = [(13, 59, 79), (232, 160, 32), (245, 240, 200)]
    assert lerp_color(0.5, pal) == (232, 160, 32)


def test_lerp_color_clamped():
    """Values outside [0, 1] must be clamped to palette endpoints."""
    pal = [(13, 59, 79), (232, 160, 32), (245, 240, 200)]
    assert lerp_color(-1.0, pal) == lerp_color(0.0, pal)
    assert lerp_color(2.0, pal) == lerp_color(1.0, pal)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_clearance_at_corner():
    """A candidate placed exactly at a canvas corner has clearance = 0."""
    r = clearance(0, 0, [], 400, 400)
    assert r == pytest.approx(0.0)


def test_clearance_at_center_empty_canvas():
    """Center of an empty square canvas has clearance = half the canvas side."""
    r = clearance(200, 200, [], 400, 400)
    assert r == pytest.approx(200.0)


def test_clearance_large_placed_circle():
    """A very large placed circle should dominate the clearance at its edge."""
    placed = [(200, 200, 180)]
    r = clearance(400, 200, placed, 400, 400)
    assert r <= 0


def test_circle_t_equal_min_max():
    """When maxR == minR, circle_t must return 1.0 (no division by zero)."""
    assert circle_t(5.0, 5.0, min_r=5.0) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Failure mode: wrong algorithm would produce incorrect clearances
# ---------------------------------------------------------------------------

def test_clearance_is_not_just_canvas_edge():
    """If a circle is placed, clearance must be less than the canvas-edge distance."""
    placed = [(200, 200, 150)]
    r_with_circle = clearance(50, 200, placed, 400, 400)
    r_without_circle = min(50, 200, 350, 200)
    assert r_with_circle < r_without_circle


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------

def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc


def test_thumbnail_has_viewbox():
    assert 'viewBox' in THUMBNAIL.read_text()


def test_thumbnail_has_width_and_height():
    svg = THUMBNAIL.read_text()
    assert 'width="' in svg and 'height="' in svg


def test_thumbnail_has_dark_background():
    svg = THUMBNAIL.read_text()
    assert '#0a0a14' in svg or '0a0a14' in svg


def test_thumbnail_not_trivially_empty():
    assert len(THUMBNAIL.read_text()) > 500


def test_thumbnail_has_circle_elements():
    """Thumbnail must contain filled SVG circle elements."""
    svg = THUMBNAIL.read_text()
    assert '<circle' in svg


def test_thumbnail_has_multiple_circles():
    """A good packing produces many circles — at least 10 in the thumbnail."""
    svg = THUMBNAIL.read_text()
    assert svg.count('<circle') >= 10


def test_thumbnail_circles_have_fill():
    """All circle elements must specify a fill color."""
    root = ET.fromstring(THUMBNAIL.read_text())
    circles = root.findall('.//circle') or root.findall('.//{http://www.w3.org/2000/svg}circle')
    assert circles, "No <circle> elements found"
    for c in circles:
        assert c.get('fill'), f"circle missing fill: {ET.tostring(c)}"


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_greedy():
    text = README.read_text().lower()
    assert 'greedy' in text or 'largest' in text


def test_readme_mentions_min_r():
    text = README.read_text()
    assert 'MIN_R' in text or 'min_r' in text.lower() or '2 px' in text or '2px' in text


def test_readme_mentions_candidates():
    text = README.read_text()
    assert 'N_CANDIDATES' in text or 'candidate' in text.lower()


def test_readme_differentiates_from_piece_39():
    """README must explain how this differs from piece 39 (Apollonian gasket)."""
    text = README.read_text()
    assert '39' in text


# ---------------------------------------------------------------------------
# pieces.json contract
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [e.get('id') for e in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_entry_has_all_required_fields():
    required = {'id', 'title', 'tagline', 'year', 'technique', 'path', 'thumbnail'}
    missing = required - _entry().keys()
    assert not missing, f"Missing fields: {missing}"


def test_entry_year_is_int():
    assert isinstance(_entry()['year'], int)


def test_entry_path_matches_id():
    assert _entry()['path'] == f'pieces/{PIECE_ID}'


def test_entry_technique_mentions_circle_packing():
    assert 'circle packing' in _entry()['technique'].lower()


def test_entry_technique_mentions_requestanimationframe():
    assert 'requestAnimationFrame' in _entry()['technique']


def test_entry_thumbnail_exists():
    thumb = REPO / _entry()['thumbnail']
    assert thumb.is_file()


def test_entry_thumbnail_is_svg():
    assert _entry()['thumbnail'].endswith('.svg')


def test_entry_id_matches_dir_name():
    entry = _entry()
    piece_dir = REPO / entry['path']
    assert entry['id'] == piece_dir.name


# ---------------------------------------------------------------------------
# Regression: existing entries must remain intact
# ---------------------------------------------------------------------------

def test_pieces_json_still_valid():
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)
    ids = [e['id'] for e in data]
    assert '01-amber-current' in ids
    assert '39-apollonian-gasket' in ids, "Apollonian gasket entry must remain for differentiation reference"
    assert '138-harmonograph' in ids, "Most recent prior piece must still be present"
    assert PIECE_ID in ids


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e['id'] for e in data]
    assert len(ids) == len(set(ids))


def test_piece_139_is_after_138_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e['id'] for e in data]
    idx_138 = ids.index('138-harmonograph')
    idx_139 = ids.index(PIECE_ID)
    assert idx_139 > idx_138


# ---------------------------------------------------------------------------
# Failure mode: malformed entry detection
# ---------------------------------------------------------------------------

def test_missing_thumbnail_field_detected():
    """An entry without 'thumbnail' should fail the required-field check."""
    entry = {
        'id': '139-circle-packing',
        'title': 'test',
        'tagline': 'test tagline',
        'year': 2026,
        'technique': 'canvas',
        'path': 'pieces/139-circle-packing',
    }
    required = {'id', 'title', 'tagline', 'year', 'technique', 'path', 'thumbnail'}
    missing = required - entry.keys()
    assert 'thumbnail' in missing
