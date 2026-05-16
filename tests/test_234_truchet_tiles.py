"""Tests for pieces/234-truchet-tiles/gen.py."""

import importlib.util
import pathlib

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "234-truchet-tiles"

_spec = importlib.util.spec_from_file_location(
    "gen_truchet_tiles", PIECE_DIR / "gen.py"
)
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)


# ---------------------------------------------------------------------------
# make_orientations
# ---------------------------------------------------------------------------


class TestMakeOrientations:
    def test_dimensions(self):
        """Grid must have exactly rows rows, each with cols values."""
        grid = gen.make_orientations(8, 5, seed=0)
        assert len(grid) == 5
        assert all(len(row) == 8 for row in grid)

    def test_values_binary(self):
        """Every cell must be 0 or 1."""
        grid = gen.make_orientations(20, 20, seed=42)
        for row in grid:
            for val in row:
                assert val in (0, 1)

    def test_deterministic(self):
        """Same (cols, rows, seed) always produces the same grid."""
        g1 = gen.make_orientations(10, 10, seed=7)
        g2 = gen.make_orientations(10, 10, seed=7)
        assert g1 == g2

    def test_different_seeds_differ(self):
        """Different seeds must produce different grids (for any reasonably sized grid)."""
        g1 = gen.make_orientations(10, 10, seed=1)
        g2 = gen.make_orientations(10, 10, seed=2)
        assert g1 != g2

    def test_both_orientations_appear(self):
        """A large grid must contain both orientation 0 and orientation 1."""
        grid = gen.make_orientations(20, 20, seed=99)
        flat = [v for row in grid for v in row]
        assert 0 in flat
        assert 1 in flat

    def test_1x1_grid(self):
        """1×1 grid must return a single-element nested list."""
        grid = gen.make_orientations(1, 1, seed=0)
        assert len(grid) == 1
        assert len(grid[0]) == 1
        assert grid[0][0] in (0, 1)


# ---------------------------------------------------------------------------
# tile_paths
# ---------------------------------------------------------------------------


class TestTilePaths:
    def test_returns_two_strings(self):
        """tile_paths must return exactly two non-empty path strings."""
        a1, a2 = gen.tile_paths(0.0, 0.0, 10.0, 0)
        assert isinstance(a1, str) and a1
        assert isinstance(a2, str) and a2

    def test_orient_a_starts_at_top_midpoint(self):
        """Orientation-A arc 1 must start at the top-edge midpoint."""
        a1, _ = gen.tile_paths(0.0, 0.0, 10.0, 0)
        assert "M 10.0,0.0" in a1

    def test_orient_b_starts_at_top_midpoint(self):
        """Orientation-B arc 1 must also start at the top-edge midpoint."""
        a1, _ = gen.tile_paths(0.0, 0.0, 10.0, 1)
        assert "M 10.0,0.0" in a1

    def test_orient_a_arc1_endpoint(self):
        """Orientation-A arc 1 must end at the left-edge midpoint."""
        a1, _ = gen.tile_paths(0.0, 0.0, 10.0, 0)
        assert a1.strip().endswith("0.0,10.0")

    def test_orient_a_arc2_endpoint(self):
        """Orientation-A arc 2 must end at the bottom-edge midpoint."""
        _, a2 = gen.tile_paths(0.0, 0.0, 10.0, 0)
        assert a2.strip().endswith("10.0,20.0")

    def test_orient_b_arc1_endpoint(self):
        """Orientation-B arc 1 must end at the right-edge midpoint."""
        a1, _ = gen.tile_paths(0.0, 0.0, 10.0, 1)
        assert a1.strip().endswith("20.0,10.0")

    def test_orient_b_arc2_endpoint(self):
        """Orientation-B arc 2 must end at the bottom-edge midpoint."""
        _, a2 = gen.tile_paths(0.0, 0.0, 10.0, 1)
        assert a2.strip().endswith("10.0,20.0")

    def test_orient_a_uses_cw_sweep_for_arc1(self):
        """Orientation-A arc 1 curves CW around the top-left corner (sweep-flag=1)."""
        a1, _ = gen.tile_paths(0.0, 0.0, 10.0, 0)
        assert " 0 0 1 " in a1

    def test_orient_a_uses_ccw_sweep_for_arc2(self):
        """Orientation-A arc 2 curves CCW around the bottom-right corner (sweep-flag=0)."""
        _, a2 = gen.tile_paths(0.0, 0.0, 10.0, 0)
        assert " 0 0 0 " in a2

    def test_orient_b_uses_ccw_sweep_for_arc1(self):
        """Orientation-B arc 1 curves CCW around the top-right corner (sweep-flag=0)."""
        a1, _ = gen.tile_paths(0.0, 0.0, 10.0, 1)
        assert " 0 0 0 " in a1

    def test_orient_b_uses_cw_sweep_for_arc2(self):
        """Orientation-B arc 2 curves CW around the bottom-left corner (sweep-flag=1)."""
        _, a2 = gen.tile_paths(0.0, 0.0, 10.0, 1)
        assert " 0 0 1 " in a2

    def test_nonzero_offset(self):
        """Tile at non-zero (px, py) must shift all coordinates by (px, py)."""
        a1_zero, _ = gen.tile_paths(0.0, 0.0, 10.0, 0)
        a1_shift, _ = gen.tile_paths(100.0, 200.0, 10.0, 0)
        assert "M 110.0,200.0" in a1_shift
        assert "M 10.0,0.0" in a1_zero


# ---------------------------------------------------------------------------
# generate_svg — structure
# ---------------------------------------------------------------------------


class TestGenerateSvgStructure:
    def test_returns_string(self):
        """generate_svg must return a non-empty string."""
        svg = gen.generate_svg(cols=5, rows=5, cell=10, seed=1)
        assert isinstance(svg, str) and svg

    def test_is_valid_svg_open_close(self):
        """SVG must open with <svg and close with </svg>."""
        svg = gen.generate_svg(cols=5, rows=5, cell=10, seed=1)
        assert svg.strip().startswith("<svg ")
        assert svg.strip().endswith("</svg>")

    def test_viewbox_matches_dimensions(self):
        """viewBox attribute must reflect cols×cell + 2×margin."""
        cell = 10
        margin = cell
        svg = gen.generate_svg(cols=4, rows=3, cell=cell, margin=margin)
        expected_w = 4 * cell + 2 * margin
        expected_h = 3 * cell + 2 * margin
        assert f'viewBox="0 0 {expected_w} {expected_h}"' in svg
        assert f'width="{expected_w}"' in svg
        assert f'height="{expected_h}"' in svg

    def test_background_rect_present(self):
        """SVG must contain a background <rect> element."""
        svg = gen.generate_svg(cols=5, rows=5, cell=10, seed=1)
        assert "<rect " in svg

    def test_path_elements_present(self):
        """SVG must contain at least one <path> element (the arc paths)."""
        svg = gen.generate_svg(cols=5, rows=5, cell=10, seed=1)
        assert "<path " in svg

    def test_at_most_two_path_elements(self):
        """SVG must have at most two <path> elements (one per color group)."""
        svg = gen.generate_svg(cols=10, rows=10, cell=10, seed=42)
        assert svg.count("<path ") <= 2

    def test_background_color_in_svg(self):
        """The chosen background color must appear in the SVG."""
        svg = gen.generate_svg(cols=5, rows=5, cell=10, seed=1, bg="#aabbcc")
        assert "#aabbcc" in svg

    def test_color_a_in_svg(self):
        """color_a must appear in the SVG whenever at least one A-orientation tile exists."""
        svg = gen.generate_svg(cols=10, rows=10, cell=10, seed=7, color_a="#111111")
        assert "#111111" in svg

    def test_color_b_in_svg(self):
        """color_b must appear in the SVG whenever at least one B-orientation tile exists."""
        svg = gen.generate_svg(cols=10, rows=10, cell=10, seed=7, color_b="#222222")
        assert "#222222" in svg

    def test_deterministic(self):
        """Same parameters must produce byte-identical SVG strings."""
        s1 = gen.generate_svg(cols=8, rows=8, cell=12, seed=5)
        s2 = gen.generate_svg(cols=8, rows=8, cell=12, seed=5)
        assert s1 == s2

    def test_different_seeds_differ(self):
        """Different seeds must produce different SVGs."""
        s1 = gen.generate_svg(cols=8, rows=8, cell=12, seed=1)
        s2 = gen.generate_svg(cols=8, rows=8, cell=12, seed=2)
        assert s1 != s2


# ---------------------------------------------------------------------------
# generate_svg — arc content
# ---------------------------------------------------------------------------


class TestGenerateSvgArcs:
    def test_arc_commands_present(self):
        """SVG path data must contain arc commands (A)."""
        svg = gen.generate_svg(cols=5, rows=5, cell=10, seed=1)
        assert " A " in svg

    def test_arc_count_matches_tiles(self):
        """Each tile contributes exactly 2 arcs; count of M subpaths must equal 2 × cols × rows."""
        cols, rows = 4, 3
        svg = gen.generate_svg(cols=cols, rows=rows, cell=10, seed=1)
        assert svg.count(" A ") == cols * rows * 2

    def test_stroke_linecap_round(self):
        """Arcs must use stroke-linecap='round' for smooth termination."""
        svg = gen.generate_svg(cols=5, rows=5, cell=10, seed=1)
        assert 'stroke-linecap="round"' in svg

    def test_fill_none(self):
        """Arc paths must have fill='none' so arcs are not filled."""
        svg = gen.generate_svg(cols=5, rows=5, cell=10, seed=1)
        assert 'fill="none"' in svg


# ---------------------------------------------------------------------------
# generate_svg — edge cases
# ---------------------------------------------------------------------------


class TestGenerateSvgEdgeCases:
    def test_1x1_grid(self):
        """A 1×1 grid must produce a valid SVG with exactly 2 arcs."""
        svg = gen.generate_svg(cols=1, rows=1, cell=20, seed=0)
        assert svg.count(" A ") == 2

    def test_large_grid(self):
        """A 50×50 grid must produce a valid SVG without error."""
        svg = gen.generate_svg(cols=50, rows=50, cell=10, seed=99)
        assert svg.count(" A ") == 50 * 50 * 2
        assert svg.strip().endswith("</svg>")

    def test_custom_margin(self):
        """A custom margin must be reflected in viewBox dimensions."""
        svg = gen.generate_svg(cols=4, rows=4, cell=10, margin=5)
        assert 'viewBox="0 0 50 50"' in svg

    def test_zero_margin(self):
        """Zero margin must produce a canvas exactly cols×cell × rows×cell."""
        svg = gen.generate_svg(cols=3, rows=2, cell=10, margin=0)
        assert 'viewBox="0 0 30 20"' in svg


# ---------------------------------------------------------------------------
# File outputs
# ---------------------------------------------------------------------------


class TestFileOutputs:
    def test_piece_svg_exists(self):
        """piece.svg must exist in the piece directory."""
        assert (PIECE_DIR / "piece.svg").exists()

    def test_thumbnail_svg_exists(self):
        """thumbnail.svg must exist in the piece directory."""
        assert (PIECE_DIR / "thumbnail.svg").exists()

    def test_gen_py_exists(self):
        """gen.py must exist in the piece directory."""
        assert (PIECE_DIR / "gen.py").exists()

    def test_readme_exists(self):
        """README.md must exist in the piece directory."""
        assert (PIECE_DIR / "README.md").exists()

    def test_piece_svg_content(self):
        """piece.svg must be a valid SVG string produced by gen.py."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert content.strip().startswith("<svg ")
        assert content.strip().endswith("</svg>")

    def test_piece_svg_matches_generator(self):
        """piece.svg on disk must match what generate_svg() produces with defaults."""
        expected = gen.generate_svg()
        actual = (PIECE_DIR / "piece.svg").read_text()
        assert actual == expected

    def test_thumbnail_is_smaller_than_piece(self):
        """thumbnail.svg must be smaller in byte size than piece.svg."""
        piece_size = (PIECE_DIR / "piece.svg").stat().st_size
        thumb_size = (PIECE_DIR / "thumbnail.svg").stat().st_size
        assert thumb_size < piece_size


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------


class TestPiecesJson:
    def test_entry_exists(self):
        """pieces.json must contain an entry for 234-truchet-tiles."""
        import json

        pieces_file = PIECE_DIR.parent.parent / "pieces.json"
        pieces = json.loads(pieces_file.read_text())
        ids = [p["id"] for p in pieces]
        assert "234-truchet-tiles" in ids

    def test_entry_path(self):
        """The pieces.json entry must point to the correct directory path."""
        import json

        pieces_file = PIECE_DIR.parent.parent / "pieces.json"
        pieces = json.loads(pieces_file.read_text())
        entry = next(p for p in pieces if p["id"] == "234-truchet-tiles")
        assert entry["path"] == "pieces/234-truchet-tiles"

    def test_entry_thumbnail(self):
        """The pieces.json entry thumbnail path must point to an existing file."""
        import json

        pieces_file = PIECE_DIR.parent.parent / "pieces.json"
        pieces = json.loads(pieces_file.read_text())
        entry = next(p for p in pieces if p["id"] == "234-truchet-tiles")
        thumb_path = PIECE_DIR.parent.parent / entry["thumbnail"]
        assert thumb_path.exists()

    def test_no_duplicate_234_perfect_maze(self):
        """234-perfect-maze must no longer be the piece-234 entry (replaced by truchet-tiles)."""
        import json

        pieces_file = PIECE_DIR.parent.parent / "pieces.json"
        pieces = json.loads(pieces_file.read_text())
        ids = [p["id"] for p in pieces]
        assert "234-perfect-maze" not in ids
