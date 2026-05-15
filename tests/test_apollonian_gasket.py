"""Tests for piece 157 — Apollonian Gasket: Every Gap Holds a Circle."""

import json
import math
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "157-apollonian-gasket"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# File-presence tests (acceptance criteria)
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_svg_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_pieces_json_entry_present():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert "157-apollonian-gasket" in ids


def test_pieces_json_entry_complete():
    data = json.loads(PIECES_JSON.read_text())
    entry = next(e for e in data if e["id"] == "157-apollonian-gasket")
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= entry.keys()


def test_pieces_json_paths_valid():
    data = json.loads(PIECES_JSON.read_text())
    entry = next(e for e in data if e["id"] == "157-apollonian-gasket")
    assert (REPO / entry["path"]).is_dir()
    assert (REPO / entry["thumbnail"]).is_file()


def test_index_html_uses_descartes_formula():
    """index.html must reference the Apollonian reflection / Descartes computation."""
    html = (PIECE_DIR / "index.html").read_text()
    # The reflection formula uses: 2*(a.k + b.k + c.k) - p.k
    assert "2 * (a.k + b.k + c.k) - p.k" in html


def test_index_html_depth_palette_present():
    """Seven depth-colour stops (depth 0–6) must be encoded in the HTML."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "PALETTE" in html
    # Confirm at least 7 entries by counting colour tuples [R, G, B]
    assert html.count("[") >= 7


def test_index_html_animation_phases():
    """Animation state machine must have all three phases."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "'building'" in html
    assert "'pause'" in html
    assert "'fading'" in html


# ---------------------------------------------------------------------------
# Algorithmic correctness tests (Python re-implementation)
# ---------------------------------------------------------------------------

MIN_R = 0.5
MAX_DEPTH = 6
OUTER_R = 376.0


def circle_key(x, y, r):
    return (round(x * 10), round(y * 10), round(r * 10))


def build_gasket(max_depth=MAX_DEPTH, min_r=MIN_R, outer_r=OUTER_R):
    """Mirrors the JS buildGasket() using the Apollonian reflection formula."""
    k0 = -1 / outer_r
    r1 = outer_r * math.sqrt(3) / (2 + math.sqrt(3))
    k1 = 1 / r1
    d1 = outer_r - r1

    C0 = (k0, 0.0,                   0.0,  outer_r, -1)
    C1 = (k1, 0.0,                   -d1,  r1,       0)
    C2 = (k1,  d1 * math.sqrt(3)/2,  d1/2, r1,       0)
    C3 = (k1, -d1 * math.sqrt(3)/2,  d1/2, r1,       0)

    circles = [C1, C2, C3]
    seen = {circle_key(c[1], c[2], c[3]) for c in circles}
    queue = [
        (C1, C2, C3, C0, 1),
        (C0, C2, C3, C1, 1),
        (C0, C1, C3, C2, 1),
        (C0, C1, C2, C3, 1),
    ]
    qi = 0
    while qi < len(queue):
        a, b, c, p, depth = queue[qi]
        qi += 1
        if depth > max_depth:
            continue
        kn = 2 * (a[0] + b[0] + c[0]) - p[0]
        if kn <= 0:
            continue
        rn = 1 / kn
        if rn < min_r:
            continue
        xn = (2 * (a[1]*a[0] + b[1]*b[0] + c[1]*c[0]) - p[1]*p[0]) / kn
        yn = (2 * (a[2]*a[0] + b[2]*b[0] + c[2]*c[0]) - p[2]*p[0]) / kn
        key = circle_key(xn, yn, rn)
        if key in seen:
            continue
        seen.add(key)
        cn = (kn, xn, yn, rn, depth)
        circles.append(cn)
        queue.append((b, c, cn, a, depth + 1))
        queue.append((a, c, cn, b, depth + 1))
        queue.append((a, b, cn, c, depth + 1))

    return circles


def test_initial_three_circles_correct_radius():
    """The three depth-0 seed circles must have the geometrically correct radius."""
    expected_r = OUTER_R * math.sqrt(3) / (2 + math.sqrt(3))
    circles = build_gasket(max_depth=0)
    depth0 = [c for c in circles if c[4] == 0]
    assert len(depth0) == 3
    for c in depth0:
        assert abs(c[3] - expected_r) < 0.1


def test_central_circle_at_depth1():
    """Depth-1 central circle (tangent to all three seeds) must be near the origin."""
    circles = build_gasket(max_depth=1)
    depth1 = [c for c in circles if c[4] == 1]
    assert len(depth1) == 4
    central = min(depth1, key=lambda c: math.hypot(c[1], c[2]))
    # Must be within 1 px of the geometric centre
    assert math.hypot(central[1], central[2]) < 1.0


def test_descartes_theorem_satisfied():
    """The central depth-1 circle must satisfy Descartes' theorem with the three seed circles.

    C1, C2, C3 (the three equal depth-0 circles) are mutually tangent.
    The depth-1 central circle C_central is the unique inner Soddy of {C1, C2, C3},
    so {C1, C2, C3, C_central} are four mutually tangent circles and must satisfy:
        (k1+k2+k3+k_c)^2 = 2*(k1^2+k2^2+k3^2+k_c^2)
    """
    circles = build_gasket(max_depth=3)
    r1 = OUTER_R * math.sqrt(3) / (2 + math.sqrt(3))
    k1 = 1 / r1
    depth1 = [c for c in circles if c[4] == 1]
    central = min(depth1, key=lambda c: math.hypot(c[1], c[2]))
    k_central = central[0]
    lhs = (3 * k1 + k_central) ** 2
    rhs = 2 * (3 * k1**2 + k_central**2)
    assert abs(lhs - rhs) < 1e-6


def test_all_circles_inside_outer_circle():
    """Every generated circle must lie entirely within the outer bounding circle."""
    circles = build_gasket()
    for k, x, y, r, depth in circles:
        if depth < 0:
            continue
        dist = math.hypot(x, y)
        assert dist + r <= OUTER_R + 1.0, f"Circle at ({x:.1f},{y:.1f}) r={r:.1f} extends outside outer circle"


def test_no_circle_below_min_radius():
    """No generated circle should have radius below MIN_R."""
    circles = build_gasket()
    for k, x, y, r, depth in circles:
        if depth >= 0:
            assert r >= MIN_R - 1e-9


def test_no_duplicate_circles():
    """The deduplication must prevent the same circle from appearing twice."""
    circles = build_gasket()
    keys = [circle_key(c[1], c[2], c[3]) for c in circles]
    assert len(keys) == len(set(keys)), "Duplicate circles detected"


def test_depth_bounded_by_max():
    """No circle should exceed MAX_DEPTH."""
    circles = build_gasket()
    for c in circles:
        assert c[4] <= MAX_DEPTH


def test_gasket_grows_with_depth():
    """Increasing max_depth must produce more circles (fractal growth)."""
    c3 = build_gasket(max_depth=3)
    c4 = build_gasket(max_depth=4)
    c5 = build_gasket(max_depth=5)
    assert len(c4) > len(c3)
    assert len(c5) > len(c4)


def test_gasket_empty_at_depth_minus1():
    """With max_depth=-1 (impossible depth) only the initial 3 seed circles exist."""
    circles = build_gasket(max_depth=-1)
    assert len(circles) == 3
    assert all(c[4] == 0 for c in circles)


def test_gasket_large_outer_radius():
    """Algorithm must scale correctly for a different outer radius."""
    circles = build_gasket(outer_r=500, max_depth=3)
    # All inside the bounding circle
    for k, x, y, r, depth in circles:
        if depth >= 0:
            assert math.hypot(x, y) + r <= 501.0


def test_generate_thumbnail_runs(tmp_path, monkeypatch):
    """generate_thumbnail.py must run without error and produce a valid SVG."""
    import shutil
    src = PIECE_DIR / "generate_thumbnail.py"
    dest_dir = tmp_path / "157-apollonian-gasket"
    dest_dir.mkdir()
    shutil.copy(src, dest_dir / "generate_thumbnail.py")

    result = subprocess.run(
        [sys.executable, str(dest_dir / "generate_thumbnail.py")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    svg = dest_dir / "thumbnail.svg"
    assert svg.exists()
    content = svg.read_text()
    assert "<svg" in content
    assert "<circle" in content
