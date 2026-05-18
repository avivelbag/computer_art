"""Tests for piece 255-islamic-stars."""
import json
import math
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "255-islamic-stars"


# ---------------------------------------------------------------------------
# File-system checks
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_svg_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

def load_entry():
    pieces = json.loads((REPO / "pieces.json").read_text())
    for p in pieces:
        if p.get("id") == "255-islamic-stars":
            return p
    return None


def test_pieces_json_entry_present():
    assert load_entry() is not None, "255-islamic-stars not found in pieces.json"


def test_pieces_json_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = load_entry()
    assert entry is not None
    assert required <= entry.keys()


def test_pieces_json_id_matches_dir():
    entry = load_entry()
    assert entry is not None
    assert entry["id"] == PIECE_DIR.name


def test_pieces_json_thumbnail_path_is_file():
    entry = load_entry()
    assert entry is not None
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file(), f"Thumbnail file missing: {thumb}"


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def html_text():
    return (PIECE_DIR / "index.html").read_text()


def test_index_html_is_self_contained():
    """No external src= or href= pointing to http(s) resources."""
    text = html_text()
    import re
    # Allow data: URIs; reject any http/https import
    external = re.findall(r'(?:src|href)\s*=\s*["\']https?://', text)
    assert not external, f"External imports found: {external}"


def test_index_html_has_canvas():
    assert "<canvas" in html_text()


def test_index_html_has_requestanimationframe():
    assert "requestAnimationFrame" in html_text()


def test_index_html_mentions_both_symmetry_families():
    """Both 6-fold (hex) and 8-fold (square) families must be present in the code."""
    text = html_text()
    assert "hexGrid" in text or "hexCells" in text, "6-fold hex grid code missing"
    assert "squareGrid" in text or "squareCells" in text, "8-fold square grid code missing"


def test_index_html_palette_colors():
    """The three required palette colors must appear in the HTML."""
    text = html_text()
    assert "#0d4040" in text or "0d4040" in text, "Deep teal fill color missing"
    assert "#c8922a" in text or "c8922a" in text, "Warm gold color missing"
    assert "#e8dfc0" in text or "e8dfc0" in text, "Off-white parchment color missing"


# ---------------------------------------------------------------------------
# Geometry unit tests (pure Python reimplementation)
# ---------------------------------------------------------------------------

def star_polygon(cx, cy, R, r, n):
    """Parametric n-pointed star polygon — mirrors the JS implementation."""
    pts = []
    step = math.pi / n
    for i in range(n):
        a1 = -math.pi / 2 + 2 * math.pi * i / n
        a2 = a1 + step
        pts.append((cx + R * math.cos(a1), cy + R * math.sin(a1)))
        pts.append((cx + r * math.cos(a2), cy + r * math.sin(a2)))
    return pts


def test_star_polygon_point_count():
    """starPolygon(n) must return exactly 2n points."""
    for n in (6, 8, 12):
        pts = star_polygon(0, 0, 100, 40, n)
        assert len(pts) == 2 * n, f"Expected {2*n} points for n={n}, got {len(pts)}"


def test_star_polygon_outer_tips_at_radius_R():
    """Every even-indexed point (outer tip) must lie at distance R from centre."""
    R, r, n = 100, 40, 8
    pts = star_polygon(0, 0, R, r, n)
    for i in range(0, len(pts), 2):
        x, y = pts[i]
        d = math.hypot(x, y)
        assert abs(d - R) < 1e-9, f"Outer tip {i} at wrong radius {d:.4f} (expected {R})"


def test_star_polygon_inner_notches_at_radius_r():
    """Every odd-indexed point (inner notch) must lie at distance r from centre."""
    R, r, n = 100, 40, 8
    pts = star_polygon(0, 0, R, r, n)
    for i in range(1, len(pts), 2):
        x, y = pts[i]
        d = math.hypot(x, y)
        assert abs(d - r) < 1e-9, f"Inner notch {i} at wrong radius {d:.4f} (expected {r})"


def test_star_polygon_centred_correctly():
    """Centroid of all star points must be very close to (cx, cy)."""
    cx, cy = 150, 200
    pts = star_polygon(cx, cy, 80, 32, 6)
    mx = sum(p[0] for p in pts) / len(pts)
    my = sum(p[1] for p in pts) / len(pts)
    assert abs(mx - cx) < 1e-9, f"x centroid off: {mx:.4f} vs {cx}"
    assert abs(my - cy) < 1e-9, f"y centroid off: {my:.4f} vs {cy}"


def test_star_polygon_n6_first_tip_points_up():
    """For n=6 with base angle -π/2, first outer tip should be directly above centre."""
    pts = star_polygon(0, 0, 100, 40, 6)
    x, y = pts[0]
    assert abs(x) < 1e-9, f"First tip should be on y-axis, got x={x:.4f}"
    assert y < 0, "First tip should be above centre (negative y in screen coords)"


def test_star_polygon_n8_tip_angles_evenly_spaced():
    """Outer tips of an 8-pointed star must be 45° apart."""
    pts = star_polygon(0, 0, 100, 40, 8)
    tips = pts[::2]  # every other point starting at 0
    angles = [math.atan2(y, x) for x, y in tips]
    diffs = [(angles[(i + 1) % 8] - angles[i]) % (2 * math.pi) for i in range(8)]
    expected = 2 * math.pi / 8
    for i, d in enumerate(diffs):
        assert abs(d - expected) < 1e-9, f"Tip angle gap {i}: {math.degrees(d):.4f}° (expected 45°)"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_star_polygon_n_equals_3():
    """n=3 produces a 3-pointed star (6 points total) without error."""
    pts = star_polygon(50, 50, 40, 15, 3)
    assert len(pts) == 6


def test_star_polygon_degenerate_r_equals_R():
    """When r == R all points lie on the same circle — polygon degenerates to n-gon."""
    R = 100
    pts = star_polygon(0, 0, R, R, 8)
    for x, y in pts:
        assert abs(math.hypot(x, y) - R) < 1e-9


def test_star_polygon_large_n():
    """Large n (e.g. 36) should not raise and should return 72 points."""
    pts = star_polygon(0, 0, 200, 100, 36)
    assert len(pts) == 72


# ---------------------------------------------------------------------------
# thumbnail.svg minimal checks
# ---------------------------------------------------------------------------

def test_thumbnail_svg_has_correct_palette():
    text = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#0d4040" in text or "0d4040" in text
    assert "#c8922a" in text or "c8922a" in text


def test_thumbnail_svg_has_polygon_elements():
    text = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<polygon" in text, "thumbnail.svg should contain polygon elements"
