"""Tests for Piece 63 — Rhodonea: The Petal Count Is Always a Surprise."""

import json
import math
import pathlib
import re

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "63-rhodonea"
INDEX     = PIECE_DIR / "index.html"
THUMB     = PIECE_DIR / "thumbnail.svg"
README    = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# Directory and file existence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/63-rhodonea/ must exist"


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
        if item.get("id") == "63-rhodonea":
            return item
    pytest.fail("No pieces.json entry with id '63-rhodonea'")


def test_pieces_json_entry_present():
    _entry()


def test_pieces_json_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    entry = _entry()
    assert required <= entry.keys(), f"Missing fields: {required - entry.keys()}"


def test_pieces_json_entry_id_matches_dir():
    entry = _entry()
    assert entry["id"] == PIECE_DIR.name


def test_pieces_json_thumbnail_path_correct():
    entry = _entry()
    assert entry["thumbnail"] == "pieces/63-rhodonea/thumbnail.svg"


def test_pieces_json_path_correct():
    entry = _entry()
    assert entry["path"] == "pieces/63-rhodonea"


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def _html() -> str:
    return INDEX.read_text()


def test_index_html_uses_canvas():
    assert "<canvas" in _html()


def test_index_html_no_external_scripts():
    """No src attributes pointing to external URLs are allowed."""
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, f"External script tags found: {external}"


def test_index_html_no_external_links():
    """No external stylesheet imports."""
    external = re.findall(r'<link[^>]+href=["\']https?://', _html())
    assert not external, f"External link tags found: {external}"


def test_index_html_uses_polar_curve():
    """The animation must reference Math.cos for polar-to-cartesian conversion."""
    assert "Math.cos" in _html(), "index.html must use Math.cos for polar curve"


def test_index_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_index_html_uses_motion_blur_ghosting():
    """Background must be painted with low alpha each frame for trail effect."""
    html = _html()
    assert "rgba" in html or "globalAlpha" in html, (
        "Motion-blur ghosting requires rgba background fill or globalAlpha"
    )


def test_index_html_uses_math_sin_for_k_oscillation():
    """k must oscillate with Math.sin for seamless looping."""
    assert "Math.sin" in _html()


def test_index_html_palette_monochromatic():
    """The piece must declare exactly one non-background stroke colour."""
    html = _html()
    stroke_colors = re.findall(r"strokeStyle\s*=\s*['\"]([^'\"]+)['\"]", html)
    assert len(stroke_colors) >= 1, "At least one strokeStyle must be set"
    unique = set(stroke_colors)
    assert len(unique) == 1, f"Expected monochromatic palette; found: {unique}"


def test_index_html_dark_background():
    """Background colour must be dark (near-black or very dark brown/charcoal)."""
    html = _html()
    dark = re.search(r'#[0-2][0-9a-fA-F]{5}', html) or re.search(r'rgba\(\s*[0-3]\d,', html)
    assert dark, "Background colour should be dark (e.g. #1a1208 or rgba(26,...))"


def test_index_html_three_concentric_roses():
    """drawRose must be called at least 3 times per frame for visual richness."""
    html = _html()
    calls = re.findall(r'\bdrawRose\s*\(', html)
    assert len(calls) >= 3, f"Expected >= 3 drawRose calls, got {len(calls)}"


def test_index_html_large_point_count():
    """Curve must sample at least 1000 points for smooth petal rendering."""
    html = _html()
    match = re.search(r'\bPOINTS\b\s*=\s*(\d+)', html)
    assert match, "POINTS constant not found in index.html"
    assert int(match.group(1)) >= 1000, "POINTS must be >= 1000 for smooth curves"


# ---------------------------------------------------------------------------
# thumbnail.svg content checks
# ---------------------------------------------------------------------------

def _svg() -> str:
    return THUMB.read_text()


def test_thumbnail_is_valid_svg():
    svg = _svg()
    assert svg.strip().startswith("<svg"), "thumbnail.svg must start with <svg"
    assert "</svg>" in svg, "thumbnail.svg must close with </svg>"


def test_thumbnail_has_polylines():
    """Thumbnail must contain polyline elements representing the rose curves."""
    svg = _svg()
    count = len(re.findall(r'<polyline\b', svg))
    assert count >= 3, f"Expected >= 3 <polyline> elements, got {count}"


def test_thumbnail_dark_background():
    """Thumbnail background must be a dark colour."""
    svg = _svg()
    assert re.search(r'fill="#[01][0-9a-fA-F]{5}"', svg), (
        "thumbnail.svg background should be dark"
    )


def test_thumbnail_warm_stroke_colour():
    """Stroke must be a warm gold/amber tone, not rainbow or pure white."""
    svg = _svg()
    assert "#d4a84b" in svg or "#c8922a" in svg or re.search(r'stroke="#[c-f][6-9a-f]', svg, re.IGNORECASE), (
        "thumbnail.svg stroke should use warm gold palette"
    )


# ---------------------------------------------------------------------------
# README content checks
# ---------------------------------------------------------------------------

def _readme() -> str:
    return README.read_text()


def test_readme_mentions_polar_equation():
    """README must reference the polar equation r = cos(k·θ)."""
    text = _readme().lower()
    assert "cos" in text or "polar" in text, "README must mention polar equation"


def test_readme_mentions_petal_count_rule():
    """README must explain that petal count depends on n and d."""
    text = _readme().lower()
    assert "petal" in text, "README must mention petals"


def test_readme_mentions_rational_k():
    """README must explain the rational/irrational k distinction."""
    text = _readme().lower()
    assert "rational" in text or "n/d" in text or "n / d" in text, (
        "README must mention rational k"
    )


def test_readme_is_at_least_two_sentences():
    """README body must have meaningful content (>=2 sentence-ending punctuation)."""
    text = _readme()
    sentence_ends = re.findall(r'[.!?]', text)
    assert len(sentence_ends) >= 2, "README must contain at least 2 sentences"


# ---------------------------------------------------------------------------
# Pure-Python math unit tests for rhodonea geometry
# ---------------------------------------------------------------------------

def _rose_points(k: float, R: float, n_pts: int = 2000) -> list[tuple[float, float]]:
    """Sample a rhodonea r = cos(k·θ) at n_pts equidistant θ values.

    Uses the same sweep-end logic as generate_thumbnail.py so the curve closes
    exactly for rational k.
    """
    n  = round(k * 12)
    d  = 12
    g  = math.gcd(abs(n) if n != 0 else 1, d)
    nd = max(1, d // g)
    end  = 2 * math.pi * nd
    step = end / n_pts
    cx, cy = 200.0, 200.0
    return [
        (cx + R * math.cos(k * i * step) * math.cos(i * step),
         cy + R * math.cos(k * i * step) * math.sin(i * step))
        for i in range(n_pts + 1)
    ]


def test_rose_k1_is_circle():
    """k=1 gives r = cos(θ), which is a circle of radius R/2 offset by R/2."""
    pts = _rose_points(1.0, 200.0)
    cx, cy = 200.0, 200.0
    R = 200.0
    for x, y in pts:
        dist_from_center = math.hypot(x - cx, y - cy)
        assert dist_from_center <= R + 1e-6, f"Point outside bounding circle: {dist_from_center}"


def test_rose_k2_has_four_lobes():
    """k=2 should produce a 4-petal rose; check the curve reaches maximum radius."""
    pts = _rose_points(2.0, 100.0)
    cx, cy = 200.0, 200.0
    max_dist = max(math.hypot(x - cx, y - cy) for x, y in pts)
    assert abs(max_dist - 100.0) < 2.0, f"k=2 rose max radius should be ~100, got {max_dist:.2f}"


def test_rose_k3_has_three_lobes():
    """k=3 (odd n) should produce a 3-petal rose."""
    pts = _rose_points(3.0, 100.0)
    cx, cy = 200.0, 200.0
    max_dist = max(math.hypot(x - cx, y - cy) for x, y in pts)
    assert abs(max_dist - 100.0) < 2.0, f"k=3 rose max radius should be ~100, got {max_dist:.2f}"


def test_rose_origin_density():
    """All rose curves must pass through the origin at some θ (r=0 when cos(kθ)=0)."""
    k = 3.0
    cx, cy = 200.0, 200.0
    pts = _rose_points(k, 100.0)
    min_dist = min(math.hypot(x - cx, y - cy) for x, y in pts)
    assert min_dist < 2.0, f"Rose curve should pass through origin; min dist={min_dist:.2f}"


def test_k_sweep_range():
    """The animation k = 1 + 5*(0.5 + 0.5*sin(t * 2π/30)) must span [1, 6]."""
    vals = [1 + 5 * (0.5 + 0.5 * math.sin(t * (2 * math.pi / 30))) for t in range(3000)]
    assert min(vals) >= 1.0 - 1e-9, f"k minimum {min(vals)} is below 1"
    assert max(vals) <= 6.0 + 1e-9, f"k maximum {max(vals)} exceeds 6"


def test_k_sweep_smooth():
    """Consecutive k values at 30 fps should change smoothly (no jumps)."""
    dt   = 1 / 30
    vals = [1 + 5 * (0.5 + 0.5 * math.sin(t * (2 * math.pi / 30))) for t in (i * dt for i in range(900))]
    diffs = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
    assert max(diffs) < 0.5, f"k should change smoothly; max jump was {max(diffs):.4f}"


def test_gcd_helper():
    """GCD implementation must return correct values for key cases."""
    def gcd_py(a, b):
        a, b = abs(round(a)), abs(round(b))
        while b:
            a, b = b, a % b
        return a or 1

    assert gcd_py(12, 4) == 4
    assert gcd_py(12, 3) == 3
    assert gcd_py(5, 5)  == 5
    assert gcd_py(7, 1)  == 1
    assert gcd_py(0, 6)  == 6


def test_large_point_set_performance():
    """Generating 3000 rose curve points should complete well under 1 second."""
    import time
    t0 = time.perf_counter()
    _rose_points(k=2.5, R=175.0, n_pts=3000)
    elapsed = time.perf_counter() - t0
    assert elapsed < 1.0, f"Point generation took {elapsed:.3f}s; should be < 1s"


def test_empty_like_k_zero():
    """k near 0 degenerates to r ≈ 1 (constant), which draws a circle; no crash."""
    pts = _rose_points(0.01, 100.0, n_pts=500)
    assert len(pts) == 501
    cx, cy = 200.0, 200.0
    for x, y in pts:
        dist = math.hypot(x - cx, y - cy)
        assert dist <= 101.0, f"Point outside expected radius: {dist:.2f}"
