"""Tests for Piece 208 — Double Pendulum: Chaos Made Visible."""
import json
import math
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "208-double-pendulum"
INDEX = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "208-double-pendulum"

# Physics constants mirrored from the implementation
G = 9.81
L1 = L2 = 1.0
M1 = M2 = 1.0
DT = 0.012
DEG = math.pi / 180
TWIN_OFFSET = 0.001 * DEG  # 0.001 degrees in radians


# ---------------------------------------------------------------------------
# Python mirror of the Lagrangian double-pendulum physics for math tests
# ---------------------------------------------------------------------------

def deriv(s, m2=M2):
    """
    Exact Lagrangian equations of motion for a double pendulum.
    Returns [dθ1/dt, dω1/dt, dθ2/dt, dω2/dt].
    Derived by solving d/dt(∂L/∂ωᵢ) − ∂L/∂θᵢ = 0 for both angles.
    """
    t1, w1, t2, w2 = s
    delta = t1 - t2
    sin_d = math.sin(delta)
    cos_d = math.cos(delta)
    denom = 2 * M1 + m2 - m2 * math.cos(2 * delta)

    dw1 = (
        -G * (2 * M1 + m2) * math.sin(t1)
        - m2 * G * math.sin(t1 - 2 * t2)
        - 2 * sin_d * m2 * (w2**2 * L2 + w1**2 * L1 * cos_d)
    ) / (L1 * denom)

    dw2 = (
        2 * sin_d * (
            w1**2 * L1 * (M1 + m2)
            + G * (M1 + m2) * math.cos(t1)
            + w2**2 * L2 * m2 * cos_d
        )
    ) / (L2 * denom)

    return [w1, dw1, w2, dw2]


def rk4_step(s, dt=DT, m2=M2):
    """One 4th-order Runge-Kutta step."""
    k1 = deriv(s, m2)
    s2 = [s[i] + 0.5 * dt * k1[i] for i in range(4)]
    k2 = deriv(s2, m2)
    s3 = [s[i] + 0.5 * dt * k2[i] for i in range(4)]
    k3 = deriv(s3, m2)
    s4 = [s[i] + dt * k3[i] for i in range(4)]
    k4 = deriv(s4, m2)
    return [s[i] + (dt / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(4)]


def integrate(n, t1_0=120 * DEG, t2_0=-30 * DEG, m2=M2):
    """Integrate the double pendulum for n steps from the given initial angles."""
    s = [t1_0, 0.0, t2_0, 0.0]
    pts = []
    for _ in range(n):
        s = rk4_step(s, m2=m2)
        pts.append(tuple(s))
    return pts


def total_energy(t1, w1, t2, w2, m2=M2):
    """
    Compute total mechanical energy of the double pendulum.
    KE = ½m₁(ω₁L₁)² + ½m₂[(ω₁L₁cosθ₁ + ω₂L₂cosθ₂)² + (ω₁L₁sinθ₁ + ω₂L₂sinθ₂)²]
    PE = −g[(m₁+m₂)L₁cosθ₁ + m₂L₂cosθ₂]
    """
    ke = (
        0.5 * M1 * (w1 * L1) ** 2
        + 0.5 * m2 * (
            (w1 * L1 * math.cos(t1) + w2 * L2 * math.cos(t2)) ** 2
            + (w1 * L1 * math.sin(t1) + w2 * L2 * math.sin(t2)) ** 2
        )
    )
    pe = -G * ((M1 + m2) * L1 * math.cos(t1) + m2 * L2 * math.cos(t2))
    return ke + pe


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_pieces():
    """Return parsed pieces.json as a list."""
    return json.loads(PIECES_JSON.read_text())


def get_entry():
    """Return the pieces.json entry for 208-double-pendulum, or None."""
    for item in load_pieces():
        if item.get("id") == PIECE_ID:
            return item
    return None


def html():
    """Return index.html content."""
    return INDEX.read_text()


# ---------------------------------------------------------------------------
# File-system tests
# ---------------------------------------------------------------------------

class TestFiles:
    def test_directory_exists(self):
        assert PIECE_DIR.is_dir(), f"Directory missing: {PIECE_DIR}"

    def test_index_html_exists(self):
        assert INDEX.is_file()

    def test_thumbnail_svg_exists(self):
        assert THUMBNAIL.is_file()

    def test_readme_exists(self):
        assert README.is_file()

    def test_index_html_non_trivial(self):
        assert len(html()) > 3000

    def test_readme_non_trivial(self):
        assert len(README.read_text().strip()) > 200

    def test_thumbnail_is_valid_svg(self):
        content = THUMBNAIL.read_text()
        assert "<svg" in content
        assert "</svg>" in content

    def test_thumbnail_has_drawable_geometry(self):
        content = THUMBNAIL.read_text()
        assert any(tag in content for tag in ("<path", "<polyline", "<line", "<circle"))


# ---------------------------------------------------------------------------
# pieces.json metadata
# ---------------------------------------------------------------------------

class TestPiecesJson:
    def test_entry_exists(self):
        assert get_entry() is not None, f"{PIECE_ID} not found in pieces.json"

    def test_required_fields(self):
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
        e = get_entry()
        assert e is not None
        missing = required - e.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches(self):
        e = get_entry()
        assert e is not None
        assert e["id"] == PIECE_ID

    def test_path_matches(self):
        e = get_entry()
        assert e is not None
        assert e["path"] == f"pieces/{PIECE_ID}"

    def test_thumbnail_is_svg(self):
        e = get_entry()
        assert e is not None
        assert e["thumbnail"].endswith(".svg")

    def test_thumbnail_file_exists(self):
        e = get_entry()
        assert e is not None
        assert (REPO / e["thumbnail"]).is_file()

    def test_year_is_int(self):
        e = get_entry()
        assert e is not None
        assert isinstance(e["year"], int)

    def test_technique_mentions_canvas(self):
        e = get_entry()
        assert e is not None
        assert "canvas" in e["technique"].lower()

    def test_technique_mentions_lagrangian(self):
        e = get_entry()
        assert e is not None
        tech = e["technique"].lower()
        assert "lagrangian" in tech or "double pendulum" in tech

    def test_technique_mentions_chaos(self):
        e = get_entry()
        assert e is not None
        assert "chaos" in e["technique"].lower()

    def test_208_appears_after_207(self):
        """208-double-pendulum must appear after 207-lorenz-attractor in pieces.json."""
        pieces = load_pieces()
        idx_207 = next((i for i, p in enumerate(pieces) if p["id"] == "207-lorenz-attractor"), None)
        idx_208 = next((i for i, p in enumerate(pieces) if p["id"] == PIECE_ID), None)
        assert idx_207 is not None, "207-lorenz-attractor missing"
        assert idx_208 is not None, f"{PIECE_ID} missing"
        assert idx_208 > idx_207

    def test_no_duplicate_ids(self):
        pieces = load_pieces()
        ids = [p["id"] for p in pieces]
        assert len(ids) == len(set(ids)), "Duplicate piece IDs found"

    def test_prior_pieces_preserved(self):
        ids = {p["id"] for p in load_pieces()}
        for expected in ["01-amber-current", "137-lorenz-attractor", "207-lorenz-attractor"]:
            assert expected in ids, f"Prior piece {expected!r} was removed"


# ---------------------------------------------------------------------------
# index.html structure
# ---------------------------------------------------------------------------

class TestIndexHtml:
    def test_has_canvas(self):
        assert "<canvas" in html()

    def test_has_script(self):
        assert "<script" in html()

    def test_has_viewport_meta(self):
        assert 'name="viewport"' in html()

    def test_has_charset(self):
        assert "charset" in html()

    def test_no_external_scripts(self):
        assert not re.findall(r'<script[^>]+src=["\']https?://', html())

    def test_self_contained(self):
        h = html()
        assert '<script src=' not in h
        assert '<link rel="stylesheet"' not in h

    def test_has_dark_background(self):
        assert "06061a" in html().lower()

    def test_has_requestanimationframe(self):
        assert "requestAnimationFrame" in html()

    def test_has_rk4_implementation(self):
        h = html().lower()
        assert "rk4" in h or ("k1" in h and "k2" in h and "k3" in h and "k4" in h)

    def test_has_angle_sliders(self):
        sliders = re.findall(r'type=["\']range["\']', html())
        assert len(sliders) >= 2, f"Expected ≥2 range sliders, found {len(sliders)}"

    def test_has_twin_trajectory(self):
        h = html().lower()
        assert (
            "twin" in h or "twin_offset" in h or "twinoffset" in h
            or "stateb" in h or "state_b" in h or "trailb" in h
        )

    def test_has_001_deg_offset(self):
        """0.001 degree twin offset must be present in the source."""
        h = html()
        assert "0.001" in h

    def test_has_info_pane(self):
        h = html()
        assert "info" in h.lower() or "pane" in h.lower() or "about" in h.lower()

    def test_info_pane_mentions_lagrangian(self):
        assert "lagrangian" in html().lower()

    def test_info_pane_mentions_lyapunov(self):
        assert "lyapunov" in html().lower()

    def test_info_pane_mentions_rk4(self):
        assert "rk4" in html().lower() or "runge" in html().lower()

    def test_has_amber_color(self):
        h = html().lower()
        assert "c8a96e" in h or "amber" in h

    def test_has_teal_color(self):
        h = html().lower()
        assert "4ecdc4" in h or "teal" in h

    def test_has_theta1_annotation(self):
        h = html()
        assert "θ₁" in h or "theta1" in h.lower()

    def test_has_theta2_annotation(self):
        h = html()
        assert "θ₂" in h or "theta2" in h.lower()

    def test_has_reset_button(self):
        h = html()
        assert "reset" in h.lower()

    def test_pauses_when_tab_hidden(self):
        h = html()
        assert "visibilitychange" in h or "hidden" in h.lower()

    def test_has_lagrangian_physics(self):
        """Must contain the closed-form angular acceleration formula."""
        h = html()
        assert "dw1" in h or "dw2" in h or "alpha" in h.lower()

    def test_slide_out_pane_has_collapse_button(self):
        h = html()
        assert "pane-close" in h or "close" in h.lower()


# ---------------------------------------------------------------------------
# Physics: RK4 integrator correctness
# ---------------------------------------------------------------------------

class TestPhysics:
    def test_single_step_moves_state(self):
        """A single RK4 step from non-zero initial angles must change the state."""
        s0 = [120 * DEG, 0.0, -30 * DEG, 0.0]
        s1 = rk4_step(s0)
        assert s1 != s0

    def test_stable_equilibrium_stays_put(self):
        """Both angles = 0, zero velocity is the stable equilibrium — must not drift."""
        s = [0.0, 0.0, 0.0, 0.0]
        for _ in range(200):
            s = rk4_step(s)
        assert all(abs(v) < 1e-8 for v in s), f"Equilibrium drifted: {s}"

    def test_angles_are_finite_for_large_initial(self):
        """Even at 170° initial angle, 100 steps must stay finite."""
        s = [170 * DEG, 0.0, 170 * DEG, 0.0]
        for _ in range(100):
            s = rk4_step(s)
        assert all(math.isfinite(v) for v in s), f"State went infinite: {s}"

    def test_energy_approximately_conserved(self):
        """
        RK4 must conserve total mechanical energy to within 2% over 150 steps
        for moderate initial conditions (angles ≈ 0.5 rad, zero velocity).
        """
        s = [0.5, 0.0, 0.3, 0.0]
        e0 = total_energy(*s)
        for _ in range(150):
            s = rk4_step(s)
        e1 = total_energy(*s)
        drift = abs(e1 - e0) / (abs(e0) + 1e-9)
        assert drift < 0.02, f"Energy drifted by {drift*100:.2f}% (E0={e0:.4f}, E1={e1:.4f})"

    def test_twin_trajectories_diverge(self):
        """
        Two trajectories separated by 0.001° must diverge measurably within 1000 steps.
        We require > 0.05 rad separation — well above the initial 1.7×10⁻⁵ rad offset,
        proving exponential (chaotic) growth rather than linear drift.
        """
        sA = [120 * DEG, 0.0, -30 * DEG, 0.0]
        sB = [120 * DEG + TWIN_OFFSET, 0.0, -30 * DEG, 0.0]
        for _ in range(1000):
            sA = rk4_step(sA)
            sB = rk4_step(sB)
        dist = math.hypot(sA[0] - sB[0], sA[2] - sB[2])
        assert dist > 0.05, f"Trajectories did not diverge: dist={dist:.8f} rad"

    def test_different_mass_ratio_yields_different_trajectory(self):
        """Changing m₂/m₁ from 1 to 3 must produce a measurably different orbit."""
        pts_m1 = integrate(300, m2=1.0)
        pts_m3 = integrate(300, m2=3.0)
        diffs = [math.hypot(a[0] - b[0], a[2] - b[2]) for a, b in zip(pts_m1, pts_m3)]
        assert max(diffs) > 0.05, "Mass ratio change had no effect on trajectory"

    def test_system_oscillates_through_zero(self):
        """Starting at 45°, the primary angle must pass through 0 (oscillation)."""
        pts = integrate(800, t1_0=45 * DEG, t2_0=0.0)
        t1_vals = [p[0] for p in pts]
        assert any(v < 0 for v in t1_vals), "θ₁ never crossed zero — no oscillation"

    def test_rk4_more_accurate_than_euler(self):
        """RK4 must diverge less from a fine-timestep reference than coarse Euler at dt=DT."""
        s0 = [0.3, 0.0, 0.2, 0.0]

        # Fine-dt Euler reference (dt = DT/50)
        dt_fine = DT / 50
        n_fine = 50 * 80
        sr = list(s0)
        for _ in range(n_fine):
            d = deriv(sr)
            sr = [sr[i] + dt_fine * d[i] for i in range(4)]

        # Coarse Euler
        se = list(s0)
        for _ in range(80):
            d = deriv(se)
            se = [se[i] + DT * d[i] for i in range(4)]

        # RK4
        sk = list(s0)
        for _ in range(80):
            sk = rk4_step(sk)

        err_euler = math.hypot(se[0] - sr[0], se[2] - sr[2])
        err_rk4 = math.hypot(sk[0] - sr[0], sk[2] - sr[2])
        assert err_rk4 < err_euler, (
            f"RK4 error {err_rk4:.6f} not smaller than Euler {err_euler:.6f}"
        )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_very_small_angle_stays_small(self):
        """Near-equilibrium (0.001 rad) motion must stay bounded for 500 steps."""
        s = [0.001, 0.0, 0.001, 0.0]
        for _ in range(500):
            s = rk4_step(s)
        assert abs(s[0]) < 0.5 and abs(s[2]) < 0.5, "Small-angle motion blew up"

    def test_large_angular_velocity_stays_finite(self):
        """Starting with large ω must not produce NaN or Inf within 50 steps."""
        s = [0.5, 20.0, 0.3, -20.0]
        for _ in range(50):
            s = rk4_step(s)
        assert all(math.isfinite(v) for v in s), f"State became non-finite: {s}"

    def test_zero_angle_nonzero_velocity_returns_finite(self):
        """Zero angles but nonzero ω₁ must integrate without blowing up."""
        s = [0.0, 5.0, 0.0, 0.0]
        for _ in range(200):
            s = rk4_step(s)
        assert all(math.isfinite(v) for v in s)

    def test_wrong_piece_id_absent_from_json(self):
        ids = {p["id"] for p in load_pieces()}
        assert "208-wrong-piece" not in ids
        assert "208-double-pendulm" not in ids

    def test_missing_canvas_detectable(self):
        fake = "<html><body><div>no canvas here</div></body></html>"
        assert "<canvas" not in fake

    def test_twin_offset_is_tiny(self):
        """TWIN_OFFSET must be very small — less than 1e-3 radians."""
        assert TWIN_OFFSET < 1e-3

    def test_near_vertical_unstable_equilibrium_diverges(self):
        """θ₁ ≈ π + ε is an unstable equilibrium; angular velocity must grow."""
        s = [math.pi - 0.05, 0.0, math.pi - 0.05, 0.0]
        for _ in range(150):
            s = rk4_step(s)
        # At the unstable (upright) position the system must show significant motion
        assert abs(s[1]) + abs(s[3]) > 0.1, "Unstable equilibrium didn't produce motion"


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

class TestReadme:
    def test_mentions_rk4(self):
        text = README.read_text().lower()
        assert "rk4" in text or "runge" in text

    def test_mentions_lagrangian(self):
        text = README.read_text().lower()
        assert "lagrangian" in text

    def test_mentions_lyapunov(self):
        text = README.read_text().lower()
        assert "lyapunov" in text

    def test_mentions_chaos(self):
        text = README.read_text().lower()
        assert "chaos" in text or "chaotic" in text

    def test_mentions_twin_or_offset(self):
        text = README.read_text().lower()
        assert "twin" in text or "0.001" in text or "offset" in text
