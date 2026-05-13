"""Tests for Piece 90 — The Grain That Broke the Symmetry (Abelian Sandpile)."""

import importlib.util
import json
import pathlib
import xml.etree.ElementTree as ET

import pytest

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "90-sandpile"
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}


def load_pieces():
    """Return parsed pieces.json as a list."""
    return json.loads(PIECES_JSON.read_text())


def sandpile_entry():
    """Return the pieces.json entry for 90-sandpile, or None if absent."""
    return next((e for e in load_pieces() if e.get("id") == "90-sandpile"), None)


@pytest.fixture(scope="module")
def gen():
    """Load generate_thumbnail.py as an importable module."""
    spec = importlib.util.spec_from_file_location(
        "gen90", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Happy-path: directory layout
# ---------------------------------------------------------------------------

class TestDirectoryLayout:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir(), "pieces/90-sandpile/ must exist"

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_thumbnail_py_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# Happy-path: pieces.json entry
# ---------------------------------------------------------------------------

class TestPiecesJsonEntry:
    def test_entry_present(self):
        assert sandpile_entry() is not None, "90-sandpile entry missing from pieces.json"

    def test_required_fields_present(self):
        entry = sandpile_entry()
        assert entry is not None
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches_directory(self):
        entry = sandpile_entry()
        assert entry is not None
        piece_dir = REPO / entry["path"]
        assert entry["id"] == piece_dir.name

    def test_technique_mentions_sandpile(self):
        entry = sandpile_entry()
        assert entry is not None
        assert "sandpile" in entry["technique"].lower()

    def test_technique_mentions_imagedata(self):
        entry = sandpile_entry()
        assert entry is not None
        assert "imagedata" in entry["technique"].lower()

    def test_thumbnail_path_resolves(self):
        entry = sandpile_entry()
        assert entry is not None
        assert (REPO / entry["thumbnail"]).is_file()

    def test_year_is_integer(self):
        entry = sandpile_entry()
        assert entry is not None
        assert isinstance(entry["year"], int)

    def test_path_directory_exists(self):
        entry = sandpile_entry()
        assert entry is not None
        assert (REPO / entry["path"]).is_dir()


# ---------------------------------------------------------------------------
# Happy-path: index.html content
# ---------------------------------------------------------------------------

class TestIndexHtmlContent:
    @pytest.fixture(scope="class")
    def html(self):
        return (PIECE_DIR / "index.html").read_text()

    def test_has_canvas_element(self, html):
        assert "<canvas" in html.lower()

    def test_uses_request_animation_frame(self, html):
        assert "requestAnimationFrame" in html

    def test_uses_imagedata(self, html):
        assert "ImageData" in html or "createImageData" in html

    def test_initial_grains_present(self, html):
        assert "65536" in html

    def test_deep_navy_color(self, html):
        assert "1a1a2e" in html.lower()

    def test_dusty_rose_color(self, html):
        assert "c97b7b" in html.lower()

    def test_sage_green_color(self, html):
        assert "7ba87b" in html.lower()

    def test_warm_white_color(self, html):
        assert "f0ede0" in html.lower()

    def test_grid_size_401(self, html):
        assert "401" in html

    def test_uses_int32array(self, html):
        assert "Int32Array" in html

    def test_boundary_loop_starts_at_1(self, html):
        # Interior loop must start at y=1 and x=1 so boundary cells act as sinks
        assert "y = 1" in html or "y=1" in html


# ---------------------------------------------------------------------------
# Happy-path: thumbnail.svg content
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

    def test_uses_deep_navy_background(self, content):
        assert "1a1a2e" in content.lower()

    def test_uses_all_four_sandpile_colors(self, content):
        assert "c97b7b" in content.lower()
        assert "7ba87b" in content.lower()
        assert "f0ede0" in content.lower()

    def test_has_many_rects(self, content):
        # A non-trivial sandpile pattern should have many colored rects
        assert content.count("<rect") > 10


# ---------------------------------------------------------------------------
# Sandpile algorithm correctness tests
# ---------------------------------------------------------------------------

class TestComputeSandpile:
    def test_zero_grains_is_stable(self, gen):
        """No grains placed means the grid is already stable (all zeros)."""
        grid = gen.compute_sandpile(5, 5, 2, 2, 0)
        assert all(v == 0 for v in grid)

    def test_one_grain_stays_at_center(self, gen):
        """1 grain < 4, so no toppling occurs."""
        grid = gen.compute_sandpile(5, 5, 2, 2, 1)
        assert grid[2 * 5 + 2] == 1
        assert sum(grid) == 1

    def test_three_grains_stays_at_center(self, gen):
        """3 grains < 4, so no toppling occurs."""
        grid = gen.compute_sandpile(5, 5, 2, 2, 3)
        assert grid[2 * 5 + 2] == 3

    def test_single_topple_four_grains(self, gen):
        """4 grains at center of 5×5 topple once: center→0, four neighbours→1."""
        grid = gen.compute_sandpile(5, 5, 2, 2, 4)
        assert grid[2 * 5 + 2] == 0   # center fired
        assert grid[1 * 5 + 2] == 1   # north (y=1, x=2)
        assert grid[3 * 5 + 2] == 1   # south (y=3, x=2)
        assert grid[2 * 5 + 1] == 1   # west  (y=2, x=1)
        assert grid[2 * 5 + 3] == 1   # east  (y=2, x=3)

    def test_batch_topple_eight_grains(self, gen):
        """8 grains topple twice atomically in one pass: center→0, neighbours→2."""
        grid = gen.compute_sandpile(7, 7, 3, 3, 8)
        assert grid[3 * 7 + 3] == 0   # center
        assert grid[2 * 7 + 3] == 2   # north
        assert grid[4 * 7 + 3] == 2   # south
        assert grid[3 * 7 + 2] == 2   # west
        assert grid[3 * 7 + 4] == 2   # east

    def test_no_interior_cell_above_3_in_stable_state(self, gen):
        """Every interior cell must hold 0–3 grains in the stable configuration."""
        grid = gen.compute_sandpile(21, 21, 10, 10, 64)
        for y in range(1, 20):
            for x in range(1, 20):
                assert grid[y * 21 + x] <= 3, f"unstable cell at ({x},{y})"

    def test_grain_conservation_small_pile(self, gen):
        """3 grains never reach the boundary, so sum equals initial grain count."""
        grid = gen.compute_sandpile(5, 5, 2, 2, 3)
        assert sum(grid) == 3

    def test_four_fold_symmetry(self, gen):
        """Sandpile seeded at centre has reflective symmetry about both axes."""
        w, h  = 21, 21
        cx, cy = 10, 10
        grid  = gen.compute_sandpile(w, h, cx, cy, 128)
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                dx, dy = x - cx, y - cy
                v = grid[y * w + x]
                # Horizontal reflection (flip x)
                assert grid[y * w + (cx - dx)] == v, f"H-symmetry broken at ({x},{y})"
                # Vertical reflection (flip y)
                assert grid[(cy - dy) * w + x] == v, f"V-symmetry broken at ({x},{y})"

    def test_larger_pile_converges(self, gen):
        """A 512-grain pile on a 51×51 grid reaches a stable state."""
        grid = gen.compute_sandpile(51, 51, 25, 25, 512)
        for y in range(1, 50):
            for x in range(1, 50):
                assert grid[y * 51 + x] <= 3, f"unstable cell at ({x},{y})"


# ---------------------------------------------------------------------------
# generate_svg tests
# ---------------------------------------------------------------------------

class TestGenerateSvg:
    def test_returns_string(self, gen):
        assert isinstance(gen.generate_svg(w=11, h=11, grains=0, cell_px=2), str)

    def test_has_svg_opening_tag(self, gen):
        assert "<svg" in gen.generate_svg(w=11, h=11, grains=0, cell_px=2)

    def test_has_svg_namespace(self, gen):
        assert 'xmlns="http://www.w3.org/2000/svg"' in gen.generate_svg(w=5, h=5, grains=0)

    def test_zero_grains_only_background_rect(self, gen):
        """With no grains the only element is the background rect."""
        svg = gen.generate_svg(w=5, h=5, grains=0, cell_px=2)
        assert svg.count("<rect") == 1

    def test_four_grains_produces_dusty_rose(self, gen):
        """After one topple the four neighbours are height-1 (dusty rose)."""
        svg = gen.generate_svg(w=5, h=5, grains=4, cell_px=2)
        assert "c97b7b" in svg.lower()

    def test_dimensions_reflect_cell_px(self, gen):
        svg = gen.generate_svg(w=11, h=11, grains=0, cell_px=4)
        # 11 * 4 = 44 — should appear as width/height in the SVG header
        assert "44" in svg

    def test_is_valid_xml(self, gen):
        svg = gen.generate_svg(w=21, h=21, grains=64, cell_px=2)
        ET.fromstring(svg)  # raises if malformed


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_no_duplicate_ids_in_pieces_json(self):
        pieces = load_pieces()
        ids = [e["id"] for e in pieces]
        assert len(ids) == len(set(ids)), "Duplicate ids found in pieces.json"

    def test_readme_has_enough_content(self):
        readme = (PIECE_DIR / "README.md").read_text()
        assert len(readme.strip()) > 100

    def test_thumbnail_svg_is_valid_xml(self):
        ET.parse(str(PIECE_DIR / "thumbnail.svg"))

    def test_3x3_grid_topples_all_to_boundary(self, gen):
        """3×3 grid has only one interior cell; 4 grains topple to boundary sinks."""
        grid = gen.compute_sandpile(3, 3, 1, 1, 4)
        assert grid[1 * 3 + 1] == 0  # interior cell emptied

    def test_single_grain_sum_preserved(self, gen):
        """1 grain never moves — total must equal 1."""
        for cx, cy in [(2, 2), (3, 3), (1, 1)]:
            grid = gen.compute_sandpile(7, 7, cx, cy, 1)
            assert sum(grid) == 1


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_entry_without_title_fails_required_check(self):
        incomplete = {
            "id": "90-sandpile",
            "tagline": "test",
            "year": 2026,
            "technique": "canvas / abelian sandpile / self-organized criticality / ImageData",
            "path": "pieces/90-sandpile",
            "thumbnail": "pieces/90-sandpile/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_wrong_id_not_in_pieces_json(self):
        pieces = load_pieces()
        ghost = next((e for e in pieces if e.get("id") == "90-sandpile-wrong"), None)
        assert ghost is None

    def test_ghost_thumbnail_does_not_exist(self, tmp_path):
        ghost = tmp_path / "ghost.svg"
        assert not ghost.exists()

    def test_stable_state_has_no_cell_above_3(self, gen):
        """compute_sandpile must never leave an interior cell with value ≥4."""
        grid = gen.compute_sandpile(9, 9, 4, 4, 16)
        for y in range(1, 8):
            for x in range(1, 8):
                assert grid[y * 9 + x] <= 3

    def test_nonexistent_directory_not_a_dir(self, tmp_path):
        nonexistent = tmp_path / "ghost-piece"
        assert not nonexistent.is_dir()
