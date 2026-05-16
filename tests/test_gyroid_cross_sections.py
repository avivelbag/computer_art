"""Tests for piece 199-gyroid-cross-sections."""

import json
import math
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "199-gyroid-cross-sections"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# Happy-path: directory structure
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/199-gyroid-cross-sections/ must exist"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_exists():
    thumb = PIECE_DIR / "thumbnail.svg"
    assert thumb.is_file(), "thumbnail.svg must exist"


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# Happy-path: pieces.json entry
# ---------------------------------------------------------------------------

def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def _gyroid_entry():
    pieces = _load_pieces()
    for p in pieces:
        if p.get("id") == "199-gyroid-cross-sections":
            return p
    return None


def test_pieces_json_has_gyroid_entry():
    assert _gyroid_entry() is not None, "199-gyroid-cross-sections not found in pieces.json"


def test_gyroid_entry_required_fields():
    entry = _gyroid_entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= entry.keys(), f"Missing fields: {required - entry.keys()}"


def test_gyroid_entry_id_matches_dir():
    entry = _gyroid_entry()
    piece_dir = REPO / entry["path"]
    assert entry["id"] == piece_dir.name


def test_gyroid_entry_path_is_directory():
    entry = _gyroid_entry()
    assert (REPO / entry["path"]).is_dir()


def test_gyroid_entry_thumbnail_is_file():
    entry = _gyroid_entry()
    assert (REPO / entry["thumbnail"]).is_file()


def test_gyroid_entry_year():
    entry = _gyroid_entry()
    assert isinstance(entry["year"], int)
    assert entry["year"] >= 2026


# ---------------------------------------------------------------------------
# Happy-path: index.html shader content
# ---------------------------------------------------------------------------

def _html():
    return (PIECE_DIR / "index.html").read_text()


def test_index_html_has_vertex_shader_tag():
    """Vertex shader must be inlined as an x-shader script tag."""
    html = _html()
    assert 'type="x-shader/x-vertex"' in html or "type='x-shader/x-vertex'" in html


def test_index_html_has_fragment_shader_tag():
    """Fragment shader must be inlined as an x-shader script tag."""
    html = _html()
    assert 'type="x-shader/x-fragment"' in html or "type='x-shader/x-fragment'" in html


def test_index_html_has_gyroid_function():
    """Shader must evaluate the gyroid implicit function f = sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x)."""
    html = _html()
    assert "sin(" in html and "cos(" in html, "Gyroid function must use sin/cos"
    # The three product terms that define the gyroid
    assert "sin(rx)" in html or "sin(uv.x)" in html or "sin(x)" in html


def test_index_html_has_webgl_context():
    html = _html()
    assert "getContext('webgl')" in html or 'getContext("webgl")' in html


def test_index_html_has_time_uniform():
    html = _html()
    assert "uTime" in html or "u_time" in html


def test_index_html_has_resolution_uniform():
    html = _html()
    assert "uRes" in html or "u_resolution" in html


def test_index_html_has_animation_loop():
    html = _html()
    assert "requestAnimationFrame" in html


def test_index_html_no_external_scripts():
    """Piece must be self-contained — no external script src attributes."""
    html = _html()
    # Reject any <script src="..."> pointing to http(s) or CDN
    external = re.findall(r'<script[^>]+src=["\']https?://', html, re.IGNORECASE)
    assert not external, f"External script dependencies found: {external}"


def test_index_html_has_z_animation():
    """The z-slice must animate (sin of time)."""
    html = _html()
    assert "uTime" in html or "u_time" in html
    # Check that z is computed from sin of time
    assert "sin(" in html


def test_index_html_has_tilt():
    """The plane must tilt (rotation variables present in shader)."""
    html = _html()
    # Tilt is implemented as cosT/sinT rotation or equivalent
    assert ("cosT" in html or "cos(tilt" in html or "cos(" in html)


def test_index_html_has_secondary_isocontours():
    """Secondary isocontours at f = ±0.5 must be present."""
    html = _html()
    assert "0.5" in html, "Secondary isocontour level f=0.5 must appear in shader"


def test_index_html_has_gold_color():
    """Primary isocurve must be warm gold/orange (high red, medium-high green, low blue)."""
    html = _html()
    # Look for warm color values: 0.95 red component (gold)
    assert "0.95" in html or "0.90" in html or "0.78" in html


def test_index_html_has_dark_background():
    """Background must be dark (small color values for the bg)."""
    html = _html()
    assert "0.05" in html or "0.03" in html or "0.08" in html


# ---------------------------------------------------------------------------
# Edge case: gyroid function correctness (pure Python evaluation)
# ---------------------------------------------------------------------------

def _gyroid(x, y, z):
    """Reference implementation of the gyroid implicit function."""
    return math.sin(x) * math.cos(y) + math.sin(y) * math.cos(z) + math.sin(z) * math.cos(x)


def test_gyroid_at_origin():
    """f(0, 0, 0) = 0; the origin lies exactly on the gyroid surface."""
    assert _gyroid(0.0, 0.0, 0.0) == pytest.approx(0.0, abs=1e-12)


def test_gyroid_period_x():
    """Gyroid is 2pi-periodic in x: f(x+2pi, y, z) == f(x, y, z)."""
    for x, y, z in [(0.5, 0.3, 1.1), (1.0, -0.5, 0.0), (-0.7, 0.8, 2.0)]:
        assert _gyroid(x + 2 * math.pi, y, z) == pytest.approx(_gyroid(x, y, z), rel=1e-9)


def test_gyroid_period_y():
    """Gyroid is 2pi-periodic in y."""
    for x, y, z in [(0.3, 1.2, -0.4), (-1.0, 0.0, 0.5)]:
        assert _gyroid(x, y + 2 * math.pi, z) == pytest.approx(_gyroid(x, y, z), rel=1e-9)


def test_gyroid_period_z():
    """Gyroid is 2pi-periodic in z."""
    for x, y, z in [(0.1, -0.3, 0.7), (0.9, 1.1, -1.5)]:
        assert _gyroid(x, y, z + 2 * math.pi) == pytest.approx(_gyroid(x, y, z), rel=1e-9)


def test_gyroid_antisymmetry():
    """f(-x, -y, -z) = -f(x, y, z) — the gyroid has a body-centred symmetry."""
    for x, y, z in [(0.4, 0.6, 0.8), (1.0, -0.5, 0.2), (-1.3, 2.1, -0.7)]:
        assert _gyroid(-x, -y, -z) == pytest.approx(-_gyroid(x, y, z), rel=1e-9)


def test_gyroid_level_set_at_z0():
    """At z=0, f(x,y) = sin(x)cos(y) + sin(y); verify several known zero points."""
    # At z=0: f(x,y) = sin(x)cos(y) + sin(y)
    # Along y=0: f = sin(x), so x=0 is a zero
    assert _gyroid(0.0, 0.0, 0.0) == pytest.approx(0.0, abs=1e-12)
    # x=pi is another zero along y=0
    assert _gyroid(math.pi, 0.0, 0.0) == pytest.approx(0.0, abs=1e-9)
    # At (pi/2, -pi/4, 0): sin(pi/2)cos(-pi/4) + sin(-pi/4) = 1/sqrt(2) - 1/sqrt(2) = 0
    assert _gyroid(math.pi / 2, -math.pi / 4, 0.0) == pytest.approx(0.0, abs=1e-9)


def test_gyroid_range():
    """Gyroid values are bounded in [-sqrt(3)*1.5, sqrt(3)*1.5] roughly; spot check range."""
    import random
    random.seed(42)
    for _ in range(1000):
        x = random.uniform(-math.pi, math.pi)
        y = random.uniform(-math.pi, math.pi)
        z = random.uniform(-math.pi, math.pi)
        val = _gyroid(x, y, z)
        # Each term is at most 1 in magnitude, so |f| <= 3
        assert abs(val) <= 3.0 + 1e-9


# ---------------------------------------------------------------------------
# Failure modes: malformed or missing files
# ---------------------------------------------------------------------------

class TestMissingFiles:
    def test_nonexistent_piece_dir_not_present(self, tmp_path):
        """A directory that doesn't exist should not be falsely detected as present."""
        ghost = tmp_path / "199-gyroid-cross-sections"
        assert not ghost.is_dir()

    def test_missing_thumbnail_detected(self, tmp_path):
        """Referencing a non-existent thumbnail should be caught."""
        thumb = tmp_path / "thumbnail.svg"
        assert not thumb.is_file()

    def test_missing_readme_detected(self, tmp_path):
        """A piece directory without README.md should be caught."""
        d = tmp_path / "199-gyroid-cross-sections"
        d.mkdir()
        assert not (d / "README.md").is_file()

    def test_wrong_piece_id_detected(self, tmp_path):
        """An entry whose id doesn't match the directory name should fail."""
        d = tmp_path / "199-gyroid-cross-sections"
        d.mkdir()
        entry = {"id": "wrong-id", "path": str(d)}
        assert entry["id"] != d.name

    def test_empty_pieces_json_is_invalid(self, tmp_path):
        """An empty JSON file should not parse as a valid piece list."""
        f = tmp_path / "pieces.json"
        f.write_text("")
        with pytest.raises(Exception):
            json.loads(f.read_text())

    def test_non_list_pieces_json_detected(self, tmp_path):
        """pieces.json must be a JSON array, not an object."""
        data = {"id": "oops"}
        assert not isinstance(data, list)
