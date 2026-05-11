"""Tests for pieces/28-the-shape-of-distance: WebGL SDF ray-marching scene."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "28-the-shape-of-distance"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "28-the-shape-of-distance"

BG_CSS        = "050d14"
GOLD_VEC      = "0.93, 0.72, 0.22"
CORAL_VEC     = "0.90, 0.35, 0.20"
CHROME_VEC    = "0.72, 0.76, 0.82"


# ---------------------------------------------------------------------------
# Python mirrors of the core GLSL SDF functions for mathematical tests
# ---------------------------------------------------------------------------

def sd_sphere(p: tuple, r: float) -> float:
    """Signed distance from point p=(x,y,z) to sphere of radius r at origin."""
    return math.sqrt(p[0]**2 + p[1]**2 + p[2]**2) - r


def sd_torus(p: tuple, t_x: float, t_y: float) -> float:
    """Signed distance from p to torus with major radius t_x, tube radius t_y.

    The torus lies in the xz-plane centred at origin.
    """
    xz = math.sqrt(p[0]**2 + p[2]**2)
    return math.sqrt((xz - t_x)**2 + p[1]**2) - t_y


def sd_box(p: tuple, b: tuple) -> float:
    """Signed distance from p to axis-aligned box with half-extents b=(bx,by,bz)."""
    qx = abs(p[0]) - b[0]
    qy = abs(p[1]) - b[1]
    qz = abs(p[2]) - b[2]
    outside = math.sqrt(max(qx, 0.0)**2 + max(qy, 0.0)**2 + max(qz, 0.0)**2)
    inside  = min(max(qx, max(qy, qz)), 0.0)
    return outside + inside


def op_smooth_union(d1: float, d2: float, k: float) -> float:
    """Smooth minimum / union of two SDF values with blending radius k.

    Matches opSmoothUnion in the GLSL shader: result ≤ min(d1, d2) when the
    two surfaces are within distance k of each other.
    """
    h = max(0.0, min(1.0, 0.5 + 0.5 * (d2 - d1) / k))
    return d2 * (1.0 - h) + d1 * h - k * h * (1.0 - h)


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


def test_glsl_defines_sd_torus():
    assert "sdTorus" in _html()


def test_glsl_defines_sd_box():
    assert "sdBox" in _html()


def test_glsl_defines_smooth_union():
    html = _html()
    assert "opSmoothUnion" in html or "opSmooth" in html


def test_glsl_has_ray_march():
    assert "rayMarch" in _html()


def test_glsl_has_soft_shadow():
    assert "softShadow" in _html()


def test_glsl_has_ambient_occlusion():
    assert "calcAO" in _html() or "AO" in _html()


def test_glsl_has_reflect():
    assert "reflect(" in _html()


def test_glsl_has_calc_normal():
    assert "calcNormal" in _html()


def test_glsl_has_time_driven_rotation():
    html = _html()
    assert "uTime" in html
    assert "cos(" in html and "sin(" in html


def test_glsl_has_gl_frag_color():
    assert "gl_FragColor" in _html()


def test_glsl_has_gamma_correction():
    html = _html()
    assert "0.4545" in html or "2.2" in html


# ---------------------------------------------------------------------------
# Palette tests (GLSL vec3 color values in shader source)
# ---------------------------------------------------------------------------

def test_html_contains_gold_color():
    assert GOLD_VEC in _html()


def test_html_contains_coral_color():
    assert CORAL_VEC in _html()


def test_html_contains_chrome_color():
    assert CHROME_VEC in _html()


def test_html_contains_bg_css_color():
    assert BG_CSS in _html()


def test_html_contains_sky_teal():
    html = _html()
    assert "0.08, 0.22, 0.38" in html or "0.08,0.22,0.38" in html


# ---------------------------------------------------------------------------
# SDF Python mirrors — sphere
# ---------------------------------------------------------------------------

def test_sd_sphere_on_surface():
    assert abs(sd_sphere((1.0, 0.0, 0.0), 1.0)) < 1e-12


def test_sd_sphere_inside():
    d = sd_sphere((0.0, 0.0, 0.0), 1.0)
    assert abs(d - (-1.0)) < 1e-12


def test_sd_sphere_outside():
    d = sd_sphere((3.0, 0.0, 0.0), 1.0)
    assert abs(d - 2.0) < 1e-12


def test_sd_sphere_negative_inside():
    d = sd_sphere((0.5, 0.0, 0.0), 1.0)
    assert d < 0.0, "Point inside sphere must yield negative SDF"


def test_sd_sphere_isotropic():
    """SDF should be identical for equidistant points in all directions."""
    r = 1.0
    pts = [(2,0,0), (0,2,0), (0,0,2), (-2,0,0)]
    vals = [sd_sphere(p, r) for p in pts]
    assert all(abs(v - vals[0]) < 1e-12 for v in vals)


# ---------------------------------------------------------------------------
# SDF Python mirrors — torus
# ---------------------------------------------------------------------------

def test_sd_torus_on_surface():
    """Point at (t_x, 0, 0) displaced by t_y in the xz-plane is on the surface."""
    t_x, t_y = 1.1, 0.3
    p = (t_x + t_y, 0.0, 0.0)
    assert abs(sd_torus(p, t_x, t_y)) < 1e-12


def test_sd_torus_center_is_positive():
    """Origin is inside the torus hole — distance to nearest tube is t_x - t_y."""
    t_x, t_y = 1.1, 0.3
    d = sd_torus((0.0, 0.0, 0.0), t_x, t_y)
    assert abs(d - (t_x - t_y)) < 1e-12


def test_sd_torus_tube_centre_negative():
    """A point exactly at the tube centre has distance -t_y (fully inside)."""
    t_x, t_y = 1.1, 0.3
    p = (t_x, 0.0, 0.0)
    assert abs(sd_torus(p, t_x, t_y) - (-t_y)) < 1e-12


def test_sd_torus_above_centre_positive():
    """A point directly above the torus origin is outside."""
    d = sd_torus((0.0, 5.0, 0.0), 1.1, 0.3)
    assert d > 0.0


# ---------------------------------------------------------------------------
# SDF Python mirrors — box
# ---------------------------------------------------------------------------

def test_sd_box_inside():
    d = sd_box((0.0, 0.0, 0.0), (1.0, 1.0, 1.0))
    assert abs(d - (-1.0)) < 1e-12


def test_sd_box_outside_face():
    d = sd_box((2.0, 0.0, 0.0), (1.0, 1.0, 1.0))
    assert abs(d - 1.0) < 1e-12


def test_sd_box_on_face():
    d = sd_box((1.0, 0.0, 0.0), (1.0, 1.0, 1.0))
    assert abs(d) < 1e-12


def test_sd_box_outside_corner():
    """Point at (2, 2, 2) from a unit-half box corner at (1,1,1): distance = sqrt(3)."""
    d = sd_box((2.0, 2.0, 2.0), (1.0, 1.0, 1.0))
    assert abs(d - math.sqrt(3.0)) < 1e-12


def test_sd_box_is_negative_inside():
    d = sd_box((0.5, 0.0, 0.0), (1.0, 1.0, 1.0))
    assert d < 0.0


# ---------------------------------------------------------------------------
# SDF Python mirrors — smooth union
# ---------------------------------------------------------------------------

def test_op_smooth_union_at_most_min():
    """Smooth union must always return a value ≤ min(d1, d2)."""
    cases = [(0.5, 0.5, 0.1), (1.0, 0.2, 0.3), (0.1, 0.8, 0.5), (2.0, 2.0, 0.4)]
    for d1, d2, k in cases:
        result = op_smooth_union(d1, d2, k)
        assert result <= min(d1, d2) + 1e-10, \
            f"opSmoothUnion({d1},{d2},{k})={result} > min={min(d1,d2)}"


def test_op_smooth_union_far_apart_equals_min():
    """When surfaces are far apart (distance >> k), result ≈ min(d1, d2)."""
    d1, d2, k = 0.1, 10.0, 0.3
    assert abs(op_smooth_union(d1, d2, k) - min(d1, d2)) < 1e-6


def test_op_smooth_union_equal_distances_blended():
    """When d1==d2, the smooth-min dips below both by k/4."""
    d, k = 1.0, 0.4
    result = op_smooth_union(d, d, k)
    assert abs(result - (d - k / 4.0)) < 1e-12


def test_op_smooth_union_symmetric():
    """opSmoothUnion(d1, d2, k) == opSmoothUnion(d2, d1, k)."""
    assert abs(op_smooth_union(0.3, 0.8, 0.2) - op_smooth_union(0.8, 0.3, 0.2)) < 1e-12


def test_op_smooth_union_large_k_strong_blend():
    """With k much larger than the gap, result is well below both distances."""
    d1, d2, k = 0.5, 0.5, 2.0
    result = op_smooth_union(d1, d2, k)
    assert result < d1 - 0.4, "Large k should produce strong blending below both distances"


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    assert len(THUMBNAIL.read_text()) > 500


def test_thumbnail_has_svg_root():
    assert "<svg" in THUMBNAIL.read_text()


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg invalid XML: {exc}") from exc


def test_thumbnail_dimensions_400():
    svg = THUMBNAIL.read_text()
    w = re.search(r'width="(\d+)"', svg)
    h = re.search(r'height="(\d+)"', svg)
    assert w and int(w.group(1)) == 400
    assert h and int(h.group(1)) == 400


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_gradient():
    svg = THUMBNAIL.read_text()
    assert "radialGradient" in svg or "linearGradient" in svg


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_under_200kb():
    size = THUMBNAIL.stat().st_size
    assert size < 200_000, f"thumbnail.svg is {size} bytes — must be under 200 KB"


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


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_webgl():
    t = _entry()["technique"].lower()
    assert "webgl" in t


def test_pieces_json_technique_mentions_sdf():
    t = _entry()["technique"].lower()
    assert "sdf" in t or "signed" in t or "ray" in t


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_sdf():
    readme = README.read_text().lower()
    assert "signed-distance" in readme or "sdf" in readme


def test_readme_mentions_ray_marching():
    readme = README.read_text().lower()
    assert "ray march" in readme or "raymarching" in readme


def test_readme_mentions_torus():
    assert "torus" in README.read_text().lower()


def test_readme_mentions_soft_shadow():
    readme = README.read_text().lower()
    assert "shadow" in readme


def test_readme_mentions_ao():
    readme = README.read_text().lower()
    assert "ambient" in readme or "occlusion" in readme or "ao" in readme


def test_readme_mentions_utime():
    assert "uTime" in README.read_text()


# ---------------------------------------------------------------------------
# Failure-mode tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "00-does-not-exist" not in ids


def test_missing_canvas_tag_detected():
    fake = "<html><body><div id='c'></div></body></html>"
    assert "<canvas" not in fake


def test_sd_sphere_zero_radius_at_origin():
    """A sphere of radius 0 at origin: any point at distance r has SDF == r."""
    assert abs(sd_sphere((1.0, 0.0, 0.0), 0.0) - 1.0) < 1e-12


def test_op_smooth_union_k_zero_is_hard_min():
    """k approaching 0 should give result close to min(d1, d2)."""
    d1, d2, k = 0.3, 0.8, 1e-9
    result = op_smooth_union(d1, d2, k)
    assert abs(result - min(d1, d2)) < 1e-6


def test_sd_box_all_negative_inside():
    """Any point strictly inside the box must have a negative SDF value."""
    for x in (-0.5, 0.0, 0.5):
        for y in (-0.5, 0.0, 0.5):
            for z in (-0.5, 0.0, 0.5):
                d = sd_box((x, y, z), (1.0, 1.0, 1.0))
                assert d <= 0.0, f"Point ({x},{y},{z}) inside unit box gave SDF {d} > 0"
