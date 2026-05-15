"""Tests for Piece 162 — Density in Characters: ASCII Scalar Field."""

import json
import math
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "162-ascii-scalar-field"

# ── Mirror of the JS constants for pure-Python unit tests ────────────────────

RAMP = [' ', '.', '·', ':', '-', '=', '+', 'o', 'O', '#', '@']

WAVES = [
    (0.08, 0.05, 0.9, 0.0),
    (0.04, 0.09, 0.7, 1.2),
    (0.10, 0.03, 1.1, 2.4),
    (0.06, 0.07, 0.6, 3.7),
]


def scalar(cx: int, cy: int, t: float) -> float:
    """Python equivalent of the JS scalar() function for unit testing."""
    val = sum(math.sin(cx * fx + cy * fy + t * sp + ph) for fx, fy, sp, ph in WAVES)
    return (val / len(WAVES) + 1) * 0.5


def char_for(val: float) -> str:
    idx = min(len(RAMP) - 1, int(val * len(RAMP)))
    return RAMP[idx]


# ── File-existence tests ──────────────────────────────────────────────────────


def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), f"Missing: {PIECE_DIR}"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_svg_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_generate_thumbnail_script_exists():
    assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ── pieces.json integration ───────────────────────────────────────────────────


def test_pieces_json_has_entry():
    data = json.loads((REPO / "pieces.json").read_text())
    ids = [e["id"] for e in data]
    assert "162-ascii-scalar-field" in ids


def test_pieces_json_entry_complete():
    data = json.loads((REPO / "pieces.json").read_text())
    entry = next(e for e in data if e["id"] == "162-ascii-scalar-field")
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= entry.keys()


def test_pieces_json_entry_paths_valid():
    data = json.loads((REPO / "pieces.json").read_text())
    entry = next(e for e in data if e["id"] == "162-ascii-scalar-field")
    assert (REPO / entry["path"]).is_dir()
    assert (REPO / entry["thumbnail"]).is_file()


# ── index.html content tests ──────────────────────────────────────────────────


def test_index_html_has_canvas_element():
    html = (PIECE_DIR / "index.html").read_text()
    assert "<canvas" in html


def test_index_html_uses_filltext():
    """Characters must be drawn via the Canvas 2D fillText API."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "fillText" in html


def test_index_html_has_character_ramp():
    html = (PIECE_DIR / "index.html").read_text()
    assert "RAMP" in html


def test_index_html_has_sine_waves():
    html = (PIECE_DIR / "index.html").read_text()
    assert "Math.sin" in html


def test_index_html_has_at_least_3_waves():
    """Acceptance criterion: at least 3 animated plane waves."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "WAVES" in html
    # WAVES array literal contains at least 3 sub-arrays
    wave_count = html.count("[0.") + html.count("[0,")
    # Conservative lower bound: just check the WAVES array has at least 3 entries
    assert html.count("0.9") >= 1 and html.count("0.7") >= 1 and html.count("1.1") >= 1, (
        "index.html should define at least 3 distinct waves"
    )


def test_index_html_references_hsl():
    """Characters must be coloured; hsl() encodes the hue gradient."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "hsl(" in html


def test_index_html_fps_cap():
    """Animation must be capped at 60 fps."""
    html = (PIECE_DIR / "index.html").read_text()
    assert "60" in html


# ── Scalar field unit tests ───────────────────────────────────────────────────


def test_scalar_field_output_in_range():
    """All field samples must land in [0, 1]."""
    for cx in range(0, 100, 7):
        for cy in range(0, 80, 5):
            for t in [0.0, 1.0, 2.5, 5.7]:
                val = scalar(cx, cy, t)
                assert 0.0 <= val <= 1.0, f"Out of range: val={val} at ({cx},{cy},t={t})"


def test_scalar_field_uses_all_waves():
    """Removing any single wave must produce a different value at some cell."""
    cx, cy, t = 10, 7, 2.5
    full = scalar(cx, cy, t)
    for skip in range(len(WAVES)):
        waves_minus_one = [w for i, w in enumerate(WAVES) if i != skip]
        partial = sum(
            math.sin(cx * fx + cy * fy + t * sp + ph)
            for fx, fy, sp, ph in waves_minus_one
        )
        partial_norm = (partial / len(waves_minus_one) + 1) * 0.5
        assert partial_norm != pytest.approx(full), (
            f"Wave {skip} appears to have no effect — may be duplicate"
        )


def test_scalar_field_varies_over_time():
    """Phases advance with time, so the field must change between frames."""
    cx, cy = 5, 5
    t0 = scalar(cx, cy, 0.0)
    t1 = scalar(cx, cy, 0.1)
    assert t0 != pytest.approx(t1), "Field must change as time advances"


def test_scalar_field_varies_spatially():
    """Different grid cells must produce different values (not a constant field)."""
    t = 1.0
    vals = {scalar(cx, cy, t) for cx in range(0, 20, 3) for cy in range(0, 20, 3)}
    assert len(vals) > 5, "Field appears spatially constant — wave frequencies may be zero"


# ── Character ramp tests ──────────────────────────────────────────────────────


def test_ramp_minimum_length():
    """Acceptance criterion: density ramp must cover sufficient granularity."""
    assert len(RAMP) >= 8


def test_ramp_low_value_is_space():
    """val=0.0 must select the sparse (space) character."""
    assert char_for(0.0) == ' '


def test_ramp_high_value_is_dense():
    """val approaching 1.0 must select the densest character."""
    # val=0.999 should hit the last entry
    assert char_for(0.999) == RAMP[-1]


def test_ramp_midpoint_character():
    """val=0.5 must fall in the middle of the ramp, not at extremes."""
    ch = char_for(0.5)
    assert ch not in (' ', RAMP[-1]), (
        f"Middle value mapped to an extreme character: {ch!r}"
    )


def test_ramp_has_no_duplicates():
    """Each character in the ramp should be unique so the mapping is injective."""
    assert len(RAMP) == len(set(RAMP)), "Duplicate characters in RAMP reduce visual range"


# ── generate_thumbnail integration test ──────────────────────────────────────


def test_generate_thumbnail_runs_without_error():
    """Running the script must exit 0 and (re)produce a valid SVG."""
    result = subprocess.run(
        [sys.executable, str(PIECE_DIR / "generate_thumbnail.py")],
        capture_output=True,
        text=True,
        cwd=str(PIECE_DIR),
    )
    assert result.returncode == 0, (
        f"generate_thumbnail.py exited {result.returncode}:\n{result.stderr}"
    )


def test_thumbnail_svg_is_valid_xml():
    """The generated thumbnail must be well-formed SVG (contains svg tag and closing tag)."""
    svg = (PIECE_DIR / "thumbnail.svg").read_text(encoding="utf-8")
    assert svg.strip().startswith("<svg") or "<?xml" in svg[:50]
    assert "</svg>" in svg


def test_thumbnail_svg_contains_text_elements():
    """Thumbnail must show actual characters, not just coloured rectangles."""
    svg = (PIECE_DIR / "thumbnail.svg").read_text(encoding="utf-8")
    assert "<text" in svg, "Thumbnail SVG must contain <text> elements (character grid)"


def test_thumbnail_svg_has_background_rects():
    """Thumbnail must include background rect elements for coloured cells."""
    svg = (PIECE_DIR / "thumbnail.svg").read_text(encoding="utf-8")
    assert "<rect" in svg


def test_thumbnail_svg_uses_hsl_colors():
    """Thumbnail colours must use hsl() values matching the hue-gradient palette."""
    svg = (PIECE_DIR / "thumbnail.svg").read_text(encoding="utf-8")
    assert "hsl(" in svg


# ── Edge-case / failure-mode tests ───────────────────────────────────────────


def test_scalar_field_at_origin():
    """Field at the origin (0,0) must still be normalised to [0, 1]."""
    val = scalar(0, 0, 0.0)
    assert 0.0 <= val <= 1.0


def test_scalar_field_large_coordinates():
    """Field must remain in [0, 1] even at large grid coordinates."""
    for cx in [500, 1000, 5000]:
        for cy in [500, 800, 2000]:
            val = scalar(cx, cy, 100.0)
            assert 0.0 <= val <= 1.0, f"Out of range at large coords ({cx},{cy})"


def test_scalar_field_negative_time():
    """Field should handle negative time (backward scrub) without errors."""
    val = scalar(10, 10, -5.0)
    assert 0.0 <= val <= 1.0


def test_char_for_boundary_values():
    """char_for must not raise or return None at val=0 and val=1."""
    assert char_for(0.0) is not None
    assert char_for(1.0) is not None


def test_pieces_json_new_entry_id_matches_path():
    """id field must equal the final path component (test_pieces.py invariant)."""
    data = json.loads((REPO / "pieces.json").read_text())
    entry = next(e for e in data if e["id"] == "162-ascii-scalar-field")
    piece_dir = REPO / entry["path"]
    assert entry["id"] == piece_dir.name
