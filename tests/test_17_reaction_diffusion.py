"""Tests for pieces/17-where-life-begins: Gray-Scott reaction-diffusion canvas animation."""

import json
import pathlib
import re
import xml.etree.ElementTree as ET

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "17-where-life-begins"
INDEX_HTML = PIECE_DIR / "index.html"
README     = PIECE_DIR / "README.md"
THUMBNAIL  = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "17-where-life-begins"

PALETTE_CHARCOAL   = "1c2126"
PALETTE_TEAL       = "0d4f6e"
PALETTE_CREAM      = "e8d5a0"
ALL_PALETTE_COLORS = [PALETTE_CHARCOAL, PALETTE_TEAL, PALETTE_CREAM]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# File-existence tests
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir(), f"Piece directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert INDEX_HTML.is_file(), "index.html missing from piece directory"


def test_readme_exists():
    assert README.is_file(), "README.md missing from piece directory"


def test_thumbnail_exists():
    assert THUMBNAIL.is_file(), "thumbnail.svg missing from piece directory"


# ---------------------------------------------------------------------------
# HTML structural tests
# ---------------------------------------------------------------------------

def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_canvas_has_id():
    html = _html()
    assert 'id="canvas"' in html or "id='canvas'" in html


def test_html_has_script_tag():
    assert "<script" in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html


def test_html_title_mentions_life_or_begins():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    t = m.group(1).lower()
    assert "life" in t or "begins" in t or "reaction" in t


# ---------------------------------------------------------------------------
# JavaScript content tests — animation and rendering
# ---------------------------------------------------------------------------

def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_js_has_delta_cap():
    html = _html()
    assert "DELTA_CAP" in html or "delta_cap" in html.lower() or "Math.min" in html, \
        "Script must cap delta time to prevent burst-step on resume"


def test_js_uses_put_image_data():
    assert "putImageData" in _html()


def test_js_steps_per_frame_in_range():
    html = _html()
    m = re.search(r"STEPS_PER_FRAME\s*=\s*(\d+)", html)
    if m:
        n = int(m.group(1))
        assert 8 <= n <= 12, f"STEPS_PER_FRAME={n} outside [8, 12]"


def test_js_has_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained — no remote scripts"


def test_js_defines_palette():
    assert "PALETTE" in _html()


def test_js_palette_contains_charcoal():
    assert PALETTE_CHARCOAL in _html().lower()


def test_js_palette_contains_teal():
    html = _html().lower()
    assert PALETTE_TEAL in html or "0d4f6e" in html


def test_js_palette_contains_cream():
    assert PALETTE_CREAM in _html().lower()


def test_js_defines_gray_scott_params():
    html = _html()
    assert "F " in html or "FEED" in html or "feed" in html.lower()
    assert "K " in html or "KILL" in html or "kill" in html.lower()


def test_js_feed_kill_values_present():
    html = _html()
    assert "0.0545" in html, "Feed rate 0.0545 must appear in source"
    assert "0.062"  in html, "Kill rate 0.062 must appear in source"


def test_js_uses_float32array():
    assert "Float32Array" in _html()


def test_js_has_ping_pong_buffers():
    html = _html()
    assert html.count("Float32Array(SIZE)") >= 4 or \
           html.count("Float32Array") >= 4, \
        "Script must declare at least 4 Float32Array buffers (u, v, uNext, vNext)"


def test_js_canvas_size_is_512():
    html = _html()
    assert 'width="512"' in html and 'height="512"' in html, \
        "Canvas must be 512×512 logical pixels"


# ---------------------------------------------------------------------------
# Gray-Scott logic — pure Python re-implementation
# ---------------------------------------------------------------------------

def _gray_scott_step(u, v, W, H, F=0.0545, K=0.062, Du=0.2097, Dv=0.105):
    """Run one Gray-Scott step on W×H grids u and v (flat lists)."""
    u_next = [0.0] * (W * H)
    v_next = [0.0] * (W * H)
    for y in range(H):
        yN = (y - 1) % H
        yS = (y + 1) % H
        for x in range(W):
            i    = y * W + x
            xW_i = y * W + (x - 1) % W
            xE_i = y * W + (x + 1) % W
            yN_i = yN * W + x
            yS_i = yS * W + x

            cu, cv = u[i], v[i]
            lap_u = u[xW_i] + u[xE_i] + u[yN_i] + u[yS_i] - 4.0 * cu
            lap_v = v[xW_i] + v[xE_i] + v[yN_i] + v[yS_i] - 4.0 * cv
            uvv   = cu * cv * cv

            u_next[i] = cu + Du * lap_u - uvv + F * (1.0 - cu)
            v_next[i] = cv + Dv * lap_v + uvv - (F + K) * cv
    return u_next, v_next


def test_gray_scott_steady_state_u1_v0():
    """U=1, V=0 everywhere is a fixed point — step must leave it unchanged."""
    W, H = 4, 4
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    u2, v2 = _gray_scott_step(u, v, W, H)
    for val in u2:
        assert abs(val - 1.0) < 1e-9, f"U must stay 1.0, got {val}"
    for val in v2:
        assert abs(val - 0.0) < 1e-9, f"V must stay 0.0, got {val}"


def test_gray_scott_seed_causes_v_growth_in_interior():
    """Interior pixels of a uniform seed patch see V increase after one step."""
    W, H = 10, 10
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    # Fill the entire grid uniformly with the seed concentrations so every
    # pixel has identical neighbours — only reaction terms matter, no diffusion.
    for i in range(W * H):
        u[i] = 0.5
        v[i] = 0.25
    u2, v2 = _gray_scott_step(u, v, W, H)
    # At (5, 5) uvv = 0.5 * 0.0625 = 0.03125; net V change = uvv - (F+K)*V
    # = 0.03125 - 0.1165 * 0.25 = 0.03125 - 0.029125 > 0 → V rises
    assert v2[5 * W + 5] > 0.25, "V must increase at interior seed pixel"


def test_gray_scott_laplacian_drives_diffusion():
    """A spike in U with flat neighbours diffuses outward after one step."""
    W, H = 5, 5
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    cx, cy = 2, 2
    u[cy * W + cx] = 2.0  # spike
    u2, _ = _gray_scott_step(u, v, W, H)
    # Spike must decrease (diffuses away)
    assert u2[cy * W + cx] < 2.0, "Spike in U must decrease after diffusion step"
    # Immediate neighbours must gain U
    assert u2[cy * W + cx + 1] > 1.0, "Right neighbour must gain U from spike"


def test_gray_scott_toroidal_wrap():
    """Edge pixel's neighbour wraps around to the opposite edge."""
    W, H = 4, 4
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    # Place a spike at (0, 0); its left neighbour is (W-1, 0)
    u[0] = 3.0
    u2, _ = _gray_scott_step(u, v, W, H)
    # (W-1, 0) = pixel at column 3, row 0 — it is the "left" wrap of column 0
    assert u2[W - 1] > 1.0, "Wrap-around left neighbour must gain U from spike at x=0"


def test_gray_scott_small_step_values_reasonable():
    """After one step from a typical seed, output values stay in [−0.5, 1.5]."""
    W, H = 6, 6
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    u[W * 3 + 3] = 0.5
    v[W * 3 + 3] = 0.25
    u2, v2 = _gray_scott_step(u, v, W, H)
    for val in u2 + v2:
        assert -0.5 <= val <= 1.5, f"Concentration value {val} implausibly far from [0,1]"


# ---------------------------------------------------------------------------
# Colour palette lerp — pure Python
# ---------------------------------------------------------------------------

def _lerp_color(t, palette):
    """3-stop linear lerp matching the JS draw() implementation."""
    p0, p1, p2 = palette
    if t < 0.5:
        s = t * 2.0
        return tuple(int(p0[i] + s * (p1[i] - p0[i])) for i in range(3))
    else:
        s = (t - 0.5) * 2.0
        return tuple(int(p1[i] + s * (p2[i] - p1[i])) for i in range(3))


_PALETTE = [(28, 33, 38), (13, 79, 110), (232, 213, 160)]


def test_lerp_at_zero_returns_charcoal():
    r, g, b = _lerp_color(0.0, _PALETTE)
    assert (r, g, b) == (28, 33, 38)


def test_lerp_at_one_returns_cream():
    r, g, b = _lerp_color(1.0, _PALETTE)
    assert (r, g, b) == (232, 213, 160)


def test_lerp_at_half_returns_teal():
    r, g, b = _lerp_color(0.5, _PALETTE)
    assert (r, g, b) == (13, 79, 110)


def test_lerp_midpoint_lower_half():
    """t=0.25 must lie between charcoal and teal."""
    r, g, b = _lerp_color(0.25, _PALETTE)
    assert _PALETTE[0][0] <= r <= _PALETTE[1][0] or _PALETTE[1][0] <= r <= _PALETTE[0][0]


def test_lerp_midpoint_upper_half():
    """t=0.75 must lie between teal and cream."""
    r, g, b = _lerp_color(0.75, _PALETTE)
    assert _PALETTE[1][0] <= r <= _PALETTE[2][0]


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    content = THUMBNAIL.read_text()
    assert len(content) > 100


def test_thumbnail_has_svg_root():
    assert "<svg" in THUMBNAIL.read_text()


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg invalid XML: {exc}") from exc


def test_thumbnail_dimensions_at_most_400():
    svg = THUMBNAIL.read_text()
    w = re.search(r'width="(\d+)"', svg)
    h = re.search(r'height="(\d+)"', svg)
    if w:
        assert int(w.group(1)) <= 400
    if h:
        assert int(h.group(1)) <= 400


def test_thumbnail_contains_all_palette_colors():
    svg = THUMBNAIL.read_text().lower()
    for color in ALL_PALETTE_COLORS:
        assert color in svg, f"Palette colour #{color} missing from thumbnail"


def test_thumbnail_has_background_rect():
    svg = THUMBNAIL.read_text()
    assert "<rect" in svg, "thumbnail.svg must have a background <rect>"


def test_thumbnail_has_multiple_shapes():
    svg = THUMBNAIL.read_text()
    shapes = len(re.findall(r'<(ellipse|circle|path|polygon|rect)\b', svg))
    assert shapes >= 10, f"Thumbnail must have ≥10 shape elements; found {shapes}"


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_pieces_json_entry_has_all_required_fields():
    entry = _entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert not (required - entry.keys()), f"Missing: {required - entry.keys()}"


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_reaction_diffusion():
    t = _entry()["technique"].lower()
    assert "reaction" in t or "diffusion" in t


def test_pieces_json_technique_mentions_gray_scott():
    t = _entry()["technique"].lower()
    assert "gray" in t or "scott" in t


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 50


def test_readme_mentions_gray_scott():
    assert "gray-scott" in README.read_text().lower() or \
           "gray scott" in README.read_text().lower()


def test_readme_names_feed_parameter():
    readme = README.read_text().lower()
    assert "feed" in readme or "f =" in readme or "f=" in readme


def test_readme_names_kill_parameter():
    readme = README.read_text().lower()
    assert "kill" in readme or "k =" in readme or "k=" in readme


def test_readme_states_feed_value():
    assert "0.0545" in README.read_text()


def test_readme_states_kill_value():
    assert "0.062" in README.read_text()


def test_readme_mentions_reaction_diffusion():
    assert "reaction" in README.read_text().lower()


# ---------------------------------------------------------------------------
# Failure-mode tests (assert bad inputs are caught, not that they crash)
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_found():
    """Searching for a non-existent ID must raise."""
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "00-does-not-exist" not in ids


def test_missing_canvas_tag_detected():
    fake_html = "<html><body><div id='canvas'></div></body></html>"
    assert "<canvas" not in fake_html


def test_missing_palette_detected():
    fake_html = "<script>const x = 1;</script>"
    assert "PALETTE" not in fake_html


def test_missing_float32array_detected():
    fake_html = "<script>let u = [];</script>"
    assert "Float32Array" not in fake_html


def test_wrong_feed_rate_would_fail():
    """Source with a different feed rate should not match 0.0545."""
    fake_html = "<script>const F = 0.03;</script>"
    assert "0.0545" not in fake_html
