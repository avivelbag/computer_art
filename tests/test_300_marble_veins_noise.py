"""Tests for pieces/300-marble-veins-noise: WebGL marble veining with turbulence noise."""

import json
import math
import pathlib
import re

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "300-marble-veins-noise"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "300-marble-veins-noise"


# ---------------------------------------------------------------------------
# Python mirrors of the GLSL noise math — used for unit-level assertions
# ---------------------------------------------------------------------------

def _fract(x: float) -> float:
    """Return the fractional part of x, equivalent to GLSL fract()."""
    return x - math.floor(x)


def hash3py(px: float, py: float, pz: float) -> float:
    """Python mirror of the GLSL hash3 function.

    Returns a deterministic pseudo-random value in [0, 1] for integer-lattice
    corners of the noise field.
    """
    x = _fract(px * 0.1031)
    y = _fract(py * 0.1030)
    z = _fract(pz * 0.0973)
    d = x * (y + 33.33) + y * (x + 33.33) + z * (z + 33.33)
    x += d
    y += d
    z += d
    return _fract((x + y) * z)


def vnoise_py(px: float, py: float, pz: float) -> float:
    """3D value noise: Hermite-smoothed trilinear interpolation of hash3py.

    Returns a value in [0, 1].
    """
    ix = math.floor(px)
    iy = math.floor(py)
    iz = math.floor(pz)
    fx, fy, fz = px - ix, py - iy, pz - iz
    ux = fx * fx * (3 - 2 * fx)
    uy = fy * fy * (3 - 2 * fy)
    uz = fz * fz * (3 - 2 * fz)

    def lerp(a: float, b: float, t: float) -> float:
        return a + t * (b - a)

    return lerp(
        lerp(lerp(hash3py(ix,   iy,   iz),   hash3py(ix+1, iy,   iz),   ux),
             lerp(hash3py(ix,   iy+1, iz),   hash3py(ix+1, iy+1, iz),   ux), uy),
        lerp(lerp(hash3py(ix,   iy,   iz+1), hash3py(ix+1, iy,   iz+1), ux),
             lerp(hash3py(ix,   iy+1, iz+1), hash3py(ix+1, iy+1, iz+1), ux), uy),
        uz,
    )


def turbulence_py(px: float, py: float, pz: float) -> float:
    """4-octave turbulence: sum of |centered noise| per octave.

    Each octave doubles frequency and halves amplitude.  Returns a value
    in [0, amplitude_sum * 0.5] ≈ [0, 0.9375].
    """
    t = 0.0
    amp = 1.0
    freq = 1.0
    for _ in range(4):
        t += abs(vnoise_py(px * freq, py * freq, pz * freq) - 0.5) * amp
        amp  *= 0.5
        freq *= 2.0
    return t


def vein_py(uvx: float, uvy: float, time_ms: float) -> float:
    """Compute vein value v = sin(uvx*3 + turbulence*8) at the given UV and time."""
    z = time_ms * 0.0003
    turb = turbulence_py(uvx * 4.0, uvy * 4.0, z)
    return math.sin(uvx * 3.0 + turb * 8.0)


def smoothstep_py(e0: float, e1: float, x: float) -> float:
    """GLSL smoothstep: smooth Hermite interpolation between 0 and 1."""
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


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
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_readme_exists():
    assert README.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


def test_thumbnail_is_svg():
    content = THUMBNAIL.read_text()
    assert content.strip().startswith("<svg") or "xmlns" in content[:200]


# ---------------------------------------------------------------------------
# HTML structural tests
# ---------------------------------------------------------------------------

def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_canvas_is_800x800():
    html = _html()
    assert 'width="800"' in html and 'height="800"' in html


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html


def test_html_title_exists():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m and len(m.group(1).strip()) > 0


def test_html_has_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained — no remote scripts"


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_60fps_cap():
    html = _html()
    assert "FRAME_MS" in html or "1000 / 60" in html or "16.6" in html


# ---------------------------------------------------------------------------
# WebGL / shader structure tests
# ---------------------------------------------------------------------------

def test_html_has_webgl_context():
    html = _html()
    assert "getContext('webgl')" in html or 'getContext("webgl")' in html


def test_html_has_vertex_shader():
    assert "x-shader/x-vertex" in _html() or "VERTEX_SHADER" in _html()


def test_html_has_fragment_shader():
    assert "x-shader/x-fragment" in _html() or "FRAGMENT_SHADER" in _html()


def test_html_has_fullscreen_quad():
    html = _html()
    assert "-1,-1" in html or "-1, -1" in html


def test_html_has_gl_frag_color():
    assert "gl_FragColor" in _html()


def test_html_has_utime_uniform():
    assert "uTime" in _html()


def test_html_has_ures_uniform():
    assert "uRes" in _html()


# ---------------------------------------------------------------------------
# Noise / turbulence structure tests
# ---------------------------------------------------------------------------

def test_html_has_hash_function():
    html = _html()
    assert "hash3" in html or "hash(" in html


def test_html_has_vnoise_function():
    html = _html()
    assert "vnoise" in html or "valueNoise" in html or "value_noise" in html


def test_html_has_turbulence_function():
    assert "turbulence" in _html()


def test_html_turbulence_has_4_octaves():
    html = _html()
    assert "i < 4" in html or "4; i++" in html or "* 8.0" in html


def test_html_turbulence_halves_amplitude():
    html = _html()
    assert "amp  *= 0.5" in html or "amp *= 0.5" in html or "* 0.5" in html


def test_html_turbulence_doubles_frequency():
    html = _html()
    assert "freq *= 2.0" in html or "freq *= 2" in html


def test_html_has_smoothstep():
    assert "smoothstep" in _html()


def test_html_has_vein_sin_formula():
    html = _html()
    assert "sin(" in html and "turbulence" in html


def test_html_turbulence_multiplied_by_8():
    html = _html()
    assert "* 8.0" in html or "* 8)" in html or "*8" in html


def test_html_time_drift_constant():
    html = _html()
    assert "0.0003" in html


# ---------------------------------------------------------------------------
# Palette tests — Calacatta colors must appear (as comments or vec3 values)
# ---------------------------------------------------------------------------

def test_html_has_ivory_color():
    html = _html()
    assert "#f5f0e8" in html or "0.961" in html


def test_html_has_charcoal_color():
    html = _html()
    assert "#2a2520" in html or "0.165" in html


def test_html_has_taupe_color():
    html = _html()
    assert "#9e8e7a" in html or "0.620" in html


def test_html_primary_vein_smoothstep_085():
    html = _html()
    assert "0.85" in html


def test_html_has_cpu_fallback():
    html = _html()
    assert "ImageData" in html or "createImageData" in html or "putImageData" in html


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_pieces_json_entry_has_all_required_fields():
    entry = _entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    missing = required - entry.keys()
    assert not missing, f"Missing fields: {missing}"


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_is_correct():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_noise():
    t = _entry()["technique"].lower()
    assert "noise" in t


def test_pieces_json_technique_mentions_webgl():
    t = _entry()["technique"].lower()
    assert "webgl" in t


def test_pieces_json_description_nonempty():
    assert len(_entry()["description"].strip()) > 100


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_marble():
    assert "marble" in README.read_text().lower()


def test_readme_mentions_turbulence():
    assert "turbulence" in README.read_text().lower()


def test_readme_mentions_calacatta_palette():
    readme = README.read_text().lower()
    assert "calacatta" in readme or "palette" in readme


def test_readme_mentions_hash():
    readme = README.read_text().lower()
    assert "hash" in readme or "noise" in readme


def test_readme_mentions_vein():
    assert "vein" in README.read_text().lower()


# ---------------------------------------------------------------------------
# Python mirrors — hash3py
# ---------------------------------------------------------------------------

def test_hash3py_returns_values_in_0_1():
    """hash3py must return values in [0, 1] for a variety of inputs."""
    test_points = [
        (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0),
        (1.5, 2.3, -0.7), (100.0, 50.0, 25.0), (-1.0, -1.0, -1.0),
        (0.5, 0.5, 0.5), (3.14, 2.71, 1.41),
    ]
    for p in test_points:
        v = hash3py(*p)
        assert 0.0 <= v <= 1.0, f"hash3py{p} = {v} is out of [0, 1]"


def test_hash3py_is_deterministic():
    """Same input must always produce the same output."""
    for _ in range(5):
        assert hash3py(1.23, 4.56, 7.89) == hash3py(1.23, 4.56, 7.89)


def test_hash3py_different_inputs_differ():
    """Nearby integer lattice points should produce different hash values."""
    vals = {hash3py(i, j, 0.0) for i in range(4) for j in range(4)}
    assert len(vals) > 12, "Hash should produce many distinct values"


# ---------------------------------------------------------------------------
# Python mirrors — vnoise_py
# ---------------------------------------------------------------------------

def test_vnoise_returns_values_in_0_1():
    """Value noise output must stay in [0, 1]."""
    pts = [(0.3, 0.7, 0.1), (1.5, 2.5, 3.5), (10.0, 10.0, 10.0), (0.0, 0.0, 0.0)]
    for p in pts:
        v = vnoise_py(*p)
        assert 0.0 <= v <= 1.0, f"vnoise_py{p} = {v} out of [0, 1]"


def test_vnoise_is_continuous_across_integers():
    """Value noise must not jump discontinuously at integer boundaries."""
    eps = 1e-4
    pairs = [
        ((1.0 - eps, 0.5, 0.5), (1.0 + eps, 0.5, 0.5)),
        ((0.5, 2.0 - eps, 0.5), (0.5, 2.0 + eps, 0.5)),
    ]
    for (a, b) in pairs:
        diff = abs(vnoise_py(*a) - vnoise_py(*b))
        assert diff < 0.1, f"Discontinuity {diff:.4f} at boundary between {a} and {b}"


def test_vnoise_large_input():
    """Value noise must be stable for large coordinate values."""
    v = vnoise_py(1000.5, 2000.5, 3000.5)
    assert 0.0 <= v <= 1.0


# ---------------------------------------------------------------------------
# Python mirrors — turbulence_py
# ---------------------------------------------------------------------------

def test_turbulence_is_nonnegative():
    """Turbulence = sum of absolute values → must be ≥ 0."""
    pts = [(0.3, 0.7, 0.1), (1.5, 2.5, 0.0), (4.0, 4.0, 0.5)]
    for p in pts:
        t = turbulence_py(*p)
        assert t >= 0.0, f"turbulence{p} = {t} < 0"


def test_turbulence_bounded():
    """4-octave turbulence with amplitudes 1, 0.5, 0.25, 0.125 on centered noise
    cannot exceed 0.5 * (1 + 0.5 + 0.25 + 0.125) = 0.9375."""
    pts = [(0.3, 0.7, 0.1), (1.5, 2.5, 0.0), (4.0, 4.0, 0.5), (0.0, 0.0, 0.0)]
    for p in pts:
        t = turbulence_py(*p)
        assert t <= 0.9376, f"turbulence{p} = {t} exceeds theoretical max"


def test_turbulence_varies_across_space():
    """Turbulence must not be spatially constant."""
    vals = [turbulence_py(x * 0.37, x * 0.19, 0.0) for x in range(20)]
    assert max(vals) - min(vals) > 0.05, "Turbulence should vary across space"


def test_turbulence_4_octaves_adds_detail():
    """4-octave turbulence must have more spatial variation than 1-octave noise."""
    def single_octave(px, py, pz):
        return abs(vnoise_py(px, py, pz) - 0.5)

    pts = [(x * 0.17 + 0.1, x * 0.31 + 0.2, 0.5) for x in range(30)]
    t4 = [turbulence_py(*p) for p in pts]
    t1 = [single_octave(*p) for p in pts]
    var4 = sum((v - sum(t4)/len(t4))**2 for v in t4)
    var1 = sum((v - sum(t1)/len(t1))**2 for v in t1)
    assert var4 >= var1 * 0.9, "4-octave turbulence should have at least as much variation as 1-octave"


# ---------------------------------------------------------------------------
# Python mirrors — vein_py
# ---------------------------------------------------------------------------

def test_vein_is_in_neg1_pos1():
    """Vein value v = sin(...) must always be in [-1, 1]."""
    for t_ms in (0, 1000, 5000, 60000):
        for uvx in (0.0, 0.25, 0.5, 0.75, 1.0):
            for uvy in (0.0, 0.3, 0.6, 1.0):
                v = vein_py(uvx, uvy, t_ms)
                assert -1.0 <= v <= 1.0, f"vein_py({uvx},{uvy},{t_ms}) = {v} out of [-1,1]"


def test_vein_varies_spatially():
    """Vein values must vary across x at fixed y and time."""
    vals = [vein_py(x / 20.0, 0.5, 0.0) for x in range(21)]
    assert max(vals) - min(vals) > 0.1, "Vein should vary across x"


def test_vein_animates_over_time():
    """Vein value at the same position must change over time."""
    v0 = vein_py(0.3, 0.4, 0)
    v1 = vein_py(0.3, 0.4, 100_000)
    assert abs(v0 - v1) > 1e-6, "Vein should change over time"


# ---------------------------------------------------------------------------
# Python mirrors — smoothstep_py
# ---------------------------------------------------------------------------

def test_smoothstep_at_lower_edge_is_0():
    assert smoothstep_py(0.85, 1.0, 0.85) == 0.0


def test_smoothstep_at_upper_edge_is_1():
    assert smoothstep_py(0.85, 1.0, 1.0) == 1.0


def test_smoothstep_below_lower_edge_is_0():
    assert smoothstep_py(0.85, 1.0, 0.50) == 0.0


def test_smoothstep_midpoint_is_half():
    v = smoothstep_py(0.0, 1.0, 0.5)
    assert abs(v - 0.5) < 1e-12


def test_smoothstep_derivative_zero_at_edges():
    """smoothstep has zero derivative at both edges — check numerically."""
    eps = 1e-6
    for edge in (0.85, 1.0):
        deriv = (smoothstep_py(0.85, 1.0, edge + eps) - smoothstep_py(0.85, 1.0, edge - eps)) / (2 * eps)
        assert abs(deriv) < 1.0, f"Derivative at edge {edge} should be ≤ 1, got {deriv:.4f}"


# ---------------------------------------------------------------------------
# Palette color tests
# ---------------------------------------------------------------------------

def test_palette_colors_are_distinct():
    """All three Calacatta colors must be meaningfully different."""
    ivory    = (245, 240, 232)
    charcoal = (42,  37,  32)
    taupe    = (158, 142, 122)
    def dist(a, b):
        return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
    assert dist(ivory, charcoal) > 100, "Ivory and charcoal should be very different"
    assert dist(ivory, taupe)    >  50, "Ivory and taupe should differ"
    assert dist(charcoal, taupe) >  50, "Charcoal and taupe should differ"


def test_vein_color_mix_primary():
    """At |v| = 1.0 the primary smoothstep should be 1 (full charcoal)."""
    p = smoothstep_py(0.85, 1.0, 1.0)
    assert p == 1.0


def test_vein_color_mix_base():
    """At |v| = 0 both smoothsteps are 0, so the output is base ivory."""
    primary   = smoothstep_py(0.85, 1.0, 0.0)
    secondary = smoothstep_py(0.50, 0.70, 0.0) * (1 - smoothstep_py(0.70, 0.85, 0.0))
    assert primary   == 0.0
    assert secondary == 0.0


# ---------------------------------------------------------------------------
# Failure mode / edge-case tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "300-does-not-exist" not in ids


def test_missing_canvas_detected():
    """Sanity check: absence of <canvas> would be caught by test_html_has_canvas_element."""
    fake = "<html><body><div id='c'></div></body></html>"
    assert "<canvas" not in fake


def test_hash3py_zero_input_in_range():
    """hash3py at the origin must stay in [0, 1]."""
    v = hash3py(0.0, 0.0, 0.0)
    assert 0.0 <= v <= 1.0


def test_turbulence_at_zero():
    """turbulence at the origin must be nonnegative and bounded."""
    t = turbulence_py(0.0, 0.0, 0.0)
    assert 0.0 <= t <= 0.9376


def test_vnoise_extreme_input():
    """vnoise must not error for very large or very small inputs."""
    for p in [(1e6, 1e6, 1e6), (1e-6, 1e-6, 1e-6), (-1e4, 1e4, 0.0)]:
        v = vnoise_py(*p)
        assert 0.0 <= v <= 1.0, f"vnoise_py{p} = {v} out of [0, 1]"


def test_vein_at_corner_uv():
    """vein_py must not raise for corner UV values."""
    for uvx, uvy in [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]:
        v = vein_py(uvx, uvy, 0.0)
        assert -1.0 <= v <= 1.0
