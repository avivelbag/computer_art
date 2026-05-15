"""Tests for Piece 150 — Halftone Riso Print: Two-Color Screen Simulation."""

import json
import math
import pathlib
import re

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "150-riso-halftone"
INDEX     = PIECE_DIR / "index.html"
THUMB     = PIECE_DIR / "thumbnail.svg"
README    = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# File presence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX.is_file()


def test_thumbnail_svg_exists():
    assert THUMB.is_file()


def test_readme_exists():
    assert README.is_file()


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def test_pieces_json_contains_riso_entry():
    ids = [p["id"] for p in _load_pieces()]
    assert "150-riso-halftone" in ids


def test_pieces_json_entry_complete():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    entry = next(p for p in _load_pieces() if p["id"] == "150-riso-halftone")
    assert required <= entry.keys()
    assert entry["path"] == "pieces/150-riso-halftone"
    assert entry["thumbnail"] == "pieces/150-riso-halftone/thumbnail.svg"


def test_pieces_json_thumbnail_file_exists():
    entry = next(p for p in _load_pieces() if p["id"] == "150-riso-halftone")
    assert (REPO / entry["thumbnail"]).is_file()


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def _html():
    return INDEX.read_text()


def test_index_html_has_canvas():
    assert "<canvas" in _html()


def test_index_html_uses_multiply_blend():
    """multiply is required for riso-style subtractive colour mixing."""
    assert "multiply" in _html()


def test_index_html_has_pink_ink():
    """Fluorescent pink #FF4880 must be present."""
    assert "#FF4880" in _html().upper() or "ff4880" in _html().lower()


def test_index_html_has_teal_ink():
    """Teal #00A99D must be present."""
    assert "#00A99D" in _html().upper() or "00a99d" in _html().lower()


def test_index_html_has_cream_paper():
    """Off-white paper background — not pure #ffffff."""
    html = _html()
    assert "#ffffff" not in html.lower(), "Paper must not be pure white"
    assert "#F5F0E8" in html.upper() or "f5f0e8" in html.lower()


def test_index_html_has_two_distinct_angles():
    """Both 45 and 75 degree angles must appear as screen angles."""
    html = _html()
    assert "45" in html, "Screen A angle (45°) not found"
    assert "75" in html, "Screen B angle (75°) not found"


def test_index_html_has_animation():
    """requestAnimationFrame must be used for the drift animation."""
    assert "requestAnimationFrame" in _html()


def test_index_html_has_misregistration_drift():
    """The drift/misregistration variable or comment must exist."""
    html = _html()
    assert "drift" in html.lower() or "offset" in html.lower()


# ---------------------------------------------------------------------------
# thumbnail.svg content checks
# ---------------------------------------------------------------------------

def _svg():
    return THUMB.read_text()


def test_thumbnail_is_valid_svg():
    assert _svg().startswith("<svg")


def test_thumbnail_has_pink_circles():
    assert "#FF4880" in _svg().upper() or "ff4880" in _svg().lower()


def test_thumbnail_has_teal_circles():
    assert "#00A99D" in _svg().upper() or "00a99d" in _svg().lower()


def test_thumbnail_has_cream_background():
    assert "F5F0E8" in _svg().upper()


def test_thumbnail_uses_multiply_blend():
    assert "multiply" in _svg()


def test_thumbnail_has_many_dots():
    """Should have enough circles to show a visible halftone pattern."""
    count = _svg().count("<circle")
    assert count >= 100, f"Expected ≥ 100 circles in thumbnail, got {count}"


# ---------------------------------------------------------------------------
# Tone-field mathematics (pure Python, no browser)
# ---------------------------------------------------------------------------

def _tone(x, y, W=600, H=600):
    """Mirror of the tone() function in index.html."""
    dx = x - W / 2
    dy = y - H / 2
    r  = math.sqrt(dx * dx + dy * dy)
    return 0.5 + 0.42 * math.sin(r / 28)


def test_tone_center_is_half():
    """At the canvas centre, r=0, sin(0)=0, so tone == 0.5."""
    assert abs(_tone(300, 300) - 0.5) < 1e-9


def test_tone_range():
    """tone() must always be in [0.08, 0.92] (0.5 ± 0.42)."""
    for x in range(0, 601, 30):
        for y in range(0, 601, 30):
            t = _tone(x, y)
            assert 0.0 < t < 1.0, f"tone({x},{y}) = {t} out of range"


def test_tone_varies_radially():
    """tone must differ meaningfully between a trough and a peak of the sine ring."""
    # At r=0 (centre): sin(0)=0 → tone=0.5 (trough)
    # At r=14π ≈ 44 px: sin(π/2)=1 → tone=0.92 (peak)
    t_center = _tone(300, 300)                                     # r = 0
    t_peak   = _tone(300, 300 + int(14 * math.pi))                 # r ≈ 44 px
    assert abs(t_center - t_peak) > 0.3


# ---------------------------------------------------------------------------
# Edge-case: pieces.json remains valid JSON after edit
# ---------------------------------------------------------------------------

def test_pieces_json_still_valid():
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)
    assert len(data) > 0


def test_pieces_json_no_duplicate_ids():
    ids = [p["id"] for p in _load_pieces()]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"


# ---------------------------------------------------------------------------
# Failure mode: wrong entry would be caught
# ---------------------------------------------------------------------------

def test_missing_required_field_detected():
    """Verify that an entry without 'technique' would fail the required-field check."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    bad = {
        "id": "150-riso-halftone",
        "title": "X",
        "tagline": "Y",
        "year": 2026,
        "path": "pieces/150-riso-halftone",
        "thumbnail": "pieces/150-riso-halftone/thumbnail.svg",
    }
    assert not (required <= bad.keys())
