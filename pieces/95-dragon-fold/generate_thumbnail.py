"""Generate thumbnail.svg for Piece 95 — Dragon Curve: The Fold That Never Repeats.

Produces an SVG with the completed dragon curve at THUMB_ITERATIONS drawn as
colour-banded polylines (teal → rose), fitted to SIZE × SIZE with a dark background.
"""

import pathlib

SIZE = 400
MARGIN = 0.08
THUMB_ITERATIONS = 13
NUM_BANDS = 32

BG_COLOR = "#0a1628"
TEAL_COLOR = (13, 115, 119)
ROSE_COLOR = (196, 92, 142)
STROKE_WIDTH = 1.5


def ctz(n: int) -> int:
    """Count trailing zero bits of positive integer n."""
    count = 0
    while (n & 1) == 0:
        n >>= 1
        count += 1
    return count


def turn_left(n: int) -> bool:
    """Return True if the dragon curve turn at position n (1-indexed) is left.

    Uses the bit-sequence shortcut: the turn direction at segment boundary n
    is determined by the bit immediately above the lowest set bit of n.
    If that bit is 0, turn left (counterclockwise); if 1, turn right.
    This gives O(1) per turn without any string rewriting.
    """
    return ((n >> (ctz(n) + 1)) & 1) == 0


def dragon_points(iterations: int) -> list[tuple[int, int]]:
    """Compute integer-grid points for the dragon curve of the given iteration.

    Directions in screen coordinates (y increases downward):
      0=East, 1=North(y-1), 2=West, 3=South(y+1)
    LEFT (counterclockwise visually) = +1 mod 4
    RIGHT (clockwise visually)       = +3 mod 4

    Returns a list of (x, y) tuples of length 2**iterations + 1.
    """
    dx = [1, 0, -1, 0]
    dy = [0, -1, 0, 1]

    x, y = 0, 0
    points: list[tuple[int, int]] = [(x, y)]
    direction = 0

    n_segments = 1 << iterations
    for i in range(1, n_segments + 1):
        x += dx[direction]
        y += dy[direction]
        points.append((x, y))
        if i < n_segments:
            if turn_left(i):
                direction = (direction + 1) & 3
            else:
                direction = (direction + 3) & 3

    return points


def _lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> str:
    r = round(c1[0] + (c2[0] - c1[0]) * t)
    g = round(c1[1] + (c2[1] - c1[1]) * t)
    b = round(c1[2] + (c2[2] - c1[2]) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def generate_svg(iterations: int = THUMB_ITERATIONS, size: int = SIZE) -> str:
    """Return SVG source string for the dragon curve at the given iteration.

    The curve is scaled to fill (1 - 2*MARGIN) of the canvas, centred.
    Colour transitions from TEAL_COLOR to ROSE_COLOR across NUM_BANDS polylines.
    """
    points = dragon_points(iterations)
    n_pts = len(points)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    fw = x_max - x_min or 1
    fh = y_max - y_min or 1
    fill_size = size * (1.0 - 2.0 * MARGIN)
    scale = fill_size / max(fw, fh)
    ox = (size - fw * scale) / 2.0 - x_min * scale
    oy = (size - fh * scale) / 2.0 - y_min * scale

    def cx(x: int) -> str:
        return f"{x * scale + ox:.1f}"

    def cy(y: int) -> str:
        return f"{y * scale + oy:.1f}"

    n_segs = n_pts - 1
    band_size = max(1, n_segs // NUM_BANDS)

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}"'
        f' width="{size}" height="{size}">',
        f'  <rect width="{size}" height="{size}" fill="{BG_COLOR}"/>',
    ]

    band = 0
    while band < NUM_BANDS:
        start = band * band_size
        if start >= n_pts:
            break
        end = min(start + band_size + 1, n_pts)

        t = band / max(NUM_BANDS - 1, 1)
        color = _lerp_color(TEAL_COLOR, ROSE_COLOR, t)

        pts_str = " ".join(f"{cx(x)},{cy(y)}" for x, y in points[start:end])
        lines.append(
            f'  <polyline points="{pts_str}" fill="none" stroke="{color}"'
            f' stroke-width="{STROKE_WIDTH}" stroke-linejoin="round"'
            f' stroke-linecap="round"/>'
        )
        band += 1

    lines.append("</svg>")
    return "\n".join(lines)


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(generate_svg())
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")
