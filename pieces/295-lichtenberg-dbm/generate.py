"""
Generate thumbnail.svg for the Arc & Ether Lichtenberg-DBM piece.

Runs a deterministic Dielectric Breakdown Model on a 120×120 grid, grows
the discharge tree for up to MAX_STEPS steps, then exports the tree edges
as SVG paths with a glow filter on a deep-indigo background.
"""
import math
import random
import pathlib

# ── Grid parameters ──────────────────────────────────────────────────────────
W, H = 120, 120
CX, CY = W // 2, H // 2
ETA = 1.5          # branching exponent
LOCAL_R = 10       # relaxation radius
RELAX_N = 40       # Gauss-Seidel iterations per growth step
MAX_STEPS = 700    # maximum segments before stopping

# Output dimensions (SVG logical pixels)
SVG_W, SVG_H = 300, 300
SCALE = SVG_W / W


def make_phi(w: int, h: int, cx: int, cy: int) -> list[float]:
    """
    Return a flat phi array initialised to dist(x,y,centre)/max_dist.
    Edge cells are fixed at 1.0 (source electrode); the radial approximation
    lets local relaxation converge quickly without a full global solve.
    """
    max_d = math.sqrt(cx * cx + cy * cy)
    phi = [0.0] * (w * h)
    for y in range(h):
        for x in range(w):
            i = y * w + x
            if x == 0 or x == w - 1 or y == 0 or y == h - 1:
                phi[i] = 1.0
            else:
                phi[i] = math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max_d
    return phi


def add_to_tree(
    x: int,
    y: int,
    par_idx: int | None,
    phi: list[float],
    tree: list[bool],
    frontier: set,
    parent_of: dict,
    w: int,
    h: int,
) -> None:
    """
    Mark cell (x, y) as a tree node: set phi=0, record parent, update frontier.
    """
    i = y * w + x
    tree[i] = True
    phi[i] = 0.0
    frontier.discard(i)
    if par_idx is not None:
        parent_of[i] = par_idx
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and not tree[ny * w + nx]:
            frontier.add(ny * w + nx)


def relax_around(
    ox: int,
    oy: int,
    phi: list[float],
    tree: list[bool],
    w: int,
    h: int,
    local_r: int,
    relax_n: int,
) -> None:
    """
    Run relax_n Gauss-Seidel sweeps on free cells within local_r of (ox, oy).
    Edge and tree cells are skipped (their phi values are fixed boundaries).
    """
    r2 = local_r * local_r
    for _ in range(relax_n):
        for dy in range(-local_r, local_r + 1):
            for dx in range(-local_r, local_r + 1):
                if dx * dx + dy * dy > r2:
                    continue
                nx, ny = ox + dx, oy + dy
                if nx <= 0 or nx >= w - 1 or ny <= 0 or ny >= h - 1:
                    continue
                i = ny * w + nx
                if tree[i]:
                    continue
                phi[i] = (phi[i - w] + phi[i + w] + phi[i - 1] + phi[i + 1]) * 0.25


def pick_frontier(
    frontier: set,
    phi: list[float],
    eta: float,
    rng: random.Random,
) -> int:
    """
    Return a frontier cell index sampled with probability ∝ phi[i]^eta.
    Falls back to uniform sampling if all weights are zero.
    """
    cells = list(frontier)
    total = 0.0
    weights = []
    for ci in cells:
        p = phi[ci]
        w = (p ** eta) if p > 0 else 0.0
        weights.append(w)
        total += w
    if total == 0.0:
        return rng.choice(cells)
    r = rng.random() * total
    for ci, wt in zip(cells, weights):
        r -= wt
        if r <= 0:
            return ci
    return cells[-1]


def grow_tree(
    w: int,
    h: int,
    cx: int,
    cy: int,
    eta: float,
    local_r: int,
    relax_n: int,
    max_steps: int,
    seed: int = 42,
) -> dict[int, int]:
    """
    Grow a DBM discharge tree on a w×h grid from (cx, cy) until the tree
    reaches the canvas boundary or max_steps is reached.

    Returns parent_of: {cell_idx: parent_idx} for all non-seed tree cells.
    """
    rng = random.Random(seed)
    phi = make_phi(w, h, cx, cy)
    tree = [False] * (w * h)
    frontier: set = set()
    parent_of: dict = {}

    add_to_tree(cx, cy, None, phi, tree, frontier, parent_of, w, h)
    # Warm up local field around seed
    relax_around(cx, cy, phi, tree, w, h, local_r, relax_n)
    relax_around(cx, cy, phi, tree, w, h, local_r, relax_n)

    for _ in range(max_steps):
        if not frontier:
            break
        chosen = pick_frontier(frontier, phi, eta, rng)
        nx, ny = chosen % w, chosen // w

        par_idx = None
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nnx, nny = nx + ddx, ny + ddy
            if 0 <= nnx < w and 0 <= nny < h and tree[nny * w + nnx]:
                par_idx = nny * w + nnx
                break

        add_to_tree(nx, ny, par_idx, phi, tree, frontier, parent_of, w, h)
        relax_around(nx, ny, phi, tree, w, h, local_r, relax_n)

        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            break

    return parent_of


def render_svg(
    parent_of: dict[int, int],
    w: int,
    h: int,
    svg_w: int,
    svg_h: int,
) -> str:
    """
    Convert the tree edge list (parent_of map) to an SVG string.
    Uses a Gaussian blur filter for the outer glow and draws the bright
    core on top in white-violet (#d0c8ff).
    """
    sx = svg_w / w
    sy = svg_h / h

    path_parts: list[str] = []
    for cell_idx, par_idx in parent_of.items():
        x1, y1 = (par_idx % w) * sx, (par_idx // w) * sy
        x2, y2 = (cell_idx % w) * sx, (cell_idx // w) * sy
        path_parts.append(f"M{x1:.2f},{y1:.2f}L{x2:.2f},{y2:.2f}")

    d = " ".join(path_parts)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{svg_w}" height="{svg_h}"'
        f' viewBox="0 0 {svg_w} {svg_h}">',
        "<defs>",
        '  <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">',
        '    <feGaussianBlur stdDeviation="2.5" result="blur"/>',
        '    <feMerge>',
        '      <feMergeNode in="blur"/>',
        '      <feMergeNode in="SourceGraphic"/>',
        '    </feMerge>',
        "  </filter>",
        "</defs>",
        f'<rect width="{svg_w}" height="{svg_h}" fill="#08071a"/>',
        f'<path d="{d}" stroke="#6040c0" stroke-width="2.5"'
        f' stroke-linecap="round" fill="none" filter="url(#glow)"/>',
        f'<path d="{d}" stroke="#d0c8ff" stroke-width="0.8"'
        f' stroke-linecap="round" fill="none"/>',
        "</svg>",
    ]
    return "\n".join(lines)


def main() -> None:
    parent_of = grow_tree(
        W, H, CX, CY, ETA, LOCAL_R, RELAX_N, MAX_STEPS, seed=42
    )
    svg = render_svg(parent_of, W, H, SVG_W, SVG_H)
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg)
    print(f"Wrote {out} ({len(parent_of)} segments)")


if __name__ == "__main__":
    main()
