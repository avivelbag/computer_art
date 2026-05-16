"""Tests for pieces/234-perfect-maze/gen.py."""

import pathlib
import sys

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "234-perfect-maze"
sys.path.insert(0, str(PIECE_DIR))
import gen  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def count_lines(svg: str) -> int:
    """Return number of <line elements in an SVG string."""
    return svg.count("<line ")


def count_polylines(svg: str) -> int:
    """Return number of <polyline elements in an SVG string."""
    return svg.count("<polyline ")


# ---------------------------------------------------------------------------
# carve_maze
# ---------------------------------------------------------------------------

class TestCarveMaze:
    def test_grid_dimensions(self):
        """carve_maze must return a grid with the requested number of rows and cols."""
        grid = gen.carve_maze(10, 8, seed=1)
        assert len(grid) == 8
        assert all(len(row) == 10 for row in grid)

    def test_all_cells_reachable(self):
        """Every cell must be reachable from (0,0) via open passages — the maze is perfect."""
        cols, rows = 12, 12
        grid = gen.carve_maze(cols, rows, seed=42)
        visited = [[False] * cols for _ in range(rows)]
        stack = [(0, 0)]
        visited[0][0] = True
        while stack:
            cx, cy = stack.pop()
            for d, (dx, dy) in gen.DELTA.items():
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx]:
                    if grid[cy][cx] & d:
                        visited[ny][nx] = True
                        stack.append((nx, ny))
        assert all(visited[r][c] for r in range(rows) for c in range(cols))

    def test_passages_are_bidirectional(self):
        """If cell A has a passage to B, B must have the reciprocal passage back."""
        cols, rows = 8, 8
        grid = gen.carve_maze(cols, rows, seed=7)
        for row in range(rows):
            for col in range(cols):
                for d, (dx, dy) in gen.DELTA.items():
                    nx, ny = col + dx, row + dy
                    if 0 <= nx < cols and 0 <= ny < rows:
                        if grid[row][col] & d:
                            assert grid[ny][nx] & gen.OPPOSITE[d], (
                                f"Passage {d} at ({col},{row}) has no reciprocal at ({nx},{ny})"
                            )

    def test_deterministic_with_same_seed(self):
        """Two calls with the same seed must produce identical grids."""
        g1 = gen.carve_maze(10, 10, seed=99)
        g2 = gen.carve_maze(10, 10, seed=99)
        assert g1 == g2

    def test_different_seeds_differ(self):
        """Different seeds should (almost certainly) produce different mazes."""
        g1 = gen.carve_maze(10, 10, seed=1)
        g2 = gen.carve_maze(10, 10, seed=2)
        assert g1 != g2

    def test_single_cell(self):
        """A 1×1 maze has one cell with no passages (no neighbors to connect to)."""
        grid = gen.carve_maze(1, 1, seed=0)
        assert len(grid) == 1
        assert len(grid[0]) == 1
        assert grid[0][0] == 0

    def test_single_row(self):
        """A 1×N maze must carve a straight corridor — each cell connects east."""
        cols = 5
        grid = gen.carve_maze(cols, 1, seed=0)
        for c in range(cols - 1):
            assert grid[0][c] & gen.E, f"Cell ({c},0) should open east"
            assert grid[0][c + 1] & gen.W, f"Cell ({c+1},0) should open west"

    def test_large_maze_completes(self):
        """carve_maze must finish for a 50×50 grid without error."""
        grid = gen.carve_maze(50, 50, seed=42)
        assert len(grid) == 50
        assert len(grid[0]) == 50


# ---------------------------------------------------------------------------
# solve_maze
# ---------------------------------------------------------------------------

class TestSolveMaze:
    def test_path_starts_at_origin(self):
        """Solution path must start at (0, 0)."""
        grid = gen.carve_maze(10, 10, seed=42)
        path = gen.solve_maze(grid, 10, 10)
        assert path[0] == (0, 0)

    def test_path_ends_at_target(self):
        """Solution path must end at (cols-1, rows-1)."""
        cols, rows = 10, 10
        grid = gen.carve_maze(cols, rows, seed=42)
        path = gen.solve_maze(grid, cols, rows)
        assert path[-1] == (cols - 1, rows - 1)

    def test_path_continuity(self):
        """Each step in the path must move exactly one cell in a cardinal direction."""
        grid = gen.carve_maze(12, 12, seed=5)
        path = gen.solve_maze(grid, 12, 12)
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            assert abs(x2 - x1) + abs(y2 - y1) == 1, (
                f"Non-adjacent step from ({x1},{y1}) to ({x2},{y2})"
            )

    def test_path_uses_open_passages(self):
        """Every step in the path must traverse an open passage in the maze."""
        grid = gen.carve_maze(12, 12, seed=5)
        path = gen.solve_maze(grid, 12, 12)
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            dx, dy = x2 - x1, y2 - y1
            d = next(d for d, delta in gen.DELTA.items() if delta == (dx, dy))
            assert grid[y1][x1] & d, (
                f"Step from ({x1},{y1}) to ({x2},{y2}) crosses a closed wall"
            )

    def test_single_cell_maze_path(self):
        """1×1 maze: path is just the single cell, no movement needed."""
        grid = gen.carve_maze(1, 1, seed=0)
        path = gen.solve_maze(grid, 1, 1)
        assert path == [(0, 0)]


# ---------------------------------------------------------------------------
# generate_svg — structure tests
# ---------------------------------------------------------------------------

class TestGenerateSVG:
    def test_svg_namespace(self):
        """SVG must carry the proper namespace declaration."""
        svg = gen.generate_svg(cols=5, rows=5)
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_background_rect_present(self):
        """SVG must include a background <rect element."""
        svg = gen.generate_svg(cols=5, rows=5)
        assert "<rect" in svg

    def test_solution_polyline_present_by_default(self):
        """With show_solution=True (default), a <polyline element must be present."""
        svg = gen.generate_svg(cols=5, rows=5, show_solution=True)
        assert count_polylines(svg) == 1

    def test_solution_polyline_absent_when_disabled(self):
        """With show_solution=False, no <polyline element should appear."""
        svg = gen.generate_svg(cols=5, rows=5, show_solution=False)
        assert count_polylines(svg) == 0

    def test_wall_lines_present(self):
        """SVG must contain <line elements representing maze walls."""
        svg = gen.generate_svg(cols=5, rows=5)
        assert count_lines(svg) > 0

    def test_viewbox_matches_dimensions(self):
        """viewBox must encode the computed canvas width and height."""
        cols, rows, cell = 5, 5, 20
        margin = cell
        w = cols * cell + 2 * margin
        h = rows * cell + 2 * margin
        svg = gen.generate_svg(cols=cols, rows=rows, cell=cell)
        assert f'viewBox="0 0 {w} {h}"' in svg

    def test_custom_bg_color_appears(self):
        """The supplied bg color must appear in the background rect."""
        svg = gen.generate_svg(cols=4, rows=4, bg="#ff0000")
        assert "#ff0000" in svg

    def test_custom_wall_color_appears(self):
        """The supplied wall color must appear in line elements."""
        svg = gen.generate_svg(cols=4, rows=4, wall="#00ff00")
        assert "#00ff00" in svg

    def test_custom_path_color_appears(self):
        """The supplied path_color must appear in the solution polyline."""
        svg = gen.generate_svg(cols=4, rows=4, path_color="#abcdef")
        assert "#abcdef" in svg

    def test_deterministic_output(self):
        """Same parameters must always produce byte-for-byte identical SVG."""
        svg1 = gen.generate_svg(cols=6, rows=6, seed=10)
        svg2 = gen.generate_svg(cols=6, rows=6, seed=10)
        assert svg1 == svg2

    def test_large_grid_completes(self):
        """generate_svg must complete for the default 27×27 grid."""
        svg = gen.generate_svg()
        assert "<svg" in svg
        assert count_lines(svg) > 100

    def test_1x1_grid(self):
        """A 1×1 grid must produce a valid SVG shell with minimal walls."""
        svg = gen.generate_svg(cols=1, rows=1)
        assert "<svg" in svg
        assert "<rect" in svg


# ---------------------------------------------------------------------------
# Committed files
# ---------------------------------------------------------------------------

class TestCommittedFiles:
    def test_gen_py_exists(self):
        """gen.py must be committed in the piece directory."""
        assert (PIECE_DIR / "gen.py").is_file()

    def test_piece_svg_exists(self):
        """piece.svg must be committed alongside gen.py."""
        assert (PIECE_DIR / "piece.svg").is_file()

    def test_thumbnail_svg_exists(self):
        """thumbnail.svg must be committed."""
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_index_html_exists(self):
        """index.html must be committed."""
        assert (PIECE_DIR / "index.html").is_file()

    def test_readme_exists(self):
        """README.md must be committed."""
        assert (PIECE_DIR / "README.md").is_file()

    def test_piece_svg_has_lines(self):
        """Committed piece.svg must contain <line wall elements."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert count_lines(content) > 0

    def test_thumbnail_smaller_than_piece(self):
        """thumbnail.svg must be smaller in bytes than piece.svg."""
        piece = (PIECE_DIR / "piece.svg").read_text()
        thumb = (PIECE_DIR / "thumbnail.svg").read_text()
        assert len(thumb) < len(piece)

    def test_piece_svg_valid_svg(self):
        """piece.svg must open with the SVG tag and carry the namespace."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert "<svg" in content
        assert 'xmlns="http://www.w3.org/2000/svg"' in content

    def test_piece_svg_has_solution_path(self):
        """Committed piece.svg must include the amber solution polyline."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert "<polyline" in content


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_no_passage_bits_set_on_fresh_grid(self):
        """Before carving, every cell should have 0 passage bits (sanity check)."""
        cols, rows = 4, 4
        grid = [[0] * cols for _ in range(rows)]
        for row in grid:
            for cell in row:
                assert cell == 0

    def test_solve_returns_only_target_if_unreachable(self):
        """solve_maze on a grid with no open passages returns only the target cell.

        BFS never reaches (2,2) so parent has no entry for it; the path
        reconstruction walk starts at the target and immediately stops,
        returning a one-element list with just the target.
        """
        grid = [[0] * 3 for _ in range(3)]
        path = gen.solve_maze(grid, 3, 3)
        assert path == [(2, 2)]

    def test_generate_svg_output_writable(self, tmp_path):
        """generate_svg output can be written to disk and read back intact."""
        svg = gen.generate_svg(cols=4, rows=4)
        out = tmp_path / "test.svg"
        out.write_text(svg)
        assert out.read_text() == svg
