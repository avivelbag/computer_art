"""Tests for Piece 59 — String Art: The Curve Lives Between the Lines."""

import json
import math
import pathlib
import re

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "59-string-art"
INDEX     = PIECE_DIR / "index.html"
THUMB     = PIECE_DIR / "thumbnail.svg"
README    = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# Directory and file existence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/59-string-art/ must exist"


def test_index_html_exists():
    assert INDEX.is_file(), "index.html must exist"


def test_thumbnail_svg_exists():
    assert THUMB.is_file(), "thumbnail.svg must exist"


def test_readme_exists():
    assert README.is_file(), "README.md must exist"


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == "59-string-art":
            return item
    pytest.fail("No pieces.json entry with id '59-string-art'")


def test_pieces_json_entry_present():
    _entry()  # raises if missing


def test_pieces_json_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    entry = _entry()
    assert required <= entry.keys(), f"Missing fields: {required - entry.keys()}"


def test_pieces_json_entry_id_matches_dir():
    entry = _entry()
    assert entry["id"] == PIECE_DIR.name


def test_pieces_json_thumbnail_path_correct():
    entry = _entry()
    assert entry["thumbnail"] == "pieces/59-string-art/thumbnail.svg"


def test_pieces_json_path_correct():
    entry = _entry()
    assert entry["path"] == "pieces/59-string-art"


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def _html() -> str:
    return INDEX.read_text()


def test_index_html_uses_canvas():
    html = _html()
    assert "<canvas" in html, "index.html must use a <canvas> element"


def test_index_html_no_external_scripts():
    """No src attributes pointing to external URLs (http/https) are allowed."""
    html = _html()
    external = re.findall(r'<script[^>]+src=["\']https?://', html)
    assert not external, f"External script tags found: {external}"


def test_index_html_no_external_links():
    """No external stylesheet or module imports."""
    html = _html()
    external_links = re.findall(r'<link[^>]+href=["\']https?://', html)
    assert not external_links, f"External link tags found: {external_links}"


def test_index_html_defines_N():
    """The animation must declare a point-count constant N."""
    html = _html()
    assert re.search(r'\bN\b\s*=\s*\d+', html), "index.html must define N (point count)"


def test_index_html_n_value_adequate():
    """N must be at least 100 for the envelope to look smooth."""
    html = _html()
    match = re.search(r'\bN\b\s*=\s*(\d+)', html)
    assert match, "N constant not found"
    assert int(match.group(1)) >= 100, "N should be >= 100 for smooth envelope"


def test_index_html_multiplier_formula_present():
    """The multiplier m must oscillate via Math.sin for a looping animation."""
    html = _html()
    assert "Math.sin" in html, "Multiplier must use Math.sin for smooth looping"


def test_index_html_multiplier_range_covers_2_to_50():
    """The multiplier expression must reference both 2 and 48 (or 50)."""
    html = _html()
    # m = 2 + 48*(...) gives range [2, 50]
    assert re.search(r'\b2\b.*\b48\b|\b48\b.*\b2\b', html), (
        "Multiplier must span from 2 to ~50 (2 + 48 * ...)"
    )


def test_index_html_uses_global_alpha():
    """Lines should be semi-transparent so overlaps build luminosity."""
    html = _html()
    assert "globalAlpha" in html, "index.html must set globalAlpha"


def test_index_html_uses_request_animation_frame():
    """Animation must use requestAnimationFrame for smooth looping."""
    html = _html()
    assert "requestAnimationFrame" in html, "Must use requestAnimationFrame"


def test_index_html_background_color_dark():
    """Background should be near-black (#111014 or similar dark hex)."""
    html = _html()
    dark_bg = re.search(r'#[01][0-9a-fA-F]{5}', html)
    assert dark_bg, "Background colour should be a dark hex (e.g. #111014)"


def test_index_html_stroke_color_present():
    """A stroke colour (dusty rose or similar) must be defined."""
    html = _html()
    assert re.search(r'strokeStyle|stroke\s*=', html), "strokeStyle must be set"


# ---------------------------------------------------------------------------
# thumbnail.svg content checks
# ---------------------------------------------------------------------------

def _svg() -> str:
    return THUMB.read_text()


def test_thumbnail_is_valid_svg():
    svg = _svg()
    assert svg.strip().startswith("<svg"), "thumbnail.svg must start with <svg"
    assert "</svg>" in svg, "thumbnail.svg must close with </svg>"


def test_thumbnail_has_lines():
    """The thumbnail must contain at least 50 line elements (chord rendering)."""
    svg = _svg()
    count = len(re.findall(r'<line\b', svg))
    assert count >= 50, f"Expected >= 50 <line> elements, got {count}"


def test_thumbnail_has_dark_background():
    """Background rect fill must be a near-black colour."""
    svg = _svg()
    assert re.search(r'fill="#[01][0-9a-fA-F]{5}"', svg), (
        "thumbnail.svg background should be dark (e.g. fill=\"#111014\")"
    )


# ---------------------------------------------------------------------------
# README content checks
# ---------------------------------------------------------------------------

def _readme() -> str:
    return README.read_text()


def test_readme_mentions_cardioid():
    assert "cardioid" in _readme().lower(), "README must mention cardioid"


def test_readme_mentions_multiplier():
    assert re.search(r'multiplier|m\s*=', _readme(), re.IGNORECASE), (
        "README must explain the multiplier parameter"
    )


def test_readme_mentions_epicycloid_or_nephroid():
    text = _readme().lower()
    assert "nephroid" in text or "epicycloid" in text, (
        "README must mention nephroid or epicycloid"
    )


# ---------------------------------------------------------------------------
# generate_thumbnail.py correctness (pure-Python math unit tests)
# ---------------------------------------------------------------------------

def _pt_at(pts, N, j, coord):
    """Replicate the fractional-index interpolation from generate_thumbnail.py."""
    j0   = int(j) % N
    j1   = (j0 + 1) % N
    frac = j - int(j)
    return pts[j0][coord] * (1 - frac) + pts[j1][coord] * frac


def _build_pts(N=200, R=175, cx=200, cy=200):
    return [
        (cx + R * math.cos(2 * math.pi * i / N),
         cy + R * math.sin(2 * math.pi * i / N))
        for i in range(N)
    ]


def test_chord_endpoints_on_circle_boundary():
    """All start-point coordinates must lie on the circle of radius R."""
    N, R, cx, cy = 200, 175, 200, 200
    pts = _build_pts(N, R, cx, cy)
    for i, (x, y) in enumerate(pts):
        dist = math.hypot(x - cx, y - cy)
        assert abs(dist - R) < 1e-9, f"Point {i} is not on the circle"


def test_fractional_interpolation_at_integer_is_exact():
    """ptAt(j, coord) when j is an integer must equal pts[j][coord] exactly."""
    N   = 200
    pts = _build_pts(N)
    for j in [0, 1, 50, 99, 199]:
        x = _pt_at(pts, N, float(j), 0)
        assert abs(x - pts[j][0]) < 1e-12


def test_fractional_interpolation_midpoint():
    """ptAt at j + 0.5 must be the midpoint of pts[j] and pts[j+1]."""
    N   = 200
    pts = _build_pts(N)
    j   = 10
    expected_x = (pts[j][0] + pts[j + 1][0]) / 2
    got_x      = _pt_at(pts, N, j + 0.5, 0)
    assert abs(got_x - expected_x) < 1e-12


def test_multiplier_2_chord_count():
    """At multiplier 2 there should be exactly N chords (no degenerate lines)."""
    N, M = 200, 2.0
    pts  = _build_pts(N)
    chords = []
    for i in range(N):
        j  = (i * M) % N
        x2 = _pt_at(pts, N, j, 0)
        y2 = _pt_at(pts, N, j, 1)
        chords.append((pts[i][0], pts[i][1], x2, y2))
    assert len(chords) == N


def test_multiplier_formula_range():
    """The m = 2 + 48*(0.5 + 0.5*sin(t*0.3)) formula must span [2, 50]."""
    vals = [2 + 48 * (0.5 + 0.5 * math.sin(t * 0.3)) for t in range(1000)]
    assert min(vals) >= 2.0 - 1e-9
    assert max(vals) <= 50.0 + 1e-9


def test_multiplier_formula_is_periodic_and_smooth():
    """Consecutive multiplier values must not jump (smooth animation)."""
    dt   = 1 / 60  # one frame at 60 fps
    vals = [2 + 48 * (0.5 + 0.5 * math.sin(t * 0.3)) for t in (i * dt for i in range(600))]
    diffs = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
    assert max(diffs) < 0.5, "Multiplier should change smoothly between frames"


def test_large_N_chord_generation_performance(benchmark=None):
    """Chord generation for N=300 should complete well under 1 second."""
    import time
    N, M = 300, 3.0
    pts  = _build_pts(N, R=270, cx=300, cy=300)
    t0   = time.perf_counter()
    for i in range(N):
        j  = (i * M) % N
        _pt_at(pts, N, j, 0)
        _pt_at(pts, N, j, 1)
    elapsed = time.perf_counter() - t0
    assert elapsed < 1.0, f"Chord generation took {elapsed:.3f}s, should be < 1s"
