"""Generate a pen-plotter-style Lissajous family as a static SVG."""

import math
import pathlib

SIZE = 800
THUMB_SIZE = 400
N_POINTS = 800
STROKE_WIDTH = 0.5
STROKE_OPACITY = 0.25
INK = "#1a1a2e"
BG = "#f5f0e8"
MARGIN = 40

FREQUENCY_PAIRS = [
    (1, 2), (1, 3), (1, 4), (2, 3), (2, 5), (3, 4), (3, 5),
    (4, 5), (3, 7), (4, 7), (5, 6), (5, 7), (1, 1), (2, 1),
]
DELTAS_PER_PAIR = 4


def _lissajous_path(
    a: int,
    b: int,
    delta: float,
    n_points: int,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
) -> str:
    """Return a single SVG path data string for one Lissajous curve.

    Samples (sin(a*t + delta), sin(b*t)) at n_points equally-spaced values
    of t in [0, 2π], mapped from [-1,1] into the canvas coordinate space
    centred at (cx, cy) with half-extents (rx, ry).
    """
    step = 2 * math.pi / n_points
    coords = []
    for i in range(n_points + 1):
        t = i * step
        x = cx + rx * math.sin(a * t + delta)
        y = cy + ry * math.sin(b * t)
        coords.append(f"{x:.2f},{y:.2f}")
    return "M " + " L ".join(coords)


def generate_svg(
    size: int = SIZE,
    n_points: int = N_POINTS,
    stroke_width: float = STROKE_WIDTH,
    stroke_opacity: float = STROKE_OPACITY,
    ink: str = INK,
    bg: str = BG,
    margin: int = MARGIN,
    frequency_pairs: list = None,
    deltas_per_pair: int = DELTAS_PER_PAIR,
) -> str:
    """Generate a self-contained SVG string with a family of Lissajous curves.

    For each (a, b) frequency pair, `deltas_per_pair` phase offsets are spread
    uniformly over [0, π/2] to produce the characteristic family spread.
    All curves share the same canvas centre and drawing extent, bounded by
    `margin` pixels of breathing room on each side.
    """
    if frequency_pairs is None:
        frequency_pairs = FREQUENCY_PAIRS

    cx = size / 2
    cy = size / 2
    rx = (size / 2) - margin
    ry = (size / 2) - margin

    paths = []
    for a, b in frequency_pairs:
        for k in range(deltas_per_pair):
            delta = (k / max(deltas_per_pair - 1, 1)) * (math.pi / 2)
            d = _lissajous_path(a, b, delta, n_points, cx, cy, rx, ry)
            paths.append(
                f'  <path d="{d}" fill="none" stroke="{ink}" '
                f'stroke-width="{stroke_width}" opacity="{stroke_opacity}"/>'
            )

    body = "\n".join(paths)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}">\n'
        f'  <rect width="{size}" height="{size}" fill="{bg}"/>\n'
        f'{body}\n</svg>'
    )


def main() -> None:
    """Write piece.svg and thumbnail.svg to the same directory as this script."""
    here = pathlib.Path(__file__).parent
    piece = generate_svg()
    thumb = generate_svg(size=THUMB_SIZE, margin=20)
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    print(f"piece.svg: {len(piece):,} bytes | thumbnail.svg: {len(thumb):,} bytes")


if __name__ == "__main__":
    main()
