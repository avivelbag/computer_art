"""Generate an Apollonian gasket as a standalone SVG using Descartes' Circle Theorem."""

import cmath
import math
import pathlib
from collections import deque

SIZE = 800
THUMB_SIZE = 400
MIN_RADIUS_PX = 2.0

BG_COLOR = "#040E14"
BOUNDING_STROKE = "#1A3040"

# 6-stop depth palette: deep teal (largest circles) → near-white cream (smallest)
PALETTE = [
    "#0D3B4F",
    "#1A7A7A",
    "#2EB5A0",
    "#F0C040",
    "#E85C3A",
    "#FFF5E0",
]


def _initial_circles(R: float) -> list[tuple[float, complex]]:
    r = R * math.sqrt(3) / (2.0 + math.sqrt(3))
    d = R - r
    return [
        (-1.0 / R, 0 + 0j),
        (1.0 / r, cmath.rect(d, math.pi / 2)),
        (1.0 / r, cmath.rect(d, 7 * math.pi / 6)),
        (1.0 / r, cmath.rect(d, 11 * math.pi / 6)),
    ]


def _circle_color(r: float, r_max: float) -> str:
    if r_max <= MIN_RADIUS_PX:
        return PALETTE[-1]
    t = math.log(r_max / r) / math.log(r_max / MIN_RADIUS_PX)
    t = max(0.0, min(1.0, t))
    idx = min(int(t * len(PALETTE)), len(PALETTE) - 1)
    return PALETTE[idx]


def apollonian_circles(R: float, min_r: float) -> list[tuple[float, complex]]:
    """Generate all circles in an Apollonian gasket via the Apollonian reflection formula.

    Starts from the canonical 4-circle configuration: one enclosing circle (negative
    curvature) and three equal inner circles. For every tangent triple (Ca, Cb, Cc)
    with a known parent circle Cp, the reflection formula finds the twin circle:

        k_new = 2*(ka + kb + kc) - k_parent
        z_new = (2*(za*ka + zb*kb + zc*kc) - z_parent*k_parent) / k_new

    Three new triples are enqueued for each discovered circle. BFS terminates once
    all inscribed circles fall below min_r.

    Returns (radius, center) pairs sorted by decreasing radius, excluding the enclosing
    bounding circle.
    """
    init = _initial_circles(R)
    c0, c1, c2, c3 = init

    result: list[tuple[float, complex]] = []
    seen: set[tuple] = set()

    def _key(r: float, z: complex) -> tuple:
        return (round(z.real, 0), round(z.imag, 0), round(r, 1))

    def _maybe_add(k: float, z: complex) -> None:
        if k <= 0:
            return
        r = 1.0 / k
        if r < min_r:
            return
        key = _key(r, z)
        if key in seen:
            return
        seen.add(key)
        result.append((r, z))

    for c in (c1, c2, c3):
        _maybe_add(*c)

    queue: deque = deque([
        ((c0, c1, c2), c3),
        ((c0, c1, c3), c2),
        ((c0, c2, c3), c1),
        ((c1, c2, c3), c0),
    ])

    while queue:
        ((ka, za), (kb, zb), (kc, zc)), (kp, zp) = queue.popleft()

        k_new = 2.0 * (ka + kb + kc) - kp
        if k_new <= 0:
            continue
        r_new = 1.0 / k_new
        if r_new < min_r:
            continue

        z_new = (2.0 * (za * ka + zb * kb + zc * kc) - zp * kp) / k_new
        key = _key(r_new, z_new)
        if key in seen:
            continue
        seen.add(key)
        result.append((r_new, z_new))

        cn = (k_new, z_new)
        ca, cb, cc = (ka, za), (kb, zb), (kc, zc)
        queue.append(((cn, cb, cc), ca))
        queue.append(((ca, cn, cc), cb))
        queue.append(((ca, cb, cn), cc))

    result.sort(key=lambda x: -x[0])
    return result


def _svg_body(circles: list[tuple[float, complex]], R: float, size: int) -> str:
    cx = cy = size / 2
    r_max = circles[0][0] if circles else 1.0
    clip_id = "bc"

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}">',
        f'<rect width="{size}" height="{size}" fill="{BG_COLOR}"/>',
        f'<defs><clipPath id="{clip_id}">',
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}"/></clipPath></defs>',
        f'<g clip-path="url(#{clip_id})">',
    ]

    for r, z in circles:
        x = cx + z.real
        y = cy + z.imag
        color = _circle_color(r, r_max)
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}"/>')

    lines.append('</g>')
    lines.append(
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="none" '
        f'stroke="{BOUNDING_STROKE}" stroke-width="1.5"/>'
    )
    lines.append('</svg>')
    return '\n'.join(lines)


def generate_svg(size: int = SIZE, min_r: float = MIN_RADIUS_PX) -> str:
    """Generate a self-contained SVG of an Apollonian gasket.

    Three equal circles packed inside a bounding circle seed the recursion.
    Interstice circles are found via the Apollonian reflection formula.
    Circle color maps log-scale radius through 6 palette stops (deep teal → cream).
    Circles smaller than min_r px are omitted.
    """
    R = size * 0.47
    circles = apollonian_circles(R, min_r)
    return _svg_body(circles, R, size)


def generate_thumbnail(size: int = THUMB_SIZE) -> str:
    """Generate a thumbnail SVG at the given size using the same min_r as the full piece."""
    return generate_svg(size=size, min_r=MIN_RADIUS_PX)


def _html_wrapper(svg: str) -> str:
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        "<title>Apollonian Gasket — circles all the way down</title>\n"
        "<style>\n"
        f"html,body{{margin:0;padding:0;background:{BG_COLOR};"
        "display:flex;align-items:center;justify-content:center;min-height:100vh}\n"
        "svg{max-width:96vmin;max-height:96vmin}\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        + svg
        + "\n</body></html>"
    )


def main() -> None:
    """Write piece.svg, thumbnail.svg, and index.html next to this script."""
    here = pathlib.Path(__file__).parent
    piece = generate_svg()
    thumb = generate_thumbnail()
    index = _html_wrapper(piece)
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    (here / "index.html").write_text(index)
    n_piece = piece.count("<circle") - 2
    n_thumb = thumb.count("<circle") - 2
    print(f"piece.svg:     {len(piece.encode()):,} bytes  ({n_piece} circles)")
    print(f"thumbnail.svg: {len(thumb.encode()):,} bytes  ({n_thumb} circles)")
    print(f"index.html:    {len(index.encode()):,} bytes")


if __name__ == "__main__":
    main()
