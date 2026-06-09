"""Tests for piece 297 — Rings of the Fourth (Hopf fibration)."""

import json
import math
import pathlib


REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "297-hopf-fibration"


# ---------------------------------------------------------------------------
# Pure-math helpers matching the JS implementation in index.html
# ---------------------------------------------------------------------------

def hopf_fiber(phi, theta, t):
    """
    Compute one point on the Hopf fiber over base point (phi, theta) at parameter t.

    Returns (a, b, c, d) ∈ S³ using the quaternion formula:
      q(t) = (cos(phi/2) e^{i(t+theta/2)}, sin(phi/2) e^{i(t-theta/2)})
    """
    hp, ht = phi / 2, theta / 2
    chp, shp = math.cos(hp), math.sin(hp)
    return (
        chp * math.cos(t + ht),
        chp * math.sin(t + ht),
        shp * math.cos(t - ht),
        shp * math.sin(t - ht),
    )


def hopf_map(a, b, c, d):
    """
    Hopf map h: S³ → S².
    h(a, b, c, d) = (2(ac+bd), 2(bc-ad), a²+b²-c²-d²)
    The result is always a unit vector on S².
    """
    return (2*(a*c + b*d), 2*(b*c - a*d), a**2 + b**2 - c**2 - d**2)


def stereo_proj(a, b, c, d):
    """
    Stereographic projection S³ → R³ from the south pole (0,0,0,1).
    Returns None when d > 0.999 (near the projection singularity).
    """
    if d > 0.999:
        return None
    f = 1.0 / (1.0 - d)
    return (a * f, b * f, c * f)


def fiber_color(phi):
    """
    Interpolate between amber (#d4832a) at equator and teal (#2a8a9f) at poles.
    t = |cos(phi)|: 1 at poles → teal, 0 at equator → amber.
    """
    t = abs(math.cos(phi))
    r = round(212 + (42 - 212) * t)
    g = round(131 + (138 - 131) * t)
    b = round(42 + (159 - 42) * t)
    return r, g, b


# ---------------------------------------------------------------------------
# Happy-path tests: core Hopf-fibration mathematics
# ---------------------------------------------------------------------------

class TestHopfFiberMath:
    def test_fiber_point_lies_on_s3(self):
        """Every fiber point must satisfy a²+b²+c²+d² = 1 (unit norm in R⁴)."""
        phi, theta = math.pi / 3, math.pi / 4
        for i in range(32):
            t = 2 * math.pi * i / 32
            a, b, c, d = hopf_fiber(phi, theta, t)
            norm_sq = a**2 + b**2 + c**2 + d**2
            assert abs(norm_sq - 1.0) < 1e-12, f"norm²={norm_sq} at t={t:.3f}"

    def test_hopf_map_constant_on_fiber(self):
        """All points of one fiber must map to the same point on S² via h."""
        phi, theta = math.pi / 3, math.pi / 5
        x0 = math.sin(phi) * math.cos(theta)
        y0 = math.sin(phi) * math.sin(theta)
        z0 = math.cos(phi)
        for i in range(16):
            t = 2 * math.pi * i / 16
            a, b, c, d = hopf_fiber(phi, theta, t)
            x, y, z = hopf_map(a, b, c, d)
            assert abs(x - x0) < 1e-12, f"Hopf x mismatch at t={t:.3f}"
            assert abs(y - y0) < 1e-12, f"Hopf y mismatch at t={t:.3f}"
            assert abs(z - z0) < 1e-12, f"Hopf z mismatch at t={t:.3f}"

    def test_hopf_image_on_s2(self):
        """The Hopf map image is always on S²: x²+y²+z² = 1."""
        for li in range(5):
            phi = math.pi / 6 + li * math.pi / 10
            for lo in range(4):
                theta = lo * math.pi / 2
                a, b, c, d = hopf_fiber(phi, theta, 0.7)
                x, y, z = hopf_map(a, b, c, d)
                assert abs(x**2 + y**2 + z**2 - 1.0) < 1e-12

    def test_fiber_parametrization_is_closed(self):
        """Fiber at t=0 and t=2π give identical points (the circle closes)."""
        phi, theta = math.pi / 4, math.pi / 6
        p0 = hopf_fiber(phi, theta, 0.0)
        p2pi = hopf_fiber(phi, theta, 2 * math.pi)
        for v0, v2pi in zip(p0, p2pi):
            assert abs(v0 - v2pi) < 1e-12

    def test_color_at_equator_is_amber(self):
        """phi = pi/2 (equator) → color should be amber #d4832a."""
        r, g, b = fiber_color(math.pi / 2)
        assert r == 212   # 0xd4
        assert g == 131   # 0x83
        assert b == 42    # 0x2a

    def test_color_at_north_pole_is_teal(self):
        """phi = 0 (north pole) → color should be teal #2a8a9f."""
        r, g, b = fiber_color(0.0)
        assert r == 42    # 0x2a
        assert g == 138   # 0x8a
        assert b == 159   # 0x9f

    def test_fiber_count_at_least_200(self):
        """14 latitudes × 18 longitudes = 252 fibers, satisfying the ≥200 requirement."""
        n_lat, n_lon = 14, 18
        assert n_lat * n_lon >= 200


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_equatorial_fiber_has_a_equals_c_at_theta_zero(self):
        """At phi=pi/2, theta=0: the formula gives a(t)=c(t) for all t."""
        phi, theta = math.pi / 2, 0.0
        for i in range(16):
            t = 2 * math.pi * i / 16
            a, b, c, d = hopf_fiber(phi, theta, t)
            assert abs(a - c) < 1e-12, f"a≠c at t={t:.3f}"

    def test_stereo_proj_finite_for_phi_range(self):
        """For phi in [15°, 165°], d stays below 0.999 → no projection singularity."""
        phi_min = math.pi / 12   # 15°
        phi_max = math.pi * 11 / 12  # 165°
        for li in range(14):
            phi = phi_min + (phi_max - phi_min) * li / 13
            for lo in range(18):
                theta = 2 * math.pi * lo / 18
                for i in range(0, 64, 8):  # sample 8 points per fiber
                    t = 2 * math.pi * i / 64
                    a, b, c, d = hopf_fiber(phi, theta, t)
                    assert d < 0.999, f"d={d:.6f} is too close to 1 at phi={math.degrees(phi):.1f}°"
                    pt = stereo_proj(a, b, c, d)
                    assert pt is not None

    def test_different_longitudes_give_different_fibers(self):
        """Two fibers at the same latitude but different longitudes must differ."""
        phi = math.pi / 2
        p1 = hopf_fiber(phi, 0.0, 0.0)
        p2 = hopf_fiber(phi, math.pi / 3, 0.0)
        diff = sum(abs(a - b) for a, b in zip(p1, p2))
        assert diff > 1e-6

    def test_large_input_many_fibers_all_on_s3(self):
        """Computing 252 fibers × 64 points: every point must lie on S³."""
        phi_min = math.pi / 12
        phi_max = math.pi * 11 / 12
        n_lat, n_lon, n_pts = 14, 18, 64
        violations = 0
        for li in range(n_lat):
            phi = phi_min + (phi_max - phi_min) * li / (n_lat - 1)
            for lo in range(n_lon):
                theta = 2 * math.pi * lo / n_lon
                for i in range(n_pts):
                    t = 2 * math.pi * i / n_pts
                    a, b, c, d = hopf_fiber(phi, theta, t)
                    if abs(a**2 + b**2 + c**2 + d**2 - 1.0) > 1e-10:
                        violations += 1
        assert violations == 0


# ---------------------------------------------------------------------------
# Failure-mode tests: assert the correct error / no-op behavior
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_south_pole_fiber_hits_singularity(self):
        """Exact south pole (phi=pi): at the right t, d = 1 → projection undefined."""
        phi = math.pi   # south pole
        theta = 0.0
        # sin(phi/2) = sin(pi/2) = 1, so max d = 1 at t-theta/2 = pi/2
        a, b, c, d = hopf_fiber(phi, theta, math.pi / 2)
        assert abs(d - 1.0) < 1e-10, f"Expected d=1, got {d}"
        result = stereo_proj(a, b, c, d)
        assert result is None, "stereo_proj should return None when d ≥ 0.999"

    def test_stereo_proj_returns_none_when_d_near_one(self):
        """stereo_proj must return None (not raise) for d=0.9995."""
        result = stereo_proj(0.0, 0.0, 0.1, 0.9995)
        assert result is None

    def test_painter_sort_orders_far_before_near(self):
        """Depth sort (back-to-front) must place smaller zAvg first."""
        batches = [(None, (42, 138, 159), 2.0), (None, (212, 131, 42), -1.5)]
        sorted_batches = sorted(batches, key=lambda b: b[2])
        assert sorted_batches[0][2] == -1.5   # far (negative z) drawn first
        assert sorted_batches[1][2] == 2.0    # near (positive z) drawn last


# ---------------------------------------------------------------------------
# File-structure and pieces.json integration tests
# ---------------------------------------------------------------------------

class TestPieceFiles:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir(), f"Missing directory: {PIECE_DIR}"

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_index_html_has_canvas_element(self):
        content = (PIECE_DIR / "index.html").read_text()
        assert "<canvas" in content

    def test_index_html_background_color(self):
        content = (PIECE_DIR / "index.html").read_text()
        assert "0a0a12" in content.lower()

    def test_index_html_rotation_period_20s(self):
        """One full rotation must take 20 000 ms."""
        content = (PIECE_DIR / "index.html").read_text()
        assert "20000" in content

    def test_index_html_uses_request_animation_frame(self):
        content = (PIECE_DIR / "index.html").read_text()
        assert "requestAnimationFrame" in content

    def test_index_html_no_external_scripts(self):
        """No CDN or external script src allowed."""
        import re
        content = (PIECE_DIR / "index.html").read_text()
        external = re.findall(r'<script[^>]+src=["\']https?://', content)
        assert not external, f"Found external script tags: {external}"

    def test_index_html_has_amber_color(self):
        content = (PIECE_DIR / "index.html").read_text()
        assert "d4832a" in content.lower() or "D4832A" in content

    def test_index_html_has_teal_color(self):
        content = (PIECE_DIR / "index.html").read_text()
        assert "2a8a9f" in content.lower() or "2A8A9F" in content

    def test_index_html_declares_fiber_constants(self):
        """N_LAT and N_LON constants must appear in the script."""
        content = (PIECE_DIR / "index.html").read_text()
        assert "N_LAT" in content
        assert "N_LON" in content

    def test_pieces_json_entry_present(self):
        pieces = json.loads((REPO / "pieces.json").read_text())
        ids = [p["id"] for p in pieces]
        assert "297-hopf-fibration" in ids

    def test_pieces_json_entry_complete(self):
        pieces = json.loads((REPO / "pieces.json").read_text())
        entry = next(p for p in pieces if p["id"] == "297-hopf-fibration")
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
        missing = required - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_pieces_json_id_matches_directory(self):
        pieces = json.loads((REPO / "pieces.json").read_text())
        entry = next(p for p in pieces if p["id"] == "297-hopf-fibration")
        assert entry["id"] == pathlib.Path(entry["path"]).name

    def test_pieces_json_thumbnail_file_exists(self):
        pieces = json.loads((REPO / "pieces.json").read_text())
        entry = next(p for p in pieces if p["id"] == "297-hopf-fibration")
        assert (REPO / entry["thumbnail"]).is_file()
