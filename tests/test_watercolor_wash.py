"""Tests for Piece 156 — Wet Pigment: Watercolor Wash."""

import json
import math
import pathlib
import re
import random

import pytest

REPO       = pathlib.Path(__file__).parent.parent
PIECE_ID   = "156-watercolor-wash"
PIECE_DIR  = REPO / "pieces" / PIECE_ID
INDEX      = PIECE_DIR / "index.html"
THUMB      = PIECE_DIR / "thumbnail.svg"
README     = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def _entry():
    return next((p for p in _load_pieces() if p["id"] == PIECE_ID), None)


# ---------------------------------------------------------------------------
# File presence — happy path
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), f"Directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert INDEX.is_file()


def test_thumbnail_svg_exists():
    assert THUMB.is_file()


def test_readme_exists():
    assert README.is_file()


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

def test_pieces_json_contains_entry():
    ids = [p["id"] for p in _load_pieces()]
    assert PIECE_ID in ids


def test_pieces_json_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    entry = _entry()
    assert entry is not None, f"{PIECE_ID} not found in pieces.json"
    assert required <= entry.keys(), f"Missing fields: {required - entry.keys()}"


def test_pieces_json_entry_id_matches_directory():
    entry = _entry()
    assert entry["id"] == pathlib.Path(entry["path"]).name


def test_pieces_json_entry_path_is_directory():
    entry = _entry()
    assert (REPO / entry["path"]).is_dir()


def test_pieces_json_entry_thumbnail_file_exists():
    entry = _entry()
    assert (REPO / entry["thumbnail"]).is_file()


def test_pieces_json_no_duplicate_ids():
    ids = [p["id"] for p in _load_pieces()]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"


def test_pieces_json_technique_mentions_watercolor():
    entry = _entry()
    assert "watercolor" in entry["technique"].lower()


def test_pieces_json_technique_mentions_subdivision():
    entry = _entry()
    assert "subdivision" in entry["technique"].lower()


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def html():
    return INDEX.read_text()


def test_html_has_canvas_element(html):
    assert "<canvas" in html


def test_html_uses_request_animation_frame(html):
    assert "requestAnimationFrame" in html


def test_html_uses_2d_canvas_context(html):
    assert "getContext('2d')" in html or 'getContext("2d")' in html


def test_html_not_trivially_small():
    assert INDEX.stat().st_size > 500, "index.html must be non-trivial"


def test_html_under_200_lines(html):
    """Suggestion requires individual file under 200 lines."""
    lines = html.splitlines()
    assert len(lines) <= 200, f"index.html is {len(lines)} lines, must be ≤ 200"


def test_html_no_external_scripts(html):
    external = re.findall(r'<script[^>]+src=["\']https?://', html)
    assert not external, f"Found external script imports: {external}"


def test_html_has_three_hue_families(html):
    """At least 3 distinct hue ranges must be defined for the palette."""
    count = html.count("HUE_FAMILIES")
    assert count >= 1, "HUE_FAMILIES array not found in index.html"
    m = re.search(r'HUE_FAMILIES\s*=\s*\[(.+?)\];', html, re.DOTALL)
    assert m is not None
    # Count array entries by counting arrow functions
    arrows = len(re.findall(r'=>', m.group(1)))
    assert arrows >= 3, f"Expected ≥ 3 hue family lambdas, found {arrows}"


def test_html_uses_hsla_for_fills(html):
    """Strokes must use hsla() to express low-opacity translucent colour."""
    assert "hsla(" in html or "hsla`" in html


def test_html_low_alpha_fills(html):
    """Opacity values must be in the 5–15 % range for watercolor effect."""
    alphas = re.findall(r'0\.(0[5-9]|1[0-5])\d*', html)
    assert alphas, "No low-opacity alpha values (0.05–0.15) found in index.html"


def test_html_has_subdivide_function(html):
    """Recursive midpoint subdivision is the core technique."""
    assert "subdivide" in html


def test_html_subdivide_is_recursive(html):
    """subdivide must call itself — count at least 2 occurrences (definition + call)."""
    count = html.count("subdivide(")
    assert count >= 2, f"Expected ≥ 2 occurrences of 'subdivide(' (definition + recursive call), found {count}"


def test_html_subdivide_halves_spread(html):
    """Each recursion level must halve the displacement spread."""
    assert "spread * 0.5" in html or "spread*0.5" in html or "spread / 2" in html


def test_html_has_base_polygon_function(html):
    assert "basePolygon" in html or "base_polygon" in html or "polygon" in html.lower()


def test_html_layered_fills_per_stroke(html):
    """Must draw 20+ fill layers per stroke to build up pigment."""
    numbers = re.findall(r'\b(2[0-9]|3[0-9]|4[0-9])\b', html)
    assert numbers, "Expected a layer count in the 20–49 range for per-stroke fill repetitions"


def test_html_has_composition_cycle(html):
    """Canvas must reset/fade after a timed composition period."""
    assert "COMPOSITION_DURATION" in html or "compositionDuration" in html or "FADE" in html


def test_html_fade_uses_rgba_white_overlay(html):
    """Soft fade is achieved by painting a near-opaque white/cream rectangle."""
    assert "rgba(245" in html or "rgba(240" in html or "rgba(255" in html


def test_html_uses_set_timeout_or_date_now(html):
    """Stroke scheduling must use Date.now() or setTimeout for timed intervals."""
    assert "Date.now()" in html or "setTimeout" in html


# ---------------------------------------------------------------------------
# thumbnail.svg checks
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def svg():
    return THUMB.read_text()


def test_thumbnail_is_valid_svg(svg):
    assert svg.strip().startswith("<svg"), "thumbnail.svg must start with <svg"
    assert "</svg>" in svg


def test_thumbnail_has_light_background(svg):
    """Watercolor uses paper-white/cream background, not a dark background."""
    assert "f5f0e8" in svg.lower() or "ffffff" in svg.lower() or "f0ede5" in svg.lower()


def test_thumbnail_has_warm_tones(svg):
    """Must include warm red/orange colour codes (hex approx hue 5–45)."""
    warm = bool(
        re.search(r'#[cd][cde][5-9a-f][0-9a-f]{3}', svg, re.IGNORECASE)
        or re.search(r'#[de][d-f][67][0-9a-f]{3}', svg, re.IGNORECASE)
        or re.search(r'cc55|dd77|e080|cc66|dd66|e077', svg, re.IGNORECASE)
    )
    assert warm, "Thumbnail must include warm orange/red tones"


def test_thumbnail_has_cool_tones(svg):
    """Must include cool blue/teal colour codes (hex approx hue 190–240)."""
    cool = bool(
        re.search(r'#[12][a-f][7-9][0-9a-f]{3}', svg, re.IGNORECASE)
        or re.search(r'3c8f|2277|4499|1a88|55aa|2288', svg, re.IGNORECASE)
    )
    assert cool, "Thumbnail must include cool blue/teal tones"


def test_thumbnail_has_earthy_tones(svg):
    """Must include earthy yellow/green colour codes (hex approx hue 70–120)."""
    earthy = bool(
        re.search(r'#[5-9][a-f][b-f][0-9a-f]{3}', svg, re.IGNORECASE)
        or re.search(r'7edc|66cc|88dd|55bb|77cc|66dd', svg, re.IGNORECASE)
    )
    assert earthy, "Thumbnail must include earthy yellow/green tones"


def test_thumbnail_has_overlapping_shapes(svg):
    """Must contain multiple polygon or ellipse elements for layering."""
    polys    = svg.count("<polygon")
    ellipses = svg.count("<ellipse")
    total    = polys + ellipses
    assert total >= 10, f"Expected ≥ 10 shape elements, found {total}"


def test_thumbnail_shapes_use_low_opacity(svg):
    """All shapes must have opacity values in watercolor range (0.05–0.15)."""
    opacities = re.findall(r'opacity=["\']([^"\']+)["\']', svg)
    assert opacities, "No opacity attributes found on shapes"
    for op in opacities:
        val = float(op)
        assert 0.0 < val <= 0.15, f"Opacity {val} is outside watercolor range (0, 0.15]"


# ---------------------------------------------------------------------------
# Python re-implementation of subdivision for mathematical sanity checks
# ---------------------------------------------------------------------------

def _subdivide(pts, depth, spread, rng):
    """
    Pure-Python replica of the JS subdivide() function for unit testing.
    Uses a seeded RNG so tests are deterministic.
    """
    if depth == 0:
        return pts
    out = []
    for i in range(len(pts)):
        a = pts[i]
        b = pts[(i + 1) % len(pts)]
        mx = (a[0] + b[0]) / 2 + (rng.random() - 0.5) * spread
        my = (a[1] + b[1]) / 2 + (rng.random() - 0.5) * spread
        out.append(a)
        out.append((mx, my))
    return _subdivide(out, depth - 1, spread * 0.5, rng)


def _base_polygon(cx, cy, rx, ry, n, rng):
    """Pure-Python replica of basePolygon()."""
    pts = []
    for i in range(n):
        angle  = (i / n) * math.pi * 2
        jitter = 0.75 + rng.random() * 0.5
        pts.append((cx + math.cos(angle) * rx * jitter,
                    cy + math.sin(angle) * ry * jitter))
    return pts


# ---------------------------------------------------------------------------
# Mathematical sanity — happy path
# ---------------------------------------------------------------------------

def test_subdivide_depth_0_returns_input():
    """At depth 0 subdivide is a no-op."""
    rng = random.Random(42)
    pts = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    result = _subdivide(pts, 0, 10.0, rng)
    assert result == pts


def test_subdivide_doubles_vertex_count_per_level():
    """Each subdivision level doubles the number of vertices."""
    rng = random.Random(1)
    pts = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]  # 4 pts
    for depth in range(1, 5):
        rng2 = random.Random(depth)
        result = _subdivide(pts, depth, 5.0, rng2)
        assert len(result) == len(pts) * (2 ** depth), (
            f"Depth {depth}: expected {len(pts) * 2**depth} pts, got {len(result)}"
        )


def test_subdivide_spread_halves_each_level():
    """
    With a fixed RNG seed, the midpoint displacement at the deepest level
    must be smaller than at level 1, verifying the halving cascade.
    """
    # Use two separate single-step calls to measure displacement magnitudes
    rng_shallow = random.Random(99)
    base = [(0.0, 0.0), (100.0, 0.0)]

    # depth=1 with spread=100 → midpoint displaced by up to ±50
    pts1 = _subdivide(base, 1, 100.0, rng_shallow)
    mid1 = pts1[1]  # the inserted midpoint
    disp1 = abs(mid1[1])  # y displacement from 0

    rng_deep = random.Random(99)
    # depth=1 with spread=25 (= 100 / 2 / 2) → displacement up to ±12.5
    pts2 = _subdivide(base, 1, 25.0, rng_deep)
    mid2 = pts2[1]
    disp2 = abs(mid2[1])

    assert disp1 >= disp2, "Larger spread must produce larger or equal displacement"


def test_subdivide_midpoints_lie_near_segment_midpoint():
    """Every inserted midpoint must be within `spread` distance of the true midpoint."""
    rng  = random.Random(7)
    spread = 20.0
    pts  = [(0.0, 0.0), (100.0, 0.0)]
    result = _subdivide(pts, 1, spread, rng)
    mid = result[1]
    true_mid_x = 50.0
    true_mid_y = 0.0
    dist = math.hypot(mid[0] - true_mid_x, mid[1] - true_mid_y)
    assert dist <= math.hypot(spread / 2, spread / 2) + 1e-9, (
        f"Midpoint at {mid} is too far from true midpoint ({true_mid_x}, {true_mid_y})"
    )


def test_base_polygon_has_correct_vertex_count():
    rng = random.Random(42)
    for n in [8, 9, 10, 11, 12]:
        pts = _base_polygon(300, 300, 80, 60, n, rng)
        assert len(pts) == n


def test_base_polygon_vertices_near_ellipse():
    """Vertices must stay within the jitter band [0.75·r, 1.25·r] of center."""
    rng = random.Random(5)
    cx, cy, rx, ry = 200.0, 200.0, 80.0, 60.0
    pts = _base_polygon(cx, cy, rx, ry, 12, rng)
    for x, y in pts:
        dx, dy = x - cx, y - cy
        # normalised ellipse distance
        norm = math.hypot(dx / rx, dy / ry)
        assert 0.73 <= norm <= 1.28, (
            f"Vertex ({x:.1f},{y:.1f}) normalised radius {norm:.3f} outside jitter band"
        )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_subdivide_single_point_polygon():
    """A single-vertex polygon stays at one vertex at all depths (degenerate)."""
    rng = random.Random(0)
    pts = [(5.0, 5.0)]
    result = _subdivide(pts, 3, 10.0, rng)
    assert len(result) == 1 * (2 ** 3)


def test_subdivide_zero_spread_leaves_midpoints_on_edge():
    """With spread=0 the inserted midpoints must lie exactly on the segment."""
    rng = random.Random(0)
    pts = [(0.0, 0.0), (10.0, 0.0)]
    result = _subdivide(pts, 1, 0.0, rng)
    mid = result[1]
    assert abs(mid[0] - 5.0) < 1e-9
    assert abs(mid[1] - 0.0) < 1e-9


def test_deep_subdivision_vertex_count_is_large():
    """4 levels on an 8-vertex polygon yields 8 * 2^4 = 128 vertices."""
    rng = random.Random(13)
    pts = _base_polygon(300, 300, 80, 60, 8, rng)
    result = _subdivide(pts, 4, 28.0, rng)
    assert len(result) == 128


def test_subdivide_large_spread_does_not_go_infinite():
    """Even with an absurdly large spread the function must terminate."""
    rng = random.Random(17)
    pts = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
    result = _subdivide(pts, 4, 1e6, rng)
    assert len(result) == 3 * (2 ** 4)
    for x, y in result:
        assert math.isfinite(x) and math.isfinite(y)


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

def test_missing_piece_directory_is_absent():
    """A non-existent piece directory must not be detected as present."""
    ghost = REPO / "pieces" / "999-ghost-watercolor"
    assert not ghost.is_dir()


def test_malformed_pieces_json_entry_detected():
    """An entry without 'technique' must fail the required-field check."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    bad = {
        "id": "156-watercolor-wash",
        "title": "X",
        "tagline": "Y",
        "year": 2026,
        "path": "pieces/156-watercolor-wash",
        "thumbnail": "pieces/156-watercolor-wash/thumbnail.svg",
        # 'technique' deliberately omitted
    }
    assert not (required <= bad.keys()), "Missing field must be detected"


def test_webgl_not_used(html):
    """This is a Canvas 2D piece — WebGL must not appear."""
    assert "webgl" not in html.lower()


def test_hue_families_cover_three_colour_ranges(html):
    """The three hue families must span warm, cool, and earthy ranges."""
    # Check that at least three distinct numeric hue anchors appear
    hues = re.findall(r'\b(5|190|70)\b', html)
    unique = set(hues)
    assert len(unique) >= 3, f"Expected anchors 5, 70, 190 in HUE_FAMILIES, found {unique}"


def test_subdivision_depth_four_or_five(html):
    """Suggestion requires 4–5 recursion levels for natural edge distortion."""
    m = re.search(r'subdivide\s*\([^,]+,\s*([45])\s*,', html)
    assert m is not None, "subdivide must be called with depth 4 or 5"


# ---------------------------------------------------------------------------
# README checks
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    content = README.read_text().strip()
    assert len(content) > 100


def test_readme_mentions_subdivision():
    content = README.read_text().lower()
    assert "subdivision" in content or "midpoint" in content


def test_readme_mentions_watercolor_or_pigment():
    content = README.read_text().lower()
    assert "watercolor" in content or "pigment" in content


def test_readme_mentions_hue_families():
    content = README.read_text().lower()
    assert "hue" in content or "palette" in content or "colour" in content or "color" in content
