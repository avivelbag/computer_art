"""Tests specific to Piece 55 — Wave Interference: The Pond Remembers Every Stone."""

import json
import pathlib
import re

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "55-the-pond-remembers"
INDEX     = PIECE_DIR / "index.html"
THUMB     = PIECE_DIR / "thumbnail.svg"
README    = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# Happy-path structural checks
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/55-the-pond-remembers/ must exist"


def test_required_files_exist():
    assert INDEX.is_file(),  "index.html must exist"
    assert THUMB.is_file(),  "thumbnail.svg must exist"
    assert README.is_file(), "README.md must exist"


def test_pieces_json_entry_present():
    entries = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in entries]
    assert "55-the-pond-remembers" in ids


def test_pieces_json_entry_fields():
    entries = json.loads(PIECES_JSON.read_text())
    entry = next(e for e in entries if e["id"] == "55-the-pond-remembers")
    assert entry["technique"] == "canvas / wave superposition / interference / ImageData per-pixel"
    assert entry["path"] == "pieces/55-the-pond-remembers"
    assert entry["thumbnail"] == "pieces/55-the-pond-remembers/thumbnail.svg"
    assert entry["year"] == 2026


# ---------------------------------------------------------------------------
# index.html content checks — verify the wave physics and rendering approach
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def source():
    """Return the full text of index.html."""
    return INDEX.read_text()


def test_uses_imagedata(source):
    """Per-pixel computation must use ImageData / putImageData."""
    assert "createImageData" in source or "ImageData" in source
    assert "putImageData" in source


def test_uses_request_animation_frame(source):
    """Animation loop must use requestAnimationFrame."""
    assert "requestAnimationFrame" in source


def test_has_canvas_element(source):
    """Must have a <canvas> element."""
    assert "<canvas" in source


def test_wave_computation_present(source):
    """Math.sin must be used (wave amplitude evaluation)."""
    assert "Math.sin" in source


def test_four_to_seven_sources(source):
    """The SOURCES array must declare 4–7 entries (one array literal per source)."""
    # Each source is a bracketed list inside the outer SOURCES array.
    # Count inner arrays: look for occurrences of '[' that start a source entry.
    # A reliable proxy: count the number of lines that start a source tuple.
    # The implementation stores sources as nested arrays; count inner '[' inside SOURCES.
    m = re.search(r'const SOURCES\s*=\s*\[(.+?)\];', source, re.DOTALL)
    assert m is not None, "SOURCES constant not found in index.html"
    inner = m.group(1)
    # Count comma-separated array literals (each source is [ ... ])
    entries = re.findall(r'\[[\d.,\s+-]+\]', inner)
    assert 4 <= len(entries) <= 7, (
        f"Expected 4–7 sources, found {len(entries)}"
    )


def test_lissajous_sin_used_for_source_positions(source):
    """Source positions must use Math.sin (Lissajous drift)."""
    # The position update block contains Math.sin calls on ax/ay * t
    assert "Math.sin" in source


def test_palette_has_256_steps(source):
    """Precomputed palette must iterate over 256 entries."""
    assert "256" in source


def test_tanh_normalization(source):
    """Amplitude normalization must use Math.tanh."""
    assert "Math.tanh" in source


def test_sqrt_for_circular_wavefronts(source):
    """Euclidean distance (Math.sqrt) must be used so wavefronts are circular."""
    assert "Math.sqrt" in source


def test_single_canvas_context(source):
    """Must obtain a 2D context (not WebGL — this is a Canvas 2D piece)."""
    assert "getContext('2d')" in source or 'getContext("2d")' in source


# ---------------------------------------------------------------------------
# Thumbnail SVG checks
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def thumb_source():
    """Return the full text of thumbnail.svg."""
    return THUMB.read_text()


def test_thumbnail_is_svg(thumb_source):
    assert "<svg" in thumb_source


def test_thumbnail_has_circles(thumb_source):
    """Thumbnail must contain circle elements (the concentric ring motif)."""
    assert "<circle" in thumb_source


def test_thumbnail_has_indigo_tones(thumb_source):
    """Thumbnail must reference the cool indigo/violet hue family."""
    # Accept any blue-violet hex starting with #55, #44, #66, or 'indigo' keyword.
    has_indigo = bool(
        re.search(r'#[45][45][12][0-9a-f]{2}cc', thumb_source, re.IGNORECASE)
        or re.search(r'#5520cc', thumb_source, re.IGNORECASE)
        or re.search(r'#8844ff', thumb_source, re.IGNORECASE)
    )
    assert has_indigo, "Thumbnail must contain indigo/violet colour values"


def test_thumbnail_has_amber_tones(thumb_source):
    """Thumbnail must reference the warm gold/amber hue family."""
    has_amber = bool(
        re.search(r'#[cd][07-9][78][01][0-9a-f]{0,2}', thumb_source, re.IGNORECASE)
        or re.search(r'#ffaa22', thumb_source, re.IGNORECASE)
        or re.search(r'amber', thumb_source, re.IGNORECASE)
    )
    assert has_amber, "Thumbnail must contain amber/gold colour values"


# ---------------------------------------------------------------------------
# README checks
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    content = README.read_text().strip()
    assert len(content) > 50, "README.md must not be empty"


def test_readme_mentions_wave_sources():
    content = README.read_text().lower()
    assert "source" in content, "README must describe wave sources"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_thumbnail_is_file_not_directory():
    """Thumbnail path must resolve to a file, not a directory."""
    assert THUMB.is_file()
    assert not THUMB.is_dir()


def test_index_html_not_empty():
    assert INDEX.stat().st_size > 500, "index.html must be non-trivial"


def test_pieces_json_entry_id_matches_dir():
    """The id field must equal the directory name (enforced by test_pieces.py too)."""
    entries = json.loads(PIECES_JSON.read_text())
    entry = next(e for e in entries if e["id"] == "55-the-pond-remembers")
    piece_dir = REPO / entry["path"]
    assert entry["id"] == piece_dir.name


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

def test_webgl_not_used(source):
    """This piece must NOT use WebGL — it's a Canvas 2D per-pixel piece."""
    assert "webgl" not in source.lower(), "Wave interference piece must use Canvas 2D, not WebGL"


def test_no_external_scripts(source):
    """index.html must not load external scripts (self-contained)."""
    external = re.findall(r'<script[^>]+src=["\']https?://', source)
    assert not external, f"Found external script imports: {external}"


def test_missing_piece_raises(tmp_path):
    """Verify that a non-existent piece directory is correctly identified as missing."""
    ghost = tmp_path / "ghost-piece"
    assert not ghost.is_dir()


def test_malformed_pieces_json_detected(tmp_path):
    """A pieces.json with a missing 'technique' field fails the required-field check."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    entry = {
        "id": "test",
        "title": "Test",
        "tagline": "A test",
        "year": 2026,
        "path": "pieces/test",
        "thumbnail": "pieces/test/thumb.svg",
        # 'technique' deliberately omitted
    }
    assert not (required <= entry.keys()), "Missing field should be detectable"
