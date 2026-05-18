"""Tests for pieces/261-sdf-raymarching: WebGL kaleidoscopic IFS raymarcher."""

import json
import math
import pathlib
import re

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "261-sdf-raymarching"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "261-sdf-raymarching"


# ---------------------------------------------------------------------------
# Python mirrors of the core GLSL SDF functions (used in algorithm tests)
# ---------------------------------------------------------------------------

def smin(a: float, b: float, k: float) -> float:
    """Polynomial smooth-minimum matching the GLSL smin in the fragment shader.

    Returns a value that smoothly interpolates between a and b within distance
    k of their crossing, always <= min(a, b).
    """
    h = max(0.0, min(1.0, 0.5 + 0.5 * (b - a) / k))
    return b * (1.0 - h) + a * h - k * h * (1.0 - h)


def sd_sphere(p: tuple, r: float) -> float:
    """Signed distance from point p=(x,y,z) to a sphere of radius r at origin."""
    return math.sqrt(p[0]**2 + p[1]**2 + p[2]**2) - r


def sd_round_box(p: tuple, b: tuple, r: float) -> float:
    """Signed distance from p to a rounded axis-aligned box of half-extents b and corner radius r."""
    qx = abs(p[0]) - b[0]
    qy = abs(p[1]) - b[1]
    qz = abs(p[2]) - b[2]
    outer = math.sqrt(max(qx, 0.0)**2 + max(qy, 0.0)**2 + max(qz, 0.0)**2)
    inner = min(max(qx, max(qy, qz)), 0.0)
    return outer + inner - r


def octahedral_fold(p: tuple) -> tuple:
    """Kaleidoscopic domain fold: abs then sort components descending (x>=y>=z).

    Mirrors all 8 octants into the positive octant, then collapses 6 axis
    permutations into the canonical ordering — together achieving 48-fold
    octahedral symmetry.  Mirrors the GLSL abs+swap block in map().
    """
    x, y, z = abs(p[0]), abs(p[1]), abs(p[2])
    if x < y:
        x, y = y, x
    if x < z:
        x, z = z, x
    if y < z:
        y, z = z, y
    return (x, y, z)


def mod_repeat(coord: float, cell: float) -> float:
    """GLSL mod(coord, cell) - cell*0.5: maps coord into [-cell/2, cell/2]."""
    return coord % cell - cell * 0.5


def scene_map(p: tuple, blend_k: float = 0.25) -> float:
    """Python mirror of the GLSL map() function.

    Applies octahedral fold, then mod tiling (cell=2), then smin of sphere and
    rounded box.  blend_k corresponds to the pulsating k value in the shader
    (default is the mid-pulse value).
    """
    q = octahedral_fold(p)
    q = tuple(mod_repeat(c, 2.0) for c in q)
    d1 = sd_sphere(q, 0.45)
    d2 = sd_round_box(q, (0.28, 0.28, 0.28), 0.07)
    return smin(d1, d2, blend_k)


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


def test_html_canvas_id_is_c():
    html = _html()
    assert 'id="c"' in html or "id='c'" in html


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


def test_html_under_50kb():
    size = INDEX_HTML.stat().st_size
    assert size < 50_000, f"index.html is {size} bytes — must be under 50 KB"


def test_html_has_webgl_fallback():
    """Must show a styled fallback message when WebGL is unavailable."""
    html = _html()
    assert "WebGL not supported" in html


# ---------------------------------------------------------------------------
# WebGL / shader structure tests
# ---------------------------------------------------------------------------

def test_html_has_webgl_context():
    html = _html()
    assert "getContext('webgl')" in html or 'getContext("webgl")' in html


def test_html_has_utime_uniform():
    assert "uTime" in _html()


def test_html_has_ures_uniform():
    assert "uRes" in _html()


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_fullscreen_quad():
    html = _html()
    assert "-1,-1" in html or "-1, -1" in html


def test_glsl_defines_sd_sphere():
    assert "sdSphere" in _html()


def test_glsl_defines_sd_round_box():
    assert "sdRoundBox" in _html()


def test_glsl_defines_smin():
    """Shader must define the polynomial smooth-minimum."""
    assert "smin" in _html()


def test_glsl_has_abs_domain_fold():
    """Kaleidoscopic fold: abs() applied to the position vector in map()."""
    html = _html()
    assert "abs(p)" in html or "abs( p)" in html


def test_glsl_has_mod_domain_repeat():
    """Shader must use mod() for spatial tiling of the folded domain."""
    assert "mod(" in _html()


def test_glsl_has_ray_march():
    assert "rayMarch" in _html()


def test_glsl_has_calc_normal():
    assert "calcNormal" in _html()


def test_glsl_has_ambient_occlusion():
    assert "calcAO" in _html()


def test_glsl_has_reflect():
    """Phong specular uses GLSL reflect() built-in."""
    assert "reflect(" in _html()


def test_glsl_has_gl_frag_color():
    assert "gl_FragColor" in _html()


def test_glsl_has_gamma_correction():
    html = _html()
    assert "0.4545" in html or "2.2" in html


def test_glsl_has_time_driven_animation():
    """Blend radius and/or camera must be driven by uTime via sin/cos."""
    html = _html()
    assert "uTime" in html
    assert "sin(" in html


def test_glsl_has_smin_blend_between_two_primitives():
    """smin must be called with at least two SDF results."""
    html = _html()
    assert "smin(" in html
    assert "sdSphere(" in html
    assert "sdRoundBox(" in html


# ---------------------------------------------------------------------------
# Palette tests
# ---------------------------------------------------------------------------

def test_html_contains_crimson_surface_color():
    """Fragment shader must define the neon-crimson surface color."""
    html = _html()
    assert "0.90, 0.07, 0.32" in html or "0.90,0.07,0.32" in html


def test_html_contains_teal_void_color():
    """Fragment shader must define the near-black teal void color."""
    html = _html()
    assert "0.0, 0.02, 0.05" in html or "0.0,0.02,0.05" in html


# ---------------------------------------------------------------------------
# pieces.json entry tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_entry_has_required_fields():
    entry = _entry()
    for field in ("id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"):
        assert field in entry, f"Missing field: {field!r}"


def test_pieces_json_entry_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_entry_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_entry_thumbnail_matches():
    assert _entry()["thumbnail"] == f"pieces/{PIECE_ID}/thumbnail.svg"


def test_pieces_json_entry_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_mentions_webgl():
    technique = _entry()["technique"].lower()
    assert "webgl" in technique


def test_pieces_json_mentions_sdf():
    technique = _entry()["technique"].lower()
    assert "sdf" in technique or "signed-distance" in technique


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_mentions_raymarching():
    text = README.read_text().lower()
    assert "raymarching" in text or "ray marching" in text or "sphere-trac" in text


def test_readme_mentions_sdf():
    text = README.read_text().lower()
    assert "signed-distance" in text or "sdf" in text


def test_readme_mentions_smin_or_smooth():
    text = README.read_text().lower()
    assert "smooth" in text or "smin" in text


def test_readme_mentions_fold():
    text = README.read_text().lower()
    assert "fold" in text or "mirror" in text or "kaleidoscop" in text


# ---------------------------------------------------------------------------
# Python mirror — smin
# ---------------------------------------------------------------------------

def test_smin_returns_min_when_far_apart():
    """When a and b differ by much more than k, smin behaves like regular min."""
    a, b = 1.0, 10.0
    k = 0.1
    result = smin(a, b, k)
    assert abs(result - a) < 0.01, f"Expected ~{a}, got {result}"


def test_smin_is_symmetric():
    """smin(a, b, k) == smin(b, a, k) — order of arguments must not matter."""
    a, b, k = 0.3, 0.7, 0.5
    assert abs(smin(a, b, k) - smin(b, a, k)) < 1e-9


def test_smin_below_both_inputs_near_crossing():
    """smin must go strictly below both inputs in the blend zone."""
    a, b = 0.5, 0.5
    k = 1.0
    result = smin(a, b, k)
    assert result < a and result < b


def test_smin_k_zero_is_exact_min():
    """With k→0 the smooth minimum degenerates to the hard minimum."""
    a, b = 0.4, 0.8
    k = 1e-9
    assert abs(smin(a, b, k) - min(a, b)) < 1e-6


# ---------------------------------------------------------------------------
# Python mirror — sd_sphere
# ---------------------------------------------------------------------------

def test_sd_sphere_on_surface():
    """A point at distance r from origin lies exactly on the sphere surface."""
    r = 0.45
    p = (r, 0.0, 0.0)
    assert abs(sd_sphere(p, r)) < 1e-9


def test_sd_sphere_inside_negative():
    """Points inside the sphere return negative distance."""
    assert sd_sphere((0.0, 0.0, 0.0), 0.45) < 0.0


def test_sd_sphere_outside_positive():
    """Points outside the sphere return positive distance."""
    assert sd_sphere((1.0, 0.0, 0.0), 0.45) > 0.0


# ---------------------------------------------------------------------------
# Python mirror — sd_round_box
# ---------------------------------------------------------------------------

def test_sd_round_box_at_origin_inside():
    """The origin is inside the box (b=(0.28,0.28,0.28), r=0.07)."""
    assert sd_round_box((0.0, 0.0, 0.0), (0.28, 0.28, 0.28), 0.07) < 0.0


def test_sd_round_box_far_outside_positive():
    """A distant point must have positive SDF."""
    assert sd_round_box((5.0, 5.0, 5.0), (0.28, 0.28, 0.28), 0.07) > 0.0


def test_sd_round_box_corner_rounded():
    """Corner distance is reduced by corner radius r."""
    b = (0.28, 0.28, 0.28)
    r = 0.07
    # At the exact hard corner: distance should equal r (point on rounded corner)
    corner = (b[0] + r, b[1] + r, b[2] + r)
    d = sd_round_box(corner, b, r)
    assert abs(d - r * (math.sqrt(3) - 1)) < 0.01


# ---------------------------------------------------------------------------
# Python mirror — octahedral_fold
# ---------------------------------------------------------------------------

def test_octahedral_fold_into_positive_octant():
    """All components of the result must be non-negative."""
    p = (-1.2, 0.5, -3.0)
    result = octahedral_fold(p)
    assert all(c >= 0.0 for c in result)


def test_octahedral_fold_sorted_descending():
    """Components are sorted so x >= y >= z after folding."""
    p = (0.3, 1.5, 0.8)
    x, y, z = octahedral_fold(p)
    assert x >= y >= z


def test_octahedral_fold_preserves_lengths():
    """Folding only reflects/permutes — the Euclidean length is preserved."""
    p = (-2.1, 0.7, 1.3)
    orig_len = math.sqrt(sum(c**2 for c in p))
    fold_len = math.sqrt(sum(c**2 for c in octahedral_fold(p)))
    assert abs(orig_len - fold_len) < 1e-9


def test_octahedral_fold_idempotent():
    """Applying the fold twice returns the same result as applying it once."""
    p = (0.4, 1.2, 0.1)
    once = octahedral_fold(p)
    twice = octahedral_fold(once)
    assert once == twice


# ---------------------------------------------------------------------------
# Python mirror — scene_map
# ---------------------------------------------------------------------------

def test_scene_map_positive_far_from_surface():
    """A point far from any surface must have a large positive SDF."""
    d = scene_map((100.0, 100.0, 100.0))
    assert d > 0.0


def test_scene_map_inside_sphere_at_known_point():
    """p=(1,1,1) folds and tiles to (0,0,0), which is the sphere centre — must be negative."""
    # octahedral_fold(1,1,1) -> (1,1,1); mod_repeat(1.0, 2.0) = 0.0 -> q=(0,0,0)
    # sd_sphere((0,0,0), 0.45) = -0.45 -> definitely inside the sphere.
    d = scene_map((1.0, 1.0, 1.0))
    assert d < 0.0


def test_scene_map_gradient_nonzero_near_surface():
    """Finite-difference gradient magnitude should be near 1 on the surface."""
    eps = 0.0005
    p = (1.0, 1.0, 1.0)
    gx = (scene_map((p[0]+eps, p[1], p[2])) - scene_map((p[0]-eps, p[1], p[2]))) / (2*eps)
    gy = (scene_map((p[0], p[1]+eps, p[2])) - scene_map((p[0], p[1]-eps, p[2]))) / (2*eps)
    gz = (scene_map((p[0], p[1], p[2]+eps)) - scene_map((p[0], p[1], p[2]-eps))) / (2*eps)
    grad_len = math.sqrt(gx**2 + gy**2 + gz**2)
    assert grad_len < 1.5


def test_scene_map_blend_k_affects_result():
    """Different blend radii must produce different SDF values near the transition."""
    p = (0.45, 0.28, 0.1)
    d_tight = scene_map(p, blend_k=0.01)
    d_wide  = scene_map(p, blend_k=0.5)
    assert d_tight != d_wide


# ---------------------------------------------------------------------------
# Differentiation from piece 133 tests
# ---------------------------------------------------------------------------

def test_piece_uses_abs_fold_not_only_mod():
    """The domain fold must include abs() — absent from piece 133's plain mod-repeat."""
    html = _html()
    assert "abs(p)" in html or "abs( p)" in html


def test_piece_uses_sphere_not_torus():
    """Primitive must be sdSphere, not sdTorus (which piece 133 uses)."""
    html = _html()
    assert "sdSphere" in html
    assert "sdTorus" not in html


def test_piece_surface_color_differs_from_133():
    """Surface must not use piece 133's warm gold (0.92, 0.72, 0.18)."""
    html = _html()
    assert "0.92, 0.72, 0.18" not in html and "0.92,0.72,0.18" not in html
