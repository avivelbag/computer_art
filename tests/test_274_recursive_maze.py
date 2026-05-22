"""Tests for Piece 274 — The Path Finds Itself (recursive-backtracking maze)."""

import json
import pathlib
import random
from collections import deque

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "274-recursive-maze"
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}

NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
DR = (-1, 0, 1, 0)
DC = (0, 1, 0, -1)
OPP = (SOUTH, WEST, NORTH, EAST)


# ---------------------------------------------------------------------------
# Algorithm helpers (mirrors the Python logic in generate_thumbnail.py)
# ---------------------------------------------------------------------------


def generate_maze(rows: int, cols: int, seed: int = 42) -> list[list[int]]:
    """Generate a perfect maze via iterative DFS backtracking.

    Returns a 2-D list where walls[r][c] is a 4-bit bitmask: bit i set means
    the wall in direction i (N=0, E=1, S=2, W=3) is still intact.

    Args:
        rows: Grid height in cells.
        cols: Grid width in cells.
        seed: PRNG seed for determinism.

    Returns:
        2-D list of shape [rows][cols] with wall bitmasks.
    """
    rng = random.Random(seed)
    walls = [[0xF] * cols for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]
    stack = [(0, 0)]
    visited[0][0] = True
    while stack:
        r, c = stack[-1]
        dirs = [0, 1, 2, 3]
        rng.shuffle(dirs)
        moved = False
        for d in dirs:
            nr, nc = r + DR[d], c + DC[d]
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                visited[nr][nc] = True
                walls[r][c] &= ~(1 << d)
                walls[nr][nc] &= ~(1 << OPP[d])
                stack.append((nr, nc))
                moved = True
                break
        if not moved:
            stack.pop()
    return walls


def solve_maze(
    walls: list[list[int]], rows: int, cols: int
) -> list[tuple[int, int]]:
    """Find the path from (0, 0) to (rows-1, cols-1) via BFS.

    Returns an empty list when the destination is unreachable (e.g. all walls
    intact and rows > 1 or cols > 1).

    Args:
        walls: Wall bitmask grid as returned by generate_maze.
        rows: Grid height.
        cols: Grid width.

    Returns:
        List of (row, col) tuples from start to end inclusive, or [].
    """
    dist = [[-1] * cols for _ in range(rows)]
    prev: list[list[tuple[int, int] | None]] = [[None] * cols for _ in range(rows)]
    queue: deque[tuple[int, int]] = deque([(0, 0)])
    dist[0][0] = 0
    while queue:
        r, c = queue.popleft()
        if r == rows - 1 and c == cols - 1:
            break
        for d in range(4):
            if walls[r][c] & (1 << d):
                continue
            nr, nc = r + DR[d], c + DC[d]
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                prev[nr][nc] = (r, c)
                queue.append((nr, nc))
    if dist[rows - 1][cols - 1] == -1:
        return []
    path: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = (rows - 1, cols - 1)
    while cur is not None:
        path.append(cur)
        cur = prev[cur[0]][cur[1]]
    path.reverse()
    return path


def count_passages(walls: list[list[int]], rows: int, cols: int) -> int:
    """Count opened passages in the maze (each counted once).

    Args:
        walls: Wall bitmask grid.
        rows: Grid height.
        cols: Grid width.

    Returns:
        Number of unique carved passages.
    """
    total = 0
    for r in range(rows):
        for c in range(cols):
            for d in range(4):
                if not (walls[r][c] & (1 << d)):
                    total += 1
    return total // 2  # each passage stored in two cells


# ---------------------------------------------------------------------------
# File structure tests
# ---------------------------------------------------------------------------


class TestFileStructure:
    def test_piece_directory_exists(self):
        """The piece directory must be present at the expected path."""
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_thumbnail_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()

    def test_index_html_not_empty(self):
        html = (PIECE_DIR / "index.html").read_text()
        assert len(html) > 500

    def test_readme_mentions_technique(self):
        readme = (PIECE_DIR / "README.md").read_text().lower()
        assert "dfs" in readme or "backtrack" in readme or "depth-first" in readme

    def test_thumbnail_is_valid_svg(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert content.strip().startswith("<svg")
        assert "xmlns" in content

    def test_thumbnail_under_500kb(self):
        size = (PIECE_DIR / "thumbnail.svg").stat().st_size
        assert size < 500 * 1024, f"Thumbnail is {size // 1024} KB, must be < 500 KB"


# ---------------------------------------------------------------------------
# pieces.json registration tests
# ---------------------------------------------------------------------------


class TestPiecesJson:
    def _load(self) -> list[dict]:
        return json.loads(PIECES_JSON.read_text())

    def _entry(self) -> dict:
        return next((e for e in self._load() if e["id"] == "274-recursive-maze"), {})

    def test_entry_present(self):
        assert self._entry(), "274-recursive-maze not found in pieces.json"

    def test_entry_has_all_required_fields(self):
        entry = self._entry()
        assert REQUIRED_FIELDS <= entry.keys(), f"Missing: {REQUIRED_FIELDS - entry.keys()}"

    def test_entry_id_matches_dir_name(self):
        entry = self._entry()
        assert entry["id"] == pathlib.Path(entry["path"]).name

    def test_entry_path_is_directory(self):
        entry = self._entry()
        assert (REPO / entry["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        entry = self._entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_entry_year_is_int(self):
        assert isinstance(self._entry()["year"], int)

    def test_entry_technique_mentions_maze(self):
        tech = self._entry().get("technique", "").lower()
        assert "maze" in tech or "dfs" in tech or "backtrack" in tech

    def test_total_entry_count_not_reduced(self):
        data = self._load()
        assert len(data) >= 111, f"Expected ≥111 entries, got {len(data)}"


# ---------------------------------------------------------------------------
# HTML content checks
# ---------------------------------------------------------------------------


class TestHtmlContent:
    def _html(self) -> str:
        return (PIECE_DIR / "index.html").read_text()

    def test_uses_canvas(self):
        assert "<canvas" in self._html()

    def test_animates_with_raf(self):
        assert "requestAnimationFrame" in self._html()

    def test_no_external_urls(self):
        html = self._html()
        assert "https://" not in html
        assert "http://" not in html

    def test_canvas_is_800_by_800(self):
        html = self._html()
        assert 'width="800"' in html and 'height="800"' in html

    def test_declares_wall_constant(self):
        assert "walls" in self._html()

    def test_declares_dfs_stack(self):
        assert "dfsStack" in self._html() or "stack" in self._html()

    def test_has_cream_color(self):
        assert "ede5d0" in self._html()

    def test_has_terracotta_color(self):
        assert "d4692a" in self._html()

    def test_has_gold_path_color(self):
        assert "f5d060" in self._html()


# ---------------------------------------------------------------------------
# Maze algorithm correctness
# ---------------------------------------------------------------------------


class TestMazeAlgorithm:
    def test_perfect_maze_has_correct_passage_count(self):
        """A spanning-tree maze of N cells must have exactly N-1 passages."""
        rows, cols = 10, 10
        walls = generate_maze(rows, cols, seed=1)
        assert count_passages(walls, rows, cols) == rows * cols - 1

    def test_maze_is_solvable_small(self):
        """BFS must find a valid path in a 5×5 maze."""
        walls = generate_maze(5, 5, seed=7)
        path = solve_maze(walls, 5, 5)
        assert len(path) > 0
        assert path[0] == (0, 0)
        assert path[-1] == (4, 4)

    def test_maze_is_solvable_large(self):
        """BFS must find a valid path in a 40×40 maze (production size)."""
        walls = generate_maze(40, 40, seed=99)
        path = solve_maze(walls, 40, 40)
        assert path[0] == (0, 0)
        assert path[-1] == (39, 39)

    def test_solve_path_is_contiguous(self):
        """Every consecutive pair in the solution path must be adjacent."""
        walls = generate_maze(8, 8, seed=13)
        path = solve_maze(walls, 8, 8)
        for i in range(1, len(path)):
            r1, c1 = path[i - 1]
            r2, c2 = path[i]
            assert abs(r1 - r2) + abs(c1 - c2) == 1, (
                f"Non-adjacent step at index {i}: {path[i-1]} → {path[i]}"
            )

    def test_solve_path_follows_open_passages(self):
        """Every step in the solution path must cross a carved (open) passage."""
        walls = generate_maze(10, 10, seed=17)
        path = solve_maze(walls, 10, 10)
        for i in range(1, len(path)):
            r1, c1 = path[i - 1]
            r2, c2 = path[i]
            dr, dc = r2 - r1, c2 - c1
            for d in range(4):
                if DR[d] == dr and DC[d] == dc:
                    assert not (walls[r1][c1] & (1 << d)), (
                        f"Wall still intact between {(r1,c1)} and {(r2,c2)}"
                    )
                    break

    def test_wall_symmetry(self):
        """If cell A lacks its east wall, cell B to the east must lack its west wall."""
        walls = generate_maze(6, 6, seed=5)
        for r in range(6):
            for c in range(5):
                has_east = bool(walls[r][c] & (1 << EAST))
                has_west = bool(walls[r][c + 1] & (1 << WEST))
                assert has_east == has_west, f"Wall asymmetry at ({r},{c}) E/W"

    def test_different_seeds_produce_different_mazes(self):
        """Two different seeds must produce different wall configurations."""
        walls_a = generate_maze(10, 10, seed=1)
        walls_b = generate_maze(10, 10, seed=999)
        assert walls_a != walls_b

    def test_same_seed_is_deterministic(self):
        """The same seed must always produce the same maze."""
        walls_a = generate_maze(10, 10, seed=42)
        walls_b = generate_maze(10, 10, seed=42)
        assert walls_a == walls_b

    def test_trivial_1x1_maze(self):
        """A 1×1 maze is trivially solved: start and end are the same cell."""
        walls = generate_maze(1, 1, seed=0)
        path = solve_maze(walls, 1, 1)
        assert path == [(0, 0)]

    def test_all_walls_up_is_unsolvable(self):
        """When all walls are intact a 3×3 maze cannot be solved."""
        walls = [[0xF] * 3 for _ in range(3)]
        path = solve_maze(walls, 3, 3)
        assert path == []

    def test_50x50_maze_generates_and_solves(self):
        """Performance sanity: a 50×50 maze must complete without error."""
        walls = generate_maze(50, 50, seed=99)
        path = solve_maze(walls, 50, 50)
        assert path[0] == (0, 0)
        assert path[-1] == (49, 49)
