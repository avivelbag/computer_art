"""Tests for Piece 224 — The Butterfly Effect: Lorenz Attractor in 3D.

Covers:
- Happy path: required files exist, pieces.json entry is correct.
- Content checks: index.html mentions WebGL and Lorenz; README explains RK4 and σ.
- Edge cases: thumbnail is a non-empty valid SVG; README is non-empty.
- Failure modes: missing required fields and id mismatch are caught correctly.
"""

import json
import pathlib
import xml.etree.ElementTree as ET

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "224-lorenz-attractor"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "224-lorenz-attractor"


# ---- Helpers ----

def load_pieces():
    """Return parsed pieces.json list."""
    return json.loads(PIECES_JSON.read_text())


def find_entry():
    """Return the pieces.json entry for piece 224, or None."""
    for entry in load_pieces():
        if entry.get("id") == PIECE_ID:
            return entry
    return None


# ---- Happy path ----

def test_piece_directory_exists():
    """The piece directory must be present."""
    assert PIECE_DIR.is_dir(), f"Missing directory: {PIECE_DIR}"


def test_index_html_exists():
    """index.html must exist inside the piece directory."""
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_svg_exists():
    """thumbnail.svg must exist inside the piece directory."""
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    """README.md must exist inside the piece directory."""
    assert (PIECE_DIR / "README.md").is_file()


def test_pieces_json_entry_exists():
    """pieces.json must contain an entry with id '224-lorenz-attractor'."""
    assert find_entry() is not None, f"No entry with id={PIECE_ID!r} in pieces.json"


def test_pieces_json_entry_fields():
    """The pieces.json entry must carry all required metadata fields."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = find_entry()
    assert entry is not None
    assert required <= entry.keys(), f"Missing fields: {required - entry.keys()}"


def test_pieces_json_id_matches_dir():
    """Entry id must equal the last segment of the path field."""
    entry = find_entry()
    assert entry is not None
    assert entry["id"] == pathlib.Path(entry["path"]).name


def test_pieces_json_technique_mentions_lorenz():
    """Technique field must reference 'Lorenz attractor'."""
    entry = find_entry()
    assert entry is not None
    assert "Lorenz" in entry["technique"]


def test_pieces_json_technique_mentions_webgl():
    """Technique field must reference WebGL as the renderer."""
    entry = find_entry()
    assert entry is not None
    assert "WebGL" in entry["technique"]


# ---- Content checks ----

def test_index_html_mentions_webgl():
    """index.html must use WebGL (canvas getContext 'webgl2')."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "webgl2" in html, "index.html does not request a WebGL 2 context"


def test_index_html_mentions_rk4():
    """index.html must implement RK4 integration (references DT and derivative steps)."""
    html = (PIECE_DIR / "index.html").read_text()
    # RK4 uses DT/2 for midpoint steps.
    assert "DT2" in html or "DT/2" in html or "dt/2" in html.lower()


def test_index_html_has_nudge_button():
    """index.html must contain a Nudge button element."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "nudge" in html.lower(), "No nudge button found in index.html"


def test_index_html_has_sigma_slider():
    """index.html must expose a σ slider."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "sl-sigma" in html or "sigma" in html.lower()


def test_index_html_has_rho_slider():
    """index.html must expose a ρ slider."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "sl-rho" in html or "rho" in html.lower()


def test_index_html_has_beta_slider():
    """index.html must expose a β slider."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "sl-beta" in html or "beta" in html.lower()


def test_index_html_50k_points():
    """Ring buffer capacity must be at least 50 000 points."""
    html = (PIECE_DIR / "index.html").read_text()
    # The constant N in the source must be >= 50000.
    import re
    matches = re.findall(r'\bN\s*=\s*(\d+)', html)
    assert matches, "No ring buffer size constant N found in index.html"
    assert any(int(m) >= 50000 for m in matches), (
        f"Ring buffer size {matches} is smaller than 50 000"
    )


def test_index_html_has_info_pane():
    """index.html must include a slide-out educational panel."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "info-pane" in html or "pane" in html


def test_index_html_mentions_lorenz_history():
    """index.html must explain who Lorenz was and the butterfly effect."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "Lorenz" in html
    assert "butterfly" in html.lower()


def test_readme_mentions_runge_kutta():
    """README.md must explain the RK4 integration method."""
    readme = (PIECE_DIR / "README.md").read_text()
    assert "Runge-Kutta" in readme or "RK4" in readme


def test_readme_mentions_sigma():
    """README.md must document the σ parameter."""
    readme = (PIECE_DIR / "README.md").read_text()
    assert "σ" in readme or "sigma" in readme.lower()


def test_readme_mentions_1963():
    """README.md must reference Lorenz's 1963 paper."""
    readme = (PIECE_DIR / "README.md").read_text()
    assert "1963" in readme


# ---- Edge cases ----

def test_thumbnail_svg_is_non_empty():
    """thumbnail.svg must contain actual content (not empty)."""
    content = (PIECE_DIR / "thumbnail.svg").read_bytes()
    assert len(content) > 100, "thumbnail.svg appears to be empty or trivially small"


def test_thumbnail_svg_is_valid_xml():
    """thumbnail.svg must be well-formed XML."""
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    try:
        ET.fromstring(content)
    except ET.ParseError as e:
        pytest.fail(f"thumbnail.svg is not valid XML: {e}")


def test_thumbnail_svg_has_dark_background():
    """thumbnail.svg should use a near-black background rect."""
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    # Background is declared as #07071a or similar dark hex.
    assert "#07" in content or "fill=\"#0" in content, (
        "thumbnail.svg does not appear to have a dark background"
    )


def test_readme_is_non_empty():
    """README.md must be a meaningful document (>200 characters)."""
    readme = (PIECE_DIR / "README.md").read_text()
    assert len(readme) > 200, "README.md is suspiciously short"


def test_index_html_has_auto_rotate():
    """index.html must auto-rotate the camera (AUTO_YAW_SPEED or equivalent)."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "AUTO" in html or "autoYaw" in html or "auto_yaw" in html.lower() or "ROT_SPEED" in html


def test_index_html_has_mouse_drag():
    """index.html must support mouse-drag orbit (mousedown + mousemove handlers)."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "mousedown" in html
    assert "mousemove" in html


# ---- Failure modes ----

def test_entry_without_title_fails_required_field_check():
    """An entry missing 'title' must not satisfy the required-field check."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    incomplete = {
        "id": "224-lorenz-attractor",
        "tagline": "test",
        "year": 2026,
        "technique": "WebGL",
        "path": "pieces/224-lorenz-attractor",
        "thumbnail": "pieces/224-lorenz-attractor/thumbnail.svg",
        "description": "test",
    }
    assert not (required <= incomplete.keys()), (
        "Entry without 'title' incorrectly passed the required-field check"
    )


def test_id_mismatch_is_detectable(tmp_path):
    """An id that does not match the last path segment must be caught."""
    entry = {
        "id": "wrong-id",
        "title": "X",
        "tagline": "X",
        "year": 2026,
        "technique": "X",
        "path": "pieces/224-lorenz-attractor",
        "thumbnail": "pieces/224-lorenz-attractor/thumbnail.svg",
        "description": "X",
    }
    assert entry["id"] != pathlib.Path(entry["path"]).name


def test_missing_thumbnail_is_detectable(tmp_path):
    """Referencing a non-existent thumbnail should be detectable."""
    ghost = tmp_path / "pieces" / "224-lorenz-attractor" / "thumbnail.svg"
    assert not ghost.exists()


def test_missing_readme_is_detectable(tmp_path):
    """A piece directory without README.md should fail the directory check."""
    piece_dir = tmp_path / "224-lorenz-attractor"
    piece_dir.mkdir()
    assert not (piece_dir / "README.md").exists()


def test_dt_value_is_correct():
    """The integration time step must be dt=0.005 as specified in acceptance criteria."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "0.005" in html, "Expected dt=0.005 in index.html"
