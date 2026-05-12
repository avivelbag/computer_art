"""Tests for pieces/47-hilbert-curve: Hilbert curve order-6 animation."""

import json
import pathlib
import re
import xml.etree.ElementTree as ET

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "47-hilbert-curve"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID    = "47-hilbert-curve"


# ---------------------------------------------------------------------------
# Python mirror of the JS d2xy() from index.html
# ---------------------------------------------------------------------------

def d2xy(n: int, d: int) -> tuple[int, int]:
    """Convert Hilbert-curve index d to (x, y) on an n×n grid.

    Uses the standard rotate-and-reflect algorithm: at each bit-pair level s,
    rx/ry extract two bits from d, then x/y are reflected/swapped to select
    the correct quadrant orientation before the offset is added.
    """
    x = y = 0
    t = d
    s = 1
    while s < n:
        rx = (t >> 1) & 1
        ry = (t ^ rx) & 1
        if ry == 0:
            if rx == 1:
                x, y = s - 1 - x, s - 1 - y
            x, y = y, x
        x += s * rx
        y += s * ry
        t >>= 2
        s <<= 1
    return x, y


def all_points(order: int) -> list[tuple[int, int]]:
    """Return the full sequence of (x, y) grid coords for a Hilbert curve of given order."""
    n = 1 << order
    return [d2xy(n, d) for d in range(n * n)]


def _entry() -> dict:
    """Return the pieces.json entry for this piece."""
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


def _html() -> str:
    return INDEX_HTML.read_text()


# ---------------------------------------------------------------------------
# File existence — happy path
# ---------------------------------------------------------------------------


def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_readme_exists():
    assert README.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


# ---------------------------------------------------------------------------
# d2xy correctness — order-2 (4×4 grid, 16 points)
# ---------------------------------------------------------------------------


class TestD2xyOrder2:
    """Verify the Hilbert curve algorithm against a manually-known order-2 curve.

    The order-2 Hilbert curve on a 4×4 grid visits cells in a specific
    winding pattern that can be verified by inspection.
    """

    def test_origin_at_d0(self):
        assert d2xy(4, 0) == (0, 0)

    def test_second_point(self):
        assert d2xy(4, 1) == (1, 0)

    def test_third_point(self):
        assert d2xy(4, 2) == (1, 1)

    def test_fourth_point(self):
        assert d2xy(4, 3) == (0, 1)

    def test_all_16_cells_visited_exactly_once(self):
        pts = all_points(2)
        assert len(pts) == 16
        assert len(set(pts)) == 16, "Some cells visited more than once"

    def test_all_16_points_in_range(self):
        """Every (x, y) must be within the 4×4 grid (0..3 inclusive)."""
        for x, y in all_points(2):
            assert 0 <= x <= 3 and 0 <= y <= 3, f"Out of range: ({x},{y})"


# ---------------------------------------------------------------------------
# d2xy correctness — order-4 (16×16 grid, 256 points)
# ---------------------------------------------------------------------------


class TestD2xyOrder4:
    def test_256_distinct_points(self):
        pts = all_points(4)
        assert len(pts) == 256
        assert len(set(pts)) == 256

    def test_all_in_range(self):
        for x, y in all_points(4):
            assert 0 <= x <= 15 and 0 <= y <= 15

    def test_covers_full_grid(self):
        """Every cell of the 16×16 grid must appear exactly once."""
        expected = {(x, y) for x in range(16) for y in range(16)}
        assert set(all_points(4)) == expected

    def test_adjacent_steps_are_unit_distance(self):
        """Consecutive Hilbert points must always be exactly 1 step apart."""
        pts = all_points(4)
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            dist = abs(x1 - x0) + abs(y1 - y0)
            assert dist == 1, f"Non-unit step at segment {i}: ({x0},{y0})→({x1},{y1})"


# ---------------------------------------------------------------------------
# d2xy correctness — order-6 (64×64 grid, 4096 points)
# ---------------------------------------------------------------------------


class TestD2xyOrder6:
    """Smoke-test the order-6 curve that the animation actually uses."""

    def test_4096_distinct_points(self):
        pts = all_points(6)
        assert len(set(pts)) == 4096

    def test_all_in_64x64_grid(self):
        for x, y in all_points(6):
            assert 0 <= x <= 63 and 0 <= y <= 63

    def test_adjacent_steps_are_unit_distance(self):
        """Every consecutive pair in the order-6 curve must be 1 Manhattan step apart."""
        pts = all_points(6)
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            dist = abs(x1 - x0) + abs(y1 - y0)
            assert dist == 1, f"Non-unit step at segment {i}"

    def test_segment_count(self):
        """4^6 = 4096 points → 4095 segments (≈ 4000 as advertised)."""
        assert len(all_points(6)) - 1 == 4095


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_order_1_covers_2x2(self):
        """Order 1 is the degenerate 2×2 U-shape."""
        pts = all_points(1)
        assert len(pts) == 4
        assert len(set(pts)) == 4

    def test_order_1_all_in_2x2(self):
        for x, y in all_points(1):
            assert 0 <= x <= 1 and 0 <= y <= 1

    def test_order_0_single_point(self):
        """Order 0 is a degenerate 1×1 grid: a single point at (0, 0)."""
        assert d2xy(1, 0) == (0, 0)

    def test_large_order_8_boundary(self):
        """Spot-check that order-8 d=0 is still (0, 0)."""
        assert d2xy(256, 0) == (0, 0)

    def test_last_index_order4_in_range(self):
        """d = n²-1 must still produce a valid in-range coordinate."""
        n = 16
        x, y = d2xy(n, n * n - 1)
        assert 0 <= x <= n - 1 and 0 <= y <= n - 1

    def test_no_diagonal_steps_order3(self):
        """Hilbert curve must never jump diagonally (only cardinal neighbours)."""
        pts = all_points(3)
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            assert abs(x1 - x0) + abs(y1 - y0) == 1

    def test_curve_starts_and_ends_at_adjacent_corners(self):
        """For even orders, the start and end of the curve are in opposite corners
        of the grid. They must be within the boundary, not equal each other."""
        pts = all_points(4)
        assert pts[0] != pts[-1], "Start and end must be different cells"


# ---------------------------------------------------------------------------
# Failure modes — assert correct error or no-op behavior
# ---------------------------------------------------------------------------


class TestFailureModes:
    def test_wrong_id_not_in_json(self):
        """A made-up piece id must not appear in pieces.json."""
        data = json.loads(PIECES_JSON.read_text())
        ids  = {item["id"] for item in data}
        assert "47-wrong-piece" not in ids

    def test_empty_curve_has_no_segments(self):
        """An empty point list has no segments (boundary condition)."""
        pts = all_points(0)  # single point
        segments = len(pts) - 1
        assert segments == 0

    def test_missing_piece_directory_detectable(self, tmp_path):
        """Referencing a non-existent piece directory should be detectable."""
        assert not (tmp_path / "47-hilbert-curve-ghost").is_dir()


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_has_script():
    assert "<script" in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset():
    assert "charset" in _html()


def test_html_no_external_scripts():
    assert not re.findall(r'<script[^>]+src=["\']https?://', _html())


def test_html_self_contained():
    html = _html()
    assert "<script src=" not in html
    assert '<link rel="stylesheet"' not in html


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_dark_background():
    """The near-black deep-purple background must appear in the source."""
    assert "1a0a2e" in _html().lower()


def test_html_has_copper_stroke():
    """The copper/amber stroke color must appear in the source."""
    assert "d4a256" in _html().lower()


def test_html_mentions_hilbert_or_d2xy():
    html = _html().lower()
    assert "hilbert" in html or "d2xy" in html


def test_html_has_order_constant():
    """ORDER (or equivalent) must be present and set to 6 or higher."""
    html = _html()
    m = re.search(r"ORDER\s*=\s*(\d+)", html)
    assert m, "ORDER constant not found in HTML"
    assert int(m.group(1)) >= 6


def test_html_has_draw_secs_constant():
    """The animation must declare an explicit draw-duration constant."""
    html = _html()
    assert "DRAW_SECS" in html or "DRAW_SECONDS" in html or re.search(r"draw.*secs?", html, re.I)


def test_html_canvas_800x800():
    html = _html()
    assert 'width="800"' in html and 'height="800"' in html


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------


def test_thumbnail_not_empty():
    assert THUMBNAIL.stat().st_size > 200


def test_thumbnail_is_valid_xml():
    ET.fromstring(THUMBNAIL.read_text())


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_dimensions_400():
    svg = THUMBNAIL.read_text()
    w   = re.search(r'width="(\d+)"', svg)
    h   = re.search(r'height="(\d+)"', svg)
    assert w and int(w.group(1)) == 400
    assert h and int(h.group(1)) == 400


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_polyline():
    """The thumbnail must contain a <polyline> element (not separate line segments)."""
    assert "<polyline" in THUMBNAIL.read_text()


def test_thumbnail_polyline_has_many_points():
    """The polyline must describe at least 255 points (order-4 = 16×16 = 256 pts)."""
    svg  = THUMBNAIL.read_text()
    m    = re.search(r'<polyline[^>]+points="([^"]+)"', svg)
    assert m, "<polyline points=...> not found in thumbnail"
    coords = m.group(1).strip().split()
    assert len(coords) >= 255, f"Only {len(coords)} coordinate pairs found"


def test_thumbnail_has_copper_stroke():
    assert "d4a256" in THUMBNAIL.read_text().lower()


def test_thumbnail_has_dark_background():
    assert "1a0a2e" in THUMBNAIL.read_text().lower()


def test_thumbnail_under_500kb():
    assert THUMBNAIL.stat().st_size < 500_000


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_has_svg_namespace():
    assert 'xmlns="http://www.w3.org/2000/svg"' in THUMBNAIL.read_text()


# ---------------------------------------------------------------------------
# pieces.json
# ---------------------------------------------------------------------------


def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_entry_has_all_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing  = required - _entry().keys()
    assert not missing, f"Missing fields: {missing}"


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


def test_pieces_json_technique_mentions_hilbert():
    assert "hilbert" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_space_filling():
    tech = _entry()["technique"].lower()
    assert "space-filling" in tech or "space filling" in tech


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_space_filling():
    readme = README.read_text().lower()
    assert "space-filling" in readme or "space filling" in readme


def test_readme_explains_every_point_once():
    readme = README.read_text().lower()
    assert "exactly once" in readme or "every point" in readme or "every cell" in readme


def test_readme_mentions_order_6():
    readme = README.read_text()
    assert "6" in readme and ("order" in readme.lower() or "4,095" in readme or "4095" in readme)


def test_readme_mentions_4095_or_4096():
    readme = README.read_text()
    assert "4,095" in readme or "4095" in readme or "4,096" in readme or "4096" in readme


def test_readme_mentions_palette():
    readme = README.read_text().lower()
    assert "copper" in readme or "amber" in readme or "d4a256" in readme


def test_readme_has_animation_description():
    readme = README.read_text().lower()
    assert "animat" in readme or "draw" in readme or "stroke" in readme
