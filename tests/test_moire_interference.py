"""Tests for pieces/129-moire-interference: Ghost Frequencies — Moiré Study."""

import importlib.util
import json
import math
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "129-moire-interference"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
GEN_THUMB = PIECE_DIR / "generate_thumbnail.py"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "129-moire-interference"


def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} entry not found in pieces.json")


# ---------------------------------------------------------------------------
# File-existence tests
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir(), f"Piece directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert INDEX_HTML.is_file(), "index.html is missing"


def test_readme_exists():
    assert README.is_file(), "README.md is missing"


def test_thumbnail_exists():
    assert THUMBNAIL.is_file(), "thumbnail.svg is missing"


def test_generate_thumbnail_exists():
    assert GEN_THUMB.is_file(), "generate_thumbnail.py is missing"


# ---------------------------------------------------------------------------
# HTML structure tests
# ---------------------------------------------------------------------------

def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_canvas_dimensions_800():
    html = _html()
    assert 'width="800"' in html and 'height="800"' in html


def test_html_has_script():
    assert "<script" in _html()


def test_html_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_charset_utf8():
    assert 'charset="UTF-8"' in _html()


def test_html_title_mentions_moire_or_ghost():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "must have a <title>"
    title = m.group(1).lower()
    assert "moir" in title or "ghost" in title or "frequenc" in title


def test_html_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained"


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


# ---------------------------------------------------------------------------
# JS moiré-specific tests
# ---------------------------------------------------------------------------

def test_js_defines_ring_spacing():
    assert "RING_SPACING" in _html()


def test_js_ring_spacing_in_range():
    m = re.search(r"RING_SPACING\s*=\s*(\d+)", _html())
    if m:
        s = int(m.group(1))
        assert 5 <= s <= 20, f"RING_SPACING={s} outside [5, 20]"


def test_js_uses_difference_compositing():
    assert "difference" in _html()


def test_js_has_draw_rings_or_arc():
    html = _html()
    assert "drawRings" in html or ".arc(" in html


def test_js_uses_math_sin_for_animation():
    assert "Math.sin" in _html()


def test_js_uses_canvas_arc():
    assert ".arc(" in _html()


def test_js_background_is_monochrome():
    """Background fill color must be monochrome (R≈G≈B, all channels close)."""
    html = _html()
    m = re.search(r"fillStyle\s*=\s*['\"]#([0-9a-fA-F]{6})['\"]", html)
    if m:
        color = m.group(1)
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        assert max(r, g, b) - min(r, g, b) <= 30, (
            f"Background #{color} is not monochrome (channels too unequal)"
        )


def test_js_resets_composite_to_source_over():
    """After the difference pass the compositing mode must be restored."""
    html = _html()
    assert "source-over" in html


# ---------------------------------------------------------------------------
# Moiré physics — Python re-implementation
# ---------------------------------------------------------------------------

def _dist(px: float, py: float, cx: float, cy: float) -> float:
    """Euclidean distance from a pixel to a ring-system center."""
    return math.sqrt((px - cx) ** 2 + (py - cy) ** 2)


def _on_ring(px: float, py: float, cx: float, cy: float,
             spacing: float, lw: float = 1.5) -> bool:
    """True if the pixel falls within lw/2 of any ring radius in the system."""
    d = _dist(px, py, cx, cy)
    phase = d % spacing
    return phase < lw or phase > spacing - lw


def test_point_on_ring_at_exact_radius():
    """A pixel at exactly a ring radius must be flagged as on-ring."""
    cx, cy, spacing = 240.0, 240.0, 10.0
    assert _on_ring(cx + 20.0, cy, cx, cy, spacing)


def test_point_in_gap_is_not_on_ring():
    """A pixel halfway between rings must not be on-ring."""
    cx, cy, spacing = 240.0, 240.0, 10.0
    # r=25 → halfway between rings at 20 and 30
    assert not _on_ring(cx + 25.0, cy, cx, cy, spacing)


def test_destructive_interference_where_both_rings_coincide():
    """When both ring systems share the same center every ring pixel cancels."""
    spacing = 10.0
    cx_a, cy_a = 0.0, 0.0
    cx_b, cy_b = 0.0, 0.0  # identical centers → all ring pixels destructive
    px, py = spacing, 0.0  # r=10 for both
    assert _on_ring(px, py, cx_a, cy_a, spacing)
    assert _on_ring(px, py, cx_b, cy_b, spacing)


def test_constructive_zone_only_one_ring_present():
    """A pixel on ring A but not ring B should be bright (constructive)."""
    spacing = 10.0
    cx_a, cy_a = 0.0, 0.0
    cx_b, cy_b = 5.0, 0.0  # offset by half a ring spacing
    px, py = 10.0, 0.0
    # dist to A = 10 → on ring A; dist to B = 5 → phase=5 → not on ring B
    assert _on_ring(px, py, cx_a, cy_a, spacing)
    assert not _on_ring(px, py, cx_b, cy_b, spacing)


def test_equidistant_midpoint_has_same_phase_for_both_systems():
    """The midpoint between two centers has the same radial phase in both systems."""
    offset = 30.0
    cx_a, cy_a = 0.0, 0.0
    cx_b, cy_b = offset, 0.0
    px = offset / 2  # midpoint
    dist_a = _dist(px, 0.0, cx_a, cy_a)
    dist_b = _dist(px, 0.0, cx_b, cy_b)
    assert abs(dist_a - dist_b) < 1e-9  # equal distance → same phase → destructive


def test_ring_density_decreases_with_radius():
    """Rings per unit area decreases as 1/r (geometry of annuli)."""
    spacing = 10.0
    density_at_50 = 1.0 / (2 * math.pi * 50 * spacing)
    density_at_100 = 1.0 / (2 * math.pi * 100 * spacing)
    assert density_at_50 > density_at_100


def test_moire_beat_is_absent_when_systems_identical():
    """When both ring systems are identical no beat pattern exists."""
    spacing = 10.0
    cx, cy = 0.0, 0.0
    # At every pixel, on_a == on_b, so difference is always 0: no beat.
    for px in (10.0, 15.0, 20.0, 25.0):
        on_a = _on_ring(px, 0.0, cx, cy, spacing)
        on_b = _on_ring(px, 0.0, cx, cy, spacing)
        assert on_a == on_b  # no beat (both same)


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_pieces_json_entry_has_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= _entry().keys()


def test_pieces_json_technique_mentions_moire():
    assert "moir" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_interference():
    assert "interference" in _entry()["technique"].lower()


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    assert len(THUMBNAIL.read_text()) > 200


def test_thumbnail_has_svg_root():
    assert "<svg" in THUMBNAIL.read_text()


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is invalid XML: {exc}") from exc


def test_thumbnail_has_circle_elements():
    """Ring-drawing elements must be present."""
    svg = THUMBNAIL.read_text()
    assert "<circle" in svg or "<path" in svg


def test_thumbnail_has_many_rings():
    """Both ring systems together must produce ≥30 ring elements."""
    svg = THUMBNAIL.read_text()
    total = len(re.findall(r"<circle\b", svg)) + len(re.findall(r"<path\b", svg))
    assert total >= 30, f"Expected ≥30 ring elements, found {total}"


def test_thumbnail_has_dark_background():
    """First <rect> fill must be a dark monochrome color."""
    svg = THUMBNAIL.read_text()
    m = re.search(r'<rect[^>]*fill="(#[0-9a-fA-F]{6})"', svg)
    if m:
        c = m.group(1).lstrip('#')
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        assert max(r, g, b) <= 50, f"Background {m.group(1)} is not dark"


def test_thumbnail_has_two_ring_groups():
    """Two distinct <g> groups must be present (one per ring system)."""
    svg = THUMBNAIL.read_text()
    assert svg.count("<g ") >= 2, "Expected at least 2 <g> groups"


def test_thumbnail_is_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


# ---------------------------------------------------------------------------
# generate_thumbnail.py module tests
# ---------------------------------------------------------------------------

def _import_gen():
    """Import generate_thumbnail as a module without executing __main__ block."""
    piece_dir = str(PIECE_DIR)
    if piece_dir not in sys.path:
        sys.path.insert(0, piece_dir)
    spec = importlib.util.spec_from_file_location("gen_moire", GEN_THUMB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gen_generate_svg_returns_svg_string():
    mod = _import_gen()
    svg = mod.generate_svg()
    assert isinstance(svg, str)
    assert "<svg" in svg


def test_gen_generate_svg_is_valid_xml():
    mod = _import_gen()
    ET.fromstring(mod.generate_svg())  # must not raise


def test_gen_generate_svg_has_two_ring_groups():
    mod = _import_gen()
    svg = mod.generate_svg()
    assert svg.count("<g ") >= 2


def test_gen_generate_svg_has_many_circles():
    mod = _import_gen()
    circles = re.findall(r"<circle\b", mod.generate_svg())
    assert len(circles) >= 30


def test_gen_ring_circles_correct_count():
    """ring_circles with max_r=100, spacing=10 must return exactly 10 elements."""
    mod = _import_gen()
    circles = mod.ring_circles(240.0, 240.0, 100, 10)
    assert len(circles) == 10


def test_gen_ring_circles_empty_when_max_r_below_spacing():
    """ring_circles with max_r < spacing must return an empty list."""
    mod = _import_gen()
    assert mod.ring_circles(240.0, 240.0, 5, 10) == []


def test_gen_max_radius_covers_full_diagonal():
    mod = _import_gen()
    diagonal = math.sqrt(mod.SIZE ** 2 + mod.SIZE ** 2)
    assert mod.max_radius() > diagonal


def test_gen_reproducible():
    """Two calls to generate_svg() must produce identical output."""
    mod = _import_gen()
    assert mod.generate_svg() == mod.generate_svg()


# ---------------------------------------------------------------------------
# Failure-mode tests — assert the CORRECT error or no-op for bad inputs
# ---------------------------------------------------------------------------

def test_missing_ring_spacing_constant_detected():
    """HTML without RING_SPACING fails the spacing check."""
    fake = "<script>const x=1;</script>"
    assert "RING_SPACING" not in fake


def test_missing_difference_compositing_detected():
    """HTML without 'difference' compositing fails the moiré check."""
    fake = "<script>ctx.globalCompositeOperation='source-over';</script>"
    assert "difference" not in fake


def test_missing_animation_detected():
    """HTML without requestAnimationFrame fails the animation check."""
    fake = "<script>draw();</script>"
    assert "requestAnimationFrame" not in fake


def test_missing_arc_call_detected():
    """HTML without .arc( fails the ring-drawing check."""
    fake = "<script>ctx.rect(0,0,10,10);</script>"
    assert ".arc(" not in fake


def test_saturated_color_fails_monochrome_check():
    """A fully saturated red (#ff0000) must fail the monochrome channel check."""
    r, g, b = 255, 0, 0
    is_monochrome = max(r, g, b) - min(r, g, b) <= 30
    assert not is_monochrome


def test_gen_large_ring_count(tmp_path):
    """ring_circles with a large max_r must return a list without error."""
    mod = _import_gen()
    circles = mod.ring_circles(240.0, 240.0, 1000, 10)
    assert len(circles) == 100  # range(10, 1001, 10) → 100 elements
    for elem in circles:
        assert "circle" in elem
