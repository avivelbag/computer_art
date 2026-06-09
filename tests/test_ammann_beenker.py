"""Tests for piece 296 — Eightfold Path (Ammann-Beenker tiling)."""

import importlib.util
import math
import pathlib
import sys
import types

import pytest

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "296-ammann-beenker"
GEN_SCRIPT = PIECE_DIR / "generate_thumbnail.py"


def load_gen():
    """Import generate_thumbnail.py as a module without running main()."""
    spec = importlib.util.spec_from_file_location("gen_ammann", GEN_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return load_gen()


# ---------------------------------------------------------------------------
# Piece structure
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_svg_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_index_no_external_libraries():
    """index.html must not load any external JS library."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "cdn." not in html
    assert "unpkg." not in html
    assert "jsdelivr" not in html
    assert "<script src=" not in html


def test_index_uses_required_colors():
    html = (PIECE_DIR / "index.html").read_text()
    assert "#f5f0e8" in html   # background
    assert "#c8882a" in html   # squares
    assert "#3a5a8a" in html   # rhombi
    assert "#1a1a1a" in html   # stroke


# ---------------------------------------------------------------------------
# Tiling math — octagonal seed
# ---------------------------------------------------------------------------

def test_seed_has_eight_rhombi(gen):
    tiles = gen.make_seed(100.0)
    assert len(tiles) == 8
    assert all(t == "R" for t, _ in tiles)


def test_seed_rhombus_edge_length(gen):
    """Each rhombus in the seed has all sides equal to the given edge length."""
    edge = 100.0
    tiles = gen.make_seed(edge)
    for _, v in tiles:
        A, B, C, D = v
        sides = [
            math.hypot(B[0]-A[0], B[1]-A[1]),
            math.hypot(C[0]-B[0], C[1]-B[1]),
            math.hypot(D[0]-C[0], D[1]-C[1]),
            math.hypot(A[0]-D[0], A[1]-D[1]),
        ]
        for s in sides:
            assert abs(s - edge) < 1e-9, f"Side {s} != {edge}"


def test_seed_8fold_rotational_symmetry(gen):
    """The octagonal seed is invariant under 45° rotation (up to reordering)."""
    edge = 100.0
    tiles = gen.make_seed(edge)
    angle = math.pi / 4
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    def rot_pt(p):
        return (p[0]*cos_a - p[1]*sin_a, p[0]*sin_a + p[1]*cos_a)

    # Rotate all tile centroids by 45° — should match original centroids
    def centroid(v):
        xs = sum(p[0] for p in v) / len(v)
        ys = sum(p[1] for p in v) / len(v)
        return (xs, ys)

    centroids = sorted((centroid(v) for _, v in tiles), key=lambda p: math.atan2(p[1], p[0]))
    rotated = sorted((rot_pt(c) for c in centroids), key=lambda p: math.atan2(p[1], p[0]))

    for orig, rot in zip(centroids, rotated):
        assert abs(orig[0] - rot[0]) < 1e-8
        assert abs(orig[1] - rot[1]) < 1e-8


# ---------------------------------------------------------------------------
# Inflation / deflation
# ---------------------------------------------------------------------------

def test_one_inflation_of_seed_tile_counts(gen):
    """One deflation of the 8-rhombus seed produces the expected tile breakdown."""
    tiles = gen.make_seed(100.0)
    inflated = gen.inflate(tiles)
    sq = sum(1 for t, _ in inflated if t == "S")
    rh = sum(1 for t, _ in inflated if t == "R")
    # Each rhombus → 1 rhombus + 2 squares + 2 rhombi; total per parent = 5
    # 8 parent rhombi × 5 = 40 children
    assert sq + rh == 40
    assert sq == 16    # 8 × 2 squares per rhombus
    assert rh == 24    # 8 × (1 + 2) rhombi per rhombus


def test_inflate_square_count(gen):
    """A single square deflates into exactly 5 children (1 sq + 4 rhombi)."""
    # Build a unit square
    sq_tile = ("S", [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)])
    out = []
    gen.inflate_square(sq_tile[1], 1.0 / gen.DELTA, out)
    sq = sum(1 for t, _ in out if t == "S")
    rh = sum(1 for t, _ in out if t == "R")
    assert sq == 1
    assert rh == 4


def test_inflate_rhombus_count(gen):
    """A single rhombus deflates into exactly 5 children (1 rh + 2 sq + 2 rh)."""
    # 45° rhombus: A at origin, B along x, D at 45°
    L = 10.0
    a45 = math.pi / 4
    A = (0.0, 0.0)
    B = (L, 0.0)
    D = (L * math.cos(a45), L * math.sin(a45))
    C = (B[0] + D[0], B[1] + D[1])
    rh_tile = ("R", [A, B, C, D])
    out = []
    gen.inflate_rhombus(rh_tile[1], 1.0 / gen.DELTA, out)
    sq = sum(1 for t, _ in out if t == "S")
    rh = sum(1 for t, _ in out if t == "R")
    assert sq == 2
    assert rh == 3


def test_child_edge_length_scales_by_silver_ratio(gen):
    """After one deflation, every child tile has edge length = parent edge / δ."""
    edge = 100.0
    tiles = gen.make_seed(edge)
    inflated = gen.inflate(tiles)

    def tile_edge(v):
        A, B = v[0], v[1]
        return math.hypot(B[0]-A[0], B[1]-A[1])

    expected = edge / gen.DELTA
    for _, v in inflated[:20]:   # sample first 20
        e = tile_edge(v)
        assert abs(e - expected) < 1e-6, f"Edge {e} != {expected}"


def test_multiple_deflations_grow_tile_count(gen):
    """Each deflation step multiplies tile count by approximately δ² ≈ 5.83."""
    tiles = gen.make_seed(100.0)
    prev = len(tiles)
    for _ in range(3):
        tiles = gen.inflate(tiles)
        ratio = len(tiles) / prev
        assert 4.5 < ratio < 7.0, f"Growth ratio {ratio} outside expected band"
        prev = len(tiles)


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------

def test_thumbnail_svg_wellformed():
    svg = (PIECE_DIR / "thumbnail.svg").read_text()
    assert svg.startswith("<svg")
    assert svg.strip().endswith("</svg>")
    assert "polygon" in svg


def test_thumbnail_svg_contains_both_tile_types():
    """The thumbnail SVG must include tiles in both ochre and slate-blue."""
    svg = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#c8882a" in svg   # square fill
    assert "#3a5a8a" in svg   # rhombus fill


def test_thumbnail_svg_has_reasonable_tile_count():
    """4 deflation steps from an 8-rhombus seed should yield at least 1000 tiles."""
    import re
    svg = (PIECE_DIR / "thumbnail.svg").read_text()
    count = len(re.findall(r"<polygon", svg))
    assert count >= 1000, f"Only {count} polygons in thumbnail"


def test_thumbnail_svg_tiles_near_center():
    """The tiling must fill the canvas center, not just the edges."""
    import re
    svg = (PIECE_DIR / "thumbnail.svg").read_text()
    polys = re.findall(r'points="([^"]+)"', svg)
    near_center = 0
    for p in polys:
        pts = [float(x) for pair in p.split() for x in pair.split(",")]
        xs = pts[::2]; ys = pts[1::2]
        cx = sum(xs) / len(xs); cy = sum(ys) / len(ys)
        if abs(cx - 200) < 80 and abs(cy - 200) < 80:
            near_center += 1
    assert near_center >= 100, f"Only {near_center} tiles near center"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_inflate_empty_list(gen):
    """Inflating an empty tile list returns an empty list without error."""
    assert gen.inflate([]) == []


def test_large_seed_edge_does_not_crash(gen):
    """A very large seed edge (10_000) should produce valid tiles."""
    tiles = gen.make_seed(10_000.0)
    inflated = gen.inflate(tiles)
    assert len(inflated) == 40   # same count regardless of edge length


def test_zero_deflations_returns_seed(gen):
    """Zero deflations: tile list is unchanged from seed."""
    tiles = gen.make_seed(50.0)
    result = tiles[:]
    for _ in range(0):
        result = gen.inflate(result)
    assert len(result) == 8
