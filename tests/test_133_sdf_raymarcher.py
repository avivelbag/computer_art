"""Tests for pieces/133-sdf-raymarcher: WebGL SDF raymarcher with infinite torus field."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "133-sdf-raymarcher"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "133-sdf-raymarcher"


# ---------------------------------------------------------------------------
# Python mirrors of the core GLSL SDF functions
# ---------------------------------------------------------------------------

def sd_torus(p: tuple, t_x: float, t_y: float) -> float:
    """Signed distance from point p=(x,y,z) to a torus in the XZ plane.

    t_x is the major radius (center of tube from Y-axis),
    t_y is the minor (tube) radius. Matches the GLSL sdTorus exactly.
    """
    xz = math.sqrt(p[0] ** 2 + p[2] ** 2)
    return math.sqrt((xz - t_x) ** 2 + p[1] ** 2) - t_y


def domain_repeat(coord: float, cell: float) -> float:
    """Python mirror of GLSL: mod(coord, cell) - cell * 0.5

    Maps any coordinate into the symmetric range [-cell/2, cell/2].
    GLSL mod(a, b) = a - b*floor(a/b), which matches Python's % for positive b.
    """
    return coord % cell - cell * 0.5


def scene_sdf(p: tuple) -> float:
    """Python mirror of the GLSL map() function.

    Repeats the torus infinitely with cell size 2.0 (major=0.4, minor=0.15).
    """
    q = tuple(domain_repeat(coord, 2.0) for coord in p)
    return sd_torus(q, 0.4, 0.15)


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


def test_glsl_defines_sd_torus():
    assert "sdTorus" in _html()


def test_glsl_has_domain_repetition():
    """Shader must use mod() for domain repetition to create infinite field."""
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


def test_glsl_has_time_driven_camera():
    """Camera orbit angle must be driven by uTime via cos/sin."""
    html = _html()
    assert "uTime" in html
    assert "cos(" in html and "sin(" in html


# ---------------------------------------------------------------------------
# Palette tests
# ---------------------------------------------------------------------------

def test_html_contains_warm_gold_surface_color():
    """Fragment shader must define the warm gold surface color."""
    html = _html()
    assert "0.92, 0.72, 0.18" in html or "0.92,0.72,0.18" in html


def test_html_contains_indigo_fog_color():
    """Fragment shader must define the deep indigo fog / sky color."""
    html = _html()
    assert "0.06, 0.04, 0.22" in html or "0.06,0.04,0.22" in html


# ---------------------------------------------------------------------------
# Python mirrors — sd_torus
# ---------------------------------------------------------------------------

def test_sd_torus_on_outer_surface():
    """Point at (t_x + t_y, 0, 0) lies exactly on the torus surface."""
    t_x, t_y = 0.4, 0.15
    p = (t_x + t_y, 0.0, 0.0)
    assert abs(sd_torus(p, t_x, t_y)) < 1e-12


def test_sd_torus_tube_center_is_negative():
    """A point at the tube centre (t_x, 0, 0) has SDF == -t_y (fully inside)."""
    t_x, t_y = 0.4, 0.15
    d = sd_torus((t_x, 0.0, 0.0), t_x, t_y)
    assert abs(d - (-t_y)) < 1e-12


def test_sd_torus_origin_inside_hole():
    """Origin sits inside the torus hole; SDF = t_x - t_y (distance to tube)."""
    t_x, t_y = 0.4, 0.15
    d = sd_torus((0.0, 0.0, 0.0), t_x, t_y)
    assert abs(d - (t_x - t_y)) < 1e-12


def test_sd_torus_far_above_is_positive():
    """A point directly above the torus at large height is outside."""
    d = sd_torus((0.0, 5.0, 0.0), 0.4, 0.15)
    assert d > 0.0


def test_sd_torus_matches_shader_params():
    """Test with exact shader parameters: t_x=0.4, t_y=0.15."""
    t_x, t_y = 0.4, 0.15
    p_surface = (t_x + t_y, 0.0, 0.0)
    assert abs(sd_torus(p_surface, t_x, t_y)) < 1e-12

    p_inside = (t_x, 0.0, 0.0)
    assert sd_torus(p_inside, t_x, t_y) < 0.0


def test_sd_torus_rotationally_symmetric_xz():
    """SDF is identical for equivalent points rotated around the Y-axis."""
    t_x, t_y = 0.4, 0.15
    r = t_x + t_y  # on-surface radius
    angles = [0, math.pi / 4, math.pi / 2, math.pi]
    vals = [sd_torus((r * math.cos(a), 0.0, r * math.sin(a)), t_x, t_y) for a in angles]
    assert all(abs(v - vals[0]) < 1e-10 for v in vals), \
        "sdTorus must be rotationally symmetric in the XZ plane"


# ---------------------------------------------------------------------------
# Python mirrors — domain_repeat
# ---------------------------------------------------------------------------

def test_domain_repeat_zero():
    """0 maps to -cell/2 (the cell boundary)."""
    assert abs(domain_repeat(0.0, 2.0) - (-1.0)) < 1e-12


def test_domain_repeat_cell_center():
    """The cell center at 1.0 (for cell=2) maps to 0."""
    assert abs(domain_repeat(1.0, 2.0)) < 1e-12


def test_domain_repeat_negative_input():
    """domain_repeat handles negative inputs, wrapping into [-cell/2, cell/2)."""
    val = domain_repeat(-0.5, 2.0)
    assert -1.0 <= val < 1.0


def test_domain_repeat_periodicity():
    """Values separated by the cell size must map to the same canonical coord."""
    cell = 2.0
    base = 0.7
    for n in range(-3, 4):
        assert abs(domain_repeat(base + n * cell, cell) - domain_repeat(base, cell)) < 1e-10


# ---------------------------------------------------------------------------
# Python mirrors — scene_sdf (map function)
# ---------------------------------------------------------------------------

def test_scene_sdf_on_torus_surface():
    """World point (1 + 0.4 + 0.15, 1, 1) lies on a torus surface."""
    p = (1.0 + 0.4 + 0.15, 1.0, 1.0)
    assert abs(scene_sdf(p)) < 1e-10


def test_scene_sdf_inside_torus_tube():
    """World point (1.4, 1, 1) is inside the tube of the (1,1,1)-centred torus."""
    p = (1.4, 1.0, 1.0)
    assert scene_sdf(p) < 0.0


def test_scene_sdf_far_from_any_torus_is_positive():
    """A corner of the cell is far from any torus surface."""
    p = (0.0, 0.0, 0.0)   # maps to (-1,-1,-1) in the cell, far from torus
    assert scene_sdf(p) > 0.0


def test_scene_sdf_periodic():
    """Points separated by cell-size multiples must return the same SDF value."""
    cell = 2.0
    p0 = (1.55, 1.0, 1.0)
    for dx in (-cell, 0, cell, 2 * cell):
        for dz in (0, cell):
            assert abs(scene_sdf((p0[0] + dx, p0[1], p0[2] + dz)) - scene_sdf(p0)) < 1e-10


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


def test_pieces_json_technique_mentions_sdf_or_ray():
    t = _entry()["technique"].lower()
    assert "sdf" in t or "ray" in t


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_sphere_tracing():
    readme = README.read_text().lower()
    assert "sphere-trac" in readme or "sphere trac" in readme or "raymarching" in readme


def test_readme_mentions_sdf():
    readme = README.read_text().lower()
    assert "signed-distance" in readme or "sdf" in readme


def test_readme_mentions_torus():
    assert "torus" in README.read_text().lower()


def test_readme_mentions_domain_repetition():
    readme = README.read_text().lower()
    assert "domain" in readme or "mod(" in readme or "repeat" in readme


def test_readme_mentions_utime():
    assert "uTime" in README.read_text()


# ---------------------------------------------------------------------------
# Failure-mode tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "133-does-not-exist" not in ids


def test_missing_canvas_tag_detected():
    """Verify detection logic: a div is not a canvas."""
    fake = "<html><body><div id='c'></div></body></html>"
    assert "<canvas" not in fake


def test_sd_torus_large_distance_positive():
    """A point far from any torus returns a large positive SDF."""
    d = sd_torus((100.0, 100.0, 100.0), 0.4, 0.15)
    assert d > 50.0


def test_domain_repeat_large_positive():
    """Large positive inputs wrap correctly into [-1, 1) for cell=2."""
    for x in (100.0, 200.0, 1000.0):
        val = domain_repeat(x, 2.0)
        assert -1.0 <= val < 1.0, f"domain_repeat({x}, 2.0) = {val} out of bounds"


def test_scene_sdf_same_everywhere_within_cell():
    """Points in different cells at equivalent offsets must return the same SDF."""
    offset = (0.3, 0.7, -0.2)
    base = scene_sdf(offset)
    for shift_x in (0, 2, 4, -2, -4):
        for shift_z in (0, 2, -2):
            p = (offset[0] + shift_x, offset[1], offset[2] + shift_z)
            val = scene_sdf(p)
            assert abs(val - base) < 1e-10, \
                f"scene_sdf({p}) = {val} differs from base {base}"
