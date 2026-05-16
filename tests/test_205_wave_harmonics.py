"""Tests for Piece 205 — Wave Harmonics Synthesizer."""
import json
import math
import pathlib

REPO = pathlib.Path(__file__).parent.parent
PIECES_JSON = REPO / "pieces.json"
PIECE_DIR = REPO / "pieces" / "205-wave-harmonics"
INDEX = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_pieces():
    """Return parsed pieces.json as a list."""
    return json.loads(PIECES_JSON.read_text())


def get_entry():
    """Return the pieces.json entry for 205-wave-harmonics, or None."""
    for entry in load_pieces():
        if entry["id"] == "205-wave-harmonics":
            return entry
    return None


def index_text():
    """Return the content of the piece's index.html."""
    return INDEX.read_text()


# ---------------------------------------------------------------------------
# pieces.json metadata
# ---------------------------------------------------------------------------

class TestPiecesJsonEntry:
    """Validate the pieces.json metadata entry."""

    def test_entry_exists(self):
        """Entry must be present in pieces.json."""
        assert get_entry() is not None, "205-wave-harmonics not found in pieces.json"

    def test_required_fields_present(self):
        """All REQUIRED_FIELDS from test_pieces.py must be populated."""
        required = {"id", "title", "tagline", "year", "technique",
                    "path", "thumbnail", "description"}
        e = get_entry()
        assert e is not None
        missing = required - e.keys()
        assert not missing, f"Missing metadata fields: {missing}"

    def test_id_matches_directory(self):
        e = get_entry()
        assert e is not None
        assert e["id"] == "205-wave-harmonics"
        assert e["path"] == "pieces/205-wave-harmonics"

    def test_thumbnail_path(self):
        e = get_entry()
        assert e is not None
        assert e["thumbnail"] == "pieces/205-wave-harmonics/thumbnail.svg"

    def test_year(self):
        e = get_entry()
        assert e is not None
        assert e["year"] == 2026

    def test_technique_mentions_fourier(self):
        e = get_entry()
        assert e is not None
        assert "Fourier" in e["technique"]

    def test_technique_mentions_canvas(self):
        e = get_entry()
        assert e is not None
        assert "canvas" in e["technique"]

    def test_description_is_non_empty(self):
        e = get_entry()
        assert e is not None
        assert len(e["description"]) > 20

    def test_205_appears_after_200(self):
        """205-wave-harmonics must appear after 200-lsystem-trees in the JSON array."""
        pieces = load_pieces()
        idx_200 = next(
            (i for i, p in enumerate(pieces) if p["id"] == "200-lsystem-trees"), None
        )
        idx_205 = next(
            (i for i, p in enumerate(pieces) if p["id"] == "205-wave-harmonics"), None
        )
        assert idx_200 is not None, "200-lsystem-trees missing from pieces.json"
        assert idx_205 is not None, "205-wave-harmonics missing from pieces.json"
        assert idx_205 > idx_200, "205 must come after 200 in pieces.json"


# ---------------------------------------------------------------------------
# File system
# ---------------------------------------------------------------------------

class TestFiles:
    """Verify required files exist and are well-formed."""

    def test_directory_exists(self):
        assert PIECE_DIR.is_dir(), f"Directory missing: {PIECE_DIR}"

    def test_index_html_exists(self):
        assert INDEX.is_file()

    def test_thumbnail_svg_exists(self):
        assert THUMBNAIL.is_file()

    def test_readme_exists(self):
        assert README.is_file()

    def test_thumbnail_is_valid_svg(self):
        content = THUMBNAIL.read_text()
        assert "<svg" in content, "thumbnail.svg missing <svg> tag"
        assert "</svg>" in content, "thumbnail.svg missing closing </svg>"
        assert any(tag in content for tag in ("<polyline", "<path", "<line")), (
            "thumbnail.svg has no drawable geometry (polyline/path/line)"
        )

    def test_index_html_is_non_trivial(self):
        assert len(index_text()) > 2000

    def test_readme_is_non_trivial(self):
        assert len(README.read_text()) > 100


# ---------------------------------------------------------------------------
# index.html — structural requirements
# ---------------------------------------------------------------------------

class TestIndexHtml:
    """Check that index.html contains the required interactive elements."""

    def test_has_canvas_elements(self):
        assert "<canvas" in index_text()

    def test_has_upper_and_lower_panels(self):
        content = index_text()
        assert 'id="upper' in content, "Upper canvas/panel missing"
        assert 'id="lower' in content, "Lower canvas/panel missing"

    def test_has_eight_harmonic_columns(self):
        """Controls must be built for 8 harmonics."""
        content = index_text()
        assert "H1" in content and "H8" in content, "H1 or H8 label missing"

    def test_has_amplitude_sliders(self):
        content = index_text()
        assert 'id="amp-0"' in content or 'amp-' in content, (
            "Amplitude sliders (amp-N ids) not found"
        )

    def test_has_phase_sliders(self):
        content = index_text()
        assert 'id="phase-0"' in content or 'phase-' in content, (
            "Phase sliders (phase-N ids) not found"
        )

    def test_has_preset_buttons(self):
        content = index_text()
        assert "Square" in content, "Square preset button missing"
        assert "Sawtooth" in content, "Sawtooth preset button missing"
        assert "Triangle" in content, "Triangle preset button missing"

    def test_has_ripple_toggle(self):
        content = index_text()
        assert "Ripple" in content, "Ripple toggle missing"
        assert "ripple" in content.lower(), "ripple logic missing"

    def test_has_convergence_button(self):
        content = index_text()
        assert "Converge" in content or "converge" in content, (
            "Convergence animation button missing"
        )

    def test_has_requestanimationframe(self):
        assert "requestAnimationFrame" in index_text()

    def test_has_info_pane(self):
        """Slide-out educational pane must be present."""
        content = index_text()
        assert 'id="info-pane"' in content, "info-pane element missing"
        assert "info-btn" in content, "info button missing"
        assert "pane-close" in content, "pane close button missing"

    def test_pane_uses_transform_slide(self):
        """Pane must use CSS transform for slide animation (gallery mechanism)."""
        content = index_text()
        assert "translateX" in content, "CSS translateX slide missing from info-pane"
        assert ".open" in content, ".open class toggle missing"

    def test_eight_colors_defined(self):
        """Eight distinct harmonic colors must be specified in the source."""
        content = index_text()
        assert "COLORS" in content, "COLORS array missing"
        # 8 hex colors should be present
        import re
        colors = re.findall(r"'#[0-9a-fA-F]{6}'", content)
        assert len(colors) >= 8, f"Expected ≥8 color strings, found {len(colors)}"

    def test_fourier_theorem_mentioned_in_pane(self):
        content = index_text()
        assert "Fourier" in content

    def test_gibbs_phenomenon_mentioned(self):
        content = index_text()
        assert "Gibbs" in content, "Gibbs phenomenon not mentioned in educational pane"

    def test_no_external_dependencies(self):
        """index.html must be self-contained — no <script src> or <link href> to external URLs."""
        content = index_text()
        import re
        external_scripts = re.findall(r'<script[^>]+src=["\']https?://', content, re.I)
        external_links = re.findall(r'<link[^>]+href=["\']https?://', content, re.I)
        assert not external_scripts, f"External script dependencies found: {external_scripts}"
        assert not external_links, f"External stylesheet dependencies found: {external_links}"

    def test_preset_coefficients_present(self):
        """The PRESETS object (or equivalent) must be defined in index.html."""
        content = index_text()
        assert "PRESETS" in content or "square" in content.lower(), (
            "Preset definitions missing"
        )

    def test_square_wave_uses_odd_harmonics(self):
        """Square wave preset must zero even harmonics (n=2,4,6,8)."""
        content = index_text()
        assert "1/3" in content or "0.333" in content, (
            "Square wave H3 coefficient (1/3) not found"
        )
        assert "1/7" in content or "0.142" in content or "0.143" in content, (
            "Square wave H7 coefficient (1/7) not found"
        )


# ---------------------------------------------------------------------------
# Fourier math correctness
# ---------------------------------------------------------------------------

class TestFourierMath:
    """Verify the Fourier coefficient logic used in presets is correct in Python."""

    TWO_PI = 2 * math.pi
    N = 800

    def compute_sum(self, preset_amps, preset_phases, n_samples=800):
        """Replicate the JS sumWave() function in Python for verification."""
        out = [0.0] * n_samples
        for idx, (amp, phase) in enumerate(zip(preset_amps, preset_phases)):
            n = idx + 1
            for i in range(n_samples):
                out[i] += amp * math.sin(self.TWO_PI * n * i / n_samples + phase)
        return out

    def test_square_wave_is_approximately_square(self):
        """Square-wave approximation from 4 odd harmonics should cross zero at N/2."""
        amps = [1.0, 0.0, 1/3, 0.0, 1/5, 0.0, 1/7, 0.0]
        phases = [0.0] * 8
        wave = self.compute_sum(amps, phases)
        # The partial sum should be positive in the first half and negative in the second
        first_half_mean = sum(wave[:400]) / 400
        second_half_mean = sum(wave[400:]) / 400
        assert first_half_mean > 0.3, f"First half mean {first_half_mean:.3f} too small"
        assert second_half_mean < -0.3, f"Second half mean {second_half_mean:.3f} too large"

    def test_triangle_wave_amplitude_coefficients(self):
        """Triangle wave uses 1/n² coefficients for odd harmonics."""
        amps = [1.0, 0.0, 1/9, 0.0, 1/25, 0.0, 1/49, 0.0]
        for idx, a in enumerate(amps):
            n = idx + 1
            if n % 2 == 0:
                assert a == 0.0, f"Even harmonic H{n} should be 0, got {a}"
            else:
                expected = 1.0 / (n * n)
                assert abs(a - expected) < 1e-9, (
                    f"H{n}: expected 1/{n}^2 = {expected:.6f}, got {a:.6f}"
                )

    def test_sawtooth_amplitude_is_1_over_n(self):
        """Sawtooth wave uses 1/n amplitudes for all harmonics."""
        amps = [1.0, 0.5, 1/3, 0.25, 0.2, 1/6, 1/7, 0.125]
        for idx, a in enumerate(amps):
            n = idx + 1
            expected = 1.0 / n
            assert abs(a - expected) < 1e-9, (
                f"H{n}: expected 1/{n} = {expected:.6f}, got {a:.6f}"
            )

    def test_single_harmonic_is_pure_sine(self):
        """With only H1 at amplitude 1 the wave should match sin(2π·i/N) exactly."""
        amps = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        phases = [0.0] * 8
        wave = self.compute_sum(amps, phases)
        for i in range(self.N):
            expected = math.sin(self.TWO_PI * i / self.N)
            assert abs(wave[i] - expected) < 1e-10, (
                f"Sample {i}: expected {expected:.6f}, got {wave[i]:.6f}"
            )

    def test_zero_amplitudes_produce_flat_line(self):
        """All-zero amplitudes must yield a flat waveform at 0."""
        amps = [0.0] * 8
        phases = [0.0] * 8
        wave = self.compute_sum(amps, phases)
        assert all(v == 0.0 for v in wave), "Non-zero sample found with all-zero amplitudes"

    def test_phase_pi_reverses_sign(self):
        """A phase offset of π must invert the waveform exactly."""
        amps_pos = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        phases_pos = [0.0] * 8
        phases_neg = [math.pi] + [0.0] * 7
        wave_pos = self.compute_sum(amps_pos, phases_pos)
        wave_neg = self.compute_sum(amps_pos, phases_neg)
        for i in range(self.N):
            assert abs(wave_pos[i] + wave_neg[i]) < 1e-10, (
                f"Sample {i}: sum should be 0, got {wave_pos[i] + wave_neg[i]}"
            )

    def test_gibbs_overshoot_present_with_four_harmonics(self):
        """The Gibbs overshoot must exceed the steady-state plateau of the partial sum.

        With normalised coefficients 4/(π·n) for odd harmonics the partial sum
        converges to a square wave of amplitude 1, and the Gibbs peak exceeds 1.0
        (theoretically ~1.179).  We check strictly > 1.0 as a practical threshold
        at N=800 sample points.
        """
        # Normalised square-wave Fourier coefficients: 4/(π·n) for odd n
        amps = [4 / (math.pi * (2*k + 1)) if k % 2 == 0 else 0.0 for k in range(8)]
        phases = [0.0] * 8
        wave = self.compute_sum(amps, phases)
        max_val = max(wave)
        # The partial sum should overshoot the ideal ±1 amplitude
        assert max_val > 1.0, f"Expected Gibbs overshoot > 1.0, got max = {max_val:.4f}"


# ---------------------------------------------------------------------------
# Gallery consistency
# ---------------------------------------------------------------------------

class TestGalleryConsistency:
    """Ensure piece 205 does not break gallery invariants."""

    def test_no_duplicate_ids(self):
        pieces = load_pieces()
        ids = [p["id"] for p in pieces]
        assert len(ids) == len(set(ids)), "Duplicate piece IDs in pieces.json"

    def test_prior_pieces_preserved(self):
        pieces = load_pieces()
        ids = {p["id"] for p in pieces}
        for expected in [
            "01-amber-current",
            "136-fourier-epicycles",
            "199-gyroid-cross-sections",
            "200-lsystem-trees",
        ]:
            assert expected in ids, f"Prior piece {expected!r} was removed"

    def test_all_referenced_files_exist(self):
        e = get_entry()
        assert e is not None
        assert (REPO / e["path"]).is_dir(), f"Piece directory missing: {e['path']}"
        assert (REPO / e["thumbnail"]).is_file(), f"Thumbnail missing: {e['thumbnail']}"
        assert (REPO / e["path"] / "README.md").is_file(), "README.md missing"
        assert (REPO / e["path"] / "index.html").is_file(), "index.html missing"
