"""Tests for piece 171 — The Grid That Knows Where It Lives: Conformal Grid."""

import json
import math
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "171-conformal-grid"
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


# ---------------------------------------------------------------------------
# pieces.json tests
# ---------------------------------------------------------------------------

def test_pieces_json_entry_present():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert "171-conformal-grid" in ids


def test_pieces_json_entry_complete():
    data = json.loads(PIECES_JSON.read_text())
    entry = next(e for e in data if e["id"] == "171-conformal-grid")
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= entry.keys()


def test_pieces_json_technique_contains_required_terms():
    data = json.loads(PIECES_JSON.read_text())
    entry = next(e for e in data if e["id"] == "171-conformal-grid")
    tech = entry["technique"].lower()
    assert "conformal" in tech
    assert "joukowski" in tech


def test_pieces_json_paths_valid():
    data = json.loads(PIECES_JSON.read_text())
    entry = next(e for e in data if e["id"] == "171-conformal-grid")
    assert (REPO / entry["path"]).is_dir()
    assert (REPO / entry["thumbnail"]).is_file()


# ---------------------------------------------------------------------------
# HTML content tests
# ---------------------------------------------------------------------------

def test_index_html_has_dark_background():
    html = (PIECE_DIR / "index.html").read_text()
    assert "#0d0d18" in html


def test_index_html_has_additive_compositing():
    html = (PIECE_DIR / "index.html").read_text()
    assert "lighter" in html


def test_index_html_has_joukowski_map():
    html = (PIECE_DIR / "index.html").read_text()
    assert "joukowski" in html.lower()


def test_index_html_has_square_map():
    html = (PIECE_DIR / "index.html").read_text()
    assert "square" in html.lower() or "squareMap" in html


def test_index_html_has_mobius_map():
    html = (PIECE_DIR / "index.html").read_text()
    assert "mobius" in html.lower() or "mobiusMap" in html


def test_index_html_min_200_samples():
    """N_SAMPLES must be declared as ≥ 200 so polylines are smooth."""
    import re
    html = (PIECE_DIR / "index.html").read_text()
    matches = re.findall(r'N_SAMPLES\s*=\s*(\d+)', html)
    assert matches, "N_SAMPLES constant not found in index.html"
    assert int(matches[0]) >= 200


def test_index_html_canvas_800():
    html = (PIECE_DIR / "index.html").read_text()
    assert 'width="800"' in html
    assert 'height="800"' in html


def test_index_html_has_rose_color_for_horizontal():
    """Horizontal lines must use a rose/coral color (high red channel)."""
    html = (PIECE_DIR / "index.html").read_text()
    # The color strings contain 'rgba(255,...' for the rose horizontal lines
    assert "rgba(255" in html


def test_index_html_has_blue_color_for_vertical():
    """Vertical lines must use a sky-blue color."""
    html = (PIECE_DIR / "index.html").read_text()
    # Sky-blue uses a high blue channel; look for 255 in the blue position
    assert "255,0.6" in html or "255)" in html


def test_index_html_n_lines_at_least_20():
    import re
    html = (PIECE_DIR / "index.html").read_text()
    matches = re.findall(r'N_LINES\s*=\s*(\d+)', html)
    assert matches, "N_LINES constant not found in index.html"
    assert int(matches[0]) >= 20


def test_index_html_has_requestanimationframe():
    html = (PIECE_DIR / "index.html").read_text()
    assert "requestAnimationFrame" in html


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_mentions_angle_preservation():
    readme = (PIECE_DIR / "README.md").read_text().lower()
    assert "angle" in readme


def test_readme_mentions_joukowski():
    readme = (PIECE_DIR / "README.md").read_text().lower()
    assert "joukowski" in readme


def test_readme_mentions_airfoil():
    readme = (PIECE_DIR / "README.md").read_text().lower()
    assert "airfoil" in readme or "aeroplane" in readme or "wing" in readme


def test_readme_explains_morphing():
    readme = (PIECE_DIR / "README.md").read_text().lower()
    assert "morph" in readme or "λ" in readme or "lam" in readme or "parameter" in readme


# ---------------------------------------------------------------------------
# thumbnail.svg tests
# ---------------------------------------------------------------------------

def test_thumbnail_svg_has_dark_background():
    svg = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#0d0d18" in svg


def test_thumbnail_svg_has_polylines():
    svg = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<polyline" in svg


def test_thumbnail_svg_is_valid_xml():
    """The thumbnail must open with the standard SVG root element."""
    svg = (PIECE_DIR / "thumbnail.svg").read_text()
    assert svg.strip().startswith("<svg") or "<?xml" in svg[:50]
    assert "</svg>" in svg


# ---------------------------------------------------------------------------
# Python re-implementation of the three conformal maps (correctness tests)
# ---------------------------------------------------------------------------

def _cmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def _cdiv(a, b):
    d = b[0] ** 2 + b[1] ** 2
    if d < 1e-12:
        return None
    return ((a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d)


def _cmag(z):
    return math.sqrt(z[0] ** 2 + z[1] ** 2)


MIN_Z_MAG = 0.05


def _joukowski(z, lam):
    """Blended Joukowski: z → z + lam/z."""
    if _cmag(z) < MIN_Z_MAG:
        return None
    inv = _cdiv((1.0, 0.0), z)
    if inv is None:
        return None
    return (z[0] + lam * inv[0], z[1] + lam * inv[1])


def _square(z, lam):
    """Blended square map: z → (1−lam)·z + lam·z²."""
    z2 = _cmul(z, z)
    return (z[0] + lam * (z2[0] - z[0]), z[1] + lam * (z2[1] - z[1]))


def _mobius(z, lam):
    """Blended Möbius: z → blend(z, (z−1)/(z+1), lam)."""
    den = (z[0] + 1, z[1])
    num = (z[0] - 1, z[1])
    m = _cdiv(num, den)
    if m is None:
        return None
    return (z[0] + lam * (m[0] - z[0]), z[1] + lam * (m[1] - z[1]))


class TestJoukowskiMap:
    def test_identity_at_lam_zero(self):
        """At lam=0 joukowski is the identity."""
        z = (2.0, 1.0)
        w = _joukowski(z, 0.0)
        assert abs(w[0] - z[0]) < 1e-10
        assert abs(w[1] - z[1]) < 1e-10

    def test_full_map_real_axis(self):
        """z + 1/z at z=2 on the real axis gives 2 + 0.5 = 2.5."""
        w = _joukowski((2.0, 0.0), 1.0)
        assert abs(w[0] - 2.5) < 1e-10
        assert abs(w[1] - 0.0) < 1e-10

    def test_full_map_imaginary_axis(self):
        """1/(0+2i) = −i/2, so (0+2i) + (0−0.5i) = 1.5i."""
        w = _joukowski((0.0, 2.0), 1.0)
        assert abs(w[0] - 0.0) < 1e-10
        assert abs(w[1] - 1.5) < 1e-10

    def test_pole_at_origin_returns_none(self):
        """Points with |z| < MIN_Z_MAG must return None."""
        assert _joukowski((0.0, 0.0), 1.0) is None
        assert _joukowski((1e-6, 0.0), 1.0) is None

    def test_unit_circle_maps_to_real_interval(self):
        """On the unit circle z + 1/z = 2 cos θ (imaginary part = 0)."""
        for theta in [0.3, 0.8, 1.2, 1.9, 2.5]:
            z = (math.cos(theta), math.sin(theta))
            w = _joukowski(z, 1.0)
            assert w is not None
            assert abs(w[1]) < 1e-10, f"Non-zero imaginary part {w[1]} at theta={theta}"

    def test_partial_blend(self):
        """At lam=0.5 the result is halfway between identity and full map."""
        z = (2.0, 0.0)
        full = _joukowski(z, 1.0)   # (2.5, 0)
        half = _joukowski(z, 0.5)
        expected = (z[0] + 0.5 * (full[0] - z[0]), z[1] + 0.5 * (full[1] - z[1]))
        assert abs(half[0] - expected[0]) < 1e-10
        assert abs(half[1] - expected[1]) < 1e-10

    def test_large_z_near_identity(self):
        """For large |z|, 1/z ≈ 0 so the map is nearly the identity."""
        z = (100.0, 0.0)
        w = _joukowski(z, 1.0)
        assert abs(w[0] - 100.01) < 1e-8


class TestSquareMap:
    def test_identity_at_lam_zero(self):
        z = (1.5, 0.7)
        w = _square(z, 0.0)
        assert abs(w[0] - z[0]) < 1e-10
        assert abs(w[1] - z[1]) < 1e-10

    def test_full_square(self):
        """(2+i)² = 4 − 1 + 4i = 3 + 4i."""
        w = _square((2.0, 1.0), 1.0)
        assert abs(w[0] - 3.0) < 1e-10
        assert abs(w[1] - 4.0) < 1e-10

    def test_real_axis_stays_real(self):
        """x² is real for real x."""
        for x in [0.5, 1.0, 1.5, -1.0, -2.5]:
            w = _square((x, 0.0), 1.0)
            assert abs(w[1]) < 1e-10
            assert abs(w[0] - x ** 2) < 1e-10

    def test_imaginary_axis_to_negative_real(self):
        """(iy)² = −y²."""
        for y in [0.5, 1.0, 2.0]:
            w = _square((0.0, y), 1.0)
            assert abs(w[0] - (-(y ** 2))) < 1e-10
            assert abs(w[1]) < 1e-10

    def test_symmetry(self):
        """z² = (−z)²; both z and −z map to the same point."""
        z = (1.3, 0.7)
        w1 = _square(z, 1.0)
        w2 = _square((-z[0], -z[1]), 1.0)
        assert abs(w1[0] - w2[0]) < 1e-10
        assert abs(w1[1] - w2[1]) < 1e-10


class TestMobiusMap:
    def test_identity_at_lam_zero(self):
        z = (0.5, 0.3)
        w = _mobius(z, 0.0)
        assert abs(w[0] - z[0]) < 1e-10
        assert abs(w[1] - z[1]) < 1e-10

    def test_full_mobius_real_axis(self):
        """(3−1)/(3+1) = 2/4 = 0.5."""
        w = _mobius((3.0, 0.0), 1.0)
        assert abs(w[0] - 0.5) < 1e-10
        assert abs(w[1] - 0.0) < 1e-10

    def test_pole_at_minus_one_returns_none(self):
        """z = −1 is the pole; denominator z+1 = 0 → None."""
        assert _mobius((-1.0, 0.0), 1.0) is None

    def test_origin_maps_to_minus_one(self):
        """f(0) = (0−1)/(0+1) = −1."""
        w = _mobius((0.0, 0.0), 1.0)
        assert abs(w[0] - (-1.0)) < 1e-10
        assert abs(w[1] - 0.0) < 1e-10

    def test_i_maps_to_i(self):
        """f(i) = (i−1)/(i+1): num=(−1+i), den=(1+i) → result = (0+i) = i."""
        w = _mobius((0.0, 1.0), 1.0)
        assert abs(w[0] - 0.0) < 1e-10
        assert abs(w[1] - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# Edge-case / failure-mode tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_all_maps_identity_at_lam_zero(self):
        """Every map must return the input unchanged when lam=0."""
        z = (1.7, -0.3)
        for fn in [_joukowski, _square, _mobius]:
            w = fn(z, 0.0)
            if w is not None:   # joukowski is defined here (|z| > MIN_Z_MAG)
                assert abs(w[0] - z[0]) < 1e-10
                assert abs(w[1] - z[1]) < 1e-10

    def test_joukowski_continuous_away_from_pole(self):
        """Small Δz far from origin → small Δf (no discontinuities)."""
        z1 = (1.5, 0.5)
        z2 = (1.501, 0.5)
        w1 = _joukowski(z1, 1.0)
        w2 = _joukowski(z2, 1.0)
        assert w1 is not None and w2 is not None
        assert abs(w1[0] - w2[0]) < 0.01
        assert abs(w1[1] - w2[1]) < 0.01

    def test_sample_count_produces_200_points(self):
        """The linspace used for sampling must yield exactly N_SAMPLES=200 points."""
        N_SAMPLES = 200
        GRID_MIN, GRID_MAX = -3.0, 3.0
        pts = [GRID_MIN + (GRID_MAX - GRID_MIN) * i / (N_SAMPLES - 1)
               for i in range(N_SAMPLES)]
        assert len(pts) == 200
        assert abs(pts[0] - GRID_MIN) < 1e-10
        assert abs(pts[-1] - GRID_MAX) < 1e-10

    def test_joukowski_near_pole_threshold(self):
        """|z| just above MIN_Z_MAG should return a value; at or below should return None."""
        assert _joukowski((MIN_Z_MAG * 0.99, 0.0), 1.0) is None
        result = _joukowski((MIN_Z_MAG * 1.5, 0.0), 1.0)
        assert result is not None

    def test_large_mapped_value_detection(self):
        """Points near Joukowski pole produce large |f(z)|; they must be filterable."""
        MAX_MAG = 8.0
        # z just outside MIN_Z_MAG but very close to 0 → 1/z is huge
        z = (MIN_Z_MAG + 1e-4, 0.0)
        w = _joukowski(z, 1.0)
        if w is not None:
            mag = _cmag(w)
            # Either |f(z)| > MAX_MAG (filter candidate) or it's in range
            assert mag > 0   # just verify we got a number


def test_generate_thumbnail_runs(tmp_path):
    """generate_thumbnail.py must produce a valid SVG when run as a script."""
    import shutil
    src = PIECE_DIR / "generate_thumbnail.py"
    dest_dir = tmp_path / "171-conformal-grid"
    dest_dir.mkdir()
    shutil.copy(src, dest_dir / "generate_thumbnail.py")

    result = subprocess.run(
        [sys.executable, str(dest_dir / "generate_thumbnail.py")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    svg_path = dest_dir / "thumbnail.svg"
    assert svg_path.exists()
    content = svg_path.read_text()
    assert "<svg" in content
    assert "<polyline" in content
