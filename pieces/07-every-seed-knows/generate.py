"""Generate a phyllotaxis golden-angle spiral as a standalone SVG."""

import math
import pathlib

GOLDEN_ANGLE_RAD = math.radians(137.508)
N_SEEDS = 800
SIZE = 600
SCALE = 10.0
PALETTE = ["#8fad75", "#d4a853", "#c2644f", "#e8dcc8", "#7a7a7a"]
BG = "#0f1a14"


def generate_svg(
    n_seeds: int = N_SEEDS,
    size: int = SIZE,
    scale: float = SCALE,
    palette: list = PALETTE,
    bg: str = BG,
    dot_r_min: float = 1.5,
    dot_r_max: float = 5.0,
) -> str:
    """Generate a self-contained SVG string for a phyllotaxis golden-angle spiral.

    Each dot n is placed at polar coordinates:
        angle = n * GOLDEN_ANGLE_RAD
        radius = sqrt(n) * scale

    Color cycles through palette by n % len(palette).
    Dot radius scales linearly from dot_r_min (center) to dot_r_max (edge).
    """
    center = size / 2
    circles = []
    for n in range(n_seeds):
        theta = n * GOLDEN_ANGLE_RAD
        r = math.sqrt(n) * scale
        x = center + r * math.cos(theta)
        y = center + r * math.sin(theta)
        dr = dot_r_min + (n / max(n_seeds - 1, 1)) * (dot_r_max - dot_r_min)
        color = palette[n % len(palette)]
        circles.append(
            f'  <circle cx="{x:.2f}" cy="{y:.2f}" r="{dr:.2f}" fill="{color}" opacity="0.9"/>'
        )
    body = "\n".join(circles)
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
    thumb = generate_svg(size=200, scale=3.2, dot_r_min=1.0, dot_r_max=2.5)
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    print(f"piece.svg: {len(piece):,} bytes | thumbnail.svg: {len(thumb):,} bytes")


if __name__ == "__main__":
    main()
