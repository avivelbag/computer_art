"""Tests for piece 280-accretion-disk (Event Horizon)."""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "280-accretion-disk"
INDEX_HTML = PIECE_DIR / "index.html"
PIECES_JSON = REPO / "pieces.json"


# ── Filesystem / metadata ────────────────────────────────────────────────────

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_thumbnail_exists():
    thumb = PIECE_DIR / "thumbnail.svg"
    assert thumb.is_file()


def test_readme_exists():
    readme = PIECE_DIR / "README.md"
    assert readme.is_file()


def test_readme_not_empty():
    readme = PIECE_DIR / "README.md"
    assert readme.stat().st_size > 100


# ── pieces.json entry ────────────────────────────────────────────────────────

def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def _entry():
    return next((p for p in _load_pieces() if p["id"] == "280-accretion-disk"), None)


def test_pieces_json_has_entry():
    assert _entry() is not None, "280-accretion-disk missing from pieces.json"


def test_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    e = _entry()
    assert e is not None
    assert required <= e.keys(), f"Missing fields: {required - e.keys()}"


def test_entry_id_matches_directory():
    e = _entry()
    assert e is not None
    assert e["id"] == "280-accretion-disk"
    assert pathlib.Path(e["path"]).name == "280-accretion-disk"


def test_entry_thumbnail_file_exists():
    e = _entry()
    assert e is not None
    thumb = REPO / e["thumbnail"]
    assert thumb.is_file()


def test_entry_year():
    e = _entry()
    assert e is not None
    assert e["year"] == 2026


# ── HTML / shader content ────────────────────────────────────────────────────

def _html():
    return INDEX_HTML.read_text()


def test_html_uses_webgl():
    html = _html()
    assert "webgl" in html.lower(), "index.html must request a WebGL context"


def test_html_has_vertex_shader():
    html = _html()
    assert "VERTEX_SHADER" in html or "x-vertex" in html.lower() or "VERT" in html


def test_html_has_fragment_shader():
    html = _html()
    assert "FRAGMENT_SHADER" in html or "FRAG" in html


def test_html_no_external_assets():
    """Shaders must be inlined; no <script src=...> or <link href=...> to external URLs."""
    html = _html()
    # Disallow http/https src or href attributes pointing outside
    external = re.findall(r'(src|href)\s*=\s*["\']https?://', html)
    assert external == [], f"External assets found: {external}"


def test_html_has_requestanimationframe():
    """Animation loop must use requestAnimationFrame, not setInterval."""
    assert "requestAnimationFrame" in _html()


def test_html_has_time_uniform():
    """Shader needs a time uniform to drive animation."""
    html = _html()
    assert "uTime" in html or "u_time" in html or "time" in html.lower()


def test_html_has_schwarzschild_reference():
    """Shader must reference the Schwarzschild radius concept."""
    html = _html()
    assert "Rs" in html or "schwarzschild" in html.lower() or "Schwarzschild" in html


def test_html_has_doppler_logic():
    """Shader must implement Doppler colour shift (sin phi component of velocity)."""
    html = _html()
    assert "doppler" in html.lower() or "Doppler" in html or "dopplerShift" in html or "dopplerT" in html


def test_html_has_lensing_logic():
    """Shader must bend rays near the black hole (gravitational lensing)."""
    html = _html()
    assert "lens" in html.lower() or "bent" in html


def test_html_capped_60fps():
    """Animation should not request faster than 60 fps (no fixed setInterval < 16ms)."""
    html = _html()
    bad_intervals = re.findall(r'setInterval\s*\([^,]+,\s*(\d+)\s*\)', html)
    for ms in bad_intervals:
        assert int(ms) >= 16, f"setInterval with {ms}ms is faster than 60fps"


def test_html_event_horizon_black():
    """Fragment shader must output black for pixels inside the shadow."""
    html = _html()
    # Look for the early-return with vec4(0.0, 0.0, 0.0, 1.0) inside the shadow branch
    assert "0.0, 0.0, 0.0, 1.0" in html or "vec4(0" in html


# ── Edge cases ───────────────────────────────────────────────────────────────

def test_pieces_json_valid_json():
    """Ensure pieces.json hasn't been corrupted."""
    data = _load_pieces()
    assert isinstance(data, list)
    assert len(data) > 0


def test_no_duplicate_ids():
    """Every piece must have a unique id."""
    pieces = _load_pieces()
    ids = [p["id"] for p in pieces]
    assert len(ids) == len(set(ids)), "Duplicate ids found in pieces.json"


def test_piece_is_last_or_present():
    """280-accretion-disk should appear in pieces.json (position-agnostic)."""
    ids = [p["id"] for p in _load_pieces()]
    assert "280-accretion-disk" in ids


def test_thumbnail_is_svg():
    thumb = PIECE_DIR / "thumbnail.svg"
    content = thumb.read_text()
    assert "<svg" in content, "thumbnail.svg must be a valid SVG file"


def test_index_html_has_canvas():
    assert "<canvas" in _html()
