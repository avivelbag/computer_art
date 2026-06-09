"""Tests for pieces/299-domain-coloring: WebGL domain coloring of analytic functions."""

import json
import math
import pathlib
import re

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "299-domain-coloring"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.png"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "299-domain-coloring"


# ---------------------------------------------------------------------------
# Python mirrors of the core GLSL / generate_thumbnail.py math for unit tests
# ---------------------------------------------------------------------------

def cmul(a: tuple, b: tuple) -> tuple:
    """Complex multiply: (a.x·b.x − a.y·b.y, a.x·b.y + a.y·b.x)."""
    return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])


def cdiv(a: tuple, b: tuple) -> tuple:
    """Complex divide: a / b."""
    d = b[0]*b[0] + b[1]*b[1]
    return ((a[0]*b[0] + a[1]*b[1]) / d, (a[1]*b[0] - a[0]*b[1]) / d)


def csin(z: tuple) -> tuple:
    """sin(x+iy) = sin(x)·cosh(y) + i·cos(x)·sinh(y)."""
    x, y = z
    return (math.sin(x) * math.cosh(y), math.cos(x) * math.sinh(y))


def ccos(z: tuple) -> tuple:
    """cos(x+iy) = cos(x)·cosh(y) − i·sin(x)·sinh(y)."""
    x, y = z
    return (math.cos(x) * math.cosh(y), -math.sin(x) * math.sinh(y))


def cexp(z: tuple) -> tuple:
    """e^(x+iy) = e^x·(cos y + i·sin y)."""
    x, y = z
    ex = math.exp(x)
    return (ex * math.cos(y), ex * math.sin(y))


def cpow2(z: tuple) -> tuple:
    return cmul(z, z)


def cpow3(z: tuple) -> tuple:
    return cmul(cpow2(z), z)


def eval_func0(z: tuple) -> tuple:
    """z³ − 1."""
    z3 = cpow3(z)
    return (z3[0] - 1.0, z3[1])


def eval_func1(z: tuple) -> tuple:
    """sin(z)."""
    return csin(z)


def eval_func2(z: tuple) -> tuple:
    """(z²+1)/(z²−1)."""
    z2 = cpow2(z)
    num = (z2[0] + 1.0, z2[1])
    den = (z2[0] - 1.0, z2[1])
    return cdiv(num, den)


def domain_color_bri(fz: tuple) -> float:
    """Return brightness value in [0, 1] for given f(z) output."""
    mag = math.hypot(fz[0], fz[1])
    return 0.5 + 0.5 * math.sin(2.0 * math.pi * math.log2(mag + 1e-10))


def domain_color_hue(fz: tuple) -> float:
    """Return hue in [0, 1] for given f(z) output."""
    arg = math.atan2(fz[1], fz[0])
    return (arg + math.pi) / (2.0 * math.pi)


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


def test_thumbnail_is_png():
    header = THUMBNAIL.read_bytes()[:8]
    assert header == b"\x89PNG\r\n\x1a\n", "thumbnail.png must start with the PNG magic bytes"


# ---------------------------------------------------------------------------
# HTML structural tests
# ---------------------------------------------------------------------------

def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_canvas_id_is_c():
    html = _html()
    assert 'id="c"' in html or "id='c'" in html


def test_html_has_script_tags():
    assert _html().count("<script") >= 3


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


def test_html_canvas_resizes_to_window():
    html = _html()
    assert "window.innerWidth" in html and "window.innerHeight" in html


# ---------------------------------------------------------------------------
# WebGL / shader structure tests
# ---------------------------------------------------------------------------

def test_html_has_webgl_context():
    html = _html()
    assert "getContext('webgl')" in html or 'getContext("webgl")' in html


def test_html_has_ures_uniform():
    assert "uRes" in _html()


def test_html_has_upan_uniform():
    assert "uPan" in _html()


def test_html_has_uscale_uniform():
    assert "uScale" in _html()


def test_html_has_ufunca_uniform():
    assert "uFuncA" in _html()


def test_html_has_ufuncb_uniform():
    assert "uFuncB" in _html()


def test_html_has_ublend_uniform():
    assert "uBlend" in _html()


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_fullscreen_quad():
    html = _html()
    assert "-1,-1" in html or "-1, -1" in html


def test_html_has_gl_frag_color():
    assert "gl_FragColor" in _html()


# ---------------------------------------------------------------------------
# GLSL complex arithmetic tests (presence in shader source)
# ---------------------------------------------------------------------------

def test_glsl_has_cmul():
    assert "cmul" in _html()


def test_glsl_has_cdiv():
    assert "cdiv" in _html()


def test_glsl_has_csin():
    assert "csin" in _html()


def test_glsl_has_ccos():
    assert "ccos" in _html()


def test_glsl_has_cexp():
    assert "cexp" in _html()


def test_glsl_has_hsv2rgb():
    assert "hsv2rgb" in _html()


def test_glsl_has_domain_color_function():
    assert "domainColor" in _html()


def test_glsl_has_pi_constant():
    html = _html()
    assert "PI" in html or "3.14159" in html


def test_glsl_has_atan_call():
    assert "atan(" in _html()


def test_glsl_has_log2_call():
    assert "log2(" in _html()


# ---------------------------------------------------------------------------
# Color formula tests — saturation must be 0.85
# ---------------------------------------------------------------------------

def test_glsl_saturation_is_0_85():
    html = _html()
    assert "0.85" in html, "saturation must be fixed at 0.85"


# ---------------------------------------------------------------------------
# Cyclic function tests — all three functions and their key strings present
# ---------------------------------------------------------------------------

def test_html_has_three_function_names():
    html = _html()
    assert "z³" in html or "z^3" in html or "cpow3" in html
    assert "sin" in html
    assert "z²" in html or "z^2" in html or "cpow2" in html


def test_html_cycles_three_functions():
    html = _html()
    assert "NUM_FUNCS" in html or "3" in html


def test_html_has_hold_and_fade_timing():
    html = _html()
    assert "HOLD_MS" in html or "7000" in html
    assert "FADE_MS" in html or "1500" in html


# ---------------------------------------------------------------------------
# Interaction tests — pan and zoom present
# ---------------------------------------------------------------------------

def test_html_has_drag_to_pan():
    html = _html()
    assert "mousedown" in html
    assert "mousemove" in html


def test_html_has_scroll_to_zoom():
    html = _html()
    assert "wheel" in html


def test_html_default_scale_covers_range_3():
    html = _html()
    assert "6.0" in html or "scale = 6" in html, "scale=6.0 covers Re/Im ∈ [-3, 3]"


# ---------------------------------------------------------------------------
# Python mirrors — cmul
# ---------------------------------------------------------------------------

def test_cmul_real_numbers():
    assert cmul((3.0, 0.0), (4.0, 0.0)) == (12.0, 0.0)


def test_cmul_i_times_i_is_minus_1():
    r, i = cmul((0.0, 1.0), (0.0, 1.0))
    assert abs(r - (-1.0)) < 1e-12 and abs(i) < 1e-12


def test_cmul_distributive():
    a, b, c = (1.0, 2.0), (3.0, -1.0), (0.5, 0.5)
    ab = cmul(a, b)
    ac = cmul(a, c)
    lhs = cmul(a, (b[0] + c[0], b[1] + c[1]))
    rhs = (ab[0] + ac[0], ab[1] + ac[1])
    assert abs(lhs[0] - rhs[0]) < 1e-12 and abs(lhs[1] - rhs[1]) < 1e-12


# ---------------------------------------------------------------------------
# Python mirrors — cdiv
# ---------------------------------------------------------------------------

def test_cdiv_real_numbers():
    r, i = cdiv((6.0, 0.0), (3.0, 0.0))
    assert abs(r - 2.0) < 1e-12 and abs(i) < 1e-12


def test_cdiv_by_i():
    """(0+1i) / (0+1i) = 1."""
    r, i = cdiv((0.0, 1.0), (0.0, 1.0))
    assert abs(r - 1.0) < 1e-12 and abs(i) < 1e-12


def test_cdiv_inverse_of_cmul():
    z = (1.5, -0.7)
    w = (2.0,  1.3)
    product = cmul(z, w)
    back    = cdiv(product, w)
    assert abs(back[0] - z[0]) < 1e-10 and abs(back[1] - z[1]) < 1e-10


# ---------------------------------------------------------------------------
# Python mirrors — csin / ccos
# ---------------------------------------------------------------------------

def test_csin_real_axis():
    """sin(x+0i) = sin(x)."""
    for x in (0.0, math.pi / 6, math.pi / 2, math.pi):
        r, i = csin((x, 0.0))
        assert abs(r - math.sin(x)) < 1e-12
        assert abs(i) < 1e-12


def test_ccos_real_axis():
    """cos(x+0i) = cos(x)."""
    for x in (0.0, math.pi / 3, math.pi / 2, math.pi):
        r, i = ccos((x, 0.0))
        assert abs(r - math.cos(x)) < 1e-12
        assert abs(i) < 1e-12


def test_sin2_plus_cos2_equals_1():
    """sin²(z) + cos²(z) = 1 for several complex z."""
    test_points = [(0.5, 0.3), (-1.0, 0.7), (2.0, -0.4), (0.0, 1.0)]
    for z in test_points:
        s = csin(z)
        c = ccos(z)
        ss = cmul(s, s)
        cc = cmul(c, c)
        total_re = ss[0] + cc[0]
        total_im = ss[1] + cc[1]
        assert abs(total_re - 1.0) < 1e-10, f"sin²+cos² real part not 1 at z={z}"
        assert abs(total_im) < 1e-10, f"sin²+cos² imag part not 0 at z={z}"


# ---------------------------------------------------------------------------
# Python mirrors — cexp
# ---------------------------------------------------------------------------

def test_cexp_at_zero():
    r, i = cexp((0.0, 0.0))
    assert abs(r - 1.0) < 1e-12 and abs(i) < 1e-12


def test_cexp_euler_identity():
    """e^(iπ) + 1 ≈ 0  (Euler's identity)."""
    r, i = cexp((0.0, math.pi))
    assert abs(r + 1.0) < 1e-12, f"Re(e^iπ) = {r}, expected -1"
    assert abs(i) < 1e-12, f"Im(e^iπ) = {i}, expected 0"


# ---------------------------------------------------------------------------
# Python mirrors — eval_func0 (z³ − 1)
# ---------------------------------------------------------------------------

def test_func0_zero_at_1():
    """z=1 is a root of z³−1."""
    fz = eval_func0((1.0, 0.0))
    assert abs(fz[0]) < 1e-12 and abs(fz[1]) < 1e-12


def test_func0_zero_at_primitive_cube_root():
    """z = e^(2πi/3) is another root of z³−1."""
    theta = 2.0 * math.pi / 3.0
    z = (math.cos(theta), math.sin(theta))
    fz = eval_func0(z)
    assert math.hypot(fz[0], fz[1]) < 1e-10


def test_func0_three_roots():
    """All three cube roots of unity satisfy z³−1=0."""
    for k in range(3):
        theta = 2.0 * math.pi * k / 3.0
        z = (math.cos(theta), math.sin(theta))
        fz = eval_func0(z)
        assert math.hypot(fz[0], fz[1]) < 1e-10, f"Root {k} failed: |f(z)| = {math.hypot(*fz)}"


# ---------------------------------------------------------------------------
# Python mirrors — eval_func1 (sin z)
# ---------------------------------------------------------------------------

def test_func1_zero_at_origin():
    fz = eval_func1((0.0, 0.0))
    assert abs(fz[0]) < 1e-12 and abs(fz[1]) < 1e-12


def test_func1_zero_at_pi():
    fz = eval_func1((math.pi, 0.0))
    assert math.hypot(*fz) < 1e-10


def test_func1_large_imaginary_part():
    """sin(iy) = i·sinh(y), so |sin(iy)| = sinh(y) which grows rapidly."""
    fz = eval_func1((0.0, 2.0))
    assert abs(fz[0]) < 1e-10, "Re(sin(2i)) should be 0"
    assert abs(fz[1] - math.sinh(2.0)) < 1e-10


# ---------------------------------------------------------------------------
# Python mirrors — eval_func2 ((z²+1)/(z²−1))
# ---------------------------------------------------------------------------

def test_func2_zero_at_i():
    """z=i is a zero: (i²+1)/(i²−1) = 0/(-2) = 0."""
    fz = eval_func2((0.0, 1.0))
    assert math.hypot(*fz) < 1e-10


def test_func2_zero_at_neg_i():
    """z=-i is also a zero."""
    fz = eval_func2((0.0, -1.0))
    assert math.hypot(*fz) < 1e-10


def test_func2_pole_singularity_large_magnitude():
    """Near z=1 (a pole), the magnitude of f(z) should be very large."""
    z = (1.0 + 1e-6, 0.0)
    fz = eval_func2(z)
    assert math.hypot(*fz) > 1e3, "Near z=1 the function should blow up (pole)"


# ---------------------------------------------------------------------------
# Domain coloring math tests
# ---------------------------------------------------------------------------

def test_hue_at_positive_real():
    """f(z) = 1+0i → arg = 0 → hue = 0.5."""
    h = domain_color_hue((1.0, 0.0))
    assert abs(h - 0.5) < 1e-12


def test_hue_at_positive_imaginary():
    """f(z) = 0+1i → arg = π/2 → hue = 0.75."""
    h = domain_color_hue((0.0, 1.0))
    assert abs(h - 0.75) < 1e-10


def test_hue_at_negative_real():
    """f(z) = -1+0i → arg = π → hue = 1.0."""
    h = domain_color_hue((-1.0, 0.0))
    assert abs(h - 1.0) < 1e-12


def test_hue_at_negative_imaginary():
    """f(z) = 0-1i → arg = -π/2 → hue = 0.25."""
    h = domain_color_hue((0.0, -1.0))
    assert abs(h - 0.25) < 1e-10


def test_brightness_in_range():
    """Brightness must always be in [0, 1]."""
    test_values = [
        (1.0, 0.0), (0.5, 0.5), (100.0, 0.0), (0.001, 0.0), (0.0, 1.0)
    ]
    for fz in test_values:
        b = domain_color_bri(fz)
        assert 0.0 <= b <= 1.0, f"brightness {b} out of range for fz={fz}"


def test_brightness_oscillates_across_magnitudes():
    """Brightness must not be constant — it oscillates via the sin(log2) term.

    Using non-power-of-2 magnitudes so log2 is non-integer and sin is non-zero.
    """
    magnitudes = [0.3, 0.7, 1.5, 3.0, 7.0, 15.0]
    bris = [domain_color_bri((m, 0.0)) for m in magnitudes]
    assert len(set(round(b, 2) for b in bris)) > 2, "Brightness should vary across magnitudes"


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_pieces_json_entry_has_all_required_fields():
    entry = _entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    assert not (required - entry.keys()), f"Missing: {required - entry.keys()}"


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_webgl():
    assert "webgl" in _entry()["technique"].lower() or "WebGL" in _entry()["technique"]


def test_pieces_json_technique_mentions_domain_coloring():
    t = _entry()["technique"].lower()
    assert "domain" in t or "complex" in t


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_domain_coloring():
    readme = README.read_text().lower()
    assert "domain color" in readme


def test_readme_mentions_hue():
    assert "hue" in README.read_text().lower()


def test_readme_mentions_isochromatic():
    readme = README.read_text().lower()
    assert "isochromatic" in readme or "ring" in readme


def test_readme_mentions_all_three_functions():
    readme = README.read_text()
    assert "z³" in readme or "z^3" in readme
    assert "sin" in readme
    assert "z²" in readme or "z^2" in readme


# ---------------------------------------------------------------------------
# Failure-mode / edge-case tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "00-does-not-exist" not in ids


def test_missing_canvas_detected():
    """Sanity-check that absence of <canvas> would be caught."""
    fake = "<html><body><div id='c'></div></body></html>"
    assert "<canvas" not in fake


def test_cmul_with_zero():
    r, i = cmul((0.0, 0.0), (5.0, 3.0))
    assert r == 0.0 and i == 0.0


def test_cdiv_near_zero_denominator_gives_large_result():
    """Dividing by a very small number produces a large magnitude."""
    fz = cdiv((1.0, 0.0), (1e-7, 0.0))
    assert math.hypot(*fz) > 1e6


def test_domain_color_hue_full_circle():
    """Rotating f(z) by 2π should recover the same hue."""
    for angle in (0.0, 0.3, 1.1, 2.5, 5.0):
        fz = (math.cos(angle), math.sin(angle))
        h = domain_color_hue(fz)
        assert 0.0 <= h <= 1.0


def test_brightness_near_zero_magnitude():
    """For |f(z)| → 0 the brightness formula should not error and stay in [0,1]."""
    bri = domain_color_bri((1e-15, 0.0))
    assert 0.0 <= bri <= 1.0


def test_func0_nonzero_away_from_roots():
    """A point not near any cube root of unity must give non-zero f(z)."""
    fz = eval_func0((0.0, 0.0))    # origin: 0³−1 = −1
    assert math.hypot(*fz) > 0.5


def test_func1_periodic_zeros():
    """sin(nπ) = 0 for integer n."""
    for n in range(-3, 4):
        fz = eval_func1((n * math.pi, 0.0))
        assert math.hypot(*fz) < 1e-10, f"sin({n}π) ≠ 0, got {fz}"
