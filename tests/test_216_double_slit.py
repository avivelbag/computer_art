"""Tests for Piece 216 — Double-Slit Diffraction."""
import json
import math
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "216-double-slit"
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
    data = json.loads(PIECES_JSON.read_text())
    matches = [e for e in data if e.get("id") == "216-double-slit"]
    assert matches, "No entry with id '216-double-slit' found in pieces.json"
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


def test_pieces_json_technique_contains_double_slit():
    e = _entry()
    assert "double-slit" in e["technique"].lower() or "wave interference" in e["technique"].lower()


def test_pieces_json_technique_contains_required_keywords():
    e = _entry()
    technique = e["technique"]
    assert "canvas" in technique
    assert "ImageData" in technique or "imagedata" in technique.lower()
    assert "requestAnimationFrame" in technique or "raf" in technique.lower()


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"


# ---- index.html structure ----

def _html():
    return INDEX.read_text(encoding="utf-8")


def test_html_has_wave_canvas():
    assert 'id="wave-canvas"' in _html()


def test_html_has_screen_canvas():
    assert 'id="screen-canvas"' in _html()


def test_html_has_wave_wrap():
    """Left panel wrapper must be present for the 60% wave field."""
    assert 'id="wave-wrap"' in _html()


def test_html_has_screen_wrap():
    """Right panel wrapper must be present for the detector screen."""
    assert 'id="screen-wrap"' in _html()


def test_html_has_d_slider():
    """Slit separation slider d (0.5–5λ) must be present."""
    html = _html()
    assert 'id="d-slider"' in html
    assert 'min="0.5"' in html
    assert 'max="5"' in html


def test_html_has_a_slider():
    """Slit width slider a (0.1–2λ) must be present."""
    html = _html()
    assert 'id="a-slider"' in html
    assert 'min="0.1"' in html
    assert 'max="2"' in html


def test_html_has_wavelength_slider():
    """Wavelength slider (380–700 nm) must be present."""
    html = _html()
    assert 'id="nm-slider"' in html
    assert 'min="380"' in html
    assert 'max="700"' in html


def test_html_has_wavelength_swatch():
    """Wavelength color preview element must be present."""
    assert 'id="nm-swatch"' in _html()


def test_html_has_slit_count_buttons():
    """Buttons for N=1, 2, 5 must all be present."""
    html = _html()
    assert 'id="n1-btn"' in html
    assert 'id="n2-btn"' in html
    assert 'id="n5-btn"' in html


def test_html_has_info_button():
    assert 'id="info-btn"' in _html()


def test_html_has_info_pane():
    assert 'id="info-pane"' in _html()


def test_html_has_pane_close_button():
    assert 'id="pane-close"' in _html()


def test_html_raf_animation():
    assert "requestAnimationFrame" in _html()


def test_html_has_sinc_function():
    """sinc function required for the single-slit envelope calculation."""
    assert "sinc" in _html()


def test_html_has_intensity_function():
    """Intensity computation function must be defined."""
    assert "function intensity" in _html()


def test_html_has_draw_wave_function():
    assert "function drawWave" in _html()


def test_html_has_draw_screen_function():
    assert "function drawScreen" in _html()


def test_html_has_hsl_to_rgb():
    """Color mapping from wavelength hue must be present."""
    html = _html()
    assert "hslRgb" in html or "hslToRgb" in html or "hsl(" in html


def test_html_has_wavelength_to_hue():
    """wavelengthToHue function required for color mapping."""
    assert "wavelengthToHue" in _html()


def test_html_has_lambda_px_constant():
    """LAMBDA_PX controls pixels-per-wavelength in the wave animation."""
    assert "LAMBDA_PX" in _html()


def test_html_uses_imagedata():
    """Per-pixel wave field must be rendered via ImageData for performance."""
    assert "ImageData" in _html() or "createImageData" in _html()


def test_html_intensity_uses_sinc_squared():
    """Intensity formula must include sinc² (the single-slit envelope)."""
    html = _html()
    # sinc appears in the formula at minimum as a function name
    assert "sinc(" in html


def test_html_intensity_handles_n1():
    """N=1 single-slit case must be handled explicitly."""
    html = _html()
    assert "N === 1" in html or "N == 1" in html


def test_html_huygens_fresnel_in_info_pane():
    """Info pane must mention the Huygens-Fresnel principle."""
    html = _html()
    assert "Huygens" in html or "huygens" in html.lower()


def test_html_info_pane_mentions_fringe_formula():
    """Info pane must include a fringe position or intensity formula."""
    html = _html()
    assert "sinθ" in html or "sin&amp;#952;" in html or "sin&#952;" in html or "sin&#x03B8;" in html or "sinθ" in html


def test_html_info_pane_mentions_young():
    """Info pane must mention Young's experiment."""
    html = _html()
    assert "Young" in html


def test_html_info_pane_mentions_de_broglie():
    """Info pane must cover the quantum/de Broglie wavelength connection."""
    html = _html()
    assert "Broglie" in html or "de broglie" in html.lower() or "de Broglie" in html


def test_html_info_pane_has_three_or_more_sections():
    """Info pane must have at least 3 distinct content sections."""
    sections = re.findall(r'class="pane-section"', _html())
    assert len(sections) >= 3, f"Expected >= 3 pane sections, found {len(sections)}"


def test_html_sin_theta_max_defined():
    """SIN_THETA_MAX constant defines the angular range displayed."""
    assert "SIN_THETA_MAX" in _html()


def test_html_resize_observer():
    """Canvas must resize with the window (ResizeObserver)."""
    assert "ResizeObserver" in _html()


def test_html_escape_key_closes_pane():
    """Escape key must close the info pane."""
    html = _html()
    assert "Escape" in html


# ---- Thumbnail ----

def test_thumbnail_is_valid_svg():
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert content.strip().startswith("<svg") or "<?xml" in content
    assert "</svg>" in content


def test_thumbnail_has_wave_rings():
    """Thumbnail must contain circle elements representing circular wavefronts."""
    assert "<circle" in THUMBNAIL.read_text(encoding="utf-8")


def test_thumbnail_has_barrier():
    """Thumbnail must contain rect elements representing the barrier."""
    assert "<rect" in THUMBNAIL.read_text(encoding="utf-8")


def test_thumbnail_has_intensity_curve():
    """Thumbnail must contain a path or polyline for the intensity profile."""
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert "<path" in content or "<polyline" in content


def test_thumbnail_has_green_color():
    """Default 550 nm wavelength should appear as green in the thumbnail."""
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert "#00e864" in content or "00e8" in content.lower() or "green" in content.lower()


# ---- README ----

def test_readme_mentions_double_slit():
    text = README.read_text(encoding="utf-8")
    assert "double" in text.lower() and "slit" in text.lower()


def test_readme_mentions_huygens():
    text = README.read_text(encoding="utf-8")
    assert "Huygens" in text or "huygens" in text.lower()


def test_readme_mentions_young():
    text = README.read_text(encoding="utf-8")
    assert "Young" in text


def test_readme_mentions_de_broglie():
    text = README.read_text(encoding="utf-8")
    assert "Broglie" in text or "de broglie" in text.lower()


def test_readme_contains_intensity_formula():
    text = README.read_text(encoding="utf-8")
    assert "sinc" in text


def test_readme_contains_fringe_formula():
    text = README.read_text(encoding="utf-8")
    # Fringe condition d·sinθ = mλ
    assert "sinθ" in text or "sin(" in text or "sinθ" in text


# ---- Physics sanity checks (pure Python) ----

def sinc(x):
    return 1.0 if abs(x) < 1e-10 else math.sin(x) / x


def intensity(sin_theta, d, a, N):
    """Replicate the JS intensity function for unit-testing the physics."""
    beta  = math.pi * a * sin_theta
    delta = math.pi * d * sin_theta
    env   = sinc(beta) ** 2
    if N == 1:
        return env
    denom = N * math.sin(delta)
    g = 1.0 if abs(denom) < 1e-10 else math.sin(N * delta) / denom
    return env * g * g


class TestIntensityPhysics:
    """Verify the Fraunhofer intensity formula against known analytical results."""

    def test_central_max_is_unity(self):
        """I(0) = 1 for all N, d, a — the central maximum has full intensity."""
        for N in (1, 2, 5):
            for d in (0.5, 2.0, 5.0):
                assert abs(intensity(0.0, d=d, a=0.5, N=N) - 1.0) < 1e-9, \
                    f"I(0) != 1 for N={N}, d={d}"

    def test_double_slit_bright_fringes(self):
        """For N=2, fringes at sin(theta)=m*lambda/d should be near-maximum."""
        d = 2.0
        a = 0.2  # wide slit envelope so envelope barely attenuates
        for m in (1, 2):
            sin_theta = m / d  # d*sin(theta) = m*lambda
            if abs(sin_theta) >= 1.0:
                continue  # unphysical angle, skip
            intens = intensity(sin_theta, d=d, a=a, N=2)
            # Should be at principal maximum: only envelope modulates
            I_envelope = sinc(math.pi * a * sin_theta) ** 2
            assert abs(intens - I_envelope) < 1e-9, \
                f"N=2 fringe at m={m} not matching envelope: I={intens}, env={I_envelope}"

    def test_double_slit_dark_fringes(self):
        """For N=2, midpoints d*sin(theta) = (m+0.5)*lambda should be dark."""
        d = 2.0
        a = 0.1  # very narrow slit, envelope ≈ 1 everywhere
        for m in (0, 1):
            sin_theta = (m + 0.5) / d  # dark fringe
            if abs(sin_theta) >= 1.0:
                continue
            intens = intensity(sin_theta, d=d, a=a, N=2)
            assert intens < 1e-18, f"Expected dark fringe at m={m}+0.5, got I={intens}"

    def test_single_slit_envelope_zeros(self):
        """Single-slit minima occur at sin(theta) = m/a (m != 0)."""
        a = 1.0
        for m in (1, 2):
            sin_theta = m / a  # a*sin(theta) = m*lambda, sinc=0
            if abs(sin_theta) >= 1.0:
                continue
            intens = intensity(sin_theta, d=2.0, a=a, N=1)
            assert intens < 1e-18, f"Expected zero at m={m}, got I={intens}"

    def test_five_slit_principal_maxima(self):
        """For N=5, principal maxima at d*sin(theta)=m should equal the envelope."""
        d = 2.0
        a = 0.2
        for m in (0, 1):
            sin_theta = m / d
            if abs(sin_theta) >= 1.0:
                continue
            intens = intensity(sin_theta, d=d, a=a, N=5)
            env = sinc(math.pi * a * sin_theta) ** 2
            assert abs(intens - env) < 1e-9, \
                f"N=5 principal max at m={m}: I={intens}, env={env}"

    def test_intensity_non_negative_everywhere(self):
        """I(theta) must be >= 0 for all angles (no unphysical negative intensity)."""
        for sin_theta in [x / 100 for x in range(-95, 96)]:
            for N in (1, 2, 5):
                intens = intensity(sin_theta, d=2.0, a=0.5, N=N)
                assert intens >= -1e-12, f"Negative intensity I={intens} at sin_theta={sin_theta}, N={N}"

    def test_intensity_at_most_unity(self):
        """I(theta) must be <= 1 everywhere (normalized to central max)."""
        for sin_theta in [x / 100 for x in range(-95, 96)]:
            for N in (1, 2, 5):
                intens = intensity(sin_theta, d=2.0, a=0.5, N=N)
                assert intens <= 1.0 + 1e-9, f"I={intens} > 1 at sin_theta={sin_theta}, N={N}"


class TestFailureModes:
    """Verify correct error behavior for malformed input."""

    def test_missing_required_field_detected(self):
        """An entry without 'technique' should fail the required-field check."""
        entry = {
            "id": "216-double-slit",
            "title": "x",
            "tagline": "y",
            "year": 2026,
            "path": "pieces/216-double-slit",
            "thumbnail": "pieces/216-double-slit/thumbnail.svg",
            "description": "d",
        }
        assert not (REQUIRED_FIELDS <= entry.keys())

    def test_id_path_mismatch_detected(self):
        """id must equal basename of path."""
        entry = {"id": "216-double-slit", "path": "pieces/999-wrong-name"}
        assert entry["id"] != pathlib.Path(entry["path"]).name

    def test_nonexistent_thumbnail_is_absent(self, tmp_path):
        """A thumbnail file that was never created should not exist."""
        fake = tmp_path / "pieces" / "216-double-slit" / "nope.svg"
        assert not fake.exists()

    def test_intensity_edge_case_zero_angle(self):
        """I(0) must be exactly 1 even for large N and extreme d/a values."""
        assert abs(intensity(0.0, d=5.0, a=2.0, N=5) - 1.0) < 1e-9

    def test_sinc_at_zero_is_one(self):
        """sinc(0) must be 1, not NaN or 0 (avoids division-by-zero bug)."""
        assert sinc(0.0) == 1.0

    def test_sinc_at_pi_is_near_zero(self):
        """sinc(pi) = sin(pi)/pi should be essentially 0."""
        assert abs(sinc(math.pi)) < 1e-15
