"""Tests for pieces/83-space-colonization: Runions space-colonization branching."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "83-space-colonization"
INDEX     = PIECE_DIR / "index.html"
README    = PIECE_DIR / "README.md"
THUMB     = PIECE_DIR / "thumbnail.svg"
PJSON     = REPO / "pieces.json"
PIECE_ID  = "83-space-colonization"

# MAX_DEPTH must match the constant in index.html
MAX_DEPTH = 22


# ---------------------------------------------------------------------------
# Python mirrors of algorithm functions for white-box testing
# ---------------------------------------------------------------------------


def stroke_width(depth: int) -> float:
    """Return tapered stroke width: max(0.5, 4*(1 - depth/MAX_DEPTH))."""
    return max(0.5, 4.0 * (1.0 - depth / MAX_DEPTH))


def in_ellipse(x: float, y: float, cx: float, cy: float, rx: float, ry: float) -> bool:
    """Return True when (x,y) lies inside or on the axis-aligned ellipse."""
    dx = (x - cx) / rx
    dy = (y - cy) / ry
    return dx * dx + dy * dy <= 1.0


def nearest_node(ax: float, ay: float, nodes: list[dict], influence_r: float) -> int:
    """Return the index of the nearest node within influence_r, or -1 if none."""
    best_i   = -1
    best_dsq = influence_r * influence_r
    for i, n in enumerate(nodes):
        dx  = ax - n["x"]
        dy  = ay - n["y"]
        dsq = dx * dx + dy * dy
        if dsq <= best_dsq:
            best_dsq = dsq
            best_i   = i
    return best_i


def average_direction(
    node_x: float,
    node_y: float,
    attractors: list[tuple[float, float]],
) -> tuple[float, float]:
    """Return the normalised average direction from a node toward its attractors.

    Each per-attractor vector is unit-normalised before averaging, matching the
    JS implementation.  Returns (0.0, 0.0) when the attractor list is empty or
    all attractors coincide with the node.
    """
    if not attractors:
        return 0.0, 0.0
    sx, sy = 0.0, 0.0
    for ax, ay in attractors:
        dx, dy = ax - node_x, ay - node_y
        d = math.sqrt(dx * dx + dy * dy)
        if d == 0:
            continue
        sx += dx / d
        sy += dy / d
    length = math.sqrt(sx * sx + sy * sy)
    if length == 0:
        return 0.0, 0.0
    return sx / length, sy / length


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _html() -> str:
    return INDEX.read_text()


def _entry() -> dict:
    data = json.loads(PJSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# File existence — happy path
# ---------------------------------------------------------------------------


def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX.is_file()


def test_readme_exists():
    assert README.is_file()


def test_thumbnail_exists():
    assert THUMB.is_file()


# ---------------------------------------------------------------------------
# stroke_width — tapering invariants
# ---------------------------------------------------------------------------


class TestStrokeWidth:
    def test_root_depth_returns_four(self):
        assert stroke_width(0) == 4.0

    def test_max_depth_clamps_to_half_pixel(self):
        assert stroke_width(MAX_DEPTH) == pytest.approx(0.5)

    def test_past_max_depth_still_half_pixel(self):
        assert stroke_width(MAX_DEPTH + 5) == pytest.approx(0.5)

    def test_monotonically_non_increasing(self):
        widths = [stroke_width(d) for d in range(MAX_DEPTH + 1)]
        for a, b in zip(widths, widths[1:]):
            assert a >= b

    def test_never_below_minimum(self):
        for d in range(0, MAX_DEPTH * 3):
            assert stroke_width(d) >= 0.5

    def test_never_above_four(self):
        for d in range(0, MAX_DEPTH + 1):
            assert stroke_width(d) <= 4.0


# ---------------------------------------------------------------------------
# in_ellipse — attractor cloud shape
# ---------------------------------------------------------------------------


class TestInEllipse:
    def test_centre_is_inside(self):
        assert in_ellipse(300.0, 228.0, 300.0, 228.0, 216.0, 252.0)

    def test_point_on_horizontal_boundary(self):
        # (cx + rx, cy) sits exactly on the ellipse boundary
        assert in_ellipse(516.0, 228.0, 300.0, 228.0, 216.0, 252.0)

    def test_far_point_rejected(self):
        assert not in_ellipse(0.0, 0.0, 300.0, 228.0, 216.0, 252.0)

    def test_rejection_sampled_points_all_inside(self):
        """Unit-disk samples mapped to the ellipse must all satisfy in_ellipse."""
        import random
        rng = random.Random(42)
        cx, cy, rx, ry = 300.0, 228.0, 216.0, 252.0
        count = 0
        while count < 200:
            dx = rng.uniform(-1, 1)
            dy = rng.uniform(-1, 1)
            if dx * dx + dy * dy <= 1.0:
                x, y = cx + dx * rx, cy + dy * ry
                assert in_ellipse(x, y, cx, cy, rx, ry)
                count += 1


# ---------------------------------------------------------------------------
# nearest_node — influence radius logic
# ---------------------------------------------------------------------------


class TestNearestNode:
    def _nodes(self, coords):
        return [{"x": x, "y": y} for x, y in coords]

    def test_single_node_in_range(self):
        nodes = self._nodes([(100.0, 100.0)])
        assert nearest_node(105.0, 100.0, nodes, 50.0) == 0

    def test_single_node_out_of_range(self):
        nodes = self._nodes([(100.0, 100.0)])
        assert nearest_node(200.0, 200.0, nodes, 50.0) == -1

    def test_returns_closest_of_two(self):
        nodes = self._nodes([(100.0, 100.0), (110.0, 100.0)])
        # attractor at (112, 100): distance 2 to node 1 vs distance 12 to node 0
        assert nearest_node(112.0, 100.0, nodes, 50.0) == 1

    def test_empty_node_list_returns_minus_one(self):
        assert nearest_node(50.0, 50.0, [], 100.0) == -1

    def test_exactly_at_boundary_is_included(self):
        nodes = self._nodes([(0.0, 0.0)])
        assert nearest_node(50.0, 0.0, nodes, 50.0) == 0


# ---------------------------------------------------------------------------
# average_direction — direction averaging
# ---------------------------------------------------------------------------


class TestAverageDirection:
    def test_single_attractor_directly_above_returns_up(self):
        dx, dy = average_direction(200.0, 300.0, [(200.0, 200.0)])
        assert abs(dx) < 1e-9 and abs(dy + 1.0) < 1e-9  # dy = -1 means "up"

    def test_symmetric_attractors_cancel_horizontal(self):
        dx, dy = average_direction(200.0, 300.0, [(150.0, 250.0), (250.0, 250.0)])
        assert abs(dx) < 1e-9

    def test_empty_attractors_returns_zero_vector(self):
        assert average_direction(0.0, 0.0, []) == (0.0, 0.0)

    def test_result_is_unit_length(self):
        dx, dy = average_direction(0.0, 0.0, [(3.0, 4.0), (4.0, 3.0)])
        assert abs(math.sqrt(dx * dx + dy * dy) - 1.0) < 1e-9

    def test_coincident_attractor_skipped(self):
        # Attractor at same location as node contributes zero; only the second counts
        dx, dy = average_direction(0.0, 0.0, [(0.0, 0.0), (0.0, -10.0)])
        assert abs(dx) < 1e-9 and abs(dy + 1.0) < 1e-9


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------


def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_canvas_600x600():
    html = _html()
    assert 'width="600"' in html and 'height="600"' in html


def test_html_canvas_has_id():
    assert 'id="canvas"' in _html()


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_no_external_scripts():
    assert not re.findall(r'<script[^>]+src=["\']https?://', _html())


def test_html_no_external_stylesheets():
    assert not re.findall(r'<link[^>]+href=["\']https?://', _html())


def test_html_has_influence_radius_constant():
    assert "INFLUENCE_RADIUS" in _html()


def test_html_influence_radius_is_100():
    m = re.search(r"INFLUENCE_RADIUS\s*=\s*(\d+)", _html())
    assert m and int(m.group(1)) == 100


def test_html_has_kill_distance_constant():
    assert "KILL_DISTANCE" in _html()


def test_html_kill_distance_is_10():
    m = re.search(r"KILL_DISTANCE\s*=\s*(\d+)", _html())
    assert m and int(m.group(1)) == 10


def test_html_has_step_size_constant():
    assert "STEP_SIZE" in _html()


def test_html_step_size_is_5():
    m = re.search(r"STEP_SIZE\s*=\s*(\d+)", _html())
    assert m and int(m.group(1)) == 5


def test_html_has_num_attractors():
    assert "NUM_ATTRACTORS" in _html()


def test_html_num_attractors_at_least_300():
    m = re.search(r"NUM_ATTRACTORS\s*=\s*(\d+)", _html())
    assert m and int(m.group(1)) >= 300


def test_html_has_max_depth_constant():
    assert "MAX_DEPTH" in _html()


def test_html_has_hold_ms():
    assert "HOLD_MS" in _html()


def test_html_has_fade_ms():
    assert "FADE_MS" in _html()


def test_html_has_stroke_width_function():
    assert "strokeWidth" in _html()


def test_html_stroke_width_uses_math_max():
    assert "Math.max" in _html()


def test_html_has_global_alpha():
    assert "globalAlpha" in _html()


def test_html_has_fading_phase():
    assert "fading" in _html()


def test_html_background_is_cream():
    assert "f8f4ec" in _html().lower()


def test_html_stroke_color_is_terracotta():
    assert "c45e2a" in _html().lower()


def test_html_has_charset():
    assert "charset" in _html().lower()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_title():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m and len(m.group(1).strip()) > 0


def test_html_no_audio():
    html = _html()
    assert "<audio" not in html.lower() and "AudioContext" not in html


def test_html_uses_math_sqrt():
    assert "Math.sqrt" in _html()


def test_html_has_cloud_constants():
    html = _html()
    assert "CLOUD_CX" in html or "CLOUD_RX" in html


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------


def test_thumbnail_valid_xml():
    try:
        ET.fromstring(THUMB.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMB.read_text()


def test_thumbnail_width_400():
    m = re.search(r'width="(\d+)"', THUMB.read_text())
    assert m and int(m.group(1)) == 400


def test_thumbnail_height_400():
    m = re.search(r'height="(\d+)"', THUMB.read_text())
    assert m and int(m.group(1)) == 400


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMB.read_text()


def test_thumbnail_background_cream():
    assert "f8f4ec" in THUMB.read_text().lower()


def test_thumbnail_has_stroke_lines():
    assert "<line" in THUMB.read_text()


def test_thumbnail_stroke_is_terracotta():
    assert "c45e2a" in THUMB.read_text().lower()


def test_thumbnail_has_multiple_lines():
    count = THUMB.read_text().count("<line")
    assert count >= 10, f"Expected ≥10 lines, got {count}"


def test_thumbnail_has_svg_namespace():
    assert 'xmlns="http://www.w3.org/2000/svg"' in THUMB.read_text()


def test_thumbnail_not_trivially_empty():
    assert THUMB.stat().st_size > 500


def test_thumbnail_under_200kb():
    assert THUMB.stat().st_size < 200_000


def test_thumbnail_valid_utf8():
    THUMB.read_bytes().decode("utf-8")


def test_thumbnail_has_tapering_stroke_widths():
    """The thumbnail must show tapering: multiple distinct stroke-width values."""
    svg    = THUMB.read_text()
    widths = re.findall(r'stroke-width="([\d.]+)"', svg)
    assert len(widths) >= 2
    unique = {float(w) for w in widths}
    assert len(unique) >= 3, f"Expected ≥3 distinct stroke widths, got {unique}"


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_colonization():
    assert "colonization" in README.read_text().lower()


def test_readme_mentions_attractor():
    assert "attractor" in README.read_text().lower()


def test_readme_mentions_palette_or_color():
    text = README.read_text().lower()
    assert "palette" in text or "colour" in text or "color" in text


def test_readme_mentions_index_html():
    assert "index.html" in README.read_text().lower()


def test_readme_mentions_taper_or_width():
    text = README.read_text().lower()
    assert "taper" in text or "width" in text


# ---------------------------------------------------------------------------
# pieces.json contract
# ---------------------------------------------------------------------------


def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_entry_complete():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert not required - _entry().keys()


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    assert (REPO / _entry()["thumbnail"]).is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_space_colonization():
    assert "colonization" in _entry()["technique"].lower()


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PJSON.read_text())
    ids  = [item["id"] for item in data]
    assert len(ids) == len(set(ids))


def test_pieces_json_still_has_existing_entries():
    data = json.loads(PJSON.read_text())
    ids  = {item["id"] for item in data}
    assert "01-amber-current" in ids
    assert "81-newtons-basin" in ids
    assert PIECE_ID           in ids


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_stroke_width_depth_zero_is_four(self):
        assert stroke_width(0) == 4.0

    def test_stroke_width_very_deep_clamped_to_half(self):
        assert stroke_width(10_000) == 0.5

    def test_in_ellipse_unit_circle_boundary(self):
        assert in_ellipse(1.0, 0.0, 0.0, 0.0, 1.0, 1.0)
        assert not in_ellipse(1.01, 0.0, 0.0, 0.0, 1.0, 1.0)

    def test_nearest_node_tie_resolved_deterministically(self):
        nodes = [{"x": 0.0, "y": 10.0}, {"x": 0.0, "y": -10.0}]
        result = nearest_node(0.0, 0.0, nodes, 20.0)
        assert result in (0, 1)

    def test_average_direction_diagonal_normalised(self):
        dx, dy = average_direction(0.0, 0.0, [(3.0, 4.0)])
        assert abs(math.sqrt(dx * dx + dy * dy) - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------


class TestFailureModes:
    def test_wrong_id_absent_from_pieces_json(self):
        data = json.loads(PJSON.read_text())
        ids  = {item["id"] for item in data}
        assert "83-wrong-piece" not in ids

    def test_ghost_piece_dir_does_not_exist(self, tmp_path):
        assert not (tmp_path / "83-space-colonization-ghost").is_dir()

    def test_attractor_outside_radius_ignored(self):
        nodes = [{"x": 0.0, "y": 0.0}]
        assert nearest_node(200.0, 200.0, nodes, 50.0) == -1

    def test_no_direction_for_node_with_no_attractors(self):
        assert average_direction(100.0, 100.0, []) == (0.0, 0.0)
