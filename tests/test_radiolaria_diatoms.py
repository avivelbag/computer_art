"""Tests for piece 176 — Radiolaria & Diatom Morphology."""

import json
import math
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "176-radiolaria-diatoms"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# File presence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_svg_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_generate_thumbnail_script_exists():
    assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

def _load_entry():
    """Return the pieces.json entry for piece 176, or None if absent."""
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == "176-radiolaria-diatoms"), None)


def test_pieces_json_has_entry():
    assert _load_entry() is not None


def test_pieces_json_entry_required_fields():
    entry = _load_entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= entry.keys()


def test_pieces_json_id_matches_dir():
    entry = _load_entry()
    assert entry["id"] == "176-radiolaria-diatoms"
    assert entry["path"] == "pieces/176-radiolaria-diatoms"


def test_pieces_json_thumbnail_file_exists():
    entry = _load_entry()
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file()


# ---------------------------------------------------------------------------
# thumbnail.svg content
# ---------------------------------------------------------------------------

def test_thumbnail_has_dark_background():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#070d1a" in content


def test_thumbnail_has_polar_paths():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<path" in content


def test_thumbnail_has_accent_color():
    """Nucleus/center elements must appear in teal."""
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#4dd9c0" in content


def test_thumbnail_has_spines():
    """Spine lines (radial line elements) must be present."""
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<line" in content


def test_thumbnail_has_concentric_rings():
    """Concentric rings rendered as SVG circles must be present."""
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<circle" in content


# ---------------------------------------------------------------------------
# index.html content
# ---------------------------------------------------------------------------

def test_index_html_has_polar_function():
    content = (PIECE_DIR / "index.html").read_text()
    assert "polarPts" in content


def test_index_html_has_smil_animation():
    content = (PIECE_DIR / "index.html").read_text()
    assert "animateTransform" in content


def test_index_html_rotation_period_at_least_20s():
    """Every organism's rotation period must be >= 20 s."""
    content = (PIECE_DIR / "index.html").read_text()
    durs = [int(x) for x in re.findall(r"dur:(\d+)", content)]
    assert durs, "No dur: values found in ORGS array"
    assert all(d >= 20 for d in durs), f"Rotation faster than 1 rev/20 s: {durs}"


def test_index_html_organism_count_in_range():
    """Composition must contain 5–9 distinct organisms.

    Count entries in the ORGS array by matching 'cx:<integer>' (only ORGS entries
    use literal integers; the el() helper uses cx:cx.toFixed(...) which is not an
    integer literal and so won't be matched).
    """
    content = (PIECE_DIR / "index.html").read_text()
    orgs = re.findall(r"cx:\d+", content)
    assert 5 <= len(orgs) <= 9, f"Expected 5–9 organisms, found {len(orgs)}"


def test_index_html_n_values_in_allowed_set():
    """All primary-lobing n values must come from {3,4,6,8,12,16,24}.

    Match 'n:<digit>,m:' which is unique to ORGS entries and avoids false
    positives such as 'margin:0' in the CSS block.
    """
    content = (PIECE_DIR / "index.html").read_text()
    allowed = {3, 4, 6, 8, 12, 16, 24}
    ns = [int(x) for x in re.findall(r"n:(\d+),m:", content)]
    assert ns, "No 'n:<n>,m:' patterns found in ORGS"
    assert all(v in allowed for v in ns), f"n values outside allowed set: {ns}"


def test_index_html_has_dark_background():
    content = (PIECE_DIR / "index.html").read_text()
    assert "#070d1a" in content


def test_index_html_has_accent_color():
    content = (PIECE_DIR / "index.html").read_text()
    assert "#4dd9c0" in content or "ACCENT" in content


def test_index_html_has_spines():
    content = (PIECE_DIR / "index.html").read_text()
    assert "spines" in content


def test_index_html_has_lattice():
    content = (PIECE_DIR / "index.html").read_text()
    assert "lattice" in content


# ---------------------------------------------------------------------------
# Polar math correctness (pure Python, mirrors the JS logic)
# ---------------------------------------------------------------------------

def polar_r(R: float, n: int, m: int, a: float, b: float, c: float,
            theta: float) -> float:
    """Compute r(θ) = R*(a + b*sin(n*θ) + c*sin(m*θ)) for a single angle."""
    return R * (a + b * math.sin(n * theta) + c * math.sin(m * theta))


def test_polar_r_at_zero():
    """At θ=0, sin terms vanish so r = R*a exactly."""
    R, n, m, a, b, c = 100.0, 12, 6, 0.55, 0.30, 0.15
    assert abs(polar_r(R, n, m, a, b, c, 0.0) - R * a) < 1e-12


def test_polar_r_positive_for_default_params():
    """All 7 organism parameter sets must produce r > 0 everywhere."""
    params = [
        (90,  12, 6,  0.55, 0.30, 0.15),
        (72,  16, 8,  0.60, 0.28, 0.12),
        (75,  6,  3,  0.65, 0.25, 0.10),
        (82,  8,  4,  0.58, 0.32, 0.10),
        (65,  24, 12, 0.62, 0.28, 0.10),
        (52,  3,  6,  0.60, 0.30, 0.10),
        (52,  4,  8,  0.58, 0.30, 0.12),
    ]
    for R, n, m, a, b, c in params:
        for i in range(1000):
            th = (i / 1000) * 2 * math.pi
            assert polar_r(R, n, m, a, b, c, th) > 0, \
                f"Negative r at θ={th:.3f} for n={n},m={m}"


def test_polar_r_max_bounded_by_sum():
    """Max r cannot exceed R*(a+b+c) since |sin| ≤ 1."""
    R, n, m, a, b, c = 100.0, 8, 4, 0.58, 0.32, 0.10
    upper = R * (a + b + c)
    for i in range(10000):
        th = (i / 10000) * 2 * math.pi
        assert polar_r(R, n, m, a, b, c, th) <= upper + 1e-12


def test_polar_r_n_fold_symmetry_single_term():
    """r(θ + 2π/n) = r(θ) when c=0, verifying pure n-fold symmetry."""
    R, n, m, a, b, c = 100.0, 12, 6, 0.60, 0.40, 0.0
    step = 2 * math.pi / n
    for i in range(n * 5):
        th = i * math.pi / (n * 3)
        assert abs(polar_r(R, n, m, a, b, c, th) -
                   polar_r(R, n, m, a, b, c, th + step)) < 1e-9


def test_polar_r_combined_period_with_shared_divisor():
    """When m divides n, the combined period is 2π/n (n-fold symmetry survives).

    For n=8, m=4: sin(8*(θ + 2π/8)) = sin(8θ + 2π) = sin(8θ), and
    sin(4*(θ + 2π/8)) = sin(4θ + π) ≠ sin(4θ).  So the LCM period is 2π/4.
    """
    R, n, m, a, b, c = 100.0, 8, 4, 0.58, 0.32, 0.10
    # 4-fold period: 2π/4
    step = 2 * math.pi / 4
    for i in range(20):
        th = i * math.pi / 17
        assert abs(polar_r(R, n, m, a, b, c, th) -
                   polar_r(R, n, m, a, b, c, th + step)) < 1e-9


def test_polar_r_min_nonnegative():
    """Min r should be >= R*(a-b-c); for all our params this is > 0."""
    R, n, m, a, b, c = 100.0, 6, 3, 0.65, 0.25, 0.10
    lower = R * (a - b - c)
    assert lower >= 0.0, "Sanity check: parameters allow negative r"
    for i in range(10000):
        th = (i / 10000) * 2 * math.pi
        assert polar_r(R, n, m, a, b, c, th) >= lower - 1e-12


# ---------------------------------------------------------------------------
# Edge / failure cases
# ---------------------------------------------------------------------------

def test_polar_r_n24_large_symmetry():
    """24-fold primary lobing with m=12 secondary: period is 2π/12 (12-fold)."""
    R, n, m, a, b, c = 100.0, 24, 12, 0.62, 0.28, 0.10
    # 12-fold period: 2π/12
    step = 2 * math.pi / 12
    for i in range(24):
        th = i * math.pi / 19
        assert abs(polar_r(R, n, m, a, b, c, th) -
                   polar_r(R, n, m, a, b, c, th + step)) < 1e-9


def test_polar_r_zero_amplitude():
    """When b=c=0, the curve degenerates to a circle of radius R*a."""
    R, n, m, a, b, c = 100.0, 12, 6, 0.7, 0.0, 0.0
    expected = R * a
    for i in range(100):
        th = (i / 100) * 2 * math.pi
        assert abs(polar_r(R, n, m, a, b, c, th) - expected) < 1e-12


def test_polar_r_2pi_periodicity():
    """r(0) == r(2π) confirming the curve closes exactly after one revolution.

    The SVG path is closed with the Z command rather than repeating the start
    point, but mathematical periodicity guarantees visual closure.
    """
    R, n, m, a, b, c = 100.0, 12, 6, 0.55, 0.30, 0.15
    assert abs(polar_r(R, n, m, a, b, c, 0.0) -
               polar_r(R, n, m, a, b, c, 2 * math.pi)) < 1e-12
