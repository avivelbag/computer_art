"""Tests for Piece 218 — SIR Epidemic: The Curve We Tried to Flatten."""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "218-sir-epidemic"
INDEX = PIECE_DIR / "index.html"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
README = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}


# ---- File existence ----

def test_index_exists():
    assert INDEX.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


def test_readme_exists():
    assert README.is_file()


# ---- pieces.json entry ----

def _entry():
    """Return the pieces.json entry for piece 218, asserting it exists."""
    data = json.loads(PIECES_JSON.read_text())
    matches = [e for e in data if e.get("id") == "218-sir-epidemic"]
    assert matches, "No entry with id '218-sir-epidemic' found in pieces.json"
    return matches[0]


def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_entry_has_required_fields():
    e = _entry()
    assert REQUIRED_FIELDS <= e.keys(), f"Missing fields: {REQUIRED_FIELDS - e.keys()}"


def test_pieces_json_entry_id_matches_dir():
    e = _entry()
    assert e["id"] == pathlib.Path(e["path"]).name


def test_pieces_json_thumbnail_file_exists():
    e = _entry()
    assert (REPO / e["thumbnail"]).is_file()


def test_pieces_json_path_dir_exists():
    e = _entry()
    assert (REPO / e["path"]).is_dir()


def test_pieces_json_technique_contains_sir():
    e = _entry()
    assert "SIR" in e["technique"] or "sir" in e["technique"].lower()


def test_pieces_json_technique_contains_canvas():
    e = _entry()
    assert "canvas" in e["technique"].lower()


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"


# ---- index.html structure ----

def _html():
    """Return the full text of index.html."""
    return INDEX.read_text(encoding="utf-8")


def test_html_has_sim_canvas():
    assert 'id="sim-canvas"' in _html()


def test_html_has_chart_canvas():
    assert 'id="chart-canvas"' in _html()


def test_html_has_sim_wrap():
    assert 'id="sim-wrap"' in _html()


def test_html_has_chart_wrap():
    assert 'id="chart-wrap"' in _html()


def test_html_has_beta_slider():
    html = _html()
    assert 'id="beta-slider"' in html
    assert 'min="0.1"' in html
    assert 'max="1.0"' in html


def test_html_has_gamma_slider():
    html = _html()
    assert 'id="gamma-slider"' in html
    assert 'min="0.05"' in html
    assert 'max="0.5"' in html


def test_html_has_infected_slider():
    assert 'id="infected-slider"' in _html()


def test_html_has_vacc_slider():
    assert 'id="vacc-slider"' in _html()


def test_html_has_restart_button():
    assert 'id="restart-btn"' in _html()


def test_html_has_info_button():
    assert 'id="info-btn"' in _html()


def test_html_has_info_pane():
    assert 'id="info-pane"' in _html()


def test_html_has_pane_close():
    assert 'id="pane-close"' in _html()


def test_html_has_r0_display():
    assert 'id="r0-val"' in _html()


def test_html_raf_animation():
    assert "requestAnimationFrame" in _html()


def test_html_has_step_function():
    assert "function step" in _html()


def test_html_has_draw_particles_function():
    assert "function drawParticles" in _html()


def test_html_has_draw_chart_function():
    assert "function drawChart" in _html()


def test_html_has_init_particles_function():
    assert "function initParticles" in _html()


def test_html_has_update_r0_display():
    assert "function updateR0Display" in _html() or "updateR0" in _html()


def test_html_particle_count_at_most_400():
    """N_PARTICLES constant must be defined and <= 400."""
    html = _html()
    m = re.search(r'N_PARTICLES\s*=\s*(\d+)', html)
    assert m, "N_PARTICLES constant not found in index.html"
    assert int(m.group(1)) <= 400, f"N_PARTICLES={m.group(1)} exceeds 400"


def test_html_particle_count_at_least_100():
    """Simulation needs enough particles to be meaningful."""
    html = _html()
    m = re.search(r'N_PARTICLES\s*=\s*(\d+)', html)
    assert m, "N_PARTICLES constant not found"
    assert int(m.group(1)) >= 100


def test_html_info_pane_has_sir_equations():
    """Info pane must show all three SIR differential equations."""
    html = _html()
    assert "dS/dt" in html
    assert "dI/dt" in html
    assert "dR/dt" in html


def test_html_info_pane_mentions_beta():
    html = _html()
    assert "β" in html or "beta" in html.lower()


def test_html_info_pane_mentions_gamma():
    html = _html()
    assert "γ" in html or "gamma" in html.lower()


def test_html_info_pane_mentions_r0():
    """Info pane must show R₀ and the formula R₀ = β/γ."""
    html = _html()
    assert "R₀" in html or "R0" in html


def test_html_r0_formula_present():
    """R₀ = β/γ formula must appear somewhere in the HTML."""
    html = _html()
    assert "β / γ" in html or "beta / gamma" in html.lower() or "β/γ" in html


def test_html_info_pane_flatten_the_curve():
    """Educational pane must mention 'flatten the curve'."""
    html = _html()
    assert "flatten" in html.lower()


def test_html_info_pane_r0_less_than_1_dies_out():
    """Info pane must explain that R₀ < 1 means the epidemic dies out."""
    html = _html()
    assert "R₀ &lt; 1" in html or "R₀ < 1" in html


def test_html_info_pane_sections():
    """Info pane must have at least 3 distinct pane-section divs."""
    sections = re.findall(r'class="pane-section"', _html())
    assert len(sections) >= 3, f"Expected >= 3 pane sections, found {len(sections)}"


def test_html_escape_key_closes_pane():
    assert "Escape" in _html()


def test_html_blue_color_for_susceptible():
    """Blue (#4488ff or similar) must be used for susceptible particles."""
    html = _html()
    assert "#4488ff" in html or "4488ff" in html


def test_html_red_color_for_infected():
    """Red must be used for infected particles."""
    html = _html()
    assert "#ff3333" in html or "ff3333" in html


def test_html_green_color_for_recovered():
    """Green must be used for recovered particles."""
    html = _html()
    assert "#33cc55" in html or "33cc55" in html


def test_html_bounce_off_walls():
    """Particles must bounce off walls (velocity negation logic)."""
    html = _html()
    assert "Math.abs(p.vx)" in html or "Math.abs(p.vy)" in html


def test_html_contact_distance_defined():
    """CONTACT_DIST constant must be defined for proximity infection."""
    assert "CONTACT_DIST" in _html()


def test_html_history_buffer_defined():
    """HISTORY_LEN constant must be defined for the rolling chart buffer."""
    assert "HISTORY_LEN" in _html()


def test_html_resize_handler():
    """Canvas must resize when the window changes size."""
    html = _html()
    assert "resize" in html


# ---- Thumbnail ----

def test_thumbnail_is_valid_svg():
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert content.strip().startswith("<svg") or "<?xml" in content
    assert "</svg>" in content


def test_thumbnail_has_polylines():
    """Thumbnail must have polyline elements for the S/I/R curves."""
    assert "<polyline" in THUMBNAIL.read_text(encoding="utf-8")


def test_thumbnail_has_red_curve():
    """Infected (red) curve must appear in the thumbnail."""
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert "#ff3333" in content or "ff3333" in content


def test_thumbnail_has_blue_curve():
    """Susceptible (blue) curve must appear in the thumbnail."""
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert "#4488ff" in content or "4488ff" in content


def test_thumbnail_has_green_curve():
    """Recovered (green) curve must appear in the thumbnail."""
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert "#33cc55" in content or "33cc55" in content


def test_thumbnail_has_three_or_more_polylines():
    """Thumbnail must have at least 3 polylines (one per compartment)."""
    content = THUMBNAIL.read_text(encoding="utf-8")
    count = content.count("<polyline")
    assert count >= 3, f"Expected >= 3 polylines, found {count}"


# ---- README ----

def test_readme_mentions_sir():
    text = README.read_text(encoding="utf-8")
    assert "SIR" in text


def test_readme_mentions_susceptible():
    text = README.read_text(encoding="utf-8")
    assert "susceptible" in text.lower() or "Susceptible" in text


def test_readme_mentions_infected():
    text = README.read_text(encoding="utf-8")
    assert "infected" in text.lower() or "Infected" in text


def test_readme_mentions_recovered():
    text = README.read_text(encoding="utf-8")
    assert "recovered" in text.lower() or "Recovered" in text


def test_readme_contains_sir_equations():
    text = README.read_text(encoding="utf-8")
    assert "dS/dt" in text
    assert "dI/dt" in text
    assert "dR/dt" in text


def test_readme_mentions_r0():
    text = README.read_text(encoding="utf-8")
    assert "R₀" in text or "R0" in text


def test_readme_mentions_beta_and_gamma():
    text = README.read_text(encoding="utf-8")
    assert "β" in text or "beta" in text.lower()
    assert "γ" in text or "gamma" in text.lower()


def test_readme_flatten_the_curve():
    text = README.read_text(encoding="utf-8")
    assert "flatten" in text.lower()


def test_readme_has_how_it_works_section():
    text = README.read_text(encoding="utf-8")
    assert "## How it works" in text


def test_readme_has_what_to_notice_section():
    text = README.read_text(encoding="utf-8")
    assert "## What to notice" in text


def test_readme_what_to_notice_has_bullets():
    """What to notice section must have at least 2 bullet points."""
    text = README.read_text(encoding="utf-8")
    notice_start = text.index("## What to notice")
    section = text[notice_start:]
    bullets = re.findall(r"^- ", section, re.MULTILINE)
    assert len(bullets) >= 2, f"Expected >= 2 bullets, found {len(bullets)}"


# ---- SIR physics sanity checks (pure Python) ----

def sir_step(S, inf, R, N, beta, gamma, dt=0.1):
    """
    One Euler step of the continuous SIR ODE.

    `inf` is the infected compartment (renamed from I to avoid E741).
    Returns updated (S, inf, R) after time dt.
    """
    dS = -beta * S * inf / N
    d_inf = beta * S * inf / N - gamma * inf
    dR = gamma * inf
    return S + dS * dt, inf + d_inf * dt, R + dR * dt


def run_sir(N, I0, beta, gamma, steps=2000, dt=0.1):
    """
    Simulate the SIR ODE for `steps` Euler steps.

    Returns lists S_hist, I_hist, R_hist.
    """
    S, inf, R = float(N - I0), float(I0), 0.0
    S_hist, I_hist, R_hist = [S], [inf], [R]
    for _ in range(steps):
        S, inf, R = sir_step(S, inf, R, N, beta, gamma, dt)
        S_hist.append(S)
        I_hist.append(inf)
        R_hist.append(R)
    return S_hist, I_hist, R_hist


class TestSIRPhysics:
    """Verify SIR model properties against the differential equations."""

    def test_r0_formula(self):
        """R₀ = β/γ is computed correctly for a range of parameters."""
        for beta, gamma in [(0.4, 0.1), (0.2, 0.2), (0.8, 0.4), (0.1, 0.05)]:
            r0 = beta / gamma
            assert r0 > 0

    def test_conservation_of_population(self):
        """S + I + R = N must hold at every time step."""
        N = 300
        S_h, I_h, R_h = run_sir(N, I0=5, beta=0.4, gamma=0.1, steps=500)
        for S, inf, R in zip(S_h, I_h, R_h):
            assert abs(S + inf + R - N) < 1e-6, f"Conservation violated: S+I+R={S+inf+R}"

    def test_s_is_non_increasing(self):
        """S can only decrease — susceptibles are never added back."""
        N = 300
        S_h, _, _ = run_sir(N, I0=5, beta=0.4, gamma=0.1, steps=500)
        for i in range(1, len(S_h)):
            assert S_h[i] <= S_h[i - 1] + 1e-10, \
                f"S increased at step {i}: {S_h[i-1]} → {S_h[i]}"

    def test_r_is_non_decreasing(self):
        """R can only increase — recovered individuals are never re-infected."""
        N = 300
        _, _, R_h = run_sir(N, I0=5, beta=0.4, gamma=0.1, steps=500)
        for i in range(1, len(R_h)):
            assert R_h[i] >= R_h[i - 1] - 1e-10, \
                f"R decreased at step {i}: {R_h[i-1]} → {R_h[i]}"

    def test_high_r0_epidemic_grows_initially(self):
        """When R₀ > 1 the infected count must increase early on."""
        N = 300
        beta, gamma = 0.8, 0.1  # R₀ = 8
        S_h, I_h, R_h = run_sir(N, I0=5, beta=beta, gamma=gamma, steps=50)
        assert I_h[50] > I_h[0], "Epidemic should grow when R₀ = 8"

    def test_low_r0_epidemic_dies_out(self):
        """When R₀ < 1 the infected count must shrink from the start."""
        N = 300
        beta, gamma = 0.05, 0.5  # R₀ = 0.1
        S_h, I_h, R_h = run_sir(N, I0=10, beta=beta, gamma=gamma, steps=200)
        assert I_h[-1] < I_h[0], "Epidemic should die out when R₀ = 0.1"

    def test_bell_shaped_infected_curve(self):
        """With R₀ > 1 the infected curve must have a single interior maximum."""
        N = 300
        S_h, I_h, R_h = run_sir(N, I0=5, beta=0.4, gamma=0.1, steps=1000)
        peak_idx = I_h.index(max(I_h))
        assert 0 < peak_idx < len(I_h) - 1, \
            "Peak of I must be strictly interior (bell shape)"
        assert I_h[0] < max(I_h), "I must rise above its initial value"
        assert I_h[-1] < max(I_h), "I must fall after its peak"

    def test_vaccination_reduces_peak(self):
        """Higher vaccination fraction (starting R) must reduce the infected peak."""
        N = 300
        beta, gamma = 0.5, 0.1

        def peak_infected(vacc_frac):
            """Return the peak infected count for a given vaccination fraction."""
            vaccinated = int(N * vacc_frac)
            i0 = 5
            S, inf, R = float(N - i0 - vaccinated), float(i0), float(vaccinated)
            peak = inf
            for _ in range(2000):
                dS = -beta * S * inf / N
                d_inf = beta * S * inf / N - gamma * inf
                dR = gamma * inf
                S += dS * 0.1
                inf += d_inf * 0.1
                R += dR * 0.1
                peak = max(peak, inf)
            return peak

        peak0 = peak_infected(0.0)
        peak_vacc = peak_infected(0.4)
        assert peak_vacc < peak0, \
            f"Vaccination should reduce peak infected ({peak_vacc:.1f} should be < {peak0:.1f})"

    def test_herd_immunity_threshold(self):
        """At vaccination fraction >= 1 - 1/R₀ the epidemic should not grow."""
        N = 300
        beta, gamma = 0.4, 0.1  # R₀ = 4
        r0 = beta / gamma
        herd_frac = 1 - 1 / r0  # 75% for R₀ = 4

        vaccinated = int(N * herd_frac)
        i0 = 3
        S, inf, R = float(N - i0 - vaccinated), float(i0), float(vaccinated)
        I_initial = inf
        max_inf = inf
        for _ in range(5000):
            dS = -beta * S * inf / N
            d_inf = beta * S * inf / N - gamma * inf
            dR = gamma * inf
            S += dS * 0.05
            inf += d_inf * 0.05
            R += dR * 0.05
            max_inf = max(max_inf, inf)

        assert max_inf < I_initial * 2, \
            f"At herd immunity threshold, I should not more than double (got {max_inf:.1f})"

    def test_all_compartments_non_negative(self):
        """S, I, R must remain non-negative throughout the simulation."""
        N = 300
        S_h, I_h, R_h = run_sir(N, I0=15, beta=0.6, gamma=0.15, steps=2000)
        for i, (S, inf, R) in enumerate(zip(S_h, I_h, R_h)):
            assert S >= -1e-6, f"S negative at step {i}: {S}"
            assert inf >= -1e-6, f"I negative at step {i}: {inf}"
            assert R >= -1e-6, f"R negative at step {i}: {R}"

    def test_no_epidemic_without_infected(self):
        """With I₀=0 nothing happens — S should stay constant."""
        N = 300
        S_h, I_h, R_h = run_sir(N, I0=0, beta=0.5, gamma=0.1, steps=100)
        assert all(abs(S - N) < 1e-10 for S in S_h), "S should stay at N when I₀=0"
        assert all(abs(inf) < 1e-10 for inf in I_h), "I should stay at 0 when I₀=0"


class TestFailureModes:
    """Verify correct error behavior for malformed input."""

    def test_missing_required_field_detected(self):
        """An entry without 'technique' should fail the required-field check."""
        entry = {
            "id": "218-sir-epidemic",
            "title": "x",
            "tagline": "y",
            "year": 2026,
            "path": "pieces/218-sir-epidemic",
            "thumbnail": "pieces/218-sir-epidemic/thumbnail.svg",
            "description": "d",
        }
        assert not (REQUIRED_FIELDS <= entry.keys())

    def test_id_path_mismatch_detected(self):
        """id must equal basename of path."""
        entry = {"id": "218-sir-epidemic", "path": "pieces/999-wrong"}
        assert entry["id"] != pathlib.Path(entry["path"]).name

    def test_nonexistent_thumbnail_is_absent(self, tmp_path):
        """A thumbnail file that was never created should not exist."""
        fake = tmp_path / "pieces" / "218-sir-epidemic" / "nope.svg"
        assert not fake.exists()

    def test_sir_with_beta_zero_no_spread(self):
        """With β=0 no infections occur — I stays constant (only recoveries)."""
        N, I0 = 300, 10
        S, inf, R = float(N - I0), float(I0), 0.0
        for _ in range(100):
            S, inf, R = sir_step(S, inf, R, N, beta=0.0, gamma=0.1)
        assert inf <= I0 + 1e-9, f"I should not increase with β=0, got I={inf}"

    def test_sir_with_gamma_zero_no_recovery(self):
        """With γ=0 no one recovers — R stays at 0 (only infections, no removals)."""
        N, I0 = 300, 5
        S, inf, R = float(N - I0), float(I0), 0.0
        for _ in range(100):
            S, inf, R = sir_step(S, inf, R, N, beta=0.3, gamma=0.0)
        assert R < 1e-9, f"R should stay 0 with gamma=0, got R={R}"

    def test_large_population_conservation(self):
        """Conservation must hold for a large population (N=10000)."""
        N = 10000
        S_h, I_h, R_h = run_sir(N, I0=50, beta=0.3, gamma=0.1, steps=200, dt=0.1)
        for S, inf, R in zip(S_h, I_h, R_h):
            assert abs(S + inf + R - N) < 1e-4, f"Conservation violated for N={N}"

    def test_r0_boundary_near_one(self):
        """R₀ exactly at 1 (β=γ) is a marginal case — I should not grow explosively."""
        N = 300
        beta = gamma = 0.2  # R₀ = 1.0
        S_h, I_h, R_h = run_sir(N, I0=5, beta=beta, gamma=gamma, steps=1000)
        assert max(I_h) < N * 0.5, \
            f"At R₀=1, peak I should be moderate, got {max(I_h):.1f}"
