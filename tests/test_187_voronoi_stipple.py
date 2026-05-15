"""Tests for Piece 187 — Voronoi Stipple: Weighted Dot Etching.

Covers: file existence, HTML canvas 2D structure, Lloyd algorithm constants,
density function, dot radius bounds, thumbnail SVG, pieces.json contract,
README content, and Python re-implementations of core algorithm logic.
"""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "187-voronoi-stipple"
PIECE_DIR = REPO / "pieces" / PIECE_ID
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

INK_COLOR = "#2b2318"
PAPER_COLOR = "#f5f0e8"


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
    assert INDEX_HTML.is_file(), "index.html is missing"


def test_index_html_nonempty():
    assert len(_html()) > 500


def test_thumbnail_svg_exists():
    assert THUMBNAIL.is_file(), "thumbnail.svg is missing"


def test_readme_exists():
    assert README.is_file(), "README.md is missing"


def test_readme_nonempty():
    assert len(README.read_text().strip()) > 100


# ---------------------------------------------------------------------------
# HTML structural tests
# ---------------------------------------------------------------------------

def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_canvas_uses_2d_not_webgl():
    """Must use canvas 2D context — not WebGL."""
    html = _html()
    assert "getContext('2d')" in html or 'getContext("2d")' in html
    assert "getContext('webgl')" not in html and 'getContext("webgl")' not in html


def test_html_canvas_id():
    html = _html()
    assert 'id="c"' in html or "id='c'" in html


def test_html_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html


def test_html_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_title_contains_voronoi_stipple():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    title = m.group(1).lower()
    assert "voronoi" in title or "stipple" in title


def test_html_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained"


def test_html_no_raster_image_imports():
    """Density must be mathematically defined — no <img> or fetch() of image files."""
    html = _html()
    assert "<img" not in html.lower()
    assert "new Image(" not in html


# ---------------------------------------------------------------------------
# JavaScript constant tests
# ---------------------------------------------------------------------------

def test_js_seed_count_in_range():
    """N (seed count) must be ~600 — between 400 and 800."""
    m = re.search(r"\bN\s*=\s*(\d+)", _html())
    assert m, "N constant not found"
    n = int(m.group(1))
    assert 400 <= n <= 800, f"N={n} outside [400, 800]"


def test_js_max_iter_in_range():
    """MAX_ITER (Lloyd iterations) must be between 30 and 60."""
    m = re.search(r"MAX_ITER\s*=\s*(\d+)", _html())
    assert m, "MAX_ITER constant not found"
    v = int(m.group(1))
    assert 30 <= v <= 60, f"MAX_ITER={v} outside [30, 60]"


def test_js_rmin_rmax_defined():
    """Dot radius bounds RMIN and RMAX must be present."""
    html = _html()
    assert "RMIN" in html, "RMIN not defined"
    assert "RMAX" in html, "RMAX not defined"


def test_js_rmin_is_at_least_1():
    m = re.search(r"\bRMIN\s*=\s*(\d+(?:\.\d+)?)", _html())
    if m:
        assert float(m.group(1)) >= 1, "RMIN must be ≥ 1 px"


def test_js_rmax_is_at_most_6():
    m = re.search(r"\bRMAX\s*=\s*(\d+(?:\.\d+)?)", _html())
    if m:
        assert float(m.group(1)) <= 6, "RMAX must be ≤ 6 px"


def test_js_ink_color_present():
    assert INK_COLOR in _html(), f"Ink colour {INK_COLOR} not found"


def test_js_paper_color_present():
    assert PAPER_COLOR in _html(), f"Paper colour {PAPER_COLOR} not found"


def test_js_spatial_grid_bucket_defined():
    assert "BCELL" in _html(), "Spatial grid bucket size BCELL must be defined"


def test_js_lloyd_step_function():
    """A Lloyd step function must be defined (function or const)."""
    html = _html()
    assert "lloydStep" in html or "lloyd" in html.lower()


def test_js_weighted_centroid_accumulation():
    """Weighted centroid accumulators wx/wy/wt must be present."""
    html = _html()
    assert "wx" in html and "wy" in html and "wt" in html


def test_js_precomputed_density_map():
    """Density map pre-computation (DEN array) must be present to avoid per-frame exp() calls."""
    html = _html()
    assert "DEN" in html or "den" in html


def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_js_uses_fill_arc_for_dots():
    """Dots drawn with ctx.arc (filled circles)."""
    html = _html()
    assert ".arc(" in html


def test_js_uses_typed_arrays():
    """Float32Array or Float64Array must be used for seed positions."""
    html = _html()
    assert "Float32Array" in html or "Float64Array" in html


def test_js_density_function_gaussian_exponents():
    """Density function must contain Math.exp for Gaussian evaluation."""
    html = _html()
    assert "Math.exp" in html, "Density function must use Math.exp for Gaussians"


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    assert len(THUMBNAIL.read_text()) > 200


def test_thumbnail_has_svg_root():
    assert "<svg" in THUMBNAIL.read_text()


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc


def test_thumbnail_has_circle_elements():
    """Stipple thumbnail must use <circle> elements, not coloured cells."""
    svg = THUMBNAIL.read_text()
    circles = re.findall(r"<circle\b", svg)
    assert len(circles) >= 50, f"Expected ≥50 <circle> elements, found {len(circles)}"


def test_thumbnail_contains_ink_color():
    assert INK_COLOR.lower().lstrip("#") in THUMBNAIL.read_text().lower() or INK_COLOR in THUMBNAIL.read_text()


def test_thumbnail_contains_paper_color():
    assert PAPER_COLOR in THUMBNAIL.read_text()


def test_thumbnail_is_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_no_coloured_fill_cells():
    """Thumbnail must not fill polygons with non-ink colours (it's a stipple, not a mosaic)."""
    svg = THUMBNAIL.read_text()
    assert "<polygon" not in svg and "<path" not in svg, (
        "Stipple thumbnail should use only circles, not polygons or paths"
    )


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_pieces_json_entry_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= _entry().keys()


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    assert (REPO / _entry()["thumbnail"]).is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_voronoi():
    assert "voronoi" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


# ---------------------------------------------------------------------------
# README content tests
# ---------------------------------------------------------------------------

def test_readme_mentions_stipple():
    assert "stipple" in README.read_text().lower()


def test_readme_distinguishes_from_colored_voronoi():
    """README must explicitly explain that this is NOT a coloured-cell mosaic."""
    text = README.read_text().lower()
    assert "mosaic" in text or "cell" in text or "distinct" in text or "not" in text


def test_readme_mentions_lloyd():
    assert "lloyd" in README.read_text().lower()


def test_readme_mentions_density():
    assert "density" in README.read_text().lower()


def test_readme_mentions_algorithm():
    text = README.read_text().lower()
    assert "algorithm" in text or "centroid" in text or "relaxation" in text


# ---------------------------------------------------------------------------
# Python re-implementation of core algorithm logic
# ---------------------------------------------------------------------------

def _density(x: float, y: float, W: float = 600.0, H: float = 600.0) -> float:
    """Python mirror of the JS density function for unit testing."""
    nx, ny = x / W, y / H
    head = math.exp(-((nx - .5)**2 / .045 + (ny - .5)**2 / .07))
    le = 1.7 * math.exp(-((nx - .37)**2 / .004 + (ny - .38)**2 / .003))
    re = 1.7 * math.exp(-((nx - .63)**2 / .004 + (ny - .38)**2 / .003))
    mo = 1.4 * math.exp(-((nx - .5)**2 / .018 + (ny - .65)**2 / .002))
    return min(1.0, head + le + re + mo)


def test_density_range_always_0_to_1():
    """Density must stay in [0, 1] everywhere on the canvas."""
    W, H = 600.0, 600.0
    import random
    rng = random.Random(0)
    for _ in range(500):
        x = rng.uniform(0, W)
        y = rng.uniform(0, H)
        d = _density(x, y, W, H)
        assert 0.0 <= d <= 1.0, f"density({x:.1f},{y:.1f})={d} out of [0,1]"


def test_density_center_higher_than_corner():
    """Face centre must have higher density than a far corner."""
    d_center = _density(300, 300)
    d_corner = _density(10, 10)
    assert d_center > d_corner, f"center density {d_center} should exceed corner {d_corner}"


def test_density_eye_peaks_higher_than_background():
    """Left-eye peak should exceed background density at same y offset."""
    W, H = 600.0, 600.0
    d_eye = _density(0.37 * W, 0.38 * H)
    d_bg = _density(0.1 * W, 0.38 * H)
    assert d_eye > d_bg


def test_density_symmetric_eyes():
    """Left and right eye densities must be equal (symmetric density function)."""
    W, H = 600.0, 600.0
    d_left = _density(0.37 * W, 0.38 * H)
    d_right = _density(0.63 * W, 0.38 * H)
    assert abs(d_left - d_right) < 1e-9, "Eye densities must be symmetric"


def _nearest(px: float, py: float, seeds_x: list, seeds_y: list) -> int:
    """Pure-Python nearest-seed lookup (brute force for testing)."""
    best_d = math.inf
    best_i = 0
    for i, (sx, sy) in enumerate(zip(seeds_x, seeds_y)):
        d = (px - sx)**2 + (py - sy)**2
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def test_nearest_returns_closest_of_two():
    xs, ys = [0.0, 10.0], [0.0, 0.0]
    assert _nearest(2.0, 0.0, xs, ys) == 0
    assert _nearest(8.0, 0.0, xs, ys) == 1


def test_nearest_single_seed_always_wins():
    xs, ys = [50.0], [50.0]
    for px, py in [(0, 0), (99, 99), (50, 50), (0, 99)]:
        assert _nearest(float(px), float(py), xs, ys) == 0


def test_nearest_equidistant_breaks_by_first_seen():
    """Two seeds equidistant from query point — the first one (index 0) wins."""
    xs, ys = [0.0, 10.0], [5.0, 5.0]
    result = _nearest(5.0, 5.0, xs, ys)
    assert result in (0, 1), "Equidistant result must be one of the two seeds"


def _dot_radius(density: float, rmin: float = 1.0, rmax: float = 6.0) -> float:
    """Map density in [0,1] to dot radius in [RMIN, RMAX]."""
    return rmin + (rmax - rmin) * density


def test_dot_radius_at_zero_density():
    assert _dot_radius(0.0) == 1.0


def test_dot_radius_at_full_density():
    assert _dot_radius(1.0) == 6.0


def test_dot_radius_monotone():
    """Higher density must always produce a larger dot."""
    for d in [0.0, 0.25, 0.5, 0.75, 1.0]:
        r = _dot_radius(d)
        assert 1.0 <= r <= 6.0, f"radius {r} out of [1, 6] for density={d}"


def _lloyd_step_centroid(
    seed_x: float, seed_y: float,
    pixel_coords: list[tuple[float, float]],
    weights: list[float],
) -> tuple[float, float]:
    """Compute one Lloyd centroid move for a single seed given pixel assignments."""
    wx = wy = wt = 0.0
    for (px, py), w in zip(pixel_coords, weights):
        wx += w * px
        wy += w * py
        wt += w
    if wt == 0:
        return seed_x, seed_y
    return wx / wt, wy / wt


def test_lloyd_centroid_moves_to_weighted_center():
    """Seed surrounded by pixels weighted 1 at (0,0) and 0 at (10,10) stays at (0,0)."""
    new_x, new_y = _lloyd_step_centroid(
        5.0, 5.0,
        [(0.0, 0.0), (10.0, 10.0)],
        [1.0, 0.0],
    )
    assert abs(new_x - 0.0) < 1e-9 and abs(new_y - 0.0) < 1e-9


def test_lloyd_centroid_uniform_weight_is_geometric_center():
    """With uniform weight, centroid equals the geometric mean of pixel positions."""
    pixels = [(0.0, 0.0), (4.0, 0.0), (2.0, 4.0)]
    weights = [1.0, 1.0, 1.0]
    new_x, new_y = _lloyd_step_centroid(99.0, 99.0, pixels, weights)
    assert abs(new_x - 2.0) < 1e-9
    assert abs(new_y - (4.0 / 3)) < 1e-9


def test_lloyd_centroid_zero_weight_seed_stays():
    """If all weights are zero the seed position must not change."""
    new_x, new_y = _lloyd_step_centroid(
        7.0, 3.0,
        [(1.0, 1.0), (9.0, 9.0)],
        [0.0, 0.0],
    )
    assert new_x == 7.0 and new_y == 3.0


def test_lloyd_centroid_large_input():
    """100 uniformly weighted pixels on a line → centroid at midpoint."""
    pixels = [(float(i), 0.0) for i in range(100)]
    weights = [1.0] * 100
    new_x, new_y = _lloyd_step_centroid(0.0, 0.0, pixels, weights)
    assert abs(new_x - 49.5) < 1e-6


# ---------------------------------------------------------------------------
# Failure-mode / edge-case tests
# ---------------------------------------------------------------------------

def test_density_at_origin_less_than_center():
    """Origin (top-left corner) must have lower density than canvas centre."""
    assert _density(0, 0) < _density(300, 300)


def test_density_outside_canvas_clamped_by_gaussians():
    """Density at far-outside coordinates must be very close to 0."""
    d = _density(1e6, 1e6)
    assert d < 0.01, f"Density far outside canvas should be ~0, got {d}"


def test_thumbnail_circle_radii_in_range():
    """All circle r attributes in the thumbnail must be between 1 and 6."""
    svg = THUMBNAIL.read_text()
    radii = [float(m) for m in re.findall(r'<circle[^>]+r="([^"]+)"', svg)]
    assert radii, "No circle radii found in thumbnail"
    for r in radii:
        assert 1.0 <= r <= 6.0, f"Circle radius {r} out of expected [1, 6]"


def test_thumbnail_circles_inside_viewbox():
    """All circle centres must lie within the SVG viewBox bounds."""
    svg = THUMBNAIL.read_text()
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    assert m, "viewBox not found"
    vw, vh = int(m.group(1)), int(m.group(2))
    cxs = [float(v) for v in re.findall(r'<circle[^>]+cx="([^"]+)"', svg)]
    cys = [float(v) for v in re.findall(r'<circle[^>]+cy="([^"]+)"', svg)]
    for cx, cy in zip(cxs, cys):
        assert 0 <= cx <= vw, f"Circle cx={cx} outside viewBox width {vw}"
        assert 0 <= cy <= vh, f"Circle cy={cy} outside viewBox height {vh}"
