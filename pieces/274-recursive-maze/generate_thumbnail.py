#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 274 — The Path Finds Itself.

Runs a deterministic recursive-backtracking DFS maze on a 20×20 grid with a
fixed seed, solves it via BFS, and exports the completed maze with its solution
path highlighted as a self-contained SVG.  Uses only the Python standard library.
"""
import pathlib
import random
from collections import deque

W, H = 400, 400
COLS, ROWS = 20, 20
CW, CH = W // COLS, H // ROWS  # 20 × 20 px per cell
WALL = 2                        # px wall border on each side of a cell interior

C_BG     = '#131008'
C_CARVED = '#ede5d0'
C_PATH   = '#f5d060'

NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
DR = (-1, 0, 1, 0)
DC = (0, 1, 0, -1)
OPP = (SOUTH, WEST, NORTH, EAST)


def generate_maze(rows: int, cols: int, seed: int = 42) -> list[list[int]]:
    """Return a perfect maze as a 2-D wall-bitmask grid via iterative DFS.

    Each cell's bitmask has 4 bits: bit i is set when the wall in direction i
    (N=0, E=1, S=2, W=3) is still intact.  Starting value is 0xF (all walls).

    Args:
        rows: Grid height in cells.
        cols: Grid width in cells.
        seed: PRNG seed for reproducibility.

    Returns:
        2-D list of shape [rows][cols] containing wall bitmasks.
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
    """Return the solution path from (0, 0) to (rows-1, cols-1) via BFS.

    Because the maze is a spanning tree (perfect maze), there is exactly one
    path between any two cells, so BFS finds it on the first try.

    Args:
        walls: Wall bitmask grid from generate_maze.
        rows: Grid height.
        cols: Grid width.

    Returns:
        List of (row, col) tuples from start to end inclusive, or [] if
        the destination is unreachable (e.g. all walls still up).
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


def cell_rect(r: int, c: int, color: str) -> str:
    """Return an SVG <rect> for the interior of cell (r, c).

    Args:
        r: Row index.
        c: Column index.
        color: CSS fill color.

    Returns:
        SVG <rect> element string.
    """
    x = c * CW + WALL
    y = r * CH + WALL
    w = CW - 2 * WALL
    h = CH - 2 * WALL
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'


def gap_rect(r1: int, c1: int, r2: int, c2: int, color: str) -> str:
    """Return an SVG <rect> bridging the 4-px wall gap between two adjacent cells.

    Each cell interior is inset by WALL px on every side.  The gap between
    neighbours is therefore 2*WALL = 4 px wide.  This rect fills that strip.

    Args:
        r1, c1: First cell coordinates.
        r2, c2: Second cell coordinates (must be directly adjacent to the first).
        color: CSS fill color.

    Returns:
        SVG <rect> element string.
    """
    if r1 == r2:
        left = min(c1, c2)
        x = (left + 1) * CW - WALL
        y = r1 * CH + WALL
        return (
            f'<rect x="{x}" y="{y}" width="{2 * WALL}" '
            f'height="{CH - 2 * WALL}" fill="{color}"/>'
        )
    top = min(r1, r2)
    x = c1 * CW + WALL
    y = (top + 1) * CH - WALL
    return (
        f'<rect x="{x}" y="{y}" width="{CW - 2 * WALL}" '
        f'height="{2 * WALL}" fill="{color}"/>'
    )


def make_svg() -> str:
    """Assemble and return the complete SVG thumbnail markup.

    Generates a deterministic maze (seed=42), overlays the BFS solution path
    in gold, and returns the SVG source string.

    Returns:
        Complete SVG document as a string.
    """
    walls = generate_maze(ROWS, COLS, seed=42)
    solution = solve_maze(walls, ROWS, COLS)

    rects: list[str] = []

    for r in range(ROWS):
        for c in range(COLS):
            rects.append(cell_rect(r, c, C_CARVED))
            for d in range(4):
                if walls[r][c] & (1 << d):
                    continue
                nr, nc = r + DR[d], c + DC[d]
                # Draw each passage exactly once by only going "forward".
                if (nr, nc) > (r, c):
                    rects.append(gap_rect(r, c, nr, nc, C_CARVED))

    for i, (r, c) in enumerate(solution):
        rects.append(cell_rect(r, c, C_PATH))
        if i > 0:
            pr, pc = solution[i - 1]
            rects.append(gap_rect(pr, pc, r, c, C_PATH))

    body = '\n  '.join(rects)
    return (
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"\n'
        f'     xmlns="http://www.w3.org/2000/svg">\n'
        f'  <rect width="{W}" height="{H}" fill="{C_BG}"/>\n'
        f'  {body}\n'
        f'</svg>\n'
    )


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text(make_svg())
    print(f'Written {out}')
