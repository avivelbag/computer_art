"""Generate a recursive quadtree subdivision SVG (Mondrian-style)."""

import pathlib
import random

SEED = 42
SIZE = 800
MAX_DEPTH = 6
SPLIT_PROB_BASE = 0.85
MIN_SIZE = 40.0
STROKE_WIDTH = 1.5
STROKE_COLOR = "#1a1a1a"

PALETTE = [
    "#c2644f",
    "#8fad75",
    "#d4a853",
    "#4a6fa5",
    "#5c5c5c",
]
WHITE_COLORS = ["#f5f0e8", "#ede7d9"]
WHITE_FRACTION = 0.22


def _subdivide(x, y, w, h, depth, rng, max_depth, min_size, split_prob_base):
    """Recursively split a rectangle into axis-aligned leaf rectangles.

    Each call decides whether to split based on split_prob_base^depth so
    the probability of splitting decreases exponentially with depth.
    The cut position is sampled uniformly from [0.3, 0.7] of the chosen
    dimension to prevent degenerate slivers; the longer axis is preferred.
    Returns a list of (x, y, w, h) leaf tuples that tile the input rect exactly.
    """
    split_prob = split_prob_base ** depth
    if depth >= max_depth or min(w, h) < min_size or rng.random() > split_prob:
        return [(x, y, w, h)]

    if w > h * 1.5:
        horizontal = False
    elif h > w * 1.5:
        horizontal = True
    else:
        horizontal = rng.random() < 0.5

    cut = rng.uniform(0.3, 0.7)

    if horizontal:
        h1 = h * cut
        h2 = h - h1
        if min(h1, h2) < min_size / 2:
            return [(x, y, w, h)]
        return _subdivide(
            x, y, w, h1, depth + 1, rng, max_depth, min_size, split_prob_base
        ) + _subdivide(
            x, y + h1, w, h2, depth + 1, rng, max_depth, min_size, split_prob_base
        )
    else:
        w1 = w * cut
        w2 = w - w1
        if min(w1, w2) < min_size / 2:
            return [(x, y, w, h)]
        return _subdivide(
            x, y, w1, h, depth + 1, rng, max_depth, min_size, split_prob_base
        ) + _subdivide(
            x + w1, y, w2, h, depth + 1, rng, max_depth, min_size, split_prob_base
        )


def generate_svg(
    size: int = SIZE,
    seed: int = SEED,
    palette: list = None,
    white_colors: list = None,
    white_fraction: float = WHITE_FRACTION,
    stroke_width: float = STROKE_WIDTH,
    stroke_color: str = STROKE_COLOR,
    max_depth: int = MAX_DEPTH,
    min_size: float = MIN_SIZE,
    split_prob_base: float = SPLIT_PROB_BASE,
) -> str:
    """Generate a self-contained SVG of a recursive quadtree subdivision.

    Uses a seeded RNG so the same seed always produces the same composition.
    Leaf rectangles pick a colour from palette; white_fraction of them get a
    cream/white tone instead, providing intentional breathing room.
    """
    if palette is None:
        palette = PALETTE
    if white_colors is None:
        white_colors = WHITE_COLORS

    rng = random.Random(seed)
    leaves = _subdivide(
        0.0, 0.0, float(size), float(size), 0, rng, max_depth, min_size, split_prob_base
    )

    rects = []
    for x, y, w, h in leaves:
        if rng.random() < white_fraction:
            color = rng.choice(white_colors)
        else:
            color = rng.choice(palette)
        rects.append(
            f'  <rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'fill="{color}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        )

    body = "\n".join(rects)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}">\n'
        f'{body}\n</svg>'
    )


def main() -> None:
    """Write piece.svg and thumbnail.svg to the same directory as this script."""
    here = pathlib.Path(__file__).parent
    piece = generate_svg()
    thumb = generate_svg(size=200, min_size=10.0)
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    print(f"piece.svg: {len(piece):,} bytes | thumbnail.svg: {len(thumb):,} bytes")


if __name__ == "__main__":
    main()
