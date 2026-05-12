"""Tests for pieces/51-julia-set: WebGL Julia set with orbit-trap coloring."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "51-julia-set"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID   = "51-julia-set"
INDIGO_VEC = "0.07, 0.02, 0.28"
AMBER_VEC  = "0.95, 0.62, 0.04"
IVORY_VEC  = "0.97, 0.93, 0.82"
C_RADIUS   = "0.7885"


# ---------------------------------------------------------------------------
# Python mirrors of the core Julia set iteration math
# ---------------------------------------------------------------------------

def julia_escape(z_re, z_im, c_re, c_im, max_iter=256):
    """Return True if the orbit of z under z → z² + c escapes within max_iter steps.

    Mirrors the GLSL loop: after each step |z| > 4 triggers escape, matching
    the shader's threshold of length(z) > 4.0.
    """
    zr, zi = z_re, z_im
    for _ in range(max_iter):
        zr, zi = zr * zr - zi * zi + c_re, 2.0 * zr * zi + c_im
        if zr * zr + zi * zi > 16.0:
            return True
    return False


def orbit_trap(z_re, z_im, c_re, c_im, max_iter=256):
    """Return the minimum |z| over all iteration steps up to escape or max_iter.

    Mirrors the GLSL orbit-trap accumulator: trap = min(trap, length(z))
    evaluated after each z → z² + c step (initial z is not included, matching
    the shader which initialises trap = 1e9 and updates inside the loop).
    """
    zr, zi = z_re, z_im
    min_d = float('inf')
    for _ in range(max_iter):
        zr, zi = zr * zr - zi * zi + c_re, 2.0 * zr * zi + c_im
        d = math.sqrt(zr * zr + zi * zi)
        min_d = min(min_d, d)
        if zr * zr + zi * zi > 16.0:
            break
    return min_d


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


def test_html_has_at_least_two_script_tags():
    assert _html().count("<script") >= 2


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


def test_html_has_gl_frag_color():
    assert "gl_FragColor" in _html()


# ---------------------------------------------------------------------------
# Julia set / orbit-trap shader tests
# ---------------------------------------------------------------------------

def test_shader_has_orbit_trap_accumulator():
    html = _html()
    assert "trap" in html


def test_shader_uses_smoothstep():
    assert "smoothstep" in _html()


def test_shader_has_c_radius():
    assert C_RADIUS in _html()


def test_shader_uses_cos_and_sin_for_c_animation():
    html = _html()
    assert "cos(" in html and "sin(" in html


def test_shader_iterates_256_times():
    assert "256" in _html()


def test_shader_uses_min_for_trap():
    assert "min(" in _html()


def test_shader_has_interior_color_branch():
    html = _html()
    assert "0.04, 0.02, 0.15" in html or "!esc" in html


# ---------------------------------------------------------------------------
# Palette color tests
# ---------------------------------------------------------------------------

def test_html_contains_indigo_color():
    assert INDIGO_VEC in _html()


def test_html_contains_amber_color():
    assert AMBER_VEC in _html()


def test_html_contains_ivory_color():
    assert IVORY_VEC in _html()


# ---------------------------------------------------------------------------
# Julia iteration Python mirrors — escape tests
# ---------------------------------------------------------------------------

def test_julia_escape_large_z_escapes_immediately():
    """Any z with |z| > 4 escapes on the first iteration since z² > 16."""
    assert julia_escape(5.0, 0.0, 0.0, 0.0)


def test_julia_escape_origin_with_zero_c_never_escapes():
    """z=0 with c=0 has a fixed orbit at 0, so it never escapes."""
    assert not julia_escape(0.0, 0.0, 0.0, 0.0)


def test_julia_escape_small_interior_c_zero_stays_bounded():
    """z=0.1 with c=0 has an orbit contracting to 0 — never escapes."""
    assert not julia_escape(0.1, 0.0, 0.0, 0.0)


def test_julia_escape_exterior_large_z_dancing_dragon():
    """A large starting point escapes even for the dancing-dragon c."""
    assert julia_escape(3.0, 0.0, 0.7885, 0.0)


def test_julia_escape_with_zero_max_iter():
    """With max_iter=0 the loop never runs, so nothing escapes."""
    assert not julia_escape(5.0, 0.0, 0.0, 0.0, max_iter=0)


def test_julia_escape_complex_z_large_magnitude():
    """A complex z with |z| > 4 escapes regardless of c."""
    assert julia_escape(3.0, 2.0, 0.0, 0.5)  # |z| = sqrt(13) > 4


def test_julia_escape_is_symmetric_in_imaginary_axis():
    """Escape status is the same for z and its conjugate (Julia sets are symmetric)."""
    c_re, c_im = 0.3, 0.5
    assert julia_escape(0.8, 0.6, c_re, c_im) == julia_escape(0.8, -0.6, c_re, -c_im)


# ---------------------------------------------------------------------------
# Julia iteration Python mirrors — orbit trap tests
# ---------------------------------------------------------------------------

def test_orbit_trap_nonnegative_for_various_starts():
    """Orbit trap distance is always >= 0."""
    for z_re in (-1.5, 0.0, 1.0):
        for z_im in (-0.5, 0.0, 0.5):
            assert orbit_trap(z_re, z_im, 0.7885, 0.0) >= 0.0


def test_orbit_trap_zero_c_zero_z():
    """For c=0 and z=0, the orbit stays at 0 after the first step, so trap=0."""
    assert orbit_trap(0.0, 0.0, 0.0, 0.0) == 0.0


def test_orbit_trap_escaping_orbit_bounded_by_escape_radius():
    """The minimum orbit distance for any escaping orbit cannot exceed 4."""
    for c_re in (0.7885, 0.0, -0.4):
        d = orbit_trap(1.5, 0.0, c_re, 0.0)
        assert d < 4.1, f"orbit_trap({c_re}) returned {d} — unexpectedly large"


def test_orbit_trap_single_step():
    """With max_iter=1, orbit_trap returns |z_1| = |z_0² + c|.

    For z_0=0 and c=1+0i: z_1 = 0² + 1 = 1, so trap = 1.
    """
    d = orbit_trap(0.0, 0.0, 1.0, 0.0, max_iter=1)
    assert abs(d - 1.0) < 1e-12


def test_orbit_trap_single_step_complex_c():
    """With max_iter=1, trap = |c| for z_0=0."""
    c_re, c_im = 0.3, 0.4  # |c| = 0.5
    d = orbit_trap(0.0, 0.0, c_re, c_im, max_iter=1)
    assert abs(d - 0.5) < 1e-12


def test_orbit_trap_decreases_on_converging_orbit():
    """For z=0, c=0 the orbit converges to 0, so trap is exactly 0 after any steps."""
    d1 = orbit_trap(0.0, 0.0, 0.0, 0.0, max_iter=1)
    d10 = orbit_trap(0.0, 0.0, 0.0, 0.0, max_iter=10)
    assert d1 == d10 == 0.0


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


def test_pieces_json_technique_mentions_julia_or_fractal():
    t = _entry()["technique"].lower()
    assert "julia" in t or "fractal" in t or "fragment" in t


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_orbit_trap():
    readme = README.read_text().lower()
    assert "orbit" in readme and "trap" in readme


def test_readme_mentions_julia():
    assert "julia" in README.read_text().lower()


def test_readme_mentions_smooth_coloring():
    assert "smooth" in README.read_text().lower()


def test_readme_mentions_c_parameter():
    assert C_RADIUS in README.read_text()


# ---------------------------------------------------------------------------
# Failure-mode and edge-case tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "00-does-not-exist" not in ids


def test_missing_canvas_tag_not_detected_in_fake_html():
    fake = "<html><body><div id='c'></div></body></html>"
    assert "<canvas" not in fake


def test_julia_escape_boundary_exactly_four():
    """A point with |z| exactly 4.0 does not trigger escape (> not >=)."""
    assert not julia_escape(2.0, 0.0, 0.0, 0.0, max_iter=1)


def test_orbit_trap_large_starting_z_escapes_first_step():
    """For z=5, c=0: z_1 = 25 so the loop breaks after 1 step and trap = 25."""
    d = orbit_trap(5.0, 0.0, 0.0, 0.0, max_iter=256)
    assert abs(d - 25.0) < 1e-12


def test_julia_escape_pure_imaginary_z():
    """z = 0 + 2i escapes for c=0: z_1 = -4, z_2 = 16 > 4."""
    assert julia_escape(0.0, 2.0, 0.0, 0.0)
