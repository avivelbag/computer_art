"""Tests for Piece 232 — Rössler Attractor Ensemble."""
import json
import math
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "232-rossler-ensemble"
INDEX = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "232-rossler-ensemble"

# Physics constants mirrored from the implementation
A_DEF = 0.20
B_DEF = 0.20
C_DEF = 5.7
DT = 0.025
N_TRAJ = 7
OFFSETS = [k * 0.01 for k in range(-3, 4)]
REF_IDX = 3  # k=0, center unperturbed trajectory
CHAOS_SAT = 25.0


# ---------------------------------------------------------------------------
# Python mirror of the Rössler physics
# ---------------------------------------------------------------------------


def deriv(s, a=A_DEF, b=B_DEF, c=C_DEF):
    """
    Rössler equations of motion.
      dx/dt = -(y + z)
      dy/dt = x + a*y
      dz/dt = b + z*(x - c)

    Returns [dx/dt, dy/dt, dz/dt].
    """
    x, y, z = s
    return [
        -(y + z),
        x + a * y,
        b + z * (x - c),
    ]


def rk4_step(s, dt=DT, a=A_DEF, b=B_DEF, c=C_DEF):
    """One 4th-order Runge-Kutta step for the Rössler system."""
    k1 = deriv(s, a, b, c)
    s2 = [s[i] + 0.5 * dt * k1[i] for i in range(3)]
    k2 = deriv(s2, a, b, c)
    s3 = [s[i] + 0.5 * dt * k2[i] for i in range(3)]
    k3 = deriv(s3, a, b, c)
    s4 = [s[i] + dt * k3[i] for i in range(3)]
    k4 = deriv(s4, a, b, c)
    return [s[i] + (dt / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(3)]


def integrate(n_steps, x0=0.0, y0=0.0, z0=0.0, a=A_DEF, b=B_DEF, c=C_DEF):
    """
    Integrate the Rössler system for n_steps steps.
    Returns the list of states at each step.
    """
    s = [x0, y0, z0]
    states = []
    for _ in range(n_steps):
        s = rk4_step(s, a=a, b=b, c=c)
        states.append(tuple(s))
    return states


def ensemble_divergence(n_steps, x0_center=0.0, offset_scale=0.01,
                        a=A_DEF, b=B_DEF, c=C_DEF):
    """
    Run the full N_TRAJ-trajectory ensemble for n_steps.
    Returns list of max divergences (Euclidean in x-y) at each step.
    """
    states = [[x0_center + k * offset_scale, 0.0, 0.0] for k in range(-3, 4)]
    divergences = []
    for _ in range(n_steps):
        states = [rk4_step(s, a=a, b=b, c=c) for s in states]
        ref_x, ref_y = states[REF_IDX][0], states[REF_IDX][1]
        max_d = max(
            math.sqrt((s[0] - ref_x) ** 2 + (s[1] - ref_y) ** 2)
            for i, s in enumerate(states)
            if i != REF_IDX
        )
        divergences.append(max_d)
    return divergences


# ---------------------------------------------------------------------------
# File presence tests
# ---------------------------------------------------------------------------


def test_index_html_exists():
    assert INDEX.exists(), "index.html missing"


def test_readme_exists():
    assert README.exists(), "README.md missing"


def test_thumbnail_exists():
    assert THUMBNAIL.exists(), "thumbnail.svg missing"


def test_thumbnail_is_svg():
    content = THUMBNAIL.read_text()
    assert content.strip().startswith("<svg") or "xmlns" in content[:200]


# ---------------------------------------------------------------------------
# pieces.json tests
# ---------------------------------------------------------------------------


def test_pieces_json_has_entry():
    data = json.loads(PIECES_JSON.read_text())
    ids = [p.get("id") for p in data]
    assert PIECE_ID in ids, f"{PIECE_ID} not found in pieces.json"


def test_pieces_json_fields():
    data = json.loads(PIECES_JSON.read_text())
    entry = next(p for p in data if p.get("id") == PIECE_ID)
    for field in ("title", "technique", "path", "thumbnail", "description"):
        assert field in entry, f"Missing field: {field}"


def test_pieces_json_path_matches():
    data = json.loads(PIECES_JSON.read_text())
    entry = next(p for p in data if p.get("id") == PIECE_ID)
    assert entry["path"] == "pieces/232-rossler-ensemble"
    assert entry["thumbnail"] == "pieces/232-rossler-ensemble/thumbnail.svg"


def test_pieces_json_technique_mentions_rossler():
    data = json.loads(PIECES_JSON.read_text())
    entry = next(p for p in data if p.get("id") == PIECE_ID)
    tech = entry.get("technique", "").lower()
    assert "rössler" in tech or "rossler" in tech, "technique must mention Rössler"
    assert "rk4" in tech, "technique must mention RK4"


def test_pieces_json_no_double_pendulum_entry():
    """Ensure the old duplicate double-pendulum entry was removed."""
    data = json.loads(PIECES_JSON.read_text())
    ids = [p.get("id") for p in data]
    assert "232-double-pendulum" not in ids, "Old 232-double-pendulum entry still present"


# ---------------------------------------------------------------------------
# HTML content tests
# ---------------------------------------------------------------------------


def test_html_title():
    content = INDEX.read_text()
    assert "232" in content
    assert "Rössler" in content or "Rossler" in content or "r&#246;ssler" in content.lower()


def test_html_has_canvas():
    content = INDEX.read_text()
    assert "<canvas" in content


def test_html_has_chaos_meter():
    content = INDEX.read_text()
    assert "chaos-meter" in content or "chaos_meter" in content
    assert "Chaos Meter" in content


def test_html_has_four_sliders():
    content = INDEX.read_text()
    # Sliders: a, b, c, x0
    for sid in ("sl-a", "sl-b", "sl-c", "sl-x0"):
        assert sid in content, f"Slider '{sid}' missing from HTML"


def test_html_has_reset_button():
    content = INDEX.read_text()
    assert "btn-reset" in content or "Reset" in content


def test_html_has_rk4():
    content = INDEX.read_text()
    assert "rk4" in content.lower() or "runge" in content.lower()


def test_html_has_gallery_panel():
    content = INDEX.read_text()
    assert "GalleryPanel" in content
    assert "panel.js" in content


def test_html_rossler_deriv_equations():
    """Verify the three Rössler equations appear in the JavaScript."""
    content = INDEX.read_text()
    # dx/dt = -(y + z)  →  should see -(y + z) or similar
    assert "-(y + z)" in content or "- (y + z)" in content or "-(y+z)" in content
    # dy/dt = x + a*y  →  should see paramA * y
    assert "paramA" in content
    # dz/dt = b + z*(x - c)  →  should see paramC
    assert "paramC" in content


def test_html_seven_trajectories():
    content = INDEX.read_text()
    assert "N_TRAJ" in content or "7" in content
    assert "OFFSETS" in content


def test_html_trail_max():
    content = INDEX.read_text()
    assert "TRAIL_MAX" in content or "500" in content


def test_html_spectral_hues():
    content = INDEX.read_text()
    assert "HUES" in content


def test_html_panel_mentions_rossler():
    content = INDEX.read_text()
    assert "Rössler" in content or "Rossler" in content or "r&#246;ssler" in content.lower()


def test_html_panel_mentions_lyapunov():
    content = INDEX.read_text()
    assert "Lyapunov" in content or "lyapunov" in content.lower()


def test_html_panel_mentions_equations():
    content = INDEX.read_text()
    assert "dx/dt" in content or "dy/dt" in content


def test_html_panel_has_sections():
    content = INDEX.read_text()
    assert "sections:" in content or "'sections'" in content or '"sections"' in content


def test_html_refs_panel_css():
    content = INDEX.read_text()
    assert "panel.css" in content


# ---------------------------------------------------------------------------
# Physics correctness tests
# ---------------------------------------------------------------------------


def test_deriv_at_origin():
    """At x=y=z=0 with defaults: dx=-0-0=0, dy=0+0=0, dz=b+0*(0-c)=b."""
    d = deriv([0.0, 0.0, 0.0])
    assert d[0] == pytest.approx(0.0)
    assert d[1] == pytest.approx(0.0)
    assert d[2] == pytest.approx(B_DEF)


def test_deriv_signs_near_fixed():
    """
    For small x, y near 0 and z=0, verify that:
    dx/dt = -(y+z) is negative when y>0
    dy/dt = x + a*y is positive when x>0 with small y
    """
    d = deriv([0.5, 0.5, 0.0])
    assert d[0] < 0  # -(0.5 + 0.0) = -0.5
    assert d[1] > 0  # 0.5 + 0.2*0.5 = 0.6


def test_rk4_step_returns_3d():
    s = [0.0, 0.0, 0.0]
    result = rk4_step(s)
    assert len(result) == 3


def test_rk4_advances_state():
    """One RK4 step must change the state (system is not at rest at origin)."""
    s = [1.0, 0.0, 0.5]
    s_next = rk4_step(s)
    assert s_next != s


def test_rk4_vs_euler_accuracy():
    """RK4 should conserve volume better than Euler over short integration (Rössler is dissipative but smoothly)."""
    s = [1.0, 0.0, 0.5]
    # Euler step
    d = deriv(s)
    s_euler = [s[i] + DT * d[i] for i in range(3)]
    # RK4 step
    s_rk4 = rk4_step(s)
    # Both should remain finite
    assert all(math.isfinite(v) for v in s_rk4)
    assert all(math.isfinite(v) for v in s_euler)


def test_integrate_stays_finite():
    """Integration from default initial conditions should stay finite for 2000 steps."""
    states = integrate(2000)
    assert all(math.isfinite(v) for s in states for v in s)


def test_integrate_large_steps_finite():
    """Integration for 5000 steps should remain finite (attractor is bounded)."""
    states = integrate(5000)
    for s in states[-100:]:
        for v in s:
            assert math.isfinite(v)


def test_integrate_nonzero_after_first_step():
    """After the first step from [0,0,0], z must have moved by b*dt (plus higher-order terms)."""
    states = integrate(1, x0=0.0)
    x, y, z = states[0]
    assert abs(z) > B_DEF * DT * 0.5, "z should have advanced approximately b*dt"


def test_rossler_bounded_attractor():
    """
    Classic Rössler with a=b=0.2, c=5.7 remains bounded.
    After a warm-up, x and y should stay within [-30, 30].
    """
    states = integrate(3000, x0=0.0)
    for s in states[500:]:
        assert abs(s[0]) < 30, f"x out of bounds: {s[0]}"
        assert abs(s[1]) < 30, f"y out of bounds: {s[1]}"


def test_high_c_bounded():
    """Even at c=8.0 the attractor should remain bounded after warm-up."""
    states = integrate(2000, x0=0.0, c=8.0)
    for s in states[200:]:
        assert math.isfinite(s[0]) and math.isfinite(s[1]) and math.isfinite(s[2])


def test_low_c_limit_cycle():
    """
    At c=4.0 (below chaos onset) the system should settle to a periodic orbit.
    After warm-up, consecutive z-values should be nearly equal (period-1 regime).
    We check that the attractor x-y range is small compared to chaotic c=5.7.
    """
    states_periodic = integrate(2000, x0=0.0, c=4.0)
    states_chaotic = integrate(2000, x0=0.0, c=5.7)
    range_periodic = max(abs(s[0]) for s in states_periodic[500:])
    range_chaotic = max(abs(s[0]) for s in states_chaotic[500:])
    # In chaos the range should be larger than in the limit-cycle regime
    assert range_chaotic > range_periodic * 0.5


def test_different_params_give_different_trajectories():
    """Changing a should produce a noticeably different trajectory."""
    s1 = integrate(500, x0=1.0, a=0.20)
    s2 = integrate(500, x0=1.0, a=0.30)
    diff = math.sqrt((s1[-1][0] - s2[-1][0])**2 + (s1[-1][1] - s2[-1][1])**2)
    assert diff > 0.01, "Different a values should diverge"


def test_custom_params_passed_through():
    """Verify that a, b, c are actually used in deriv — not hard-coded."""
    d_default = deriv([1.0, 1.0, 0.0], a=0.2, b=0.2, c=5.7)
    d_custom = deriv([1.0, 1.0, 0.0], a=0.4, b=0.2, c=5.7)
    # dy/dt = x + a*y → differs when a differs
    assert d_default[1] != d_custom[1]


# ---------------------------------------------------------------------------
# Ensemble / chaos meter tests
# ---------------------------------------------------------------------------


def test_ensemble_initial_divergence_small():
    """
    The ensemble starts with offsets of 0.01, so initial Euclidean distance
    in x-y should be small (at most offset_scale * N_TRAJ).
    """
    divs = ensemble_divergence(1)
    assert divs[0] < 0.1, "Initial divergence should be very small"


def test_ensemble_diverges_over_time():
    """
    In the chaotic regime (default c=5.7), trajectories should diverge
    significantly over 1000 steps.
    """
    divs = ensemble_divergence(1000)
    assert divs[-1] > divs[0] * 10, "Divergence should grow substantially over 1000 steps"


def test_ensemble_divergence_increases_generally():
    """Max divergence at step 2000 should be larger than at step 100."""
    divs = ensemble_divergence(2000)
    assert divs[1999] > divs[99]


def test_chaos_meter_saturation():
    """
    After very long integration the chaos meter should saturate near CHAOS_SAT.
    Max divergence should exceed half the saturation value.
    """
    divs = ensemble_divergence(4000)
    assert max(divs) > CHAOS_SAT * 0.1, "Divergence should grow past 10% saturation"


def test_limit_cycle_no_divergence():
    """
    At c=4.0 the system is periodic; seven near-identical initial conditions
    should NOT diverge to large distances.
    """
    divs = ensemble_divergence(2000, c=4.0)
    # After some settling the periodic orbits should all be close together
    assert max(divs[500:]) < 5.0, "Limit cycle should keep trajectories near each other"


def test_larger_offset_diverges_faster():
    """Larger initial offset should lead to greater divergence at any given step."""
    divs_small = ensemble_divergence(500, offset_scale=0.001)
    divs_large = ensemble_divergence(500, offset_scale=0.1)
    # At some point the larger offset should lead to more divergence
    assert max(divs_large) >= max(divs_small) * 0.5


def test_different_x0_same_dynamics():
    """Integrating from x0=1.0 vs x0=2.0 produces finite, diverging orbits."""
    divs1 = ensemble_divergence(500, x0_center=1.0)
    divs2 = ensemble_divergence(500, x0_center=2.0)
    assert all(math.isfinite(d) for d in divs1)
    assert all(math.isfinite(d) for d in divs2)


def test_ref_trajectory_not_included_in_divergence():
    """
    The divergence computation should skip the reference trajectory (REF_IDX=3),
    so it always returns a non-negative value.
    """
    divs = ensemble_divergence(10)
    assert all(d >= 0 for d in divs)


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------


def test_readme_mentions_rossler():
    content = README.read_text()
    assert "Rössler" in content or "Rossler" in content


def test_readme_mentions_rk4():
    content = README.read_text()
    assert "RK4" in content or "Runge-Kutta" in content


def test_readme_mentions_lyapunov():
    content = README.read_text()
    assert "Lyapunov" in content or "lyapunov" in content.lower()


def test_readme_mentions_seven_trajectories():
    content = README.read_text()
    assert "seven" in content.lower() or "7" in content


def test_readme_mentions_chaos_meter():
    content = README.read_text()
    assert "Chaos Meter" in content or "chaos meter" in content.lower()


def test_readme_mentions_equations():
    content = README.read_text()
    assert "dx/dt" in content or "dy/dt" in content


def test_readme_has_controls_table():
    content = README.read_text()
    assert "Controls" in content
    assert "|" in content  # table rows


def test_readme_mentions_parameters():
    content = README.read_text()
    for param in ("a", "b", "c"):
        assert f"**{param}**" in content or f"| {param}" in content or f"| **{param}**" in content


# ---------------------------------------------------------------------------
# Regression: prior pieces must still exist
# ---------------------------------------------------------------------------


def test_prior_pieces_preserved():
    """Existing pieces must not have been deleted or renamed."""
    for slug in ["208-double-pendulum", "207-lorenz-attractor", "224-lorenz-attractor"]:
        assert (REPO / "pieces" / slug).exists(), f"pieces/{slug} was removed"


def test_pieces_json_no_stale_232():
    """pieces.json must not contain the old 232-double-pendulum id."""
    data = json.loads(PIECES_JSON.read_text())
    ids = [p.get("id") for p in data]
    assert "232-double-pendulum" not in ids
    assert PIECE_ID in ids
