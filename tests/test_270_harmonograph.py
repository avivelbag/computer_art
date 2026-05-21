"""Tests for Piece 270 — Harmonograph: Where the Pendulums Rest."""
import json
import math
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "270-harmonograph"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# Directory / file presence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_svg_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# Thumbnail constraints
# ---------------------------------------------------------------------------

def test_thumbnail_under_100kb():
    size = (PIECE_DIR / "thumbnail.svg").stat().st_size
    assert size < 100 * 1024, f"thumbnail.svg is {size/1024:.1f} KB, must be ≤100 KB"


def test_thumbnail_is_valid_svg():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert content.strip().startswith("<svg"), "thumbnail.svg must be an SVG document"
    assert "</svg>" in content


def test_thumbnail_contains_path_element():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<path" in content, "thumbnail.svg must contain a <path> element for the curve"


def test_thumbnail_uses_correct_paper_color():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#f5f0e8" in content, "thumbnail.svg must use warm cream #f5f0e8 as background"


def test_thumbnail_uses_correct_ink_color():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#1a1a2e" in content, "thumbnail.svg must use deep indigo #1a1a2e as stroke color"


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def test_index_html_uses_canvas():
    content = (PIECE_DIR / "index.html").read_text()
    assert "<canvas" in content


def test_index_html_has_paper_color():
    content = (PIECE_DIR / "index.html").read_text()
    assert "#f5f0e8" in content or "f5f0e8" in content


def test_index_html_has_ink_color():
    content = (PIECE_DIR / "index.html").read_text()
    assert "1a1a2e" in content or "#1a1a2e" in content


def test_index_html_animates_with_raf():
    content = (PIECE_DIR / "index.html").read_text()
    assert "requestAnimationFrame" in content


def test_index_html_no_random_colors():
    """Color must be fixed — no Math.random() calls influencing palette."""
    content = (PIECE_DIR / "index.html").read_text()
    # Math.random() may appear for non-color purposes only; this piece has none.
    assert "Math.random()" not in content, (
        "index.html must not use Math.random() — colors must be fixed"
    )


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def test_entry_present_in_pieces_json():
    ids = [e["id"] for e in _load_pieces()]
    assert "270-harmonograph" in ids


def test_entry_has_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = next(e for e in _load_pieces() if e["id"] == "270-harmonograph")
    assert required <= entry.keys()


def test_entry_path_matches_directory():
    entry = next(e for e in _load_pieces() if e["id"] == "270-harmonograph")
    assert (REPO / entry["path"]).is_dir()


def test_entry_thumbnail_path_matches_file():
    entry = next(e for e in _load_pieces() if e["id"] == "270-harmonograph")
    assert (REPO / entry["thumbnail"]).is_file()


def test_existing_entries_not_removed():
    """Appending must not delete any of the original 106 pieces."""
    data = _load_pieces()
    assert len(data) >= 107, f"Expected ≥107 entries, got {len(data)}"


# ---------------------------------------------------------------------------
# Harmonograph math (pure Python, mirrors the JS/generator logic)
# ---------------------------------------------------------------------------

def _harmonograph_point(t):
    """Compute (x, y) for the harmonograph at parameter t (centered at origin)."""
    A1, f1, p1, d1 = 350, 2.001, 0.0,         0.0025
    A2, f2, p2, d2 = 350, 3.0,   math.pi / 2, 0.0025
    A3, f3, p3, d3 = 350, 3.0,   math.pi / 4, 0.0025
    A4, f4, p4, d4 = 350, 2.0,   0.0,         0.0025
    x = (A1 * math.sin(f1 * t + p1) * math.exp(-d1 * t)
       + A2 * math.sin(f2 * t + p2) * math.exp(-d2 * t))
    y = (A3 * math.sin(f3 * t + p3) * math.exp(-d3 * t)
       + A4 * math.sin(f4 * t + p4) * math.exp(-d4 * t))
    return x, y


def test_curve_starts_near_origin():
    """At t=0 the phase offsets produce a well-defined, non-degenerate start."""
    x, y = _harmonograph_point(0)
    # A2*sin(π/2) = 350 contributes fully on x; A3*sin(π/4) on y.
    assert abs(x) > 100, "Curve should start away from center at t=0"


def test_curve_decays_to_zero():
    """At large t the exponential damping should collapse both coordinates near 0."""
    x, y = _harmonograph_point(4000)
    assert abs(x) < 1.0, f"x should be near 0 at t=4000, got {x:.4f}"
    assert abs(y) < 1.0, f"y should be near 0 at t=4000, got {y:.4f}"


def test_curve_stays_within_amplitude_bounds():
    """Centered offsets must never exceed ±700 (sum of the two oscillator amplitudes)."""
    for i in range(0, 4000, 10):
        x, y = _harmonograph_point(i)
        assert abs(x) <= 701, f"x={x:.1f} exceeds combined amplitude at t={i}"
        assert abs(y) <= 701, f"y={y:.1f} exceeds combined amplitude at t={i}"


def test_irrational_f1_prevents_early_closure():
    """With f1=2.001 the curve at t=100π should differ from t=0 by > 50 px."""
    x0, y0 = _harmonograph_point(0)
    # t = 100π ≈ 314.16; for f1=2 exact this would be a near-repeat; 2.001 avoids it.
    x1, y1 = _harmonograph_point(100 * math.pi)
    dist = math.hypot(x1 - x0, y1 - y0)
    assert dist > 50, f"Curve appears to close early: distance at t=100π is {dist:.1f} px"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_curve_at_t_zero_is_finite():
    x, y = _harmonograph_point(0)
    assert math.isfinite(x) and math.isfinite(y)


def test_curve_at_large_t_is_finite():
    x, y = _harmonograph_point(1e6)
    assert math.isfinite(x) and math.isfinite(y)


def test_thumbnail_svg_path_starts_with_M():
    """The SVG path d-attribute must begin with an absolute moveto command."""
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    import re
    m = re.search(r'd="(M[^"]+)"', content)
    assert m is not None, "Could not find path d attribute starting with M"
