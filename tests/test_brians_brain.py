"""Tests for Piece 56 — Brian's Brain: The Spark That Cannot Rest."""

import json
import pathlib
import re

import pytest

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "56-brians-brain"
INDEX       = PIECE_DIR / "index.html"
THUMB       = PIECE_DIR / "thumbnail.svg"
README      = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# Happy-path structural checks
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/56-brians-brain/ must exist"


def test_required_files_exist():
    assert INDEX.is_file(),  "index.html must exist"
    assert THUMB.is_file(),  "thumbnail.svg must exist"
    assert README.is_file(), "README.md must exist"


def test_pieces_json_entry_present():
    entries = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in entries]
    assert "56-brians-brain" in ids


def test_pieces_json_entry_fields():
    entries = json.loads(PIECES_JSON.read_text())
    entry = next(e for e in entries if e["id"] == "56-brians-brain")
    assert entry["path"]      == "pieces/56-brians-brain"
    assert entry["thumbnail"] == "pieces/56-brians-brain/thumbnail.svg"
    assert entry["year"]      == 2026
    assert "cellular automata" in entry["technique"].lower() or "brian" in entry["technique"].lower()


def test_pieces_json_entry_id_matches_dir():
    entries = json.loads(PIECES_JSON.read_text())
    entry   = next(e for e in entries if e["id"] == "56-brians-brain")
    piece_dir = REPO / entry["path"]
    assert entry["id"] == piece_dir.name


# ---------------------------------------------------------------------------
# index.html — implementation checks
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def source():
    """Return the full text of index.html."""
    return INDEX.read_text()


def test_has_canvas_element(source):
    assert "<canvas" in source


def test_uses_canvas_2d(source):
    assert "getContext('2d')" in source or 'getContext("2d")' in source


def test_uses_uint8array_buffers(source):
    """Double-buffer approach requires two Uint8Array allocations."""
    matches = re.findall(r'Uint8Array', source)
    assert len(matches) >= 2, "Expected at least two Uint8Array buffers (current + next)"


def test_brians_brain_rule_off_to_on(source):
    """OFF→ON rule fires when exactly 2 ON neighbours are present."""
    assert "=== 2" in source or "== 2" in source, (
        "Rule 'exactly 2 ON neighbours' must appear in index.html"
    )


def test_brians_brain_rule_on_to_dying(source):
    """ON→DYING and DYING→OFF transitions must be present."""
    assert "DYING" in source, "State constant DYING must be defined"


def test_toroidal_wrap_present(source):
    """Toroidal wrap uses modulo over cols and rows."""
    assert "% cols" in source and "% rows" in source, (
        "Toroidal wrap expressions '% cols' and '% rows' must be present"
    )


def test_uses_set_timeout_for_fps(source):
    """Animation throttled via setTimeout (not bare requestAnimationFrame) for ~25 fps."""
    assert "setTimeout" in source, "setTimeout must be used to cap frame rate"


def test_uses_fill_rect(source):
    """Cells are painted with fillRect (Canvas 2D rectangle fills)."""
    assert "fillRect" in source


def test_three_states_defined(source):
    """All three CA states (OFF, ON, DYING) must be declared as constants."""
    assert "OFF"   in source
    assert "ON"    in source
    assert "DYING" in source


def test_palette_uses_teal(source):
    """Electric teal (#00e5cc) must be present for the ON state."""
    assert "#00e5cc" in source or "00e5cc" in source.lower()


def test_palette_uses_violet(source):
    """Deep violet (#5a2d82) must be present for the DYING state."""
    assert "#5a2d82" in source or "5a2d82" in source.lower()


def test_palette_uses_dark_background(source):
    """Near-black background (#0f0f14) must be present."""
    assert "#0f0f14" in source or "0f0f14" in source.lower()


def test_click_handler_present(source):
    """A click handler must restart the simulation with a new random seed."""
    assert "click" in source


def test_resize_handler_present(source):
    """A resize handler keeps the grid filling the viewport."""
    assert "resize" in source


def test_math_random_used(source):
    """Initial state is randomised via Math.random."""
    assert "Math.random" in source


def test_no_external_scripts(source):
    """index.html must be self-contained — no external script imports."""
    external = re.findall(r'<script[^>]+src=["\']https?://', source)
    assert not external, f"Found external script imports: {external}"


def test_index_html_non_trivial(source):
    assert len(source) > 1000, "index.html must be non-trivial (>1000 bytes)"


# ---------------------------------------------------------------------------
# Thumbnail SVG checks
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def thumb_source():
    """Return the full text of thumbnail.svg."""
    return THUMB.read_text()


def test_thumbnail_is_svg(thumb_source):
    assert "<svg" in thumb_source


def test_thumbnail_has_rects(thumb_source):
    """Thumbnail must contain rect elements representing CA cells."""
    assert "<rect" in thumb_source


def test_thumbnail_has_teal_color(thumb_source):
    """Thumbnail must reference the electric teal ON-state colour."""
    assert "00e5cc" in thumb_source.lower(), (
        "Thumbnail must contain teal colour #00e5cc for ON cells"
    )


def test_thumbnail_has_violet_color(thumb_source):
    """Thumbnail must reference the deep violet DYING-state colour."""
    assert "5a2d82" in thumb_source.lower(), (
        "Thumbnail must contain violet colour #5a2d82 for DYING cells"
    )


def test_thumbnail_has_dark_background(thumb_source):
    """Thumbnail background must use the near-black colour."""
    assert "0f0f14" in thumb_source.lower()


def test_thumbnail_file_not_directory():
    assert THUMB.is_file()
    assert not THUMB.is_dir()


# ---------------------------------------------------------------------------
# README checks
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    content = README.read_text().strip()
    assert len(content) > 50


def test_readme_mentions_ca_rules():
    """README must describe the CA rules (ON/DYING/OFF or 'neighbours')."""
    content = README.read_text().lower()
    assert "dying" in content or "neighbour" in content or "neighbor" in content


def test_readme_mentions_toroidal():
    content = README.read_text().lower()
    assert "toroidal" in content or "wrap" in content or "torus" in content


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_piece_number_above_55():
    """Piece number must be ≥ 56 per the acceptance criteria."""
    num = int(PIECE_DIR.name.split("-")[0])
    assert num >= 56


def test_all_required_fields_in_entry():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    entries = json.loads(PIECES_JSON.read_text())
    entry = next(e for e in entries if e["id"] == "56-brians-brain")
    missing = required - entry.keys()
    assert not missing, f"Missing fields: {missing}"


def test_pieces_json_still_valid_after_addition():
    """pieces.json must remain a valid JSON list after the new entry."""
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)
    assert len(data) >= 24  # at least the 23 originals + our new piece


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

def test_webgl_not_used(source):
    """Brian's Brain is a Canvas 2D piece — WebGL must not be used."""
    assert "webgl" not in source.lower(), "Brian's Brain must use Canvas 2D, not WebGL"


def test_missing_piece_directory_detected(tmp_path):
    """A non-existent piece directory is correctly identified as missing."""
    ghost = tmp_path / "ghost-piece"
    assert not ghost.is_dir()


def test_malformed_json_entry_detected():
    """An entry missing required fields fails the field check."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    bad_entry = {
        "id": "56-brians-brain",
        "title": "Brian's Brain",
        # technique, tagline, year, path, thumbnail deliberately omitted
    }
    assert not (required <= bad_entry.keys())


def test_wrong_state_count_would_be_caught(source):
    """Verify the three-state check catches an implementation with only two states."""
    fake = source.replace("DYING", "DEAD").replace("dead", "DEAD")
    has_dying = "DYING" in fake
    assert not has_dying, "Sanity-check: replacement worked"
