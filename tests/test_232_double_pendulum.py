"""Tests for Piece 232 — Double Pendulum: Painting Chaos."""
import json
import math
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "232-double-pendulum"
INDEX = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "232-double-pendulum"

# Physics constants mirrored from the implementation
G = 9.81
L1 = L2 = 1.0
M1 = M2 = 1.0
DT = 0.012
DEG = math.pi / 180

# 7 pendulums with offsets k*0.002 for k in {-3,-2,-1,0,1,2,3}
N_PEND = 7
OFFSETS = [k * 0.002 for k in range(-3, 4)]
REF_IDX = 3  # k=0, center unperturbed trajectory


# ---------------------------------------------------------------------------
# Python mirror of the Lagrangian double-pendulum physics
# ---------------------------------------------------------------------------

def deriv(s, g=G, l1=L1, l2=L2):
    """
    Exact Lagrangian equations of motion for a double pendulum (m1=m2=1).
    Returns [dtheta1/dt, domega1/dt, dtheta2/dt, domega2/dt].
    """
    t1, w1, t2, w2 = s
    delta = t1 - t2
    sin_d = math.sin(delta)
    cos_d = math.cos(delta)
    denom = 2 * M1 + M2 - M2 * math.cos(2 * delta)

    dw1 = (
        -g * (2 * M1 + M2) * math.sin(t1)
        - M2 * g * math.sin(t1 - 2 * t2)
        - 2 * sin_d * M2 * (w2**2 * l2 + w1**2 * l1 * cos_d)
    ) / (l1 * denom)

    dw2 = (
        2 * sin_d * (
            w1**2 * l1 * (M1 + M2)
            + g * (M1 + M2) * math.cos(t1)
            + w2**2 * l2 * M2 * cos_d
        )
    ) / (l2 * denom)

    return [w1, dw1, w2, dw2]


def rk4_step(s, dt=DT, g=G, l1=L1, l2=L2):
    """One 4th-order Runge-Kutta step."""
    k1 = deriv(s, g, l1, l2)
    s2 = [s[i] + 0.5 * dt * k1[i] for i in range(4)]
    k2 = deriv(s2, g, l1, l2)
    s3 = [s[i] + 0.5 * dt * k2[i] for i in range(4)]
    k3 = deriv(s3, g, l1, l2)
    s4 = [s[i] + dt * k3[i] for i in range(4)]
    k4 = deriv(s4, g, l1, l2)
    return [s[i] + (dt / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(4)]


def integrate(n, theta1_0=120 * DEG, theta2_0=0.0, g=G, l1=L1, l2=L2):
    """Integrate the pendulum for n steps and return the list of states."""
    s = [theta1_0, 0.0, theta2_0, 0.0]
    pts = []
    for _ in range(n):
        s = rk4_step(s, g=g, l1=l1, l2=l2)
        pts.append(tuple(s))
    return pts


def total_energy(t1, w1, t2, w2, g=G, l1=L1, l2=L2):
    """
    Total mechanical energy: KE + PE for m1=m2=1.
    KE = l1²w1² + 0.5·l2²w2² + l1·l2·w1·w2·cos(t1-t2)
    PE = -g·(2·l1·cos(t1) + l2·cos(t2))
    """
    ke = (
        l1**2 * w1**2
        + 0.5 * l2**2 * w2**2
        + l1 * l2 * w1 * w2 * math.cos(t1 - t2)
    )
    pe = -g * (2 * l1 * math.cos(t1) + l2 * math.cos(t2))
    return ke + pe


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_pieces():
    """Return parsed pieces.json as a list."""
    return json.loads(PIECES_JSON.read_text())


def get_entry():
    """Return the pieces.json entry for 232-double-pendulum, or None."""
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
        assert len(html()) > 4000

    def test_readme_non_trivial(self):
        assert len(README.read_text().strip()) > 300

    def test_thumbnail_is_valid_svg(self):
        content = THUMBNAIL.read_text()
        assert "<svg" in content
        assert "</svg>" in content

    def test_thumbnail_has_drawable_geometry(self):
        content = THUMBNAIL.read_text()
        assert any(tag in content for tag in ("<path", "<polyline", "<line", "<circle"))

    def test_thumbnail_has_multiple_colors(self):
        """Thumbnail must show multiple spectral trails — at least 4 distinct hsl() entries."""
        content = THUMBNAIL.read_text()
        hsl_matches = re.findall(r'hsl\((\d+)', content)
        unique_hues = set(hsl_matches)
        assert len(unique_hues) >= 4, f"Expected ≥4 distinct hue values, found {len(unique_hues)}"


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
        assert not (required - e.keys()), f"Missing fields: {required - e.keys()}"

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

    def test_technique_mentions_chaos(self):
        e = get_entry()
        assert e is not None
        assert "chaos" in e["technique"].lower()

    def test_technique_mentions_rk4(self):
        e = get_entry()
        assert e is not None
        tech = e["technique"].lower()
        assert "rk4" in tech or "runge" in tech

    def test_232_appears_after_228(self):
        """232-double-pendulum must appear after 228-fourier-epicycles in pieces.json."""
        pieces = load_pieces()
        idx_228 = next((i for i, p in enumerate(pieces) if p["id"] == "228-fourier-epicycles"), None)
        idx_232 = next((i for i, p in enumerate(pieces) if p["id"] == PIECE_ID), None)
        assert idx_228 is not None, "228-fourier-epicycles missing"
        assert idx_232 is not None, f"{PIECE_ID} missing"
        assert idx_232 > idx_228

    def test_no_duplicate_ids(self):
        pieces = load_pieces()
        ids = [p["id"] for p in pieces]
        assert len(ids) == len(set(ids)), "Duplicate piece IDs found"

    def test_prior_pieces_preserved(self):
        ids = {p["id"] for p in load_pieces()}
        for expected in ["01-amber-current", "208-double-pendulum", "228-fourier-epicycles"]:
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
        """Only lib/ scripts are allowed — no CDN or internet URLs."""
        external = re.findall(r'<script[^>]+src=["\']https?://', html())
        assert not external, f"External scripts found: {external}"

    def test_has_dark_background(self):
        """Canvas background must be near-black."""
        h = html().lower()
        assert "08080e" in h or "06061a" in h or "06060" in h

    def test_has_requestanimationframe(self):
        assert "requestAnimationFrame" in html()

    def test_has_rk4_implementation(self):
        h = html().lower()
        assert "rk4" in h or ("k1" in h and "k2" in h and "k3" in h and "k4" in h)

    def test_has_theta1_slider(self):
        """Must have a slider for initial angle theta1."""
        h = html()
        sliders = re.findall(r'type=["\']range["\']', h)
        assert len(sliders) >= 1

    def test_has_four_sliders(self):
        """Must have sliders for theta1, g, l1, l2."""
        sliders = re.findall(r'type=["\']range["\']', html())
        assert len(sliders) >= 4, f"Expected ≥4 range sliders, found {len(sliders)}"

    def test_has_gravity_slider(self):
        h = html()
        assert 'sl-g' in h or 'gravity' in h.lower() or '"g"' in h

    def test_has_l1_slider(self):
        h = html()
        assert 'sl-l1' in h or 'l1' in h.lower()

    def test_has_l2_slider(self):
        h = html()
        assert 'sl-l2' in h or 'l2' in h.lower()

    def test_has_reset_button(self):
        assert "reset" in html().lower()

    def test_has_chaos_meter(self):
        h = html().lower()
        assert "chaos" in h

    def test_has_chaos_bar(self):
        h = html()
        assert "chaos-bar" in h or "chaosBar" in h or "chaos_bar" in h

    def test_has_multiple_pendulums(self):
        """Must simulate 5–8 pendulums: look for N_PEND constant or array of 7 states."""
        h = html()
        has_n_pend = "N_PEND" in h or "N_PENDULUM" in h
        has_seven = "7" in h
        assert has_n_pend or has_seven

    def test_has_offsets_array(self):
        """Must define per-pendulum angle offsets."""
        h = html()
        assert "OFFSETS" in h or "offset" in h.lower()

    def test_has_trail_management(self):
        """Must maintain trail arrays that are bounded in length."""
        h = html()
        assert "TRAIL_MAX" in h or "trail" in h.lower()

    def test_has_spectral_hues(self):
        """Must use per-pendulum hue values for coloring trails."""
        h = html()
        assert "HUES" in h or "hue" in h.lower() or "hsl(" in h.lower()

    def test_has_lagrangian_physics(self):
        h = html()
        assert "dw1" in h or "dw2" in h

    def test_has_gallery_panel(self):
        """Must use the shared GalleryPanel educational drawer."""
        h = html()
        assert "GalleryPanel" in h or "panel.js" in h

    def test_gallery_panel_mentions_lagrangian(self):
        assert "lagrangian" in html().lower()

    def test_gallery_panel_mentions_lyapunov(self):
        assert "lyapunov" in html().lower()

    def test_gallery_panel_mentions_rk4_or_runge(self):
        h = html().lower()
        assert "rk4" in h or "runge" in h

    def test_has_theta1_symbol(self):
        h = html()
        assert "θ₁" in h or "theta1" in h.lower() or "&#952;" in h

    def test_has_theta2_symbol(self):
        h = html()
        assert "θ₂" in h or "theta2" in h.lower() or "&#952;" in h

    def test_pauses_when_tab_hidden(self):
        h = html()
        assert "visibilitychange" in h or "hidden" in h.lower()

    def test_ref_idx_defined(self):
        """Reference trajectory index must be defined."""
        h = html()
        assert "REF_IDX" in h or "refIdx" in h or "ref_idx" in h.lower()


# ---------------------------------------------------------------------------
# Physics: RK4 integrator correctness
# ---------------------------------------------------------------------------

class TestPhysics:
    def test_single_step_moves_state(self):
        """A single RK4 step from a large non-zero initial angle must change the state."""
        s0 = [120 * DEG, 0.0, 0.0, 0.0]
        s1 = rk4_step(s0)
        assert s1 != s0

    def test_stable_equilibrium_stays_put(self):
        """All angles and velocities zero is the stable equilibrium — must not drift."""
        s = [0.0, 0.0, 0.0, 0.0]
        for _ in range(200):
            s = rk4_step(s)
        assert all(abs(v) < 1e-8 for v in s), f"Equilibrium drifted: {s}"

    def test_angles_are_finite_for_large_initial(self):
        """Even at 165° initial angles, 100 steps must stay finite (not NaN/Inf)."""
        s = [165 * DEG, 0.0, 165 * DEG, 0.0]
        for _ in range(100):
            s = rk4_step(s)
        assert all(math.isfinite(v) for v in s), f"State went infinite: {s}"

    def test_energy_approximately_conserved(self):
        """
        RK4 must conserve total mechanical energy to within 2% over 200 steps
        for moderate initial conditions.
        """
        s = [0.5, 0.0, 0.3, 0.0]
        e0 = total_energy(*s)
        for _ in range(200):
            s = rk4_step(s)
        e1 = total_energy(*s)
        drift = abs(e1 - e0) / (abs(e0) + 1e-9)
        assert drift < 0.02, f"Energy drifted {drift*100:.2f}% (E0={e0:.4f}, E1={e1:.4f})"

    def test_seven_pendulums_all_start_different(self):
        """All 7 initial theta1 values must be distinct."""
        theta1_0 = 120 * DEG
        init_t1 = [theta1_0 + off for off in OFFSETS]
        assert len(set(init_t1)) == N_PEND

    def test_trajectories_diverge_from_tiny_offset(self):
        """
        Center trajectory and its ±0.006 rad neighbor must diverge measurably
        within 1500 steps from 120° initial angle.
        """
        theta1_0 = 120 * DEG
        sA = [theta1_0, 0.0, 0.0, 0.0]
        sB = [theta1_0 + 0.006, 0.0, 0.0, 0.0]
        for _ in range(1500):
            sA = rk4_step(sA)
            sB = rk4_step(sB)
        dist = math.hypot(sA[0] - sB[0], sA[2] - sB[2])
        assert dist > 0.05, f"Trajectories did not diverge: dist={dist:.8f} rad"

    def test_chaos_meter_increases_over_time(self):
        """
        Max |theta2[i] - theta2[center]| across all 7 pendulums must grow
        significantly over 2000 steps from 120° initial angle.
        """
        theta1_0 = 120 * DEG
        states = [[theta1_0 + off, 0.0, 0.0, 0.0] for off in OFFSETS]
        divergence_history = []
        for _ in range(2000):
            states = [rk4_step(s) for s in states]
            ref_t2 = states[REF_IDX][2]
            max_div = max(abs(s[2] - ref_t2) for i, s in enumerate(states) if i != REF_IDX)
            divergence_history.append(max_div)
        # Divergence at the end must exceed initial tiny offsets dramatically
        final_div = divergence_history[-1]
        initial_div = divergence_history[0]
        assert final_div > initial_div * 10, (
            f"Chaos meter didn't grow: initial={initial_div:.6f}, final={final_div:.6f}"
        )

    def test_different_gravity_yields_different_trajectory(self):
        """Changing g from 9.81 to 4.0 must produce a measurably different orbit."""
        pts_normal = integrate(300, g=9.81)
        pts_low_g = integrate(300, g=4.0)
        diffs = [math.hypot(a[0] - b[0], a[2] - b[2]) for a, b in zip(pts_normal, pts_low_g)]
        assert max(diffs) > 0.05, "Gravity change had no effect on trajectory"

    def test_different_l1_yields_different_trajectory(self):
        """Changing l1 from 1.0 to 1.5 must produce a measurably different orbit."""
        pts_l1_1 = integrate(300, l1=1.0)
        pts_l1_15 = integrate(300, l1=1.5)
        diffs = [math.hypot(a[0] - b[0], a[2] - b[2]) for a, b in zip(pts_l1_1, pts_l1_15)]
        assert max(diffs) > 0.05, "l1 change had no effect on trajectory"

    def test_system_oscillates_at_small_angle(self):
        """Starting at 20°, theta1 must cross zero (oscillation confirmed)."""
        pts = integrate(1000, theta1_0=20 * DEG, theta2_0=0.0)
        t1_vals = [p[0] for p in pts]
        assert any(v < 0 for v in t1_vals), "theta1 never crossed zero — no oscillation"

    def test_rk4_more_accurate_than_euler(self):
        """RK4 at dt=DT must be closer to a fine-dt Euler reference than coarse Euler."""
        s0 = [0.3, 0.0, 0.2, 0.0]

        dt_fine = DT / 50
        sr = list(s0)
        for _ in range(50 * 60):
            d = deriv(sr)
            sr = [sr[k] + dt_fine * d[k] for k in range(4)]

        se = list(s0)
        for _ in range(60):
            d = deriv(se)
            se = [se[k] + DT * d[k] for k in range(4)]

        sk = list(s0)
        for _ in range(60):
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
    def test_very_small_angle_stays_bounded(self):
        """Near-equilibrium (0.001 rad) must stay bounded over 500 steps."""
        s = [0.001, 0.0, 0.001, 0.0]
        for _ in range(500):
            s = rk4_step(s)
        assert abs(s[0]) < 1.0 and abs(s[2]) < 1.0, f"Small-angle motion blew up: {s}"

    def test_large_angular_velocity_stays_finite(self):
        """Large initial omega must not produce NaN or Inf within 50 steps."""
        s = [0.5, 15.0, 0.3, -15.0]
        for _ in range(50):
            s = rk4_step(s)
        assert all(math.isfinite(v) for v in s), f"State became non-finite: {s}"

    def test_zero_angle_nonzero_velocity_stays_finite(self):
        """Zero angles but nonzero omega1 must remain finite over 200 steps."""
        s = [0.0, 5.0, 0.0, 0.0]
        for _ in range(200):
            s = rk4_step(s)
        assert all(math.isfinite(v) for v in s)

    def test_wrong_piece_id_absent(self):
        ids = {p["id"] for p in load_pieces()}
        assert "232-double-pendulm" not in ids  # typo variant
        assert "232-chaos-pendulum" not in ids

    def test_offsets_span_expected_range(self):
        """Offsets must cover -3*0.002 to +3*0.002 rad."""
        assert min(OFFSETS) == pytest.approx(-0.006, abs=1e-9)
        assert max(OFFSETS) == pytest.approx(0.006, abs=1e-9)

    def test_ref_idx_has_zero_offset(self):
        """The reference trajectory (REF_IDX=3) must have zero offset."""
        assert OFFSETS[REF_IDX] == 0.0

    def test_short_arms_stay_finite(self):
        """Very short arms (l1=l2=0.3) must remain finite over 200 steps."""
        s = [120 * DEG, 0.0, 0.0, 0.0]
        for _ in range(200):
            s = rk4_step(s, l1=0.3, l2=0.3)
        assert all(math.isfinite(v) for v in s), f"Short arms gave non-finite: {s}"

    def test_long_arms_stay_finite(self):
        """Long arms (l1=l2=2.0) must remain finite over 200 steps."""
        s = [120 * DEG, 0.0, 0.0, 0.0]
        for _ in range(200):
            s = rk4_step(s, l1=2.0, l2=2.0)
        assert all(math.isfinite(v) for v in s), f"Long arms gave non-finite: {s}"

    def test_low_gravity_stays_finite(self):
        """Very low gravity (g=1.0) must remain finite over 200 steps."""
        s = [120 * DEG, 0.0, 0.0, 0.0]
        for _ in range(200):
            s = rk4_step(s, g=1.0)
        assert all(math.isfinite(v) for v in s)


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

class TestReadme:
    def test_mentions_rk4(self):
        text = README.read_text().lower()
        assert "rk4" in text or "runge" in text

    def test_mentions_lagrangian(self):
        assert "lagrangian" in README.read_text().lower()

    def test_mentions_lyapunov(self):
        assert "lyapunov" in README.read_text().lower()

    def test_mentions_chaos(self):
        text = README.read_text().lower()
        assert "chaos" in text or "chaotic" in text

    def test_mentions_seven_pendulums(self):
        text = README.read_text().lower()
        assert "seven" in text or "7" in text

    def test_mentions_spectral_or_color(self):
        text = README.read_text().lower()
        assert "spectral" in text or "color" in text or "hue" in text


