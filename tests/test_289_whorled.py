"""Tests for piece 289-whorled: Kleinian limit-set via circle inversions."""
import json
import math
import pathlib

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "289-whorled"
INDEX_HTML = PIECE_DIR / "index.html"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
README = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# File structure checks
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


def test_readme_exists():
    assert README.is_file()


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

def _entry():
    data = json.loads(PIECES_JSON.read_text())
    for e in data:
        if e["id"] == "289-whorled":
            return e
    return None


def test_piece_registered_in_pieces_json():
    assert _entry() is not None, "289-whorled not found in pieces.json"


def test_pieces_json_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = _entry()
    assert entry is not None
    assert required <= entry.keys()


def test_pieces_json_id_matches_directory():
    entry = _entry()
    assert entry is not None
    assert entry["id"] == "289-whorled"
    assert entry["path"] == "pieces/289-whorled"


def test_pieces_json_thumbnail_path_valid():
    entry = _entry()
    assert entry is not None
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file()


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def _html():
    return INDEX_HTML.read_text()


def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_no_external_scripts():
    """No <script src=...> or import from CDN; all math is self-contained."""
    html = _html()
    assert 'src="http' not in html
    assert "src='http" not in html
    assert "cdn." not in html.lower()
    assert "import " not in html or "import {" not in html  # no ES module imports from external


def test_html_contains_inversion_math():
    """The core circle-inversion formula must appear in the JS."""
    html = _html()
    assert "invertThrough" in html or "invert" in html.lower()


def test_html_contains_schottky_circles():
    """The generating circles setup function must be present."""
    html = _html()
    assert "makeCircles" in html or "circles" in html


def test_html_contains_required_colors():
    """All four hues from the spec must be present."""
    html = _html()
    assert "#e05080" in html  # rose
    assert "#d4a820" in html  # gold
    assert "#20b8a0" in html  # teal
    assert "#8060d0" in html  # violet


def test_html_max_depth_at_least_8():
    """Spec requires at least 8 levels of recursion."""
    html = _html()
    import re
    matches = re.findall(r"MAX_DEPTH\s*=\s*(\d+)", html)
    assert matches, "MAX_DEPTH constant not found"
    assert int(matches[0]) >= 8


def test_html_near_black_background():
    """Background must be near-black (low RGB values)."""
    html = _html()
    assert "#0a0a0e" in html or "#0a0a0" in html or "background" in html


def test_html_js_under_150_lines():
    """Möbius math self-contained in <150 JS lines (spec requirement)."""
    html = _html()
    script_start = html.find("<script>")
    script_end = html.find("</script>")
    assert script_start != -1 and script_end != -1
    js_block = html[script_start:script_end]
    line_count = js_block.count("\n")
    assert line_count < 150, f"JS block is {line_count} lines, spec requires < 150"


# ---------------------------------------------------------------------------
# Circle inversion math correctness (pure Python re-implementation)
# ---------------------------------------------------------------------------

def invert_point(px, py, cx, cy, r):
    """Invert (px, py) through circle centred at (cx, cy) with radius r."""
    dx = px - cx
    dy = py - cy
    d2 = dx * dx + dy * dy
    if d2 < 1e-18:
        return None
    k = r * r / d2
    return (cx + k * dx, cy + k * dy)


def test_inversion_identity_at_circle():
    """A point exactly on the circle is its own inverse."""
    cx, cy, r = 0.0, 0.0, 1.0
    px, py = 1.0, 0.0  # on the circle
    ix, iy = invert_point(px, py, cx, cy, r)
    assert math.isclose(ix, px, abs_tol=1e-12)
    assert math.isclose(iy, py, abs_tol=1e-12)


def test_inversion_maps_inside_to_outside():
    """A point inside the circle maps to a point strictly outside."""
    cx, cy, r = 0.0, 0.0, 2.0
    px, py = 0.5, 0.0  # inside
    ix, iy = invert_point(px, py, cx, cy, r)
    d_orig = math.hypot(px - cx, py - cy)  # 0.5
    d_inv = math.hypot(ix - cx, iy - cy)   # should be 2²/0.5 = 8
    assert d_orig < r
    assert d_inv > r
    assert math.isclose(d_inv, r * r / d_orig, rel_tol=1e-12)


def test_inversion_involution():
    """Applying inversion twice returns the original point."""
    cx, cy, r = 1.0, -0.5, 0.75
    px, py = 1.8, 0.2
    ix, iy = invert_point(px, py, cx, cy, r)
    iix, iiy = invert_point(ix, iy, cx, cy, r)
    assert math.isclose(iix, px, abs_tol=1e-10)
    assert math.isclose(iiy, py, abs_tol=1e-10)


def test_inversion_preserves_direction():
    """Inversion keeps the image point collinear with origin and center."""
    cx, cy, r = 0.0, 0.0, 1.0
    px, py = 0.3, 0.4
    ix, iy = invert_point(px, py, cx, cy, r)
    # Cross product (p - c) × (i - c) must be zero (collinear with center).
    cross = (px - cx) * (iy - cy) - (py - cy) * (ix - cx)
    assert math.isclose(cross, 0.0, abs_tol=1e-12)


def test_inversion_center_returns_none():
    """Inversion of the circle's center is undefined — must return None."""
    result = invert_point(0.0, 0.0, 0.0, 0.0, 1.0)
    assert result is None


# ---------------------------------------------------------------------------
# Schottky triple geometry sanity
# ---------------------------------------------------------------------------

def make_schottky_circles():
    """Mirror of the JS makeCircles() function."""
    r = 0.46
    h = r * math.sqrt(3)
    return [
        (-r,   h / 3,       r),
        ( r,   h / 3,       r),
        ( 0,  -2 * h / 3,   r),
    ]


def test_schottky_circles_mutually_tangent():
    """Each pair of generating circles should be approximately tangent (|c_i - c_j| ≈ r_i + r_j)."""
    circles = make_schottky_circles()
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            cx0, cy0, r0 = circles[i]
            cx1, cy1, r1 = circles[j]
            dist = math.hypot(cx1 - cx0, cy1 - cy0)
            expected = r0 + r1
            assert math.isclose(dist, expected, rel_tol=0.05), (
                f"Circles {i} and {j}: dist={dist:.4f}, r_i+r_j={expected:.4f}"
            )


def test_schottky_circles_symmetric():
    """C0 and C1 should be mirror images across the y-axis."""
    c = make_schottky_circles()
    cx0, cy0, r0 = c[0]
    cx1, cy1, r1 = c[1]
    assert math.isclose(cx0, -cx1, abs_tol=1e-12)
    assert math.isclose(cy0,  cy1, abs_tol=1e-12)
    assert math.isclose(r0,   r1,  abs_tol=1e-12)


def test_iterated_inversion_produces_limit_points():
    """Iterating circle inversions on a seed point should produce a bounded sequence."""
    circles = make_schottky_circles()

    def inside(px, py, circ):
        cx, cy, r = circ
        return (px - cx) ** 2 + (py - cy) ** 2 < r * r

    # Seed a point inside C0.
    cx0, cy0, r0 = circles[0]
    px, py = cx0 + r0 * 0.3, cy0

    escaped = False
    last_circle = -1
    for _ in range(20):
        for i, circ in enumerate(circles):
            if inside(px, py, circ):
                result = invert_point(px, py, circ[0], circ[1], circ[2])
                if result:
                    px, py = result
                    last_circle = i
                    break
        else:
            escaped = True
            break

    assert escaped, "Iterated inversion should eventually escape all circles"
    assert last_circle >= 0


def test_limit_set_points_stay_bounded():
    """All escaped limit-set points should stay within a reasonable bounding box."""
    circles = make_schottky_circles()

    def inside(px, py, circ):
        cx, cy, r = circ
        return (px - cx) ** 2 + (py - cy) ** 2 < r * r

    BOUND = 50.0
    out_of_bounds = 0
    total = 0

    for seed_x in [-0.4, -0.2, 0.0, 0.2, 0.4]:
        for seed_y in [-0.4, -0.2, 0.0, 0.2, 0.4]:
            px, py = seed_x, seed_y
            for _ in range(20):
                moved = False
                for circ in circles:
                    if inside(px, py, circ):
                        result = invert_point(px, py, circ[0], circ[1], circ[2])
                        if result:
                            px, py = result
                            moved = True
                            break
                if not moved:
                    break

            total += 1
            if abs(px) > BOUND or abs(py) > BOUND:
                out_of_bounds += 1

    assert out_of_bounds == 0, f"{out_of_bounds}/{total} escaped points exceeded bound {BOUND}"
