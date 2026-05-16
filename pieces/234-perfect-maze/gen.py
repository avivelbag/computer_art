"""Generate a perfect DFS maze as a self-contained SVG."""

import pathlib
import random
from collections import deque

COLS = 27
ROWS = 27
CELL = 22
SEED = 42
STROKE = 2.0
BG = "#0d0d1a"
WALL = "#e8dcc8"
PATH_COLOR = "#d4a853"

N, E, S, W = 1, 2, 4, 8
OPPOSITE = {N: S, S: N, E: W, W: E}
DELTA = {N: (0, -1), E: (1, 0), S: (0, 1), W: (-1, 0)}


def carve_maze(cols: int, rows: int, seed: int = SEED) -> list[list[int]]:
    """Return a grid[row][col] bitmask of open passages via iterative DFS.

    Each cell's bitmask has bits set for directions where a wall is removed
    (N=1, E=2, S=4, W=8). The DFS visits every cell exactly once, guaranteeing
    a perfect maze: fully connected, no loops, exactly one path between any two
    cells. Iteration avoids Python recursion-depth limits on large grids.
    """
    grid = [[0] * cols for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]
    rng = random.Random(seed)

    stack = [(0, 0)]
    visited[0][0] = True

    while stack:
        cx, cy = stack[-1]
        dirs = [
            d for d in (N, E, S, W)
            if 0 <= cx + DELTA[d][0] < cols
            and 0 <= cy + DELTA[d][1] < rows
            and not visited[cy + DELTA[d][1]][cx + DELTA[d][0]]
        ]
        if dirs:
            d = rng.choice(dirs)
            nx, ny = cx + DELTA[d][0], cy + DELTA[d][1]
            grid[cy][cx] |= d
            grid[ny][nx] |= OPPOSITE[d]
            visited[ny][nx] = True
            stack.append((nx, ny))
        else:
            stack.pop()

    return grid


def solve_maze(
    grid: list[list[int]], cols: int, rows: int
) -> list[tuple[int, int]]:
    """BFS from (0, 0) to (cols-1, rows-1); return solution path as (x, y) list.

    Uses standard BFS with a parent map so the path is reconstructed by walking
    backwards from the target. In a perfect maze BFS always finds the unique path.
    """
    target = (cols - 1, rows - 1)
    parent: dict[tuple[int, int], tuple[int, int] | None] = {(0, 0): None}
    queue: deque[tuple[int, int]] = deque([(0, 0)])

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) == target:
            break
        for d, (dx, dy) in DELTA.items():
            if grid[cy][cx] & d:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in parent:
                    parent[(nx, ny)] = (cx, cy)
                    queue.append((nx, ny))

    path: list[tuple[int, int]] = []
    pos: tuple[int, int] | None = target
    while pos is not None:
        path.append(pos)
        pos = parent.get(pos)
    path.reverse()
    return path


def generate_svg(
    cols: int = COLS,
    rows: int = ROWS,
    cell: int = CELL,
    seed: int = SEED,
    bg: str = BG,
    wall: str = WALL,
    path_color: str = PATH_COLOR,
    stroke: float = STROKE,
    show_solution: bool = True,
) -> str:
    """Generate a self-contained SVG of a DFS perfect maze with optional solution.

    Walls are rendered as line segments. Per-cell convention: draw the North wall
    if no north passage, and the West wall if no west passage; then draw the full
    South border and East border to close the frame. This avoids rendering any
    shared interior wall twice. The entrance gap is top-left (north wall of cell
    (0,0) is omitted) and the exit gap is bottom-right (south wall of
    (cols-1, rows-1) is omitted). The solution path is a polyline through cell
    centers in path_color.
    """
    margin = cell
    w = cols * cell + 2 * margin
    h = rows * cell + 2 * margin

    grid = carve_maze(cols, rows, seed)

    segments: list[str] = []

    def line(x1: float, y1: float, x2: float, y2: float) -> str:
        return (
            f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{wall}" stroke-width="{stroke}" stroke-linecap="square"/>'
        )

    for row in range(rows):
        for col in range(cols):
            x0 = margin + col * cell
            y0 = margin + row * cell

            # North wall — skip entrance gap at top-left cell
            if not (grid[row][col] & N):
                if not (row == 0 and col == 0):
                    segments.append(line(x0, y0, x0 + cell, y0))

            # West wall
            if not (grid[row][col] & W):
                segments.append(line(x0, y0, x0, y0 + cell))

    # South border — skip exit gap at bottom-right cell
    for col in range(cols):
        x0 = margin + col * cell
        y0 = margin + rows * cell
        if col == cols - 1:
            continue
        segments.append(line(x0, y0, x0 + cell, y0))

    # East border
    x_right = margin + cols * cell
    segments.append(line(x_right, margin, x_right, margin + rows * cell))

    solution_el = ""
    if show_solution:
        path = solve_maze(grid, cols, rows)
        half = cell // 2
        pts = " ".join(
            f"{margin + x * cell + half},{margin + y * cell + half}"
            for x, y in path
        )
        sw = max(1.0, stroke * 0.8)
        solution_el = (
            f'  <polyline points="{pts}" fill="none" stroke="{path_color}" '
            f'stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="0.9"/>\n'
        )

    body = "\n".join(segments)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">\n'
        f'  <rect width="{w}" height="{h}" fill="{bg}"/>\n'
        f'{solution_el}'
        f'{body}\n</svg>'
    )


def main() -> None:
    """Write piece.svg and thumbnail.svg next to this script."""
    here = pathlib.Path(__file__).parent
    piece = generate_svg()
    thumb = generate_svg(cols=15, rows=15, cell=14, stroke=1.5)
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    print(f"piece.svg: {len(piece):,} bytes | thumbnail.svg: {len(thumb):,} bytes")


if __name__ == "__main__":
    main()
