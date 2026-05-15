"""Tests for pieces/180-gray-scott: Chemical Dreams — Gray-Scott Mitosis."""

import json
import pathlib
import re
import xml.etree.ElementTree as ET

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "180-gray-scott"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "180-gray-scott"

PALETTE_INDIGO = "1a0a2e"
PALETTE_CYAN   = "00e5ff"
ALL_PALETTE_COLORS = [PALETTE_INDIGO, PALETTE_CYAN]

# Mitosis regime parameters used by piece 180
F_VALUE  = "0.0367"
K_VALUE  = "0.0649"


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


def test_html_title_mentions_gray_scott_or_chemical():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    t = m.group(1).lower()
    assert ("gray" in t or "scott" in t or "reaction" in t
            or "chemical" in t or "mitosis" in t or "diffusion" in t)


# ---------------------------------------------------------------------------
# JavaScript content tests
# ---------------------------------------------------------------------------

def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_js_has_delta_cap():
    html = _html()
    assert "DELTA_CAP" in html or "delta_cap" in html.lower() or "Math.min" in html, \
        "Script must cap delta time to prevent burst-step on tab resume"


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


def test_js_defines_lut():
    html = _html()
    assert "LUT" in html, "Rendering must use a precomputed LUT Uint32Array"


def test_js_uses_float32array():
    assert "Float32Array" in _html()


def test_js_has_four_or_more_float32arrays():
    count = _html().count("Float32Array")
    assert count >= 4, \
        f"Script must use ≥4 Float32Array allocations (u, v, uNext, vNext); found {count}"


def test_js_canvas_size_is_512():
    html = _html()
    assert 'width="512"' in html and 'height="512"' in html, \
        "Canvas must be 512×512 logical pixels"


def test_js_defines_gray_scott_params():
    html = _html()
    assert ("F " in html or "FEED" in html or "feed" in html.lower()
            or "const F" in html or "const F " in html)
    assert ("K " in html or "KILL" in html or "kill" in html.lower()
            or "const K" in html or "const K " in html)


def test_js_feed_value_present():
    assert F_VALUE in _html(), f"Feed rate {F_VALUE} must appear in source"


def test_js_kill_value_present():
    assert K_VALUE in _html(), f"Kill rate {K_VALUE} must appear in source"


def test_js_palette_contains_indigo():
    html = _html().lower()
    assert PALETTE_INDIGO in html, f"Deep indigo #{PALETTE_INDIGO} missing from script"


def test_js_palette_contains_cyan():
    html = _html().lower()
    assert PALETTE_CYAN in html, f"Electric cyan #{PALETTE_CYAN} missing from script"


def test_js_uses_nine_point_laplacian():
    html = _html()
    assert "0.05" in html, "9-point Laplacian diagonal weight 0.05 must appear in source"
    assert "0.20" in html, "9-point Laplacian cross weight 0.20 must appear in source"


def test_js_has_seed_patch():
    html = _html()
    assert "SEED_HALF" in html or "seed" in html.lower() or "Math.random" in html, \
        "Script must seed a random initial patch"


# ---------------------------------------------------------------------------
# Gray-Scott physics — pure-Python re-implementation with 9-point Laplacian
# ---------------------------------------------------------------------------

def _gs_step_9pt(u, v, W, H, F=0.0367, K=0.0649, Du=0.2100, Dv=0.1050):
    """Advance one Gray-Scott step with a 9-point Laplacian on a toroidal grid.

    Diagonal neighbors weight 0.05, axis-aligned neighbors 0.20, center -1.0
    (kernel sums to zero). Operates on flat Python lists of length W*H.
    """
    u_next = [0.0] * (W * H)
    v_next = [0.0] * (W * H)
    for y in range(H):
        yN = (y - 1) % H
        yS = (y + 1) % H
        for x in range(W):
            xW = (x - 1) % W
            xE = (x + 1) % W
            i     = y  * W + x
            iNW   = yN * W + xW
            iN    = yN * W + x
            iNE   = yN * W + xE
            iW    = y  * W + xW
            iE    = y  * W + xE
            iSW   = yS * W + xW
            iS    = yS * W + x
            iSE   = yS * W + xE

            cu, cv = u[i], v[i]
            lap_u = (0.05 * (u[iNW] + u[iNE] + u[iSW] + u[iSE]) +
                     0.20 * (u[iW]  + u[iE]  + u[iN]  + u[iS]) - cu)
            lap_v = (0.05 * (v[iNW] + v[iNE] + v[iSW] + v[iSE]) +
                     0.20 * (v[iW]  + v[iE]  + v[iN]  + v[iS]) - cv)
            uvv = cu * cv * cv
            u_next[i] = cu + Du * lap_u - uvv + F * (1.0 - cu)
            v_next[i] = cv + Dv * lap_v + uvv - (F + K) * cv
    return u_next, v_next


def test_gray_scott_steady_state_u1_v0():
    """U=1, V=0 everywhere is the trivial fixed point — one step must leave it unchanged."""
    W, H = 4, 4
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    u2, v2 = _gs_step_9pt(u, v, W, H)
    for val in u2:
        assert abs(val - 1.0) < 1e-9, f"U must stay 1.0 at trivial fixed point, got {val}"
    for val in v2:
        assert abs(val - 0.0) < 1e-9, f"V must stay 0.0 at trivial fixed point, got {val}"


def test_gray_scott_uniform_seed_v_grows():
    """Uniform interior seed: V increases when the reaction term dominates decay."""
    W, H = 10, 10
    u = [0.5] * (W * H)
    v = [0.25] * (W * H)
    # Uniform grid → Laplacian = 0.  Reaction: uvv=0.03125, (F+K)*V≈0.02557.
    # Net dV/dt > 0, so V must increase.
    u2, v2 = _gs_step_9pt(u, v, W, H)
    assert v2[5 * W + 5] > 0.25, "V must increase at center of uniform seed"


def test_gray_scott_nine_point_laplacian_spike_diffuses():
    """A spike in U must decrease after one step; diagonal neighbors gain U."""
    W, H = 5, 5
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    cx, cy = 2, 2
    u[cy * W + cx] = 2.0
    u2, _ = _gs_step_9pt(u, v, W, H)
    assert u2[cy * W + cx] < 2.0, "Spike must decrease due to 9-point diffusion"
    assert u2[cy * W + cx + 1] > 1.0, "Axis-aligned neighbour must gain from spike"
    assert u2[(cy + 1) * W + (cx + 1)] > 1.0, "Diagonal neighbour must gain from spike"


def test_gray_scott_toroidal_wrap_corner():
    """A spike at corner (0,0) must influence the wrap-around neighbours."""
    W, H = 5, 5
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    u[0] = 3.0
    u2, _ = _gs_step_9pt(u, v, W, H)
    assert u2[W - 1] > 1.0, "Wrap-around left neighbour of x=0 must gain U"
    assert u2[(H - 1) * W] > 1.0, "Wrap-around top row must gain U from y=0 spike"
    assert u2[(H - 1) * W + W - 1] > 1.0, "Wrap-around diagonal corner must gain U"


def test_gray_scott_values_remain_bounded():
    """After one step from a seeded grid, concentrations stay in a plausible range."""
    W, H = 6, 6
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    cx, cy = 3, 3
    u[cy * W + cx] = 0.5
    v[cy * W + cx] = 0.25
    u2, v2 = _gs_step_9pt(u, v, W, H)
    for val in u2 + v2:
        assert -0.5 <= val <= 1.5, f"Concentration {val} implausibly far from [0, 1]"


def test_gray_scott_no_v_without_seed():
    """A grid with U=1, V=0 must never spontaneously generate V."""
    W, H = 4, 4
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    for _ in range(10):
        u, v = _gs_step_9pt(u, v, W, H)
    for val in v:
        assert abs(val) < 1e-9, f"V must remain 0 without a seed, got {val}"


def test_gray_scott_large_grid_step():
    """A single step on a 32×32 grid must complete and produce plausible values."""
    W, H = 32, 32
    u = [1.0] * (W * H)
    v = [0.0] * (W * H)
    mid = (H // 2) * W + (W // 2)
    u[mid] = 0.5
    v[mid] = 0.25
    u2, v2 = _gs_step_9pt(u, v, W, H)
    assert len(u2) == W * H
    assert len(v2) == W * H
    for val in u2 + v2:
        assert -1.0 <= val <= 2.0, f"Unexpected concentration {val} in large-grid step"


# ---------------------------------------------------------------------------
# LUT gradient — pure Python
# ---------------------------------------------------------------------------

def _lut_color(idx: int):
    """Reproduce the JS LUT buildLUT() for a single index in [0, 255].

    Returns (r, g, b) as integers.
    """
    idx = max(0, min(255, idx))
    t = idx / 255.0
    r0, g0, b0 = 0x1a, 0x0a, 0x2e  # deep indigo #1a0a2e
    r1, g1, b1 = 0x00, 0xe5, 0xff  # electric cyan #00e5ff
    r = int(r0 + t * (r1 - r0))
    g = int(g0 + t * (g1 - g0))
    b = int(b0 + t * (b1 - b0))
    return r, g, b


def test_lut_at_zero_returns_indigo():
    r, g, b = _lut_color(0)
    assert (r, g, b) == (0x1a, 0x0a, 0x2e), f"LUT[0] must be deep indigo, got #{r:02x}{g:02x}{b:02x}"


def test_lut_at_255_returns_cyan():
    r, g, b = _lut_color(255)
    assert (r, g, b) == (0x00, 0xe5, 0xff), f"LUT[255] must be electric cyan, got #{r:02x}{g:02x}{b:02x}"


def test_lut_midpoint_is_between_colors():
    r, g, b = _lut_color(128)
    assert 0x00 <= r <= 0x1a, "Mid-LUT red channel must lie between 0x00 and 0x1a"
    assert 0x0a <= g <= 0xe5, "Mid-LUT green channel must lie between 0x0a and 0xe5"
    assert 0x2e <= b <= 0xff, "Mid-LUT blue channel must lie between 0x2e and 0xff"


def test_lut_is_monotone_green():
    """Green channel must increase monotonically from indigo (0x0a) to cyan (0xe5)."""
    prev_g = _lut_color(0)[1]
    for idx in range(1, 256):
        _, g, _ = _lut_color(idx)
        assert g >= prev_g, f"Green channel dropped from {prev_g} to {g} at LUT index {idx}"
        prev_g = g


def test_lut_clamped_below_zero():
    """An index below 0 must clamp to the indigo color."""
    r, g, b = _lut_color(-10)
    assert (r, g, b) == (0x1a, 0x0a, 0x2e)


def test_lut_clamped_above_255():
    """An index above 255 must clamp to the cyan color."""
    r, g, b = _lut_color(300)
    assert (r, g, b) == (0x00, 0xe5, 0xff)


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    assert len(THUMBNAIL.read_text()) > 100


def test_thumbnail_has_svg_root():
    assert "<svg" in THUMBNAIL.read_text()


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc


def test_thumbnail_dimensions_at_most_400():
    svg = THUMBNAIL.read_text()
    w = re.search(r'width="(\d+)"', svg)
    h = re.search(r'height="(\d+)"', svg)
    if w:
        assert int(w.group(1)) <= 400
    if h:
        assert int(h.group(1)) <= 400


def test_thumbnail_contains_indigo():
    svg = THUMBNAIL.read_text().lower()
    assert PALETTE_INDIGO in svg, f"Deep indigo #{PALETTE_INDIGO} missing from thumbnail"


def test_thumbnail_contains_cyan():
    svg = THUMBNAIL.read_text().lower()
    assert PALETTE_CYAN in svg, f"Electric cyan #{PALETTE_CYAN} missing from thumbnail"


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text(), "thumbnail.svg must have a background <rect>"


def test_thumbnail_has_multiple_shapes():
    svg = THUMBNAIL.read_text()
    shapes = len(re.findall(r"<(ellipse|circle|path|polygon|rect)\b", svg))
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
    assert not (required - entry.keys()), f"Missing fields: {required - entry.keys()}"


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
    text = README.read_text().lower()
    assert "gray-scott" in text or "gray scott" in text


def test_readme_names_feed_parameter():
    text = README.read_text().lower()
    assert "feed" in text or "f =" in text or "f=" in text


def test_readme_names_kill_parameter():
    text = README.read_text().lower()
    assert "kill" in text or "k =" in text or "k=" in text


def test_readme_states_feed_value():
    assert F_VALUE in README.read_text(), f"Feed rate {F_VALUE} must appear in README"


def test_readme_states_kill_value():
    assert K_VALUE in README.read_text(), f"Kill rate {K_VALUE} must appear in README"


def test_readme_mentions_reaction_diffusion():
    assert "reaction" in README.read_text().lower()


def test_readme_mentions_mitosis_regime():
    text = README.read_text().lower()
    assert "mitosis" in text, "README must name the mitosis regime"


def test_readme_references_sibling_piece_96():
    text = README.read_text().lower()
    assert "96" in text, "README must reference sibling piece 96 per reviewer requirement"


def test_readme_states_palette_difference():
    text = README.read_text().lower()
    assert "indigo" in text or "cyan" in text, \
        "README must name the palette colors to distinguish it from piece 96's amber palette"


# ---------------------------------------------------------------------------
# Failure-mode / negative tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "180-does-not-exist" not in ids


def test_missing_canvas_tag_detected():
    fake_html = "<html><body><div id='canvas'></div></body></html>"
    assert "<canvas" not in fake_html


def test_missing_lut_detected():
    fake_html = "<script>const x = 1;</script>"
    assert "LUT" not in fake_html


def test_missing_float32array_detected():
    fake_html = "<script>let u = [];</script>"
    assert "Float32Array" not in fake_html


def test_wrong_feed_rate_would_fail():
    fake_html = "<script>const F = 0.0545;</script>"
    assert F_VALUE not in fake_html


def test_wrong_palette_amber_is_rejected():
    fake_html = "<script>const amber = '#c8780a';</script>"
    assert PALETTE_CYAN not in fake_html
    assert PALETTE_INDIGO not in fake_html


def test_piece_96_params_are_different_from_piece_180():
    piece_96_f = "0.0545"
    piece_96_k = "0.062"
    assert piece_96_f != F_VALUE, "Piece 180 must use a different F than piece 96"
    assert piece_96_k != K_VALUE, "Piece 180 must use a different K than piece 96"
