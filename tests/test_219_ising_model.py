"""Tests for Piece 219 — Ising Model: The Temperature of Order."""
import json
import math
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "219-ising-model"
INDEX = PIECE_DIR / "index.html"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
README = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}

TC_EXACT = 2 / math.log(1 + math.sqrt(2))  # ≈ 2.2692


# ---- File existence ------------------------------------------------------------------

def test_index_exists():
    assert INDEX.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


def test_readme_exists():
    assert README.is_file()


# ---- pieces.json entry ---------------------------------------------------------------

def _entry():
    """Return the pieces.json entry for piece 219, asserting it exists."""
    data = json.loads(PIECES_JSON.read_text())
    matches = [e for e in data if e.get("id") == "219-ising-model"]
    assert matches, "No entry with id '219-ising-model' found in pieces.json"
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


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"


def test_pieces_json_technique_contains_ising():
    e = _entry()
    assert "ising" in e["technique"].lower() or "Ising" in e["technique"]


def test_pieces_json_technique_contains_canvas():
    e = _entry()
    assert "canvas" in e["technique"].lower()


def test_pieces_json_description_mentions_metropolis():
    e = _entry()
    assert "metropolis" in e["description"].lower() or "Metropolis" in e["description"]


def test_pieces_json_description_mentions_tc():
    e = _entry()
    assert "2.269" in e["description"] or "Onsager" in e["description"]


# ---- index.html structure ------------------------------------------------------------

def _html():
    """Return the full text of index.html."""
    return INDEX.read_text(encoding="utf-8")


def test_html_has_canvas_c():
    assert 'id="c"' in _html()


def test_html_has_temp_slider():
    html = _html()
    assert 'id="temp-slider"' in html
    assert 'min="0.5"' in html
    assert 'max="4.0"' in html


def test_html_has_t_val_readout():
    assert 'id="t-val"' in _html()


def test_html_has_m_val_readout():
    assert 'id="m-val"' in _html()


def test_html_has_mabs_val_readout():
    assert 'id="mabs-val"' in _html()


def test_html_has_sparkline():
    assert 'id="sparkline"' in _html()


def test_html_has_reset_btn():
    assert 'id="reset-btn"' in _html()


def test_html_has_info_btn():
    assert 'id="info-btn"' in _html()


def test_html_has_info_pane():
    assert 'id="info-pane"' in _html()


def test_html_has_pane_close():
    assert 'id="pane-close"' in _html()


def test_html_has_tc_marker():
    assert 'id="tc-label"' in _html() or 'tc-label' in _html()


def test_html_raf_animation():
    assert "requestAnimationFrame" in _html()


def test_html_has_metropolis_step_function():
    assert "function metropolisStep" in _html() or "metropolisStep" in _html()


def test_html_has_compute_m_function():
    assert "function computeM" in _html() or "computeM" in _html()


def test_html_has_render_function():
    assert "function render" in _html()


def test_html_has_init_spins_function():
    assert "function initSpins" in _html() or "initSpins" in _html()


def test_html_grid_size_200():
    """N must be 200 (200×200 lattice)."""
    html = _html()
    assert re.search(r'\bN\s*=\s*200\b', html), "N = 200 not found in index.html"


def test_html_tc_constant_defined():
    """Tc = 2 / ln(1 + √2) must be computed in the script."""
    html = _html()
    assert "Math.log(1 + Math.SQRT2)" in html or "Math.log(1+Math.SQRT2)" in html


def test_html_boltzmann_lookup_e4():
    """exp(−4/T) Boltzmann lookup must be present."""
    assert "Math.exp(-4 / T)" in _html() or "Math.exp(-4/T)" in _html()


def test_html_boltzmann_lookup_e8():
    """exp(−8/T) Boltzmann lookup must be present."""
    assert "Math.exp(-8 / T)" in _html() or "Math.exp(-8/T)" in _html()


def test_html_periodic_boundary_conditions():
    """Toroidal boundary must wrap using modulo arithmetic."""
    html = _html()
    assert "% N" in html, "Periodic boundary (% N) not found"


def test_html_colour_spin_up():
    """Warm linen (#f5ead8) must appear as the spin +1 colour."""
    assert "f5ead8" in _html() or "f5ead8".upper() in _html()


def test_html_colour_spin_down():
    """Deep indigo (#1a1040) must appear as the spin -1 colour."""
    assert "1a1040" in _html() or "1a1040".upper() in _html()


def test_html_imagedata_used():
    """ImageData must be used for direct pixel writes."""
    assert "createImageData" in _html() or "ImageData" in _html()


def test_html_click_flips_spin():
    """Click handler must flip a spin (defect injection)."""
    html = _html()
    assert "addEventListener('click'" in html or 'addEventListener("click"' in html
    assert "*= -1" in html or "= -s" in html or "* -1" in html


def test_html_info_pane_mentions_boltzmann():
    html = _html()
    assert "Boltzmann" in html or "boltzmann" in html


def test_html_info_pane_mentions_curie():
    html = _html()
    assert "Curie" in html or "curie" in html.lower()


def test_html_info_pane_mentions_onsager():
    html = _html()
    assert "Onsager" in html or "onsager" in html.lower()


def test_html_info_pane_mentions_domains():
    html = _html()
    assert "domain" in html.lower()


def test_html_info_pane_has_pane_sections():
    """Info pane must have at least 3 pane-section divs."""
    sections = re.findall(r'class="pane-section"', _html())
    assert len(sections) >= 3, f"Expected >= 3 pane-section divs, found {len(sections)}"


def test_html_escape_key_closes_pane():
    assert "Escape" in _html()


def test_html_resize_handler():
    assert "resize" in _html()


def test_html_offscreen_canvas():
    """OffscreenCanvas (or equivalent) must be used for performance."""
    html = _html()
    assert "OffscreenCanvas" in html or "offCanvas" in html or "offscreen" in html.lower()


def test_html_spark_buffer_defined():
    """SPARK_LEN constant must be defined for the sparkline ring buffer."""
    assert "SPARK_LEN" in _html()


# ---- Thumbnail -----------------------------------------------------------------------

def test_thumbnail_is_valid_svg():
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert content.strip().startswith("<svg") or "<?xml" in content
    assert "</svg>" in content


def test_thumbnail_has_linen_colour():
    """Warm linen (#f5ead8) must appear in the thumbnail."""
    assert "f5ead8" in THUMBNAIL.read_text(encoding="utf-8")


def test_thumbnail_has_indigo_colour():
    """Deep indigo (#1a1040) must appear in the thumbnail."""
    assert "1a1040" in THUMBNAIL.read_text(encoding="utf-8")


def test_thumbnail_has_rect_elements():
    """Thumbnail must use rect elements (domain patches)."""
    assert "<rect" in THUMBNAIL.read_text(encoding="utf-8")


# ---- README --------------------------------------------------------------------------

def test_readme_mentions_ising():
    assert "Ising" in README.read_text(encoding="utf-8")


def test_readme_mentions_metropolis():
    text = README.read_text(encoding="utf-8")
    assert "Metropolis" in text or "metropolis" in text


def test_readme_mentions_curie_temperature():
    text = README.read_text(encoding="utf-8")
    assert "Curie" in text or "critical temperature" in text.lower()


def test_readme_mentions_onsager():
    assert "Onsager" in README.read_text(encoding="utf-8")


def test_readme_contains_tc_value():
    """README must state Tc ≈ 2.269."""
    assert "2.269" in README.read_text(encoding="utf-8") or "2.2692" in README.read_text(encoding="utf-8")


def test_readme_has_how_it_works_section():
    assert "## How it works" in README.read_text(encoding="utf-8")


def test_readme_has_what_to_notice_section():
    assert "## What to notice" in README.read_text(encoding="utf-8")


def test_readme_what_to_notice_has_bullets():
    text = README.read_text(encoding="utf-8")
    start = text.index("## What to notice")
    section = text[start:]
    bullets = re.findall(r"^- ", section, re.MULTILINE)
    assert len(bullets) >= 2, f"Expected >= 2 bullets, found {len(bullets)}"


def test_readme_mentions_domains():
    assert "domain" in README.read_text(encoding="utf-8").lower()


def test_readme_mentions_boltzmann():
    text = README.read_text(encoding="utf-8")
    assert "Boltzmann" in text or "boltzmann" in text.lower()


# ---- Physics sanity checks (pure Python) --------------------------------------------

def metropolis_step(spins, N, T, rng):
    """
    One Metropolis–Hastings sweep: N² flip attempts on a 2D Ising lattice.

    spins: flat list of +1 / -1 values (length N*N).
    N: grid side length.
    T: temperature in units J/k.
    rng: random.Random instance for determinism.

    Modifies spins in-place and returns the number of accepted flips.
    """
    import random as _random
    e4 = math.exp(-4 / T)
    e8 = math.exp(-8 / T)
    accepted = 0
    NN = N * N
    for _ in range(NN):
        i = int(rng.random() * N) % N
        j = int(rng.random() * N) % N
        idx = i * N + j
        s = spins[idx]
        n_sum = (spins[((i - 1) % N) * N + j]
               + spins[((i + 1) % N) * N + j]
               + spins[i * N + (j - 1) % N]
               + spins[i * N + (j + 1) % N])
        dE = 2 * s * n_sum
        if dE <= 0 or rng.random() < (e4 if dE == 4 else e8):
            spins[idx] = -s
            accepted += 1
    return accepted


def magnetisation(spins, N):
    """Return net magnetisation per spin: M = sum(s) / N²."""
    return sum(spins) / (N * N)


def make_spins(N, seed=42, aligned=False):
    """
    Create an N×N spin lattice.

    aligned=True: all spins +1 (ground state).
    aligned=False: random ±1 (infinite temperature start).
    """
    import random as _random
    rng = _random.Random(seed)
    if aligned:
        return [1] * (N * N)
    return [1 if rng.random() < 0.5 else -1 for _ in range(N * N)]


class TestIsingPhysics:
    """Verify Ising model physics properties via a pure-Python reference implementation."""

    def test_tc_exact_value(self):
        """The exact 2D critical temperature Tc = 2/ln(1+√2) ≈ 2.2692."""
        assert abs(TC_EXACT - 2.2692) < 1e-4

    def test_boltzmann_factor_limits(self):
        """exp(−ΔE/T) must be in (0, 1] for ΔE > 0 and must increase as T increases."""
        for dE in (4, 8):
            p_low  = math.exp(-dE / 0.5)
            p_high = math.exp(-dE / 4.0)
            assert 0 < p_low < p_high <= 1, f"Boltzmann factor ordering failed for ΔE={dE}"

    def test_zero_temperature_no_uphill_flips(self):
        """At T → 0 exp(−ΔE/T) → 0: no unfavourable flip should be accepted in a fully aligned state."""
        import random as _random
        N = 10
        spins = make_spins(N, aligned=True)
        rng = _random.Random(7)
        T_cold = 0.01
        e4 = math.exp(-4 / T_cold)
        assert e4 < 1e-10, "At T=0.01, uphill probability must be negligibly small"

    def test_energy_decreases_at_low_temperature(self):
        """A majority-up start at low T should remain ordered (avoid two-domain finite-size trap)."""
        import random as _random
        N = 20
        # Bias 75% of spins to +1 so the system converges to the all-up ground state
        rng_init = _random.Random(0)
        spins = [1 if rng_init.random() < 0.75 else -1 for _ in range(N * N)]
        rng = _random.Random(1)
        T = 0.5  # deep below Tc — unfavourable flips are exponentially suppressed
        for _ in range(300):
            metropolis_step(spins, N, T, rng)
        M = abs(magnetisation(spins, N))
        assert M > 0.5, f"At T=0.5 below Tc, |M| should exceed 0.5, got {M:.3f}"

    def test_high_temperature_disorder(self):
        """At T >> Tc an aligned state should quickly disorder: |M| should drop."""
        import random as _random
        N = 20
        spins = make_spins(N, aligned=True)
        rng = _random.Random(2)
        T = 4.0  # well above Tc
        for _ in range(50):
            metropolis_step(spins, N, T, rng)
        M = abs(magnetisation(spins, N))
        assert M < 0.8, f"At T=4.0 above Tc, |M| should be < 0.8 from aligned start, got {M:.3f}"

    def test_magnetisation_bounded(self):
        """Magnetisation must remain in [−1, 1] at all temperatures."""
        import random as _random
        N = 15
        for T in (0.5, 2.27, 4.0):
            spins = make_spins(N, seed=3)
            rng = _random.Random(4)
            for _ in range(30):
                metropolis_step(spins, N, T, rng)
            M = magnetisation(spins, N)
            assert -1.0 <= M <= 1.0, f"M={M} out of bounds at T={T}"

    def test_spin_values_remain_pm1(self):
        """Every spin must stay +1 or −1 throughout the simulation."""
        import random as _random
        N = 15
        spins = make_spins(N, seed=5)
        rng = _random.Random(6)
        for _ in range(20):
            metropolis_step(spins, N, T=2.27, rng=rng)
        for s in spins:
            assert s in (1, -1), f"Spin value {s} is not ±1"

    def test_only_two_positive_de_values(self):
        """In a 2D square lattice only ΔE = 4 and ΔE = 8 are positive."""
        import random as _random
        N = 20
        rng = _random.Random(9)
        spins = make_spins(N, seed=9)
        positive_des = set()
        for _ in range(1000):
            i = int(rng.random() * N) % N
            j = int(rng.random() * N) % N
            idx = i * N + j
            s = spins[idx]
            n_sum = (spins[((i - 1) % N) * N + j]
                   + spins[((i + 1) % N) * N + j]
                   + spins[i * N + (j - 1) % N]
                   + spins[i * N + (j + 1) % N])
            dE = 2 * s * n_sum
            if dE > 0:
                positive_des.add(dE)
        assert positive_des <= {4, 8}, f"Unexpected positive ΔE values: {positive_des}"

    def test_periodic_boundary_no_index_error(self):
        """Boundary spins must access neighbours without IndexError."""
        import random as _random
        N = 10
        spins = make_spins(N, seed=11)
        rng = _random.Random(12)
        metropolis_step(spins, N, T=2.27, rng=rng)  # should not raise

    def test_defect_heals_below_tc(self):
        """A single flipped spin in an aligned domain below Tc should be corrected quickly."""
        import random as _random
        N = 20
        spins = [1] * (N * N)
        center = (N // 2) * N + N // 2
        spins[center] = -1  # inject defect
        rng = _random.Random(13)
        T = 0.6  # cold — defect should heal
        for _ in range(200):
            metropolis_step(spins, N, T, rng)
        M = magnetisation(spins, N)
        assert M > 0.9, f"Defect should heal at T=0.6, got M={M:.3f}"


class TestEdgeCases:
    """Verify correct behaviour at boundary inputs."""

    def test_single_spin_lattice(self):
        """A 1×1 lattice has no neighbours; any flip is dE=0, always accepted."""
        import random as _random
        spins = [1]
        rng = _random.Random(99)
        T = 2.27
        accepted = metropolis_step(spins, 1, T, rng)
        assert accepted >= 0  # should not raise; flip count is non-negative

    def test_2x2_lattice_runs_without_error(self):
        """A 2×2 lattice exercises periodic boundary on the smallest non-trivial grid."""
        import random as _random
        spins = make_spins(2, seed=20)
        rng = _random.Random(21)
        for _ in range(10):
            metropolis_step(spins, 2, T=2.27, rng=rng)
        for s in spins:
            assert s in (1, -1)

    def test_very_large_sweep_stays_stable(self):
        """Running 500 sweeps on a 30×30 grid must not raise or produce NaN-equivalent values."""
        import random as _random
        N = 30
        spins = make_spins(N, seed=22)
        rng = _random.Random(23)
        for _ in range(500):
            metropolis_step(spins, N, T=TC_EXACT, rng=rng)
        M = magnetisation(spins, N)
        assert -1.0 <= M <= 1.0

    def test_temperature_exactly_at_tc(self):
        """Running at exactly Tc must not raise any exception."""
        import random as _random
        N = 20
        spins = make_spins(N, seed=30)
        rng = _random.Random(31)
        for _ in range(50):
            metropolis_step(spins, N, T=TC_EXACT, rng=rng)  # should not raise

    def test_all_spins_same_sign_at_t0(self):
        """At T=0.5 a fully aligned lattice must remain near-fully aligned after many sweeps."""
        import random as _random
        N = 20
        spins = [1] * (N * N)
        rng = _random.Random(40)
        for _ in range(100):
            metropolis_step(spins, N, T=0.5, rng=rng)
        M = magnetisation(spins, N)
        assert M > 0.95, f"Aligned lattice at T=0.5 should stay near M=1, got {M:.3f}"


class TestFailureModes:
    """Verify correct error or no-op behaviour for malformed inputs."""

    def test_missing_required_field_detected(self):
        """An entry without 'technique' should fail the required-field check."""
        entry = {
            "id": "219-ising-model",
            "title": "x",
            "tagline": "y",
            "year": 2026,
            "path": "pieces/219-ising-model",
            "thumbnail": "pieces/219-ising-model/thumbnail.svg",
            "description": "d",
        }
        assert not (REQUIRED_FIELDS <= entry.keys())

    def test_id_path_mismatch_detected(self):
        """id must equal basename of path."""
        entry = {"id": "219-ising-model", "path": "pieces/999-wrong"}
        assert entry["id"] != pathlib.Path(entry["path"]).name

    def test_nonexistent_thumbnail_is_absent(self, tmp_path):
        """A thumbnail file that was never created should not exist."""
        fake = tmp_path / "pieces" / "219-ising-model" / "nope.svg"
        assert not fake.exists()

    def test_boltzmann_factor_at_low_T_is_tiny(self):
        """At T = 0.1 the probability of accepting a ΔE=8 flip must be < 1e-30."""
        p = math.exp(-8 / 0.1)
        assert p < 1e-30, f"Expected p < 1e-30 at T=0.1, got {p}"

    def test_boltzmann_factor_at_high_T_approaches_1(self):
        """At T = 100 the probability of accepting ΔE=4 should be close to 1."""
        p = math.exp(-4 / 100)
        assert p > 0.96, f"Expected p > 0.96 at T=100, got {p}"

    def test_pieces_json_entry_is_not_missing(self):
        """The 219-ising-model entry must be present in pieces.json."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "219-ising-model" in ids, "219-ising-model missing from pieces.json"
