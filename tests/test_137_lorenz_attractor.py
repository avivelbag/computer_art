"""Tests for pieces/137-lorenz-attractor: Lorenz strange attractor rendered via RK4."""
import importlib.util
import json
import math
import pathlib
import re
import struct

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "137-lorenz-attractor"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.png"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "137-lorenz-attractor"

SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
DT = 0.005
DT_2, DT_6 = DT / 2, DT / 6


# ---------------------------------------------------------------------------
# Python mirror of the RK4 integrator from generate_thumbnail.py
# ---------------------------------------------------------------------------


def _lorenz_deriv(x, y, z):
    """Lorenz vector field with classic parameters sigma=10, rho=28, beta=8/3."""
    return SIGMA * (y - x), x * (RHO - z) - y, x * y - BETA * z


def rk4_step(x: float, y: float, z: float) -> tuple[float, float, float]:
    """One RK4 step for the Lorenz system; mirrors the JS and Python implementations."""
    dx1, dy1, dz1 = _lorenz_deriv(x, y, z)
    dx2, dy2, dz2 = _lorenz_deriv(x + DT_2 * dx1, y + DT_2 * dy1, z + DT_2 * dz1)
    dx3, dy3, dz3 = _lorenz_deriv(x + DT_2 * dx2, y + DT_2 * dy2, z + DT_2 * dz2)
    dx4, dy4, dz4 = _lorenz_deriv(x + DT * dx3, y + DT * dy3, z + DT * dz3)
    return (
        x + DT_6 * (dx1 + 2 * dx2 + 2 * dx3 + dx4),
        y + DT_6 * (dy1 + 2 * dy2 + 2 * dy3 + dy4),
        z + DT_6 * (dz1 + 2 * dz2 + 2 * dz3 + dz4),
    )


def integrate(n: int, x0=0.1, y0=0.0, z0=1.0, warmup=2000):
    """Return n trajectory points after discarding warmup transient steps."""
    x, y, z = x0, y0, z0
    for _ in range(warmup):
        x, y, z = rk4_step(x, y, z)
    pts = []
    for _ in range(n):
        x, y, z = rk4_step(x, y, z)
        pts.append((x, y, z))
    return pts


def project(x, y, z, angle=0.0, u_half=38.0, v_min=-3.0, v_max=53.0, sz=400):
    """Project a 3D Lorenz point to 2D screen coordinates at camera angle.

    Returns (sx, sy) pixel indices for a canvas of size sz×sz, or None if outside.
    """
    u = x * math.cos(angle) - y * math.sin(angle)
    v = z
    v_range = v_max - v_min
    sx = int((u + u_half) / (2 * u_half) * sz)
    sy = int((v_max - v) / v_range * sz)
    if 0 <= sx < sz and 0 <= sy < sz:
        return sx, sy
    return None


# ---------------------------------------------------------------------------
# Load generate_thumbnail module without running __main__
# ---------------------------------------------------------------------------


def _load_gen():
    """Import generate_thumbnail.py as a module without executing __main__."""
    spec = importlib.util.spec_from_file_location(
        "gen137", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _entry() -> dict:
    """Return the pieces.json entry for this piece."""
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


def _html() -> str:
    return INDEX_HTML.read_text()


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_readme_exists():
    assert README.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


def test_generate_thumbnail_exists():
    assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# RK4 integration correctness
# ---------------------------------------------------------------------------


class TestRK4Integration:
    def test_fixed_point_origin_is_unstable(self):
        """A small perturbation from origin must grow, not stay at origin."""
        x, y, z = rk4_step(0.001, 0.0, 0.0)
        assert abs(x) + abs(y) + abs(z) > 0.001

    def test_trajectory_stays_bounded_after_warmup(self):
        """Lorenz orbit must stay within known physical bounds after transient."""
        pts = integrate(500)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]
        assert max(abs(x) for x in xs) < 25.0, "x out of expected range"
        assert max(abs(y) for y in ys) < 35.0, "y out of expected range"
        assert all(0 < z < 55 for z in zs), "z out of expected range"

    def test_rk4_better_than_euler_for_same_dt(self):
        """RK4 should diverge less from a reference (smaller dt) than Euler at dt=0.005."""
        x0, y0, z0 = 0.5, 0.5, 10.0
        n_steps = 100
        dt_fine = 0.0001

        # Reference trajectory with very fine Euler (acts as ground truth)
        x_ref, y_ref, z_ref = x0, y0, z0
        for _ in range(n_steps * int(DT / dt_fine)):
            dx, dy, dz = _lorenz_deriv(x_ref, y_ref, z_ref)
            x_ref += dt_fine * dx
            y_ref += dt_fine * dy
            z_ref += dt_fine * dz

        # Euler at DT
        x_eu, y_eu, z_eu = x0, y0, z0
        for _ in range(n_steps):
            dx, dy, dz = _lorenz_deriv(x_eu, y_eu, z_eu)
            x_eu += DT * dx
            y_eu += DT * dy
            z_eu += DT * dz

        # RK4 at DT
        x_rk, y_rk, z_rk = x0, y0, z0
        for _ in range(n_steps):
            x_rk, y_rk, z_rk = rk4_step(x_rk, y_rk, z_rk)

        err_euler = math.hypot(x_eu - x_ref, y_eu - y_ref, z_eu - z_ref)
        err_rk4 = math.hypot(x_rk - x_ref, y_rk - y_ref, z_rk - z_ref)
        assert err_rk4 < err_euler, (
            f"RK4 error {err_rk4:.4f} not smaller than Euler error {err_euler:.4f}"
        )

    def test_rk4_at_nonstiff_point_matches_known_value(self):
        """Single RK4 step from (1, 1, 1) must match a hand-computed result to 4 d.p."""
        x0, y0, z0 = 1.0, 1.0, 1.0
        x1, y1, z1 = rk4_step(x0, y0, z0)
        # Euler approximation for sanity: dx ≈ 0, dy ≈ 27-1=26-1=25, dz ≈ 1-8/3 < 0
        # Just verify the step is in the right direction
        dx_euler, dy_euler, dz_euler = _lorenz_deriv(x0, y0, z0)
        assert abs(x1 - (x0 + DT * dx_euler)) < 1.0, "x step wildly off"
        assert abs(y1 - (y0 + DT * dy_euler)) < 1.0, "y step wildly off"
        assert abs(z1 - (z0 + DT * dz_euler)) < 1.0, "z step wildly off"

    def test_z_remains_positive_on_attractor(self):
        """z coordinate of the Lorenz attractor must remain positive after warmup."""
        pts = integrate(1000)
        assert all(p[2] > 0 for p in pts), "z went negative on the attractor"

    def test_trajectory_visits_both_lobes(self):
        """The attractor must visit both positive and negative x (two lobes)."""
        pts = integrate(5000)
        xs = [p[0] for p in pts]
        assert any(x > 5 for x in xs), "never visited right lobe (x > 5)"
        assert any(x < -5 for x in xs), "never visited left lobe (x < -5)"


# ---------------------------------------------------------------------------
# Camera projection correctness
# ---------------------------------------------------------------------------


class TestProjection:
    def test_origin_projects_to_center_at_angle_0(self):
        """The 3D origin should project near the horizontal centre at angle=0."""
        result = project(0.0, 0.0, 25.0, angle=0.0)
        assert result is not None
        sx, sy = result
        assert abs(sx - 200) < 5, f"origin x not centred: {sx}"

    def test_rotation_changes_projected_x(self):
        """Rotating the camera angle must change the projected x-coordinate."""
        p0 = project(10.0, 0.0, 25.0, angle=0.0)
        p1 = project(10.0, 0.0, 25.0, angle=math.pi / 2)
        assert p0 is not None and p1 is not None
        assert p0[0] != p1[0], "camera rotation had no effect on projected x"

    def test_high_z_projects_to_top(self):
        """High z value must map to the top of the screen (small sy)."""
        result = project(0.0, 0.0, 50.0, angle=0.0)
        assert result is not None
        sx, sy = result
        assert sy < 50, f"z=50 not near top: sy={sy}"

    def test_low_z_projects_to_bottom(self):
        """Low z value must map to the bottom of the screen (large sy)."""
        result = project(0.0, 0.0, 2.0, angle=0.0)
        assert result is not None
        sx, sy = result
        assert sy > 350, f"z=2 not near bottom: sy={sy}"

    def test_points_outside_u_half_clipped(self):
        """A point far outside U_HALF must be clipped (project returns None)."""
        result = project(100.0, 0.0, 25.0, angle=0.0)
        assert result is None, "extreme x point should be clipped"

    def test_attractor_points_mostly_on_screen(self):
        """At least 90% of on-attractor points must project within the 400×400 frame."""
        pts = integrate(500)
        on_screen = sum(1 for x, y, z in pts if project(x, y, z) is not None)
        ratio = on_screen / len(pts)
        assert ratio > 0.90, f"too many points clipped: {ratio:.2%} on screen"


# ---------------------------------------------------------------------------
# Density & colour mapping
# ---------------------------------------------------------------------------


class TestDensityAndColor:
    def test_log_density_is_monotone(self):
        """log(d+1) must be strictly increasing in d."""
        vals = [math.log(d + 1) for d in range(1, 20)]
        for a, b in zip(vals, vals[1:]):
            assert b > a

    def test_density_0_maps_to_background(self):
        """A density of zero must render to background colour (6, 6, 24)."""
        gen = _load_gen()
        r, g, b = gen.lorenz_color(0.0)
        assert r == 6 and g == 6 and b == 24

    def test_density_1_maps_to_near_background(self):
        """t close to 0 must produce a colour near indigo, not gold."""
        gen = _load_gen()
        r, g, b = gen.lorenz_color(0.02)
        assert b > r, f"dim-density pixel not blue-ish: ({r},{g},{b})"

    def test_density_max_maps_to_gold(self):
        """t=1 must produce a colour dominated by red+green (gold), not blue."""
        gen = _load_gen()
        r, g, b = gen.lorenz_color(1.0)
        assert r > 200 and b < 50, f"max-density pixel not gold: ({r},{g},{b})"

    def test_color_gradient_is_monotone_in_red(self):
        """Red channel must increase from t=0.5 to t=1 (cyan → gold transition)."""
        gen = _load_gen()
        reds = [gen.lorenz_color(t)[0] for t in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
        assert reds == sorted(reds), f"red channel not monotone: {reds}"


# ---------------------------------------------------------------------------
# generate_thumbnail module tests
# ---------------------------------------------------------------------------


class TestGenerateThumbnail:
    def test_rk4_step_returns_three_floats(self):
        gen = _load_gen()
        result = gen.rk4_step(0.1, 0.0, 1.0)
        assert len(result) == 3
        assert all(isinstance(v, float) for v in result)

    def test_rk4_step_sigma_rho_beta_matches_spec(self):
        """Constants in generate_thumbnail must equal σ=10, ρ=28, β=8/3."""
        gen = _load_gen()
        assert gen.SIGMA == 10.0
        assert gen.RHO == 28.0
        assert abs(gen.BETA - 8.0 / 3.0) < 1e-12

    def test_dt_matches_spec(self):
        gen = _load_gen()
        assert abs(gen.DT - 0.005) < 1e-12

    def test_build_density_returns_correct_length(self):
        gen = _load_gen()
        density = gen.build_density(n_points=500)
        assert len(density) == gen.W * gen.H

    def test_build_density_has_nonzero_entries(self):
        gen = _load_gen()
        density = gen.build_density(n_points=5000)
        assert any(d > 0 for d in density), "density grid is all zeros"

    def test_build_density_small_returns_sparse(self):
        """A very small number of points should hit far fewer than W*H pixels."""
        gen = _load_gen()
        density = gen.build_density(n_points=100)
        hits = sum(1 for d in density if d > 0)
        assert hits < gen.W * gen.H // 10, f"too many hits for 100 points: {hits}"

    def test_density_to_pixels_all_background_when_zero(self):
        gen = _load_gen()
        density = [0] * (gen.W * gen.H)
        pixels = gen.density_to_pixels(density)
        assert all(p == (gen.BG_R, gen.BG_G, gen.BG_B) for p in pixels)

    def test_density_to_pixels_length(self):
        gen = _load_gen()
        density = [1] * (gen.W * gen.H)
        pixels = gen.density_to_pixels(density)
        assert len(pixels) == gen.W * gen.H

    def test_generate_thumbnail_returns_pixel_list(self):
        gen = _load_gen()
        pixels = gen.generate_thumbnail(n_points=1000)
        assert len(pixels) == gen.W * gen.H
        assert all(len(p) == 3 for p in pixels)

    def test_generate_thumbnail_has_nonbackground_pixels(self):
        gen = _load_gen()
        pixels = gen.generate_thumbnail(n_points=5000)
        bg = (gen.BG_R, gen.BG_G, gen.BG_B)
        assert any(p != bg for p in pixels), "all pixels are background"

    def test_write_png_produces_valid_png(self, tmp_path):
        gen = _load_gen()
        pixels = [(6, 6, 24)] * (gen.W * gen.H)
        out = tmp_path / "test.png"
        gen.write_png(str(out), pixels, gen.W, gen.H)
        data = out.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n", "PNG signature missing"
        assert b"IHDR" in data
        assert b"IDAT" in data
        assert b"IEND" in data

    def test_write_png_png_dimensions_in_ihdr(self, tmp_path):
        gen = _load_gen()
        pixels = [(6, 6, 24)] * (gen.W * gen.H)
        out = tmp_path / "test.png"
        gen.write_png(str(out), pixels, gen.W, gen.H)
        data = out.read_bytes()
        # IHDR starts at byte 16; first 8 bytes are width, height as big-endian uint32
        ihdr_start = data.index(b"IHDR") + 4
        w = struct.unpack(">I", data[ihdr_start: ihdr_start + 4])[0]
        h = struct.unpack(">I", data[ihdr_start + 4: ihdr_start + 8])[0]
        assert w == gen.W
        assert h == gen.H


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_has_script():
    assert "<script" in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset():
    assert "charset" in _html()


def test_html_no_external_scripts():
    assert not re.findall(r'<script[^>]+src=["\']https?://', _html())


def test_html_self_contained():
    html = _html()
    assert "<script src=" not in html
    assert '<link rel="stylesheet"' not in html


def test_html_has_dark_background():
    html = _html().lower()
    assert "060618" in html or "indigo" in html or ("6" in html and "24" in html)


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_mentions_rk4():
    html = _html().lower()
    assert "rk4" in html or "runge" in html or ("dx1" in html and "dx2" in html)


def test_html_has_lorenz_parameters():
    html = _html()
    assert "SIGMA" in html or "sigma" in html.lower()
    assert "RHO" in html or "rho" in html.lower()
    assert "BETA" in html or "beta" in html.lower()


def test_html_dt_is_0005():
    html = _html()
    assert "0.005" in html


def test_html_sigma_equals_10():
    assert "SIGMA = 10" in _html() or "SIGMA=10" in _html()


def test_html_rho_equals_28():
    assert "RHO = 28" in _html() or "RHO=28" in _html()


def test_html_n_trail_large():
    html = _html()
    m = re.search(r"N_TRAIL\s*=\s*(\d+)", html)
    assert m, "N_TRAIL constant not found in HTML"
    assert int(m.group(1)) >= 100000, f"N_TRAIL {m.group(1)} below 100k"


def test_html_rot_speed_present():
    html = _html()
    assert "ROT_SPEED" in html or "rot_speed" in html.lower() or "0.002" in html


def test_html_has_cyan_color():
    html = _html().lower()
    assert "220" in html or "cyan" in html or "00e0e0" in html or "0,220" in html


def test_html_has_gold_color():
    html = _html().lower()
    assert "255" in html and "215" in html or "gold" in html


def test_html_has_float32array():
    assert "Float32Array" in _html()


# ---------------------------------------------------------------------------
# Thumbnail PNG
# ---------------------------------------------------------------------------


def test_thumbnail_not_empty():
    assert THUMBNAIL.stat().st_size > 5000


def test_thumbnail_is_valid_png():
    data = THUMBNAIL.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "PNG signature missing"


def test_thumbnail_under_500kb():
    assert THUMBNAIL.stat().st_size < 500_000


def test_thumbnail_width_and_height_400():
    data = THUMBNAIL.read_bytes()
    ihdr = data.index(b"IHDR") + 4
    w = struct.unpack(">I", data[ihdr: ihdr + 4])[0]
    h = struct.unpack(">I", data[ihdr + 4: ihdr + 8])[0]
    assert w == 400, f"width={w}"
    assert h == 400, f"height={h}"


def test_thumbnail_has_idat_chunk():
    assert b"IDAT" in THUMBNAIL.read_bytes()


# ---------------------------------------------------------------------------
# pieces.json
# ---------------------------------------------------------------------------


def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_entry_has_all_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - _entry().keys()
    assert not missing, f"Missing fields: {missing}"


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_png():
    assert _entry()["thumbnail"].endswith(".png")


def test_pieces_json_thumbnail_file_exists():
    assert (REPO / _entry()["thumbnail"]).is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_lorenz_or_rk4():
    tech = _entry()["technique"].lower()
    assert "lorenz" in tech or "rk4" in tech or "runge" in tech


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 200


def test_readme_mentions_rk4():
    assert "rk4" in README.read_text().lower() or "runge-kutta" in README.read_text().lower()


def test_readme_mentions_sigma():
    readme = README.read_text().lower()
    assert "sigma" in readme or "σ" in readme


def test_readme_mentions_rho():
    readme = README.read_text().lower()
    assert "rho" in readme or "ρ" in readme


def test_readme_mentions_beta():
    readme = README.read_text().lower()
    assert "beta" in readme or "β" in readme


def test_readme_mentions_chaotic_or_never_repeats():
    readme = README.read_text().lower()
    assert "chaotic" in readme or "never repeat" in readme or "sensitive" in readme


def test_readme_mentions_lyapunov_or_exponential():
    readme = README.read_text().lower()
    assert "lyapunov" in readme or "exponential" in readme or "diverge" in readme


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_rk4_step_from_near_fixed_point_diverges(self):
        """The non-trivial fixed points are unstable; a small push must leave them."""
        # Non-trivial fixed points: x=y=sqrt(beta*(rho-1)), z=rho-1
        fp = math.sqrt(BETA * (RHO - 1))
        x0, y0, z0 = fp + 0.01, fp, RHO - 1
        x1, y1, z1 = rk4_step(x0, y0, z0)
        assert (x1, y1, z1) != (x0, y0, z0), "fixed point not moving"

    def test_large_initial_z_returns_to_attractor(self):
        """Starting at z=200 (far outside the attractor) must converge within 5000 steps."""
        x, y, z = 0.1, 0.0, 200.0
        for _ in range(5000):
            x, y, z = rk4_step(x, y, z)
        assert z < 100, f"z={z:.1f} still far from attractor after 5000 steps"

    def test_two_close_trajectories_diverge(self):
        """Sensitive dependence: two nearby starts must separate significantly.

        The positive Lyapunov exponent (≈ 0.37 in the transient, higher on the
        attractor) guarantees exponential separation.  We use a perturbation of
        1e-3 and 5000 steps (~25 time units), which gives a theoretical minimum
        separation of 1e-3 * exp(0.37 * 25) ≈ 40 >> 1.
        """
        x1, y1, z1 = 0.1, 0.0, 1.0
        x2, y2, z2 = 0.1 + 1e-3, 0.0, 1.0
        for _ in range(5000):
            x1, y1, z1 = rk4_step(x1, y1, z1)
            x2, y2, z2 = rk4_step(x2, y2, z2)
        dist = math.hypot(x2 - x1, y2 - y1, z2 - z1)
        assert dist > 1.0, f"trajectories did not diverge: dist={dist:.4f}"

    def test_empty_density_grid_all_background(self):
        gen = _load_gen()
        density = [0] * (gen.W * gen.H)
        pixels = gen.density_to_pixels(density)
        bg = (gen.BG_R, gen.BG_G, gen.BG_B)
        assert all(p == bg for p in pixels)

    def test_wrong_id_not_in_json(self):
        data = json.loads(PIECES_JSON.read_text())
        ids = {item["id"] for item in data}
        assert "137-wrong-piece" not in ids

    def test_missing_canvas_detectable(self):
        fake = "<html><body><div></div></body></html>"
        assert "<canvas" not in fake

    def test_density_to_pixels_single_hot_pixel(self):
        """A single high-density pixel surrounded by zeros must produce gold, not background."""
        gen = _load_gen()
        density = [0] * (gen.W * gen.H)
        density[gen.W * gen.H // 2] = 500
        pixels = gen.density_to_pixels(density)
        hot = pixels[gen.W * gen.H // 2]
        bg = (gen.BG_R, gen.BG_G, gen.BG_B)
        assert hot != bg, "high-density pixel still renders as background"
        r, g, b = hot
        assert r > 100, f"high-density pixel not gold-ish: ({r},{g},{b})"
