"""Tests for piece 293-substrate-cracks (Ancient Glaze)."""
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "293-substrate-cracks"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}


# ---------------------------------------------------------------------------
# Happy-path: directory layout
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), f"Directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_exists():
    svg = PIECE_DIR / "thumbnail.svg"
    png = PIECE_DIR / "thumbnail.png"
    assert svg.is_file() or png.is_file(), "No thumbnail.svg or thumbnail.png found"


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# Happy-path: pieces.json registration
# ---------------------------------------------------------------------------

def _get_entry():
    pieces = json.loads(PIECES_JSON.read_text())
    matches = [p for p in pieces if p["id"] == PIECE_ID]
    assert matches, f"{PIECE_ID} not found in pieces.json"
    return matches[0]


def test_pieces_json_has_entry():
    entry = _get_entry()
    assert entry["id"] == PIECE_ID


def test_pieces_json_entry_has_required_fields():
    entry = _get_entry()
    missing = REQUIRED_FIELDS - entry.keys()
    assert not missing, f"Missing fields: {missing}"


def test_pieces_json_id_matches_path():
    entry = _get_entry()
    assert pathlib.Path(entry["path"]).name == entry["id"]


def test_pieces_json_path_directory_exists():
    entry = _get_entry()
    assert (REPO / entry["path"]).is_dir()


def test_pieces_json_thumbnail_file_exists():
    entry = _get_entry()
    assert (REPO / entry["thumbnail"]).is_file()


# ---------------------------------------------------------------------------
# Happy-path: algorithm implementation markers in index.html
# ---------------------------------------------------------------------------

def _html():
    return (PIECE_DIR / "index.html").read_text()


def test_html_uses_uint8array_grid():
    """Crack occupancy grid must be a Uint8Array for efficient per-pixel lookup."""
    assert "Uint8Array" in _html()


def test_html_has_value_noise():
    """A precomputed noise grid (noiseGrid / sampleNoise) must be present."""
    html = _html()
    assert "noiseGrid" in html or "sampleNoise" in html


def test_html_has_seed_growth_logic():
    """Active-seed list and spawn function must be present."""
    html = _html()
    assert "live" in html or "seeds" in html
    assert "spawn" in html or "spawnSeed" in html


def test_html_has_perpendicular_branching():
    """Perpendicular spawn at ~90° must appear in the source."""
    html = _html()
    assert "Math.PI / 2" in html or "Math.PI/2" in html


def test_html_correct_background_color():
    assert "#e8dfc8" in _html()


def test_html_correct_crack_color():
    assert "#3d2b1a" in _html()


def test_html_n_seeds_approximately_six():
    """N_SEEDS constant (or literal 6) must appear in the source."""
    html = _html()
    assert "N_SEEDS" in html or "= 6" in html or "=6" in html


def test_html_requestanimationframe_present():
    assert "requestAnimationFrame" in _html()


def test_html_no_external_library_imports():
    """The piece must be self-contained — no CDN or external script tags."""
    html = _html()
    assert "cdn." not in html
    assert "unpkg.com" not in html
    assert "jsdelivr" not in html
    assert 'src="http' not in html


# ---------------------------------------------------------------------------
# Happy-path: thumbnail is valid SVG
# ---------------------------------------------------------------------------

def test_thumbnail_svg_structure():
    thumb = PIECE_DIR / "thumbnail.svg"
    if not thumb.is_file():
        pytest.skip("thumbnail.svg not present")
    content = thumb.read_text()
    assert "<svg" in content
    assert "xmlns" in content
    assert "#e8dfc8" in content, "SVG should use the parchment background color"
    assert "#3d2b1a" in content, "SVG should use the crack color"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_piece_id_has_numeric_prefix():
    parts = PIECE_ID.split("-")
    assert parts[0].isdigit(), "Piece ID must start with a numeric prefix"


def test_piece_id_contains_slug():
    assert "substrate" in PIECE_ID or "cracks" in PIECE_ID


def test_pieces_json_is_valid_list():
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)
    assert len(data) > 0


def test_pieces_json_no_duplicate_ids():
    pieces = json.loads(PIECES_JSON.read_text())
    ids = [p["id"] for p in pieces]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"


def test_index_html_is_non_empty():
    content = _html()
    assert len(content) > 500, "index.html seems too short to contain a real implementation"


def test_readme_mentions_substrate():
    readme = (PIECE_DIR / "README.md").read_text().lower()
    assert "substrate" in readme


# ---------------------------------------------------------------------------
# Failure-mode assertions
# ---------------------------------------------------------------------------

class TestFailureModes:
    """Verify that missing or malformed inputs produce the expected no-op or error."""

    def test_missing_piece_returns_false_for_isdir(self, tmp_path):
        nonexistent = tmp_path / "ghost-piece"
        assert not nonexistent.is_dir()

    def test_entry_without_required_field_fails_check(self):
        incomplete = {
            "id": PIECE_ID,
            "title": "Ancient Glaze",
            "year": 2026,
        }
        missing = REQUIRED_FIELDS - incomplete.keys()
        assert missing, "Expected missing fields to be detected"
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_wrong_id_does_not_match_path(self, tmp_path):
        piece_dir = tmp_path / "some-piece"
        piece_dir.mkdir()
        entry = {"id": "wrong-id", "path": f"pieces/{piece_dir.name}"}
        assert entry["id"] != pathlib.Path(entry["path"]).name

    def test_nonexistent_thumbnail_is_not_a_file(self, tmp_path):
        ghost_thumb = tmp_path / "pieces" / "293-substrate-cracks" / "thumbnail.svg"
        assert not ghost_thumb.is_file()

    def test_empty_string_not_a_valid_piece_id(self):
        pieces = json.loads(PIECES_JSON.read_text())
        ids = [p["id"] for p in pieces]
        assert "" not in ids
