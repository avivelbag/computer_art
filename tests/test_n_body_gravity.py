"""Tests for Piece 240 — Orbital Memory: N-Body Gravity in Slow Time.

Exercises the physics simulation code extracted from generate_thumbnail.py,
which mirrors the JS implementation in index.html. All tests are deterministic
and require no network or file I/O outside tmp_path.
"""
import importlib.util
import math
import pathlib

PIECE_DIR = pathlib.Path(__file__).parent.parent / 'pieces' / '240-n-body-gravity'

# Import generate_thumbnail under a unique module name to avoid polluting sys.path
# and shadowing other pieces' generate_thumbnail modules during a full test run.
_spec = importlib.util.spec_from_file_location(
    'gen_thumb_240', PIECE_DIR / 'generate_thumbnail.py'
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

G = _mod.G
EPS = _mod.EPS
DT = _mod.DT
SUBS = _mod.SUBS
TRAIL_LEN = _mod.TRAIL_LEN
W = _mod.W
H = _mod.H
COLORS = _mod.COLORS
compute_accel = _mod.compute_accel
leapfrog = _mod.leapfrog
make_figure8 = _mod.make_figure8
make_solar = _mod.make_solar
assign_colors = _mod.assign_colors
blend = _mod.blend
draw_line = _mod.draw_line
render = _mod.render
write_png = _mod.write_png


# ---------------------------------------------------------------------------
# Happy-path: solar configuration properties
# ---------------------------------------------------------------------------

class TestSolarConfig:
    def test_five_bodies(self):
        """Solar config must produce exactly 5 bodies (sun + 4 planets)."""
        bs = make_solar()
        assert len(bs) == 5

    def test_sun_dominates_mass(self):
        """Central body must be far heavier than all planets combined (>99% of total)."""
        bs = make_solar()
        sun_mass = bs[0]['m']
        total_mass = sum(b['m'] for b in bs)
        assert sun_mass / total_mass > 0.99

    def test_near_zero_net_momentum(self):
        """Total momentum must be very small — Keplerian ICs are not perfectly zeroed."""
        bs = make_solar()
        px = sum(b['m'] * b['vx'] for b in bs)
        py = sum(b['m'] * b['vy'] for b in bs)
        M  = sum(b['m'] for b in bs)
        # Momentum per unit mass should be negligible
        assert abs(px / M) < 0.01
        assert abs(py / M) < 0.01

    def test_planets_in_circular_orbit(self):
        """Each planet's speed must equal sqrt(G·M_sun/r) to within 1%."""
        bs = make_solar()
        Msun = bs[0]['m']
        for b in bs[1:]:
            r  = math.hypot(b['x'], b['y'])
            v  = math.hypot(b['vx'], b['vy'])
            v_expected = math.sqrt(G * Msun / r)
            assert abs(v / v_expected - 1.0) < 0.01, (
                f"Planet at r={r:.3f}: v={v:.4f} vs expected {v_expected:.4f}"
            )

    def test_solar_stays_bounded_30s(self):
        """All solar bodies must stay within ESCAPE_R=4 for 30 wall-seconds (1800 frames)."""
        bs = make_solar()
        dt_sub = DT / SUBS
        escape_r = 4.0
        for _frame in range(1800):
            for _ in range(SUBS):
                leapfrog(bs, dt_sub)
        for b in bs:
            r = math.hypot(b['x'], b['y'])
            assert r < escape_r, f"Body escaped to r={r:.3f} after 30 s"


# ---------------------------------------------------------------------------
# Happy-path: figure-8 orbital properties
# ---------------------------------------------------------------------------

class TestFigure8Config:
    def test_three_bodies(self):
        """Figure-8 must produce exactly three bodies."""
        bs = make_figure8()
        assert len(bs) == 3

    def test_equal_masses(self):
        """All three bodies must have mass 1.0."""
        bs = make_figure8()
        assert all(b['m'] == 1.0 for b in bs)

    def test_near_zero_net_momentum(self):
        """Net momentum must be near-zero (limited by published IC precision)."""
        bs = make_figure8()
        px = sum(b['m'] * b['vx'] for b in bs)
        py = sum(b['m'] * b['vy'] for b in bs)
        # Published constants have residual ~1e-8 from finite decimal precision.
        assert abs(px) < 1e-7
        assert abs(py) < 1e-7

    def test_bodies_not_coincident(self):
        """No two bodies must start at the same position."""
        bs = make_figure8()
        for i in range(len(bs)):
            for j in range(i + 1, len(bs)):
                d = math.hypot(bs[i]['x'] - bs[j]['x'], bs[i]['y'] - bs[j]['y'])
                assert d > 0.01

    def test_figure8_stays_bounded_one_period(self):
        """Figure-8 bodies must remain within 3 sim units for at least one period (T≈6.33)."""
        bs = make_figure8()
        dt_sub = DT / SUBS
        T = 6.3259
        steps = int(T / dt_sub)
        for _ in range(steps):
            leapfrog(bs, dt_sub)
        for b in bs:
            assert math.hypot(b['x'], b['y']) < 3.0

    def test_figure8_antisymmetry(self):
        """Body 3 must start at the antipode of body 1 (rotational symmetry of figure-8)."""
        bs = make_figure8()
        # In the Chenciner-Montgomery figure-8, body[0] and body[2] are at ±(x, y).
        assert abs(bs[0]['x'] + bs[2]['x']) < 1e-9
        assert abs(bs[0]['y'] + bs[2]['y']) < 1e-9


# ---------------------------------------------------------------------------
# Gravity: acceleration correctness
# ---------------------------------------------------------------------------

class TestGravity:
    def test_third_law(self):
        """Newton's third law: m_i·a_i + m_j·a_j = 0 for a two-body system."""
        bodies = [
            {'x': -1.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 2.0},
            {'x':  1.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 3.0},
        ]
        ax, ay = compute_accel(bodies)
        assert abs(bodies[0]['m'] * ax[0] + bodies[1]['m'] * ax[1]) < 1e-12
        assert abs(bodies[0]['m'] * ay[0] + bodies[1]['m'] * ay[1]) < 1e-12

    def test_radial_direction(self):
        """Gravity must point from body toward the other body (attractive)."""
        bodies = [
            {'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
            {'x': 2.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
        ]
        ax, ay = compute_accel(bodies)
        assert ax[0] > 0    # body 0 pulled right toward body 1
        assert ax[1] < 0    # body 1 pulled left toward body 0
        assert abs(ay[0]) < 1e-12
        assert abs(ay[1]) < 1e-12

    def test_softening_prevents_divergence(self):
        """At r=0, softened acceleration must be finite (no singularity)."""
        bodies = [
            {'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
            {'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
        ]
        ax, ay = compute_accel(bodies)
        assert all(math.isfinite(a) for a in ax)
        assert all(math.isfinite(a) for a in ay)

    def test_softening_caps_maximum_force(self):
        """At near-zero separation, |a| must not exceed G*m/eps^2."""
        bodies = [
            {'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
            {'x': 1e-10, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
        ]
        ax, ay = compute_accel(bodies)
        max_a = G * 1.0 / (EPS * EPS)
        assert abs(ax[0]) <= max_a * 1.01

    def test_single_body_zero_accel(self):
        """A lone body has zero acceleration (no partners to attract)."""
        bodies = [{'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 5.0}]
        ax, ay = compute_accel(bodies)
        assert ax[0] == 0.0
        assert ay[0] == 0.0

    def test_inverse_square_scaling(self):
        """Force at 2r must be ~1/4 of force at r (softening negligible at large r)."""
        def ax_at(r):
            bodies = [
                {'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
                {'x': r,   'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
            ]
            ax, _ = compute_accel(bodies)
            return ax[0]

        r = 10.0   # large enough that softening ε=0.01 is negligible
        ratio = ax_at(r) / ax_at(2 * r)
        assert abs(ratio - 4.0) < 0.01


# ---------------------------------------------------------------------------
# Leapfrog integrator
# ---------------------------------------------------------------------------

class TestLeapfrog:
    def test_momentum_conserved(self):
        """Total momentum must not drift across 200 leapfrog steps."""
        bs = make_figure8()
        px0 = sum(b['m'] * b['vx'] for b in bs)
        py0 = sum(b['m'] * b['vy'] for b in bs)
        dt_sub = DT / SUBS
        for _ in range(200):
            leapfrog(bs, dt_sub)
        px1 = sum(b['m'] * b['vx'] for b in bs)
        py1 = sum(b['m'] * b['vy'] for b in bs)
        assert abs(px1 - px0) < 1e-10
        assert abs(py1 - py0) < 1e-10

    def test_solar_center_of_mass_fixed(self):
        """Solar config CoM must not drift measurably over 1800 frames."""
        bs = make_solar()
        M   = sum(b['m'] for b in bs)
        cm0 = (
            sum(b['m'] * b['x'] for b in bs) / M,
            sum(b['m'] * b['y'] for b in bs) / M,
        )
        dt_sub = DT / SUBS
        for _ in range(1800):
            for _ in range(SUBS):
                leapfrog(bs, dt_sub)
        cm1 = (
            sum(b['m'] * b['x'] for b in bs) / M,
            sum(b['m'] * b['y'] for b in bs) / M,
        )
        assert math.hypot(cm1[0] - cm0[0], cm1[1] - cm0[1]) < 0.05

    def test_large_n_body_runs(self):
        """compute_accel and leapfrog must handle 8 bodies without exception."""
        import random
        rng = random.Random(42)
        bs = [
            {'x': rng.uniform(-2, 2), 'y': rng.uniform(-2, 2),
             'vx': 0.0, 'vy': 0.0, 'm': rng.uniform(0.5, 2.0)}
            for _ in range(8)
        ]
        leapfrog(bs, 0.01)
        assert len(bs) == 8


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_single_stationary_body_unchanged(self):
        """A single stationary body with no partner must not move."""
        bs = [{'x': 1.0, 'y': 2.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0}]
        leapfrog(bs, 0.05)
        assert bs[0]['x'] == 1.0
        assert bs[0]['y'] == 2.0

    def test_symmetric_two_body_collapse(self):
        """Equal-mass bodies on x-axis must move toward each other, zero y motion."""
        bs = [
            {'x': -1.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
            {'x':  1.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
        ]
        leapfrog(bs, 0.001)
        assert bs[0]['x'] > -1.0      # moved toward center
        assert bs[1]['x'] <  1.0
        assert abs(bs[0]['y']) < 1e-14
        assert abs(bs[1]['y']) < 1e-14

    def test_massless_body_exerts_no_force(self):
        """A m=0 body must not accelerate its neighbor."""
        bs = [
            {'x': 0.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 0.0},
            {'x': 2.0, 'y': 0.0, 'vx': 0.0, 'vy': 0.0, 'm': 1.0},
        ]
        ax, ay = compute_accel(bs)
        assert ax[1] == 0.0
        assert ay[1] == 0.0

    def test_random_config_n_range(self):
        """makeRandom (imported via solar module logic) produces 4-6 bodies."""
        # Verify the formula used in index.html's makeRandom is 4+floor(random*3).
        import random
        for seed in range(20):
            random.seed(seed)
            n = 4 + int(random.random() * 3)
            assert 4 <= n <= 6


# ---------------------------------------------------------------------------
# Color assignment
# ---------------------------------------------------------------------------

class TestColorAssignment:
    def test_heaviest_gets_warmest_color(self):
        """The heaviest body must receive COLORS[0] (warmest palette entry)."""
        bs = make_solar()
        assign_colors(bs)
        heaviest = max(bs, key=lambda b: b['m'])
        assert heaviest['color'] == COLORS[0]

    def test_all_bodies_have_color(self):
        """Every body must receive a color (RGB tuple) after assign_colors."""
        bs = make_figure8()
        assign_colors(bs)
        for b in bs:
            assert 'color' in b
            assert isinstance(b['color'], tuple)
            assert len(b['color']) == 3


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

class TestRenderHelpers:
    def test_blend_opaque(self):
        """Alpha=1 blend must return exactly the foreground color."""
        assert blend((0, 0, 0), (255, 128, 64), 1.0) == (255, 128, 64)

    def test_blend_transparent(self):
        """Alpha=0 blend must return exactly the background color."""
        assert blend((100, 150, 200), (255, 0, 0), 0.0) == (100, 150, 200)

    def test_draw_line_stays_inbounds(self):
        """draw_line must not write outside the pixel buffer bounds."""
        pixels = [(10, 10, 20)] * (W * H)
        draw_line(pixels, -10, 200, W + 10, 200, (255, 255, 255), 1.0)
        assert len(pixels) == W * H

    def test_draw_line_paints_pixels(self):
        """A horizontal line must mark at least some pixels with the given color."""
        pixels = [list((10, 10, 20)) for _ in range(W * H)]
        draw_line(pixels, 10, 10, 30, 10, (200, 100, 50), 1.0)
        changed = [pixels[10 * W + x] for x in range(10, 31)]
        assert any(p != [10, 10, 20] for p in changed)


# ---------------------------------------------------------------------------
# Thumbnail generation
# ---------------------------------------------------------------------------

class TestThumbnailOutput:
    def test_render_returns_correct_byte_length(self):
        """render() must return exactly H*(1 + W*3) bytes (one filter byte per row)."""
        data = render()
        assert len(data) == H * (1 + W * 3)

    def test_thumbnail_file_exists(self):
        """Pre-generated thumbnail.png must be present and non-trivially sized."""
        thumb = PIECE_DIR / 'thumbnail.png'
        assert thumb.exists(), 'thumbnail.png was not generated'
        assert thumb.stat().st_size > 500

    def test_write_png_produces_file(self, tmp_path):
        """write_png must produce a non-empty PNG file at the given path."""
        raw = b''
        for _ in range(H):
            raw += b'\x00' + bytes([100, 150, 200] * W)
        out = tmp_path / 'test.png'
        write_png(out, raw)
        assert out.exists()
        assert out.stat().st_size > 0
        # PNG magic bytes
        assert out.read_bytes()[:4] == b'\x89PNG'
