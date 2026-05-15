"""Tests for pieces/142-light-divided: Bowyer-Watson Delaunay triangulation SVG."""

import importlib.util
import json
import math
import pathlib
import random
import xml.etree.ElementTree as ET


REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "142-light-divided"
GENERATE_PY = PIECE_DIR / "generate.py"
PIECE_SVG = PIECE_DIR / "piece.svg"
THUMBNAIL_SVG = PIECE_DIR / "thumbnail.svg"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "142-light-divided"

# ---------------------------------------------------------------------------
# Import generate.py for white-box algorithm tests
# ---------------------------------------------------------------------------

spec = importlib.util.spec_from_file_location("generate_142", GENERATE_PY)
_gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_gen)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry() -> dict:
    """Return the pieces.json entry for this piece, or raise AssertionError."""
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_generate_py_exists():
    assert GENERATE_PY.is_file()


def test_piece_svg_exists():
    assert PIECE_SVG.is_file()


def test_thumbnail_svg_exists():
    assert THUMBNAIL_SVG.is_file()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_readme_exists():
    assert README.is_file()


# ---------------------------------------------------------------------------
# piece.svg validation
# ---------------------------------------------------------------------------

def test_piece_svg_is_valid_xml():
    """piece.svg must be well-formed XML."""
    ET.fromstring(PIECE_SVG.read_text())


def test_piece_svg_under_500kb():
    assert PIECE_SVG.stat().st_size < 500_000, (
        f"piece.svg is {PIECE_SVG.stat().st_size:,} bytes (limit 500 000)"
    )


def test_piece_svg_has_polygon_elements():
    assert "<polygon" in PIECE_SVG.read_text()


def test_piece_svg_has_many_triangles():
    """~400 seed points should yield well over 200 triangles."""
    count = PIECE_SVG.read_text().count("<polygon")
    assert count >= 200, f"Expected ≥200 triangles, got {count}"


def test_piece_svg_polygons_have_fill():
    root = ET.fromstring(PIECE_SVG.read_text())
    polys = root.findall(".//polygon") or root.findall(
        ".//{http://www.w3.org/2000/svg}polygon"
    )
    assert polys, "No <polygon> elements found in piece.svg"
    for p in polys[:10]:
        assert p.get("fill"), f"polygon missing fill: {ET.tostring(p)}"


def test_piece_svg_has_thin_stroke():
    """Stroke-width of 0.5 gives the stained-glass lead-came look."""
    assert "0.5" in PIECE_SVG.read_text()


def test_piece_svg_has_viewbox():
    assert "viewBox" in PIECE_SVG.read_text()


def test_piece_svg_has_background_rect():
    svg = PIECE_SVG.read_text()
    assert "<rect" in svg


# ---------------------------------------------------------------------------
# thumbnail.svg validation
# ---------------------------------------------------------------------------

def test_thumbnail_is_valid_xml():
    ET.fromstring(THUMBNAIL_SVG.read_text())


def test_thumbnail_has_polygon_elements():
    assert "<polygon" in THUMBNAIL_SVG.read_text()


def test_thumbnail_not_trivially_empty():
    assert len(THUMBNAIL_SVG.read_text()) > 500


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL_SVG.read_text()


def test_thumbnail_has_width_400():
    svg = THUMBNAIL_SVG.read_text()
    assert 'width="400"' in svg


# ---------------------------------------------------------------------------
# index.html validation
# ---------------------------------------------------------------------------

def test_index_html_has_doctype():
    assert INDEX_HTML.read_text().strip().startswith("<!DOCTYPE html>")


def test_index_html_references_piece_svg():
    html = INDEX_HTML.read_text()
    assert "piece.svg" in html or "<svg" in html


def test_index_html_has_charset():
    assert 'charset="UTF-8"' in INDEX_HTML.read_text()


# ---------------------------------------------------------------------------
# README validation
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_bowyer_watson():
    assert "bowyer" in README.read_text().lower()


def test_readme_mentions_delaunay():
    assert "delaunay" in README.read_text().lower()


def test_readme_mentions_stdlib_only():
    """README must state that no external dependencies are used."""
    text = README.read_text().lower()
    assert "stdlib" in text or "standard library" in text or "no numpy" in text


# ---------------------------------------------------------------------------
# No external dependencies in generate.py
# ---------------------------------------------------------------------------

def test_generate_py_no_numpy():
    src = GENERATE_PY.read_text()
    assert "import numpy" not in src
    assert "from numpy" not in src


def test_generate_py_no_scipy():
    src = GENERATE_PY.read_text()
    assert "import scipy" not in src
    assert "from scipy" not in src


# ---------------------------------------------------------------------------
# circumcircle — white-box unit tests
# ---------------------------------------------------------------------------

def test_circumcircle_right_angle_triangle():
    """Circumcircle of a right-angle triangle: center is the hypotenuse midpoint."""
    # Right triangle at (0,0), (2,0), (0,2): hypotenuse midpoint = (1,1), r=√2
    cc = _gen.circumcircle(0, 0, 2, 0, 0, 2)
    assert cc is not None
    ux, uy, r2 = cc
    assert abs(ux - 1.0) < 1e-6
    assert abs(uy - 1.0) < 1e-6
    assert abs(math.sqrt(r2) - math.sqrt(2)) < 1e-6


def test_circumcircle_equilateral():
    """Circumcenter of an equilateral triangle is at its centroid."""
    # Equilateral: (0,0), (2,0), (1, √3)
    h = math.sqrt(3)
    cc = _gen.circumcircle(0, 0, 2, 0, 1, h)
    assert cc is not None
    ux, uy, r2 = cc
    assert abs(ux - 1.0) < 1e-6
    assert abs(uy - h / 3) < 1e-6


def test_circumcircle_collinear_returns_none():
    """Collinear points have no circumcircle."""
    assert _gen.circumcircle(0, 0, 1, 0, 2, 0) is None


def test_circumcircle_all_three_vertices_equidistant():
    """All three triangle vertices must lie on the circumcircle."""
    ax, ay = 0.0, 0.0
    bx, by = 4.0, 0.0
    cx, cy = 1.0, 3.0
    cc = _gen.circumcircle(ax, ay, bx, by, cx, cy)
    assert cc is not None
    ux, uy, r2 = cc
    for px, py in [(ax, ay), (bx, by), (cx, cy)]:
        d2 = (px - ux) ** 2 + (py - uy) ** 2
        assert abs(d2 - r2) < 1e-6, f"vertex ({px},{py}) not on circumcircle"


# ---------------------------------------------------------------------------
# bowyer_watson — white-box unit tests
# ---------------------------------------------------------------------------

def test_bowyer_watson_empty_returns_empty():
    """Zero points → no triangles."""
    assert _gen.bowyer_watson([], 800, 800) == []


def test_bowyer_watson_one_point_returns_empty():
    """One point cannot form a triangle."""
    assert _gen.bowyer_watson([(400, 400)], 800, 800) == []


def test_bowyer_watson_two_points_returns_empty():
    """Two points cannot form a triangle."""
    assert _gen.bowyer_watson([(100, 100), (700, 700)], 800, 800) == []


def test_bowyer_watson_three_points_one_triangle():
    """Three non-collinear points produce exactly one triangle."""
    pts = [(100, 100), (700, 100), (400, 700)]
    tris = _gen.bowyer_watson(pts, 800, 800)
    assert len(tris) == 1


def test_bowyer_watson_four_corners_two_triangles():
    """Four corners of a rectangle triangulate into exactly two triangles."""
    pts = [(10, 10), (790, 10), (790, 790), (10, 790)]
    tris = _gen.bowyer_watson(pts, 800, 800)
    assert len(tris) == 2


def test_bowyer_watson_indices_in_range():
    """All returned vertex indices must be valid indices into the points list."""
    rng = random.Random(7)
    pts = [(rng.uniform(50, 750), rng.uniform(50, 750)) for _ in range(50)]
    tris = _gen.bowyer_watson(pts, 800, 800)
    for tri in tris:
        for v in tri:
            assert 0 <= v < len(pts), f"vertex index {v} out of range [0, {len(pts)})"


def test_bowyer_watson_no_duplicate_triangles():
    """Each triangle must appear at most once in the result."""
    rng = random.Random(13)
    pts = [(rng.uniform(50, 750), rng.uniform(50, 750)) for _ in range(80)]
    tris = _gen.bowyer_watson(pts, 800, 800)
    # Normalise each triangle to a frozenset so order doesn't matter
    as_sets = [frozenset(tri) for tri in tris]
    assert len(as_sets) == len(set(as_sets)), "Duplicate triangles found"


def test_bowyer_watson_euler_relation():
    """For N random interior points, Euler's formula gives T ≈ 2N triangles."""
    rng = random.Random(99)
    N = 100
    pts = [(rng.uniform(50, 750), rng.uniform(50, 750)) for _ in range(N)]
    tris = _gen.bowyer_watson(pts, 800, 800)
    # Delaunay: T ≈ 2N − 2 − b where b is boundary count; loose bounds
    assert N < len(tris) < 3 * N, f"Unexpected triangle count {len(tris)} for N={N}"


# ---------------------------------------------------------------------------
# lerp3 — white-box unit tests
# ---------------------------------------------------------------------------

def test_lerp3_at_zero_returns_first_stop():
    stops = [(220, 100, 130), (210, 148, 55), (90, 110, 145)]
    assert _gen.lerp3(0.0, stops) == (220, 100, 130)


def test_lerp3_at_one_returns_last_stop():
    stops = [(220, 100, 130), (210, 148, 55), (90, 110, 145)]
    assert _gen.lerp3(1.0, stops) == (90, 110, 145)


def test_lerp3_at_half_returns_middle_stop():
    stops = [(220, 100, 130), (210, 148, 55), (90, 110, 145)]
    assert _gen.lerp3(0.5, stops) == (210, 148, 55)


def test_lerp3_clamped_below():
    stops = [(220, 100, 130), (210, 148, 55), (90, 110, 145)]
    assert _gen.lerp3(-1.0, stops) == _gen.lerp3(0.0, stops)


def test_lerp3_clamped_above():
    stops = [(220, 100, 130), (210, 148, 55), (90, 110, 145)]
    assert _gen.lerp3(2.0, stops) == _gen.lerp3(1.0, stops)


def test_lerp3_quarter_is_between_first_and_middle():
    stops = [(0, 0, 0), (100, 100, 100), (200, 200, 200)]
    r, g, b = _gen.lerp3(0.25, stops)
    assert 0 < r < 100


# ---------------------------------------------------------------------------
# generate_svg — integration tests
# ---------------------------------------------------------------------------

def test_generate_svg_returns_string():
    assert isinstance(_gen.generate_svg(n_points=10, width=200, height=200), str)


def test_generate_svg_is_valid_xml():
    ET.fromstring(_gen.generate_svg(n_points=15, width=200, height=200))


def test_generate_svg_has_polygon_elements():
    svg = _gen.generate_svg(n_points=20, width=300, height=300)
    assert "<polygon" in svg


def test_generate_svg_deterministic():
    """Same seed always produces identical SVG."""
    a = _gen.generate_svg(n_points=20, width=200, height=200, seed=77)
    b = _gen.generate_svg(n_points=20, width=200, height=200, seed=77)
    assert a == b


def test_generate_svg_different_seeds_differ():
    a = _gen.generate_svg(n_points=20, width=200, height=200, seed=1)
    b = _gen.generate_svg(n_points=20, width=200, height=200, seed=2)
    assert a != b


def test_generate_svg_more_points_more_triangles():
    """Larger point count must produce more triangles."""
    few = _gen.generate_svg(n_points=10, width=400, height=400, seed=42)
    many = _gen.generate_svg(n_points=100, width=400, height=400, seed=42)
    assert many.count("<polygon") > few.count("<polygon")


def test_generate_svg_three_points_no_crash():
    """Edge case: minimum viable point count must not raise."""
    svg = _gen.generate_svg(n_points=3, width=100, height=100)
    assert "<svg" in svg


# ---------------------------------------------------------------------------
# Failure mode: incorrect implementation detection
# ---------------------------------------------------------------------------

def test_bowyer_watson_collinear_three_points_no_triangle():
    """Collinear points cannot form a valid Delaunay triangle.

    The circumcircle function returns None for collinear inputs, so any
    triangle formed from three collinear points should not appear in the
    output. The algorithm must handle this gracefully (no crash, 0 results).
    """
    pts = [(100, 100), (400, 400), (700, 700)]
    tris = _gen.bowyer_watson(pts, 800, 800)
    # Collinear: super-triangle handling may produce 0 real triangles
    for tri in tris:
        verts = [pts[v] for v in tri]
        xs = [v[0] for v in verts]
        ys = [v[1] for v in verts]
        # Compute area; must be non-zero for any returned triangle
        area2 = abs(
            (xs[1] - xs[0]) * (ys[2] - ys[0])
            - (xs[2] - xs[0]) * (ys[1] - ys[0])
        )
        assert area2 > 1e-6, f"Degenerate (zero-area) triangle returned: {tri}"


# ---------------------------------------------------------------------------
# pieces.json contract
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [e.get("id") for e in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_entry_has_all_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - _entry().keys()
    assert not missing, f"Missing fields: {missing}"


def test_entry_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_entry_path_matches_id():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_entry_technique_mentions_delaunay():
    assert "delaunay" in _entry()["technique"].lower()


def test_entry_technique_mentions_bowyer_watson():
    assert "bowyer" in _entry()["technique"].lower() or "watson" in _entry()["technique"].lower()


def test_entry_thumbnail_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file(), f"Thumbnail not found: {thumb}"


def test_entry_id_matches_dir_name():
    entry = _entry()
    piece_dir = REPO / entry["path"]
    assert entry["id"] == piece_dir.name


def test_entry_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids))


def test_pieces_json_still_valid():
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)
    ids = [e["id"] for e in data]
    assert "01-amber-current" in ids
    assert "139-circle-packing" in ids, "Previous piece must still be present"
    assert PIECE_ID in ids


def test_piece_142_is_after_139_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    idx_139 = ids.index("139-circle-packing")
    idx_142 = ids.index(PIECE_ID)
    assert idx_142 > idx_139
