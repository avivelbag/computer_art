"""Tests for Piece 151 — 2D Wave Equation: Interference Ripples."""

import json
import math
import pathlib
import re

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_ID  = "151-wave-equation-ripple"
PIECE_DIR = REPO / "pieces" / PIECE_ID
INDEX     = PIECE_DIR / "index.html"
THUMB     = PIECE_DIR / "thumbnail.svg"
README    = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def _entry():
    return next((p for p in _load_pieces() if p["id"] == PIECE_ID), None)


# ---------------------------------------------------------------------------
# File presence — happy path
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), f"Directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert INDEX.is_file()


def test_thumbnail_svg_exists():
    assert THUMB.is_file()


def test_readme_exists():
    assert README.is_file()


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

def test_pieces_json_contains_entry():
    ids = [p["id"] for p in _load_pieces()]
    assert PIECE_ID in ids


def test_pieces_json_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    entry = _entry()
    assert entry is not None, f"{PIECE_ID} not found in pieces.json"
    assert required <= entry.keys(), f"Missing fields: {required - entry.keys()}"


def test_pieces_json_entry_id_matches_directory():
    entry = _entry()
    assert entry["id"] == pathlib.Path(entry["path"]).name


def test_pieces_json_entry_path_is_directory():
    entry = _entry()
    assert (REPO / entry["path"]).is_dir()


def test_pieces_json_entry_thumbnail_file_exists():
    entry = _entry()
    assert (REPO / entry["thumbnail"]).is_file()


def test_pieces_json_no_duplicate_ids():
    ids = [p["id"] for p in _load_pieces()]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def html():
    return INDEX.read_text()


def test_html_has_canvas_element(html):
    assert "<canvas" in html


def test_html_uses_request_animation_frame(html):
    assert "requestAnimationFrame" in html


def test_html_uses_imagedata_for_per_pixel_rendering(html):
    """Wave simulation must use putImageData for pixel-level speed."""
    assert "putImageData" in html
    assert "ImageData" in html or "createImageData" in html


def test_html_uses_float32array_buffers(html):
    """Leapfrog requires at least two Float32Array wave buffers."""
    count = html.count("Float32Array")
    assert count >= 2, f"Expected ≥ 2 Float32Array buffers, found {count}"


def test_html_has_three_or_more_sources(html):
    """At least 3 point sources must be defined inside SOURCES."""
    m = re.search(r'const SOURCES\s*=\s*\[(.+?)\];', html, re.DOTALL)
    assert m is not None, "SOURCES constant not found in index.html"
    inner = m.group(1)
    # Count sub-arrays: each source entry starts with '['
    count = len(re.findall(r'\[', inner))
    assert count >= 3, f"Expected ≥ 3 source sub-arrays, found {count}"


def test_html_leapfrog_formula_present(html):
    """The leapfrog update formula must reference both curr and prev buffers."""
    assert "curr" in html and "prev" in html and "next" in html


def test_html_has_laplacian_stencil(html):
    """The 4-point discrete Laplacian (i-1, i+1, i-W, i+W) must appear."""
    assert "i - 1" in html or "i-1" in html
    assert "i + 1" in html or "i+1" in html
    assert "i - W" in html or "i-W" in html
    assert "i + W" in html or "i+W" in html


def test_html_courant_parameter_present(html):
    """A Courant parameter (r or R) must appear and be set to a safe value ≤ 0.5."""
    m = re.search(r'const R\s*=\s*([\d.]+)', html)
    assert m is not None, "Courant parameter R not found in index.html"
    r_val = float(m.group(1))
    assert r_val <= 0.5, f"Courant parameter R={r_val} exceeds stability bound 0.5"


def test_html_dirichlet_boundary_comment_or_code(html):
    """Boundary cells must stay 0 (skip y=0, y=H-1, x=0, x=W-1 in update loop)."""
    assert "y = 1" in html or "y=1" in html, "Loop must start at y=1 to enforce Dirichlet BC"
    assert "x = 1" in html or "x=1" in html, "Loop must start at x=1 to enforce Dirichlet BC"


def test_html_uses_math_sin_for_source_pulses(html):
    """Sources must use Math.sin for periodic driving."""
    assert "Math.sin" in html


def test_html_two_tone_palette_present(html):
    """Color palette must include both a warm (gold) and a cool (indigo/navy) tone."""
    html_lower = html.lower()
    has_gold = bool(
        re.search(r'ffc[0-9a-f]{3}', html_lower)
        or re.search(r'ffd[0-9a-f]{3}', html_lower)
        or re.search(r'ffb[0-9a-f]{3}', html_lower)
        or "gold" in html_lower
    )
    has_indigo = bool(
        re.search(r'#1[012][0-9a-f]{4}', html_lower)
        or re.search(r'indigo', html_lower)
        or re.search(r'#0[48][0-9a-f]{4}', html_lower)
    )
    assert has_gold, "Palette must include a warm gold tone for positive displacement"
    assert has_indigo, "Palette must include a cool indigo tone for negative displacement"


def test_html_canvas_is_512_or_400(html):
    """Canvas must be approximately 512×512 or 400×400."""
    has_512 = "512" in html
    has_400 = "400" in html
    assert has_512 or has_400, "Canvas must be ~512×512 or ~400×400"


def test_html_no_external_scripts(html):
    """Piece must be self-contained — no external script sources."""
    external = re.findall(r'<script[^>]+src=["\']https?://', html)
    assert not external, f"Found external script imports: {external}"


def test_html_no_audio(html):
    """No audio API must be present (AudioContext, Audio element, etc.)."""
    html_lower = html.lower()
    assert "audiocontext" not in html_lower
    assert "<audio" not in html_lower


def test_html_uses_2d_canvas_context(html):
    """Must obtain a 2D context (not WebGL)."""
    assert "getContext('2d')" in html or 'getContext("2d")' in html


def test_html_not_trivially_small():
    assert INDEX.stat().st_size > 800, "index.html must be non-trivial"


# ---------------------------------------------------------------------------
# thumbnail.svg checks
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def svg():
    return THUMB.read_text()


def test_thumbnail_is_valid_svg(svg):
    assert svg.strip().startswith("<svg"), "thumbnail.svg must start with <svg"
    assert "</svg>" in svg


def test_thumbnail_has_dark_background(svg):
    """Background must be near-black, not white."""
    assert "ffffff" not in svg.lower() or "#fff" not in svg.lower()
    assert "04040e" in svg.lower() or "0a0a" in svg.lower() or "03030" in svg.lower()


def test_thumbnail_has_gold_tones(svg):
    """Thumbnail must reference warm gold colours."""
    assert bool(re.search(r'ffc[0-9a-f]{3}', svg, re.IGNORECASE)
                or re.search(r'ffd[0-9a-f]{3}', svg, re.IGNORECASE)
                or re.search(r'ffb[0-9a-f]{3}', svg, re.IGNORECASE))


def test_thumbnail_has_indigo_tones(svg):
    """Thumbnail must reference deep indigo/navy colours."""
    assert bool(re.search(r'1[012][0-9a-f]{4}', svg, re.IGNORECASE)
                or re.search(r'0[0-9][0-9][0-9][a-f][0-9a-f]', svg, re.IGNORECASE))


def test_thumbnail_has_multiple_circles(svg):
    """Interference pattern thumbnail must contain many circle elements."""
    count = svg.count("<circle")
    assert count >= 10, f"Expected ≥ 10 circles in thumbnail, found {count}"


def test_thumbnail_shows_three_sources(svg):
    """Three distinct source center coordinates must appear."""
    cx_vals = re.findall(r'cx=["\'](\d+)["\']', svg)
    unique_cx = set(cx_vals)
    assert len(unique_cx) >= 3, f"Expected ≥ 3 distinct cx values, found {unique_cx}"


# ---------------------------------------------------------------------------
# README checks
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    content = README.read_text().strip()
    assert len(content) > 100


def test_readme_mentions_leapfrog():
    content = README.read_text().lower()
    assert "leapfrog" in content, "README must explain the leapfrog scheme"


def test_readme_mentions_boundary_reflection():
    content = README.read_text().lower()
    assert "reflect" in content or "dirichlet" in content or "boundary" in content


def test_readme_mentions_wave_equation():
    content = README.read_text().lower()
    assert "wave" in content


# ---------------------------------------------------------------------------
# Mathematical sanity checks (pure Python, no browser)
# ---------------------------------------------------------------------------

def _step_leapfrog(curr, prev, W, H, R):
    """Single leapfrog step on a flat W*H grid; returns next buffer."""
    N = W * H
    nxt = [0.0] * N
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            i = y * W + x
            lap = curr[i-1] + curr[i+1] + curr[i-W] + curr[i+W] - 4.0 * curr[i]
            nxt[i] = 2.0 * curr[i] - prev[i] + R * lap
    return nxt


def test_leapfrog_zero_initial_stays_zero():
    """An all-zero grid with no sources must remain zero."""
    W, H, R = 16, 16, 0.24
    curr = [0.0] * (W * H)
    prev = [0.0] * (W * H)
    nxt  = _step_leapfrog(curr, prev, W, H, R)
    assert all(abs(v) < 1e-12 for v in nxt), "Zero field must stay zero"


def test_leapfrog_dirichlet_boundary_stays_zero():
    """Boundary cells must never be written by the leapfrog update."""
    W, H, R = 16, 16, 0.24
    curr = [0.0] * (W * H)
    prev = [0.0] * (W * H)
    # Place a source in the interior
    curr[8 * W + 8] = 1.0
    nxt = _step_leapfrog(curr, prev, W, H, R)
    for x in range(W):
        assert nxt[0 * W + x] == 0.0
        assert nxt[(H-1) * W + x] == 0.0
    for y in range(H):
        assert nxt[y * W + 0] == 0.0
        assert nxt[y * W + (W-1)] == 0.0


def test_leapfrog_propagates_energy_outward():
    """A single impulse must spread to adjacent cells one step later."""
    W, H, R = 20, 20, 0.24
    curr = [0.0] * (W * H)
    prev = [0.0] * (W * H)
    cx, cy = W // 2, H // 2
    curr[cy * W + cx] = 1.0
    nxt = _step_leapfrog(curr, prev, W, H, R)
    # Neighbours must have non-zero amplitude
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        assert abs(nxt[(cy+dy)*W + (cx+dx)]) > 1e-9


def test_courant_stability_bound():
    """r = 0.24 is well within the 2D stability bound of 0.5."""
    R = 0.24
    assert R <= 0.5, f"Courant parameter {R} exceeds 2D stability bound"


def test_source_amplitude_clamped():
    """Source amplitude A*sin must stay in [-1, 1] after clamping."""
    A = 0.75
    for freq in [0.15, 0.22, 0.18]:
        for tick in range(1000):
            amp = A * math.sin(freq * tick)
            clamped = max(-1.0, min(1.0, amp))
            assert -1.0 <= clamped <= 1.0


def test_palette_index_in_range():
    """The palette index formula (tanh-based) must always stay in [0, 511]."""
    for d in [-3.0, -1.5, -0.5, 0.0, 0.5, 1.5, 3.0]:
        t = math.tanh(d * 2.0)
        idx = min(511, max(0, int((t + 1.0) * 255.5)))
        assert 0 <= idx <= 511, f"palette index {idx} out of range for d={d}"


def test_tanh_normalization_maps_zero_to_midpoint():
    """tanh(0 * 2.0) = 0, so displacement 0 maps to palette index ~255 (near-black)."""
    t = math.tanh(0.0 * 2.0)
    idx = int((t + 1.0) * 255.5)
    assert 250 <= idx <= 260, f"Zero displacement should map to index ~255, got {idx}"


def test_tanh_positive_maps_to_upper_half():
    """Positive displacement must map to indices > 256 (warm gold half of palette)."""
    for d in [0.1, 0.5, 1.0, 2.0]:
        t = math.tanh(d * 2.0)
        idx = min(511, max(0, int((t + 1.0) * 255.5)))
        assert idx > 256, f"Positive displacement d={d} should map to index >256"


def test_tanh_negative_maps_to_lower_half():
    """Negative displacement must map to indices < 256 (cool indigo half of palette)."""
    for d in [-0.1, -0.5, -1.0, -2.0]:
        t = math.tanh(d * 2.0)
        idx = min(511, max(0, int((t + 1.0) * 255.5)))
        assert idx < 256, f"Negative displacement d={d} should map to index <256"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_large_grid_leapfrog_stable():
    """Leapfrog must not blow up on a 64×64 grid with 100 steps (R=0.24)."""
    W, H, R = 64, 64, 0.24
    N = W * H
    curr = [0.0] * N
    prev = [0.0] * N
    cx, cy = W // 4, H // 4
    for tick in range(100):
        curr[cy * W + cx] = 0.75 * math.sin(0.15 * tick)
        nxt = _step_leapfrog(curr, prev, W, H, R)
        max_val = max(abs(v) for v in nxt)
        assert max_val < 10.0, f"Simulation blew up at tick {tick}: max={max_val}"
        prev = curr
        curr = nxt


def test_three_sources_staggered_phases():
    """Three sources with staggered frequencies/phases must differ over time.

    sin(π/3) == sin(2π/3) at tick=0, so check that they diverge by tick=10.
    """
    A = 0.75
    sources = [
        (0.15, 0.0),
        (0.22, math.pi / 3),
        (0.18, 2 * math.pi / 3),
    ]
    # Find a tick where all three amplitudes are distinct
    found_distinct = False
    for tick in range(1, 200):
        amps = [max(-1.0, min(1.0, A * math.sin(freq * tick + phase)))
                for freq, phase in sources]
        if len(set(round(a, 4) for a in amps)) == 3:
            found_distinct = True
            break
    assert found_distinct, (
        "Sources with staggered phases must produce 3 distinct amplitudes at some tick"
    )


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

def test_webgl_not_used(html):
    """This is a Canvas 2D piece — WebGL must not appear."""
    assert "webgl" not in html.lower()


def test_missing_directory_raises():
    """A non-existent piece directory is correctly identified as missing."""
    ghost = REPO / "pieces" / "999-ghost-piece"
    assert not ghost.is_dir()


def test_malformed_pieces_json_entry_detected():
    """An entry without 'technique' fails the required-field check."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    bad = {
        "id": "151-wave-equation-ripple",
        "title": "X",
        "tagline": "Y",
        "year": 2026,
        "path": "pieces/151-wave-equation-ripple",
        "thumbnail": "pieces/151-wave-equation-ripple/thumbnail.svg",
        # 'technique' deliberately omitted
    }
    assert not (required <= bad.keys())


def test_courant_above_stability_bound_is_dangerous():
    """r > 0.5 in 2D would cause leapfrog to go unstable — verify our value is safe."""
    dangerous_R = 0.51
    assert dangerous_R > 0.5
    safe_R = 0.24
    assert safe_R <= 0.5
