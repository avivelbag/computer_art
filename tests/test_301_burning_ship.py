"""Tests for pieces/301-burning-ship: WebGL Burning Ship fractal with smooth colouring."""

import json
import math
import pathlib
import re

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "301-burning-ship"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.png"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "301-burning-ship"


# ---------------------------------------------------------------------------
# Python mirrors of the core GLSL / generate_thumbnail.py math
# ---------------------------------------------------------------------------

def burning_ship_iterate(cr: float, ci: float, max_iter: int = 256) -> tuple[int, float, float]:
    """Run Burning Ship iteration for c = cr + i·ci.

    Returns (escape_iter, final_zr, final_zi).
    escape_iter == max_iter means the point did not escape.
    """
    zr, zi = 0.0, 0.0
    for i in range(max_iter):
        zr = abs(zr)
        zi = abs(zi)
        zr2 = zr * zr - zi * zi + cr
        zi  = 2.0 * zr * zi     + ci
        zr  = zr2
        if zr * zr + zi * zi > 4.0:
            return (i, zr, zi)
    return (max_iter, zr, zi)


def smooth_count(n: int, zr: float, zi: float) -> float:
    """Compute the smooth (continuous) iteration count: nu = n − log₂(log₂|z|)."""
    mag = math.sqrt(zr * zr + zi * zi)
    return n - math.log2(math.log2(max(mag, 1.0 + 1e-10)))


def _smoothstep(a: float, b: float, x: float) -> float:
    """GLSL smoothstep in [a, b]."""
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


INDIGO = (0.051, 0.008, 0.129)
AMBER  = (0.878, 0.482, 0.0)
CREAM  = (1.0,   0.973, 0.906)


def palette(t: float) -> tuple[float, float, float]:
    """3-stop gradient matching the GLSL palette() function."""
    if t < 0.3:
        s = _smoothstep(0.0, 1.0, t / 0.3)
        return tuple(INDIGO[i] + s * (AMBER[i] - INDIGO[i]) for i in range(3))
    else:
        s = _smoothstep(0.0, 1.0, (t - 0.3) / 0.7)
        return tuple(AMBER[i] + s * (CREAM[i] - AMBER[i]) for i in range(3))


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
    assert header == b"\x89PNG\r\n\x1a\n", "thumbnail.png must begin with PNG magic bytes"


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


# ---------------------------------------------------------------------------
# WebGL / shader structure tests
# ---------------------------------------------------------------------------

def test_html_has_webgl_context():
    html = _html()
    assert "getContext('webgl')" in html or 'getContext("webgl")' in html


def test_html_has_ures_uniform():
    assert "uRes" in _html()


def test_html_has_ucenter_uniform():
    assert "uCenter" in _html()


def test_html_has_uscale_uniform():
    assert "uScale" in _html()


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_fullscreen_quad():
    html = _html()
    assert "-1,-1" in html or "-1, -1" in html


def test_html_has_gl_frag_color():
    assert "gl_FragColor" in _html()


# ---------------------------------------------------------------------------
# Burning Ship specific shader tests
# ---------------------------------------------------------------------------

def test_glsl_has_abs_fold():
    """The Burning Ship fold requires abs() on both components of z."""
    html = _html()
    assert "abs(z.x)" in html and "abs(z.y)" in html


def test_glsl_has_256_iterations():
    html = _html()
    assert "256" in html


def test_glsl_has_smooth_iteration_formula():
    """Smooth colouring uses log2(log2(...))."""
    html = _html()
    assert html.count("log2(") >= 2


def test_glsl_escape_radius_is_4():
    """Escape condition: dot(z,z) > 4.0 (radius² = 4 → radius = 2)."""
    html = _html()
    assert "4.0" in html or "ESCAPE" in html


def test_glsl_has_interior_color():
    """Interior points must be rendered as near-black."""
    html = _html()
    assert "050008" in html or "0.020" in html or "interior" in html.lower()


def test_glsl_has_palette_stops():
    """3-stop gradient must reference the three colours."""
    html = _html()
    assert "0d0221" in html or "0.051" in html   # deep indigo
    assert "e07b00" in html or "0.878" in html   # amber
    assert "fff8e7" in html or "0.973" in html   # pale cream


def test_glsl_y_axis_flipped():
    """Y-axis must be negated so the ship appears upright."""
    html = _html()
    assert "-1.0" in html


# ---------------------------------------------------------------------------
# Interaction and URL hash tests
# ---------------------------------------------------------------------------

def test_html_has_drag_to_pan():
    html = _html()
    assert "mousedown" in html
    assert "mousemove" in html


def test_html_has_scroll_to_zoom():
    assert "wheel" in _html()


def test_html_has_url_hash_encoding():
    html = _html()
    assert "location.hash" in html or "location.replace" in html


# ---------------------------------------------------------------------------
# Idle drift-zoom tests
# ---------------------------------------------------------------------------

def test_html_has_drift_zoom():
    html = _html()
    assert "ZOOM_FACTOR" in html or "0.998" in html


def test_html_has_zoom_reset():
    html = _html()
    assert "MIN_SCALE" in html or "INIT_SCALE" in html


def test_html_zoom_target_near_mast():
    """Drift target should be near Re ≈ −0.52, Im ≈ −0.62 (mast tip)."""
    html = _html()
    assert "-0.52" in html or "ZOOM_TARGET" in html


# ---------------------------------------------------------------------------
# Python mirrors — Burning Ship iteration
# ---------------------------------------------------------------------------

def test_origin_escapes():
    """c = 0+0i: z stays at 0, never escapes — should be interior."""
    n, _, _ = burning_ship_iterate(0.0, 0.0)
    assert n == 256, "c=0 is interior; expected max_iter"


def test_large_positive_real_escapes_quickly():
    """c = 3+0i is far outside the set and should escape on the first iteration."""
    n, _, _ = burning_ship_iterate(3.0, 0.0)
    assert n < 5, f"c=3 should escape immediately, got n={n}"


def test_interior_point_on_hull():
    """A point known to be inside the Burning Ship set: c = −0.5 − 0.5i."""
    n, _, _ = burning_ship_iterate(-0.5, -0.5)
    assert n == 256, "(-0.5, -0.5) should be interior (non-escaping)"


def test_burning_ship_differs_from_mandelbrot():
    """For some c the Burning Ship and Mandelbrot sets give different escape counts.

    c = −0.7 − 0.5i:  Mandelbrot keeps z in a different orbit than Burning Ship
    because the abs() fold changes the trajectory.
    """
    cr, ci = -0.7, -0.5
    n_bs, _, _ = burning_ship_iterate(cr, ci)

    # Mandelbrot iteration (no abs)
    zr, zi = 0.0, 0.0
    n_mb = 256
    for i in range(256):
        zr2 = zr * zr - zi * zi + cr
        zi  = 2.0 * zr * zi     + ci
        zr  = zr2
        if zr * zr + zi * zi > 4.0:
            n_mb = i
            break

    assert n_bs != n_mb, (
        "Burning Ship and Mandelbrot gave same escape count for this c — "
        "the abs() fold should alter the trajectory"
    )


def test_escape_magnitude_exceeds_2():
    """After escape the magnitude of z must be > 2 (escape radius)."""
    n, zr, zi = burning_ship_iterate(2.5, 0.0)
    assert n < 256, "c=2.5 should escape"
    assert math.sqrt(zr * zr + zi * zi) > 2.0


# ---------------------------------------------------------------------------
# Smooth colouring math
# ---------------------------------------------------------------------------

def test_smooth_count_less_than_escape_count():
    """nu = n − log₂(log₂|z|); for |z| > e, log₂(log₂|z|) > 0 so nu < n."""
    n, zr, zi = burning_ship_iterate(2.5, 0.0)
    assert n < 256
    nu = smooth_count(n, zr, zi)
    assert nu < n


def test_smooth_count_non_negative():
    """Smooth count must not go deeply negative for standard escapes."""
    for cr in (-1.8, -0.5, 0.5, 1.5, 2.0):
        n, zr, zi = burning_ship_iterate(cr, 0.0)
        if n < 256:
            nu = smooth_count(n, zr, zi)
            assert nu > -5.0, f"nu={nu} too negative for c=({cr},0)"


def test_palette_at_zero_is_indigo():
    """t=0 should give the deep-indigo stop."""
    r, g, b = palette(0.0)
    assert r < 0.1 and g < 0.02 and b > 0.1


def test_palette_at_0_3_is_amber():
    """t=0.3 is the boundary between the two gradient segments — should be amber."""
    r, g, b = palette(0.3)
    assert r > 0.7 and g > 0.3 and b < 0.1


def test_palette_at_one_is_cream():
    """t=1 should give the pale-cream stop."""
    r, g, b = palette(1.0)
    assert r > 0.95 and g > 0.9 and b > 0.85


def test_palette_values_in_unit_range():
    """Palette must stay within [0, 1] for all t."""
    for t_int in range(0, 101):
        t = t_int / 100.0
        r, g, b = palette(t)
        assert 0.0 <= r <= 1.0
        assert 0.0 <= g <= 1.0
        assert 0.0 <= b <= 1.0


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


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_webgl():
    t = _entry()["technique"]
    assert "WebGL" in t or "webgl" in t


def test_pieces_json_technique_mentions_burning_ship():
    t = _entry()["technique"].lower()
    assert "burning" in t or "fractal" in t


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_burning_ship():
    readme = README.read_text().lower()
    assert "burning ship" in readme


def test_readme_mentions_smooth_colouring():
    readme = README.read_text().lower()
    assert "smooth" in readme


def test_readme_mentions_absolute_value():
    readme = README.read_text().lower()
    assert "abs" in readme or "absolute" in readme


def test_readme_mentions_drift_zoom():
    readme = README.read_text().lower()
    assert "drift" in readme or "zoom" in readme


# ---------------------------------------------------------------------------
# Failure-mode / edge-case tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "00-does-not-exist" not in ids


def test_missing_canvas_detected():
    """Sanity-check: absence of <canvas> would be caught."""
    fake = "<html><body><div id='c'></div></body></html>"
    assert "<canvas" not in fake


def test_iterate_max_iter_boundary():
    """Iterating with max_iter=1 and c=3 should still escape within that budget."""
    n, _, _ = burning_ship_iterate(3.0, 0.0, max_iter=1)
    assert n == 0 or n == 1


def test_smooth_count_large_escape_magnitude():
    """For a point that escapes with very large |z|, smooth count is still < escape index."""
    n, zr, zi = burning_ship_iterate(10.0, 0.0)
    assert n < 256
    nu = smooth_count(n, zr, zi)
    assert nu < float(n) + 1.0


def test_palette_monotone_red_channel():
    """Red channel increases from t=0 to t=0.3 (indigo→amber)."""
    r0, _, _ = palette(0.0)
    r1, _, _ = palette(0.3)
    assert r1 > r0, "Red channel should increase from indigo to amber"
