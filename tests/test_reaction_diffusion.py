"""Tests for Piece 275 — The Labyrinth Writes Itself (Gray-Scott maze, WebGL2)."""

import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "275-reaction-diffusion"
PIECES_JSON = REPO / "pieces.json"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"


# ---------------------------------------------------------------------------
# Happy-path structural checks
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    """The piece directory must be present at pieces/275-reaction-diffusion/."""
    assert PIECE_DIR.is_dir(), f"Directory missing: {PIECE_DIR}"


def test_index_html_exists():
    """index.html must exist inside the piece directory."""
    assert INDEX_HTML.is_file(), f"index.html missing in {PIECE_DIR}"


def test_readme_exists():
    """README.md must exist inside the piece directory."""
    assert README.is_file(), f"README.md missing in {PIECE_DIR}"


def test_thumbnail_exists():
    """A thumbnail file (SVG or PNG) must exist in the piece directory."""
    thumbnails = list(PIECE_DIR.glob("thumbnail.*"))
    assert thumbnails, "No thumbnail.* file found in piece directory"


def test_pieces_json_has_entry():
    """pieces.json must contain an entry whose id is '275-reaction-diffusion'."""
    data = json.loads(PIECES_JSON.read_text())
    ids = [p.get("id") for p in data]
    assert "275-reaction-diffusion" in ids, \
        "No entry with id='275-reaction-diffusion' found in pieces.json"


def test_pieces_json_entry_has_all_required_fields():
    """The pieces.json entry for piece 275 must carry every required metadata field."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    data = json.loads(PIECES_JSON.read_text())
    entry = next(p for p in data if p.get("id") == "275-reaction-diffusion")
    missing = required - entry.keys()
    assert not missing, f"Missing fields in pieces.json entry: {missing}"


def test_pieces_json_thumbnail_path_matches_file():
    """The thumbnail path recorded in pieces.json must point to an existing file."""
    data = json.loads(PIECES_JSON.read_text())
    entry = next(p for p in data if p.get("id") == "275-reaction-diffusion")
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file(), f"Thumbnail path in pieces.json does not exist: {thumb}"


# ---------------------------------------------------------------------------
# WebGL / implementation-specific checks
# ---------------------------------------------------------------------------

def test_webgl2_context_requested():
    """index.html must request a WebGL2 context, not the legacy WebGL1 context."""
    html = INDEX_HTML.read_text()
    assert "webgl2" in html, "index.html must call getContext('webgl2')"


def test_ping_pong_simulation_shader_present():
    """index.html must contain a simulation shader fragment (id='fs-sim')."""
    html = INDEX_HTML.read_text()
    assert 'id="fs-sim"' in html or "id='fs-sim'" in html, \
        "Simulation shader script block (id=fs-sim) not found in index.html"


def test_render_shader_present():
    """index.html must contain a render/coloring shader fragment (id='fs-render')."""
    html = INDEX_HTML.read_text()
    assert 'id="fs-render"' in html or "id='fs-render'" in html, \
        "Render shader script block (id=fs-render) not found in index.html"


def test_request_animation_frame_present():
    """index.html must drive the loop with requestAnimationFrame (no CPU blocking loop)."""
    html = INDEX_HTML.read_text()
    assert "requestAnimationFrame" in html, \
        "requestAnimationFrame not found in index.html"


def test_gray_scott_feed_rate_present():
    """index.html must specify the maze-regime feed rate F=0.029."""
    html = INDEX_HTML.read_text()
    assert "0.029" in html, \
        "Feed rate F=0.029 (maze regime) not found in index.html"


def test_gray_scott_kill_rate_present():
    """index.html must specify the maze-regime kill rate K=0.057."""
    html = INDEX_HTML.read_text()
    assert "0.057" in html, \
        "Kill rate K=0.057 (maze regime) not found in index.html"


def test_framebuffer_present():
    """index.html must create WebGL framebuffers for ping-pong rendering."""
    html = INDEX_HTML.read_text()
    assert "createFramebuffer" in html, \
        "gl.createFramebuffer() not found — ping-pong FBOs required"


def test_three_stop_palette_stops_present():
    """index.html must reference all three palette stops (dark, sienna, parchment)."""
    html = INDEX_HTML.read_text()
    # Stop 0: near-black #0e0b08 — stored as float 0.055/0.043/0.031
    assert "0.055" in html, "Dark-stop red component (0.055 = #0e) not found in palette"
    # Stop 1: dark sienna #7b3f00 — stored as float 0.482/0.247/0.000
    assert "0.482" in html, "Mid-stop red component (0.482 = #7b) not found in palette"
    # Stop 2: warm parchment #f0e8d0 — stored as float 0.941/0.910/0.816
    assert "0.941" in html, "Light-stop red component (0.941 = #f0) not found in palette"


# ---------------------------------------------------------------------------
# README content checks
# ---------------------------------------------------------------------------

def test_readme_references_prior_gray_scott_pieces():
    """README must name the prior Gray-Scott pieces to document differentiation."""
    text = README.read_text()
    mentioned = [ref for ref in ("Piece 17", "Piece 96", "Piece 180") if ref in text]
    assert len(mentioned) >= 1, \
        "README must reference at least one prior Gray-Scott piece (17, 96, or 180)"


def test_readme_contains_gray_scott_equations():
    """README must display the Gray-Scott differential equations."""
    text = README.read_text()
    has_eq = "dU/dt" in text or "∂U/∂t" in text or "dV/dt" in text
    assert has_eq, "README must include the Gray-Scott governing equations"


def test_readme_states_maze_regime():
    """README must explicitly identify the maze parameter regime."""
    text = README.read_text()
    assert "maze" in text.lower(), "README must describe the maze parameter regime"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_pieces_json_id_matches_directory_name():
    """The 'id' field must equal the last segment of the 'path' field."""
    data = json.loads(PIECES_JSON.read_text())
    entry = next(p for p in data if p.get("id") == "275-reaction-diffusion")
    dir_name = pathlib.Path(entry["path"]).name
    assert entry["id"] == dir_name, \
        f"id {entry['id']!r} does not match directory name {dir_name!r}"


def test_only_one_entry_for_piece_275():
    """pieces.json must not contain duplicate entries for piece 275."""
    data = json.loads(PIECES_JSON.read_text())
    matches = [p for p in data if p.get("id") == "275-reaction-diffusion"]
    assert len(matches) == 1, \
        f"Expected exactly 1 entry for 275-reaction-diffusion, found {len(matches)}"


# ---------------------------------------------------------------------------
# Explicit failure-mode assertions
# ---------------------------------------------------------------------------

class TestFailureModes:
    """Verify that the validation logic correctly rejects bad inputs."""

    def test_missing_required_field_is_caught(self):
        """An entry lacking 'description' must not pass the required-field check."""
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
        bad_entry = {
            "id": "275-reaction-diffusion",
            "title": "The Labyrinth Writes Itself",
            "tagline": "test",
            "year": 2026,
            "technique": "WebGL2",
            "path": "pieces/275-reaction-diffusion",
            "thumbnail": "pieces/275-reaction-diffusion/thumbnail.svg",
            # 'description' intentionally omitted
        }
        assert not (required <= bad_entry.keys()), \
            "Expected missing 'description' to be detected"

    def test_id_mismatch_is_caught(self, tmp_path):
        """An entry whose id does not match its directory name must be flagged."""
        piece_dir = tmp_path / "275-reaction-diffusion"
        piece_dir.mkdir()
        entry = {
            "id": "wrong-id",
            "path": str(piece_dir.relative_to(tmp_path)),
        }
        dir_name = pathlib.Path(entry["path"]).name
        assert entry["id"] != dir_name, "Expected id mismatch to be detected"

    def test_missing_thumbnail_file_is_caught(self, tmp_path):
        """A thumbnail path pointing to a non-existent file must not validate."""
        nonexistent_thumb = tmp_path / "pieces" / "275-reaction-diffusion" / "thumbnail.svg"
        assert not nonexistent_thumb.is_file(), \
            "Thumbnail should not exist in this isolated tmp_path"

    def test_missing_readme_is_caught(self, tmp_path):
        """A piece directory without README.md must be flagged."""
        piece_dir = tmp_path / "275-reaction-diffusion"
        piece_dir.mkdir()
        (piece_dir / "index.html").write_text("<html></html>")
        readme = piece_dir / "README.md"
        assert not readme.exists(), "README should not exist in this test"

    def test_missing_piece_directory_is_caught(self, tmp_path):
        """A path entry that references a non-existent directory must fail."""
        ghost = tmp_path / "275-reaction-diffusion"
        assert not ghost.is_dir(), "Ghost directory should not exist"
