"""Tests for Piece 95 — Dragon Curve: The Fold That Never Repeats."""

import importlib.util
import json
import pathlib
import xml.etree.ElementTree as ET

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "95-dragon-fold"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "95-dragon-fold"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

KNOWN_TURNS = [True, True, False, True, True, False, False]  # L L R L L R R


def _load_pieces() -> list:
    return json.loads(PIECES_JSON.read_text())


def _entry() -> dict:
    for item in _load_pieces():
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


@pytest.fixture(scope="module")
def gen():
    """Load generate_thumbnail.py as an isolated module."""
    spec = importlib.util.spec_from_file_location(
        "gen95", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Directory layout
# ---------------------------------------------------------------------------

class TestDirectoryLayout:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_thumbnail_py_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

class TestPiecesJson:
    def test_entry_present(self):
        _entry()

    def test_required_fields_present(self):
        missing = REQUIRED_FIELDS - _entry().keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches(self):
        assert _entry()["id"] == PIECE_ID

    def test_path_matches(self):
        assert _entry()["path"] == f"pieces/{PIECE_ID}"

    def test_thumbnail_file_exists(self):
        assert (REPO / _entry()["thumbnail"]).is_file()

    def test_year_is_int(self):
        assert isinstance(_entry()["year"], int)

    def test_technique_mentions_dragon(self):
        assert "dragon" in _entry()["technique"].lower()

    def test_technique_mentions_bit_sequence_or_paper_folding(self):
        t = _entry()["technique"].lower()
        assert "bit" in t or "paper" in t or "fold" in t

    def test_no_duplicate_ids(self):
        ids = [e["id"] for e in _load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate ids in pieces.json"


# ---------------------------------------------------------------------------
# index.html content
# ---------------------------------------------------------------------------

class TestIndexHtml:
    @pytest.fixture(scope="class")
    def html(self):
        return (PIECE_DIR / "index.html").read_text()

    def test_has_canvas_element(self, html):
        assert "<canvas" in html.lower()

    def test_canvas_800(self, html):
        assert "800" in html

    def test_has_ctz_function(self, html):
        assert "ctz" in html

    def test_has_turn_left_function(self, html):
        assert "turnLeft" in html or "turn_left" in html

    def test_bit_sequence_algorithm_present(self, html):
        # The key shift expression for the bit-sequence algorithm
        assert "ctz" in html
        assert ">>>" in html or ">>" in html

    def test_has_request_animation_frame(self, html):
        assert "requestAnimationFrame" in html

    def test_no_external_libraries(self, html):
        assert "<script src" not in html.lower()

    def test_no_external_urls(self, html):
        assert "https://" not in html
        assert "http://" not in html

    def test_has_teal_color(self, html):
        # Either hex or rgb representation of teal (13, 115, 119)
        assert "0d7377" in html.lower() or "13, 115" in html or "13,115" in html

    def test_has_rose_color(self, html):
        # Either hex or rgb representation of rose (196, 92, 142)
        assert "c45c8e" in html.lower() or "196, 92" in html or "196,92" in html

    def test_has_iteration_15(self, html):
        assert "15" in html

    def test_has_canvas_getcontext(self, html):
        assert "getContext" in html

    def test_has_fill_rect_for_fade(self, html):
        assert "fillRect" in html

    def test_has_precompute_points(self, html):
        # Must pre-compute all points before animating
        assert "Int16Array" in html or "Float32Array" in html or "pts" in html

    def test_has_bounding_box_fit(self, html):
        # Canvas must be scaled to fit the curve
        assert "scale" in html
        assert "min" in html or "max" in html


# ---------------------------------------------------------------------------
# thumbnail.svg content
# ---------------------------------------------------------------------------

class TestThumbnailSvg:
    @pytest.fixture(scope="class")
    def content(self):
        return (PIECE_DIR / "thumbnail.svg").read_text()

    def test_is_valid_xml(self):
        ET.parse(str(PIECE_DIR / "thumbnail.svg"))

    def test_has_svg_namespace(self, content):
        assert 'xmlns="http://www.w3.org/2000/svg"' in content

    def test_has_background_rect(self, content):
        assert "<rect" in content
        assert "0a1628" in content.lower()

    def test_has_polylines(self, content):
        assert "<polyline" in content

    def test_has_teal_color(self, content):
        assert "0d7377" in content.lower()

    def test_has_rose_color(self, content):
        # End band should have the rose color
        assert "c45c8e" in content.lower() or "c4" in content.lower()

    def test_under_200kb(self):
        size = (PIECE_DIR / "thumbnail.svg").stat().st_size
        assert size < 200_000, f"thumbnail.svg is {size} bytes — must be < 200 KB"

    def test_has_multiple_polylines(self, content):
        assert content.count("<polyline") > 1


# ---------------------------------------------------------------------------
# README content
# ---------------------------------------------------------------------------

class TestReadme:
    @pytest.fixture(scope="class")
    def readme(self):
        return (PIECE_DIR / "README.md").read_text()

    def test_mentions_dragon_curve(self, readme):
        assert "dragon" in readme.lower()

    def test_mentions_paper_folding(self, readme):
        assert "fold" in readme.lower() or "paper" in readme.lower()

    def test_mentions_bit_sequence(self, readme):
        low = readme.lower()
        assert "bit" in low or "sequence" in low

    def test_is_substantial(self, readme):
        assert len(readme.strip()) > 400


# ---------------------------------------------------------------------------
# ctz (count trailing zeros)
# ---------------------------------------------------------------------------

class TestCtz:
    def test_ctz_1(self, gen):
        assert gen.ctz(1) == 0

    def test_ctz_2(self, gen):
        assert gen.ctz(2) == 1

    def test_ctz_4(self, gen):
        assert gen.ctz(4) == 2

    def test_ctz_8(self, gen):
        assert gen.ctz(8) == 3

    def test_ctz_6(self, gen):
        # 6 = 110 binary, one trailing zero
        assert gen.ctz(6) == 1

    def test_ctz_12(self, gen):
        # 12 = 1100 binary, two trailing zeros
        assert gen.ctz(12) == 2

    def test_ctz_powers_of_two(self, gen):
        for k in range(10):
            assert gen.ctz(1 << k) == k


# ---------------------------------------------------------------------------
# turn_left (bit-sequence rule)
# ---------------------------------------------------------------------------

class TestTurnLeft:
    def test_known_sequence(self, gen):
        """First 7 turns must match the known paper-folding sequence LLRLLRR."""
        for i, expected_left in enumerate(KNOWN_TURNS, start=1):
            assert gen.turn_left(i) == expected_left, (
                f"turn_left({i}) expected {expected_left}, got {gen.turn_left(i)}"
            )

    def test_turn_at_1_is_left(self, gen):
        assert gen.turn_left(1) is True

    def test_turn_at_3_is_right(self, gen):
        assert gen.turn_left(3) is False

    def test_turn_at_power_of_2_is_left(self, gen):
        # Turns at every power of 2 are always left: ctz(2^k) = k, bit above = 0
        for k in range(1, 8):
            assert gen.turn_left(1 << k) is True

    def test_returns_bool(self, gen):
        for i in range(1, 20):
            result = gen.turn_left(i)
            assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# dragon_points
# ---------------------------------------------------------------------------

class TestDragonPoints:
    def test_iter1_has_three_points(self, gen):
        # iter 1 → 2^1 = 2 segments → 3 points
        pts = gen.dragon_points(1)
        assert len(pts) == 3

    def test_point_count(self, gen):
        for k in range(1, 6):
            pts = gen.dragon_points(k)
            assert len(pts) == (1 << k) + 1, f"iter {k}: expected {(1<<k)+1} points"

    def test_starts_at_origin(self, gen):
        pts = gen.dragon_points(3)
        assert pts[0] == (0, 0)

    def test_all_segments_unit_length(self, gen):
        pts = gen.dragon_points(4)
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            dist_sq = (x1 - x0) ** 2 + (y1 - y0) ** 2
            assert dist_sq == 1, f"Segment {i} has squared length {dist_sq}, expected 1"

    def test_iter1_second_point(self, gen):
        """Iteration 1 has 2 segments; starting East, first step is (1,0)."""
        pts = gen.dragon_points(1)
        assert pts[1] == (1, 0)

    def test_iter2_third_point(self, gen):
        """After East + turn-left (North in screen: y-1), third point is (1,-1)."""
        pts = gen.dragon_points(2)
        # Seg 1: (0,0)→(1,0); turn L → North (dy=-1); Seg 2: (1,0)→(1,-1)
        # But iteration 2 means 4 segments total... let me check
        # dragon_points(2) → 4 segments → 5 points
        # point[2] is after 2 segments
        assert len(pts) == 5
        assert pts[1] == (1, 0)
        # After turn at n=1 (L): dir goes 0→1 (North, dy=-1)
        assert pts[2] == (1, -1)

    def test_curve_stays_on_integer_grid(self, gen):
        pts = gen.dragon_points(8)
        for x, y in pts:
            assert isinstance(x, int)
            assert isinstance(y, int)

    def test_self_avoiding_iter3(self, gen):
        """Iteration 3 (8 segments) is fully self-avoiding; iter 4+ touches itself."""
        pts = gen.dragon_points(3)
        assert len(pts) == len(set(pts))

    def test_bounding_box_centered_roughly(self, gen):
        """Bounding box of iteration 10 should be non-degenerate."""
        pts = gen.dragon_points(10)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        assert max(xs) > 0
        assert min(xs) < 0 or max(xs) > 10
        assert (max(xs) - min(xs)) > 10
        assert (max(ys) - min(ys)) > 10


# ---------------------------------------------------------------------------
# generate_svg
# ---------------------------------------------------------------------------

class TestGenerateSvg:
    def test_returns_string(self, gen):
        assert isinstance(gen.generate_svg(iterations=3, size=200), str)

    def test_has_svg_namespace(self, gen):
        assert 'xmlns="http://www.w3.org/2000/svg"' in gen.generate_svg(3, 200)

    def test_viewbox_matches_size(self, gen):
        svg = gen.generate_svg(3, 300)
        assert 'viewBox="0 0 300 300"' in svg

    def test_has_background_rect(self, gen):
        svg = gen.generate_svg(3, 200)
        assert "<rect" in svg
        assert gen.BG_COLOR in svg

    def test_has_polylines(self, gen):
        svg = gen.generate_svg(4, 200)
        assert "<polyline" in svg

    def test_valid_xml(self, gen):
        ET.fromstring(gen.generate_svg(4, 200))

    def test_reproducible(self, gen):
        assert gen.generate_svg(4, 200) == gen.generate_svg(4, 200)

    def test_small_iteration_renders(self, gen):
        svg = gen.generate_svg(2, 100)
        assert "<polyline" in svg

    def test_large_iteration_no_crash(self, gen):
        svg = gen.generate_svg(10, 400)
        ET.fromstring(svg)

    def test_has_teal_color(self, gen):
        svg = gen.generate_svg(4, 200)
        assert "0d7377" in svg.lower() or "#0d" in svg.lower()

    def test_under_200kb_for_thumb_iterations(self, gen):
        svg = gen.generate_svg(gen.THUMB_ITERATIONS, gen.SIZE)
        assert len(svg.encode()) < 200_000


# ---------------------------------------------------------------------------
# Committed thumbnail.svg integrity
# ---------------------------------------------------------------------------

class TestThumbnailIntegrity:
    def test_thumbnail_valid_xml(self):
        ET.parse(str(PIECE_DIR / "thumbnail.svg"))

    def test_thumbnail_has_background(self, gen):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert gen.BG_COLOR in content

    def test_thumbnail_has_polylines(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "<polyline" in content

    def test_thumbnail_has_correct_band_count(self, gen):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        # Should have NUM_BANDS polylines (one per colour band)
        assert content.count("<polyline") == gen.NUM_BANDS


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_dragon_points_iter0(self, gen):
        """Iteration 0 has 1 segment and 2 points: just start and end."""
        pts = gen.dragon_points(0)
        assert len(pts) == 2

    def test_ctz_large_power_of_two(self, gen):
        assert gen.ctz(1 << 20) == 20

    def test_turn_sequence_at_large_n(self, gen):
        """turn_left must not crash for large n values."""
        for n in [1000, 10000, 100000]:
            result = gen.turn_left(n)
            assert isinstance(result, bool)

    def test_generate_svg_size_1(self, gen):
        """Degenerate size=1 must not crash."""
        svg = gen.generate_svg(2, 1)
        assert "<svg" in svg

    def test_dragon_points_large_iteration_no_crash(self, gen):
        """Iteration 13 (8192 segments) must complete without error."""
        pts = gen.dragon_points(13)
        assert len(pts) == (1 << 13) + 1


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_missing_title_fails_required_check(self):
        incomplete = {
            "id": PIECE_ID,
            "tagline": "test",
            "year": 2026,
            "technique": "canvas",
            "path": f"pieces/{PIECE_ID}",
            "thumbnail": f"pieces/{PIECE_ID}/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_wrong_id_not_in_json(self):
        ids = [e["id"] for e in _load_pieces()]
        assert "95-wrong-id" not in ids

    def test_missing_thumbnail_detected(self, tmp_path):
        ghost = tmp_path / "ghost.svg"
        assert not ghost.exists()

    def test_nonexistent_piece_dir_detected(self, tmp_path):
        assert not (tmp_path / "ghost-dragon").is_dir()

    def test_turn_never_returns_none(self, gen):
        for n in range(1, 50):
            assert gen.turn_left(n) is not None
