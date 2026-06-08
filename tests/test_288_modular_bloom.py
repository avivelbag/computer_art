"""Tests for piece 288 — Modular Bloom (times-table cardioid chord diagram)."""

import importlib.util
import math
import pathlib
import sys

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "288-modular-bloom"
INDEX     = PIECE_DIR / "index.html"
THUMB     = PIECE_DIR / "thumbnail.svg"
README    = PIECE_DIR / "README.md"
GEN_PY    = PIECE_DIR / "gen_thumbnail.py"


# ---------------------------------------------------------------------------
# File-system presence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX.is_file()


def test_thumbnail_svg_exists():
    assert THUMB.is_file()


def test_readme_exists():
    assert README.is_file()


def test_gen_thumbnail_exists():
    assert GEN_PY.is_file()


# ---------------------------------------------------------------------------
# index.html content
# ---------------------------------------------------------------------------

def test_n_200_in_script():
    """The JS must declare N = 200 to satisfy the acceptance criterion."""
    content = INDEX.read_text()
    assert "N     = 200" in content or "N = 200" in content or "const N=200" in content


def test_background_color_0a0a0f():
    """Background must be near-black #0a0a0f as specified."""
    content = INDEX.read_text()
    assert "#0a0a0f" in content


def test_opacity_15_percent():
    """Chords must be drawn at ~15% opacity."""
    content = INDEX.read_text()
    assert "0.15" in content


def test_no_external_dependencies():
    """index.html must be fully self-contained — no external URLs."""
    content = INDEX.read_text()
    assert "https://" not in content
    assert "http://" not in content


def test_requestanimationframe_present():
    content = INDEX.read_text()
    assert "requestAnimationFrame" in content


def test_canvas_element_present():
    content = INDEX.read_text()
    assert "<canvas" in content


def test_hsl_color_present():
    """Hue-based coloring via hsla() must be present."""
    content = INDEX.read_text()
    assert "hsla(" in content or "hsl(" in content


def test_js_line_count_under_80():
    """The <script> block must contain fewer than 80 lines of JavaScript."""
    content = INDEX.read_text()
    start = content.index("<script>") + len("<script>")
    end   = content.index("</script>")
    script = content[start:end]
    non_empty = [l for l in script.splitlines() if l.strip()]
    assert len(non_empty) < 80, f"Script has {len(non_empty)} non-empty lines"


# ---------------------------------------------------------------------------
# thumbnail.svg content
# ---------------------------------------------------------------------------

def test_thumbnail_is_valid_svg():
    content = THUMB.read_text()
    assert "<svg" in content
    assert "</svg>" in content


def test_thumbnail_background():
    """Thumbnail must use the same near-black background colour."""
    content = THUMB.read_text()
    assert "#0a0a0f" in content


def test_thumbnail_has_200_chords():
    """K=2 cardioid needs exactly 200 chord lines."""
    content = THUMB.read_text()
    assert content.count("<line") == 200


def test_thumbnail_has_lines():
    content = THUMB.read_text()
    assert "<line" in content


# ---------------------------------------------------------------------------
# Geometry correctness — pure Python, no canvas required
# ---------------------------------------------------------------------------

def _circle_pts(n: int, r: float = 1.0) -> list[tuple[float, float]]:
    """Return n equally-spaced points on a circle of radius r."""
    return [
        (r * math.cos(2 * math.pi * i / n),
         r * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]


def _chords(n: int, k: float) -> list[tuple[int, int]]:
    """Return (src, dst) index pairs for the chord diagram with multiplier k."""
    return [(i, round(i * k) % n) for i in range(n)]


def test_chord_count_equals_n():
    chords = _chords(200, 2)
    assert len(chords) == 200


def test_k2_point_0_maps_to_0():
    """0 × 2 mod 200 = 0 — the first point is a self-loop for K=2."""
    chords = _chords(200, 2)
    assert chords[0] == (0, 0)


def test_k2_point_100_maps_to_0():
    """100 × 2 mod 200 = 0 — the antipodal point also folds back to 0."""
    chords = _chords(200, 2)
    assert chords[100] == (100, 0)


def test_k2_symmetric_pairs():
    """For K=2, points i and i+100 both map to the same target (mod 200).

    This symmetry is the hallmark of the cardioid envelope.
    """
    chords = _chords(200, 2)
    for i in range(100):
        assert chords[i][1] == chords[i + 100][1]


def test_all_targets_in_range():
    """All destination indices must lie within [0, N-1]."""
    n = 200
    for k in [2, 3, 7, 13, 49, 50]:
        for i, j in _chords(n, k):
            assert 0 <= j < n, f"k={k}, i={i} → j={j} out of range"


def test_circle_points_lie_on_unit_circle():
    """Every point in the precomputed array must have radius exactly 1."""
    pts = _circle_pts(200)
    for x, y in pts:
        assert abs(math.hypot(x, y) - 1.0) < 1e-12


# ---------------------------------------------------------------------------
# gen_thumbnail module
# ---------------------------------------------------------------------------

def _load_gen():
    """Dynamically import gen_thumbnail.py from the piece directory."""
    spec   = importlib.util.spec_from_file_location("gen_thumbnail", GEN_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gen_compute_pts_returns_n_points():
    gen = _load_gen()
    pts = gen.compute_pts(200, 200.0, 200.0, 170.0)
    assert len(pts) == 200


def test_gen_compute_pts_on_circle():
    gen = _load_gen()
    pts = gen.compute_pts(200, 0.0, 0.0, 1.0)
    for x, y in pts:
        assert abs(math.hypot(x, y) - 1.0) < 1e-10


def test_gen_svg_contains_200_lines():
    gen = _load_gen()
    pts = gen.compute_pts(200, 200.0, 200.0, 170.0)
    svg = gen.gen_svg(pts, 2, 400, 400, "#0a0a0f")
    assert svg.count("<line") == 200


def test_gen_svg_is_valid_structure():
    gen = _load_gen()
    pts = gen.compute_pts(10, 200.0, 200.0, 100.0)
    svg = gen.gen_svg(pts, 2, 400, 400, "#000000")
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_k_range_always_gte_2():
    """K = 2 + (t * SPEED) % 48 must never fall below 2 regardless of t."""
    speed = 3
    for t_ms in range(0, 1_000_001, 1000):
        t = t_ms / 1000.0
        k = 2 + (t * speed) % 48
        assert k >= 2.0


def test_k_range_always_lt_50():
    """K = 2 + (t * SPEED) % 48 must always stay below 50."""
    speed = 3
    for t_ms in range(0, 1_000_001, 137):
        t = t_ms / 1000.0
        k = 2 + (t * speed) % 48
        assert k < 50.0


def test_large_n_stays_in_bounds():
    """Chord destinations remain valid for a larger N."""
    n = 1000
    for k in [2, 10, 49]:
        for i, j in _chords(n, k):
            assert 0 <= j < n


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------

def test_modulo_zero_raises():
    """Computing chord indices with N=0 must raise ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        _ = round(5 * 2) % 0


def test_missing_canvas_id_would_break():
    """The JS must reference canvas id 'c' to match the HTML element."""
    content = INDEX.read_text()
    assert "'c'" in content or '"c"' in content


def test_k2_nephroid_k3_distinct():
    """K=2 and K=3 chord sets must differ — cardioid vs nephroid are distinct."""
    chords2 = set(_chords(200, 2))
    chords3 = set(_chords(200, 3))
    assert chords2 != chords3
