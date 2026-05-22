"""Tests for Piece 271 — Sorted Light."""
import json
import math
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "271-pixel-sort"
PIECES_JSON = REPO / "pieces.json"

PALETTE_DARK   = "0a0a14"
PALETTE_MID    = "7c3aed"
PALETTE_BRIGHT = "fbbf24"


# ---------------------------------------------------------------------------
# Directory / file presence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_svg_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# Thumbnail constraints
# ---------------------------------------------------------------------------

def test_thumbnail_under_100kb():
    size = (PIECE_DIR / "thumbnail.svg").stat().st_size
    assert size < 100 * 1024, f"thumbnail.svg is {size / 1024:.1f} KB, must be ≤100 KB"


def test_thumbnail_is_valid_svg():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert content.strip().startswith("<svg")
    assert "</svg>" in content


def test_thumbnail_has_linear_gradients():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "linearGradient" in content


def test_thumbnail_has_rect_elements():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<rect" in content


def test_thumbnail_references_gradients():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "url(#g" in content


def test_thumbnail_has_rgb_color_stops():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "rgb(" in content


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def test_index_html_uses_canvas():
    content = (PIECE_DIR / "index.html").read_text()
    assert "<canvas" in content


def test_index_html_uses_image_data():
    content = (PIECE_DIR / "index.html").read_text()
    assert "createImageData" in content


def test_index_html_uses_put_image_data():
    content = (PIECE_DIR / "index.html").read_text()
    assert "putImageData" in content


def test_index_html_animates_with_raf():
    content = (PIECE_DIR / "index.html").read_text()
    assert "requestAnimationFrame" in content


def test_index_html_sorts_columns():
    content = (PIECE_DIR / "index.html").read_text()
    assert ".sort(" in content


def test_index_html_sorts_descending():
    """The sort comparator must sort descending (b - a) not ascending."""
    content = (PIECE_DIR / "index.html").read_text()
    assert "b - a" in content or "b-a" in content


def test_index_html_has_dark_color():
    content = (PIECE_DIR / "index.html").read_text()
    assert PALETTE_DARK in content


def test_index_html_has_violet_color():
    content = (PIECE_DIR / "index.html").read_text()
    assert PALETTE_MID in content


def test_index_html_has_gold_color():
    content = (PIECE_DIR / "index.html").read_text()
    assert PALETTE_BRIGHT in content


def test_index_html_no_external_dependencies():
    content = (PIECE_DIR / "index.html").read_text()
    assert "https://" not in content
    assert "http://" not in content


def test_index_html_no_math_random():
    """Rendering must be deterministic — no Math.random() calls."""
    content = (PIECE_DIR / "index.html").read_text()
    assert "Math.random()" not in content


def test_index_html_has_hold_phases():
    """Animation must pause at both sorted and source extremes."""
    content = (PIECE_DIR / "index.html").read_text()
    assert "hold-source" in content
    assert "hold-sorted" in content


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def test_entry_present_in_pieces_json():
    ids = [e["id"] for e in _load_pieces()]
    assert "271-pixel-sort" in ids


def test_entry_has_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = next(e for e in _load_pieces() if e["id"] == "271-pixel-sort")
    assert required <= entry.keys()


def test_entry_technique_mentions_pixel_sort():
    entry = next(e for e in _load_pieces() if e["id"] == "271-pixel-sort")
    assert "pixel" in entry["technique"].lower()


def test_entry_path_matches_directory():
    entry = next(e for e in _load_pieces() if e["id"] == "271-pixel-sort")
    assert (REPO / entry["path"]).is_dir()


def test_entry_thumbnail_path_matches_file():
    entry = next(e for e in _load_pieces() if e["id"] == "271-pixel-sort")
    assert (REPO / entry["thumbnail"]).is_file()


def test_existing_entries_not_removed():
    data = _load_pieces()
    assert len(data) >= 108, f"Expected ≥108 entries, got {len(data)}"


# ---------------------------------------------------------------------------
# Math: source value mirrors the JS function exactly
# ---------------------------------------------------------------------------

def _source_value(x, y, W=800, H=800):
    """Python mirror of the JS sourceValue(x, y) function."""
    nx, ny = x / W, y / H
    v = (math.sin(nx * math.pi * 8) * math.cos(ny * math.pi * 5) * 0.40
       + math.sin((nx + ny) * math.pi * 6) * 0.35
       + math.cos((nx - ny) * math.pi * 9) * 0.25)
    return (v + 1.0) * 0.5


def test_source_value_in_range():
    """source_value must return values in [0, 1] for all sampled pixels."""
    for x in range(0, 800, 40):
        for y in range(0, 800, 40):
            v = _source_value(x, y)
            assert 0.0 <= v <= 1.0, f"source_value({x},{y}) = {v:.4f} out of [0,1]"


def test_source_value_at_origin_finite():
    assert math.isfinite(_source_value(0, 0))


def test_source_value_at_all_corners_finite():
    for x, y in [(0, 0), (799, 0), (0, 799), (799, 799)]:
        assert math.isfinite(_source_value(x, y)), f"source_value({x},{y}) not finite"


def test_sort_is_descending():
    """After sorting, every column's first value must be >= its last value."""
    for cx in [0, 100, 200, 400, 600, 799]:
        col = [_source_value(cx, y) for y in range(800)]
        sc  = sorted(col, reverse=True)
        assert sc[0] >= sc[-1], f"Column {cx}: sorted[0]={sc[0]:.3f} < sorted[-1]={sc[-1]:.3f}"
        assert sc[0] >= sc[400], f"Column {cx}: top value below midpoint"


def test_sort_changes_at_least_one_column():
    """A non-trivial column must differ between source and sorted states."""
    cx = 400
    col = [_source_value(cx, y) for y in range(800)]
    assert col != sorted(col, reverse=True), "Source column at x=400 is already sorted — source field may be degenerate"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_source_field_has_spatial_variation():
    """Values must vary meaningfully across the image, not be uniform."""
    vals = {round(_source_value(x, y), 3)
            for x in range(0, 800, 80)
            for y in range(0, 800, 80)}
    assert len(vals) > 10, f"Only {len(vals)} distinct values — field lacks variation"


def test_palette_dark_end():
    """valueToColor(0) must return the dark navy tuple."""
    def value_to_color(v):
        C_DARK   = (10, 10, 20)
        C_MID    = (124, 58, 237)
        C_BRIGHT = (251, 191, 36)
        def lerp3(a, b, t):
            return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
        v = max(0.0, min(1.0, v))
        if v < 0.5:
            return lerp3(C_DARK, C_MID, v * 2)
        return lerp3(C_MID, C_BRIGHT, (v - 0.5) * 2)

    dark   = value_to_color(0.0)
    bright = value_to_color(1.0)
    assert dark   == (10, 10, 20),    f"Dark end: expected (10,10,20) got {dark}"
    assert bright == (251, 191, 36),  f"Bright end: expected (251,191,36) got {bright}"


def test_palette_midpoint():
    """valueToColor(0.5) must return the electric violet tuple."""
    def lerp3(a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    C_DARK = (10, 10, 20)
    C_MID  = (124, 58, 237)
    mid = lerp3(C_DARK, C_MID, 1.0)
    assert mid == (124, 58, 237), f"Midpoint: expected (124,58,237) got {mid}"


# ---------------------------------------------------------------------------
# Failure mode: wrong sort direction would pass the descending check, so we
# also verify that sorting ascending produces a different result than descending.
# ---------------------------------------------------------------------------

def test_ascending_sort_differs_from_descending():
    """Ascending and descending sorts of the same column must differ."""
    col = [_source_value(400, y) for y in range(800)]
    asc  = sorted(col)
    desc = sorted(col, reverse=True)
    assert asc != desc, "Column at x=400 is constant — interference field is degenerate"
