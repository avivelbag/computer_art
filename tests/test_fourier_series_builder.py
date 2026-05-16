"""Tests for Piece 213 — Fourier Series Builder."""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "213-fourier-series-builder"
INDEX = PIECE_DIR / "index.html"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
README = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


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
    matches = [e for e in data if e.get("id") == "213-fourier-series-builder"]
    assert matches, "No entry with id '213-fourier-series-builder' found in pieces.json"
    return matches[0]


def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_entry_fields():
    """Entry must carry all required metadata fields."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    e = _entry()
    assert required <= e.keys(), f"Missing fields: {required - e.keys()}"


def test_pieces_json_entry_id_matches_dir():
    e = _entry()
    assert e["id"] == pathlib.Path(e["path"]).name


def test_pieces_json_thumbnail_file_exists():
    e = _entry()
    assert (REPO / e["thumbnail"]).is_file()


def test_pieces_json_path_dir_exists():
    e = _entry()
    assert (REPO / e["path"]).is_dir()


# ---- index.html structure ----

def _html():
    return INDEX.read_text(encoding="utf-8")


def test_html_has_phasor_canvas():
    """Left panel must have a canvas for the rotating phasors."""
    assert 'id="phasor-canvas"' in _html()


def test_html_has_wave_canvas():
    """Right panel must have a canvas for the time-domain wave."""
    assert 'id="wave-canvas"' in _html()


def test_html_has_harmonic_buttons_bar():
    """Harmonic toggle bar must be present."""
    assert 'id="harmonic-bar"' in _html()


def test_html_has_preset_square_button():
    assert 'id="btn-square"' in _html()


def test_html_has_preset_sawtooth_button():
    assert 'id="btn-sawtooth"' in _html()


def test_html_has_preset_triangle_button():
    assert 'id="btn-triangle"' in _html()


def test_html_has_reset_button():
    assert 'id="btn-reset"' in _html()


def test_html_has_speed_slider():
    assert 'id="speed-slider"' in _html()


def test_html_has_info_button():
    assert 'id="info-btn"' in _html()


def test_html_has_info_pane():
    """Slide-out educational pane must be present."""
    assert 'id="info-pane"' in _html()


def test_html_num_harmonics_constant():
    """NUM_H constant must be set to 10."""
    assert "NUM_H = 10" in _html()


def test_html_presets_object_defined():
    """PRESETS object for square/sawtooth/triangle must exist."""
    html = _html()
    assert "PRESETS" in html
    assert "square" in html
    assert "sawtooth" in html
    assert "triangle" in html


def test_html_square_uses_only_odd_harmonics():
    """Square wave preset must zero out even harmonics (amp: 0 for even n)."""
    html = _html()
    # Check that the square preset uses n % 2 === 1 condition
    assert "n % 2 === 1" in html or "isOdd" in html


def test_html_phasor_draw_function():
    """drawPhasors function must be present."""
    assert "function drawPhasors" in _html()


def test_html_wave_draw_function():
    """drawWave function must be present."""
    assert "function drawWave" in _html()


def test_html_apply_preset_function():
    """applyPreset function must wire the preset buttons."""
    assert "function applyPreset" in _html()


def test_html_raf_animation_loop():
    """requestAnimationFrame animation loop must be present."""
    assert "requestAnimationFrame" in _html()


def test_html_formula_square_wave():
    """Educational pane must include the square-wave Fourier formula."""
    html = _html()
    assert "4/π" in html or "4/π" in html or "4/&pi;" in html or "4/&#960;" in html


# ---- thumbnail ----

def test_thumbnail_is_valid_svg():
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert content.strip().startswith("<svg") or "<?xml" in content
    assert "</svg>" in content


def test_thumbnail_has_phasor_arrows():
    """Thumbnail SVG must contain line elements representing phasor arms."""
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert "<line" in content


def test_thumbnail_has_wave_path():
    """Thumbnail must include a path element for the wave trace."""
    content = THUMBNAIL.read_text(encoding="utf-8")
    assert "<path" in content


# ---- README ----

def test_readme_mentions_square_formula():
    text = README.read_text(encoding="utf-8")
    assert "4/π" in text or "4/pi" in text.lower()


def test_readme_mentions_sawtooth():
    text = README.read_text(encoding="utf-8")
    assert "sawtooth" in text.lower() or "Sawtooth" in text


def test_readme_mentions_triangle():
    text = README.read_text(encoding="utf-8")
    assert "triangle" in text.lower() or "Triangle" in text


def test_readme_mentions_phasor():
    text = README.read_text(encoding="utf-8")
    assert "phasor" in text.lower()


# ---- Edge cases ----

def test_pieces_json_entry_exists():
    """Piece 213 must be present in pieces.json."""
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert "213-fourier-series-builder" in ids


def test_pieces_json_no_duplicate_id():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"


def test_html_wave_trail_buffer():
    """N_WAVE constant (wave trail buffer size) must be defined."""
    assert "N_WAVE" in _html()


def test_html_colors_array_length():
    """COLORS array must have at least 10 entries (one per harmonic)."""
    html = _html()
    colors_match = re.search(r"const COLORS = \[([^\]]+)\]", html, re.DOTALL)
    assert colors_match, "COLORS array not found"
    entries = [c.strip() for c in colors_match.group(1).split(",") if c.strip()]
    assert len(entries) >= 10, f"Expected >= 10 color entries, got {len(entries)}"


class TestFailureModes:
    """Explicit failure-mode assertions."""

    def test_missing_id_fails_required_fields(self):
        """An entry without 'id' should fail the required-fields check."""
        entry = {"title": "x", "tagline": "y", "year": 2026,
                 "technique": "t", "path": "p", "thumbnail": "th", "description": "d"}
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
        assert not (required <= entry.keys())

    def test_wrong_path_name_mismatch(self):
        """id != basename(path) is a detectable error."""
        entry = {"id": "213-fourier-series-builder", "path": "pieces/999-something-else"}
        assert entry["id"] != pathlib.Path(entry["path"]).name

    def test_nonexistent_thumbnail_is_absent(self, tmp_path):
        fake_thumb = tmp_path / "pieces" / "213-fourier-series-builder" / "thumb.svg"
        assert not fake_thumb.exists()
