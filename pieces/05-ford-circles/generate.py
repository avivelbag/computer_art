"""Generate Ford circles SVG: fractal packing derived from the Farey sequence."""

import pathlib

MAX_Q = 60
CANVAS_W = 900
CANVAS_H = 560
BG = "#0a0614"

COLOR_STOPS = [
    (0.0, (26, 16, 96)),    # #1a1060 deep indigo (small q, large circles)
    (0.5, (42, 128, 112)),  # #2a8070 teal (mid denominator)
    (1.0, (224, 80, 96)),   # #e05060 warm rose (large q, fine circles)
]


def lerp_color(t: float) -> str:
    """Map t in [0, 1] through the 3-stop indigo→teal→rose palette."""
    t = max(0.0, min(1.0, t))
    for i in range(len(COLOR_STOPS) - 1):
        t0, c0 = COLOR_STOPS[i]
        t1, c1 = COLOR_STOPS[i + 1]
        if t <= t1:
            s = (t - t0) / (t1 - t0)
            r = int(round(c0[0] + s * (c1[0] - c0[0])))
            g = int(round(c0[1] + s * (c1[1] - c0[1])))
            b = int(round(c0[2] + s * (c1[2] - c0[2])))
            return f"#{r:02x}{g:02x}{b:02x}"
    r, g, b = COLOR_STOPS[-1][1]
    return f"#{r:02x}{g:02x}{b:02x}"


def ford_fractions(max_q: int) -> list[tuple[int, int]]:
    """Return all (p, q) Farey fractions with gcd(p, q)=1 and q <= max_q.

    Uses an iterative Stern-Brocot tree traversal: start from adjacent boundary
    fractions 0/1 and 1/1, insert the mediant (a+c)/(b+d) between every adjacent
    pair (a/b, c/d) whose denominator sum b+d <= max_q. This generates each
    reduced fraction in [0, 1] with denominator at most max_q exactly once.

    The count equals the Farey sequence length |F_n| = 1 + sum_{k=1}^{n} phi(k).
    For max_q=60 this is 1103 fractions.
    """
    if max_q < 1:
        return []
    result = [(0, 1), (1, 1)]
    stack = [(0, 1, 1, 1)]
    while stack:
        a, b, c, d = stack.pop()
        p, q = a + c, b + d
        if q <= max_q:
            result.append((p, q))
            stack.append((a, b, p, q))
            stack.append((p, q, c, d))
    return result


def generate_svg(
    max_q: int = MAX_Q,
    canvas_w: int = CANVAS_W,
    canvas_h: int = CANVAS_H,
) -> str:
    """Generate a Ford circles SVG string.

    Each reduced fraction p/q (gcd=1, q<=max_q) defines a Ford circle:
        center: (p/q, 1/(2q²)) in mathematical coordinates
        radius: 1/(2q²)

    The SVG maps the unit interval [0,1] to the full canvas width and scales y
    so the q=1 circles occupy ~88% of canvas height. Circles are stroke-only
    (fill=none), colored indigo→teal→rose by denominator q, and stroke-weighted
    by 2/q so large circles are bold and fine circles are hairlines. The q=1
    endpoint circles at 0/1 and 1/1 are naturally clipped at the canvas edges,
    showing the classic Gothic-arch semicircular composition.
    """
    y_scale = canvas_h * 0.88
    y_base = canvas_h - 8   # y position of the x-axis in SVG coords

    fractions = ford_fractions(max_q)
    fractions.sort(key=lambda pq: pq[1])   # large circles (low q) drawn first

    elements = []
    for p, q in fractions:
        r_math = 1.0 / (2 * q * q)
        cx = (p / q) * canvas_w
        r_svg = r_math * y_scale
        cy = y_base - r_svg

        t = (q - 1) / max(max_q - 1, 1)
        color = lerp_color(t)
        sw = max(0.15, 2.0 / q)

        elements.append(
            f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r_svg:.2f}" '
            f'fill="none" stroke="{color}" stroke-width="{sw:.3f}"/>'
        )

    body = "\n".join(elements)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" '
        f'width="{canvas_w}" height="{canvas_h}">\n'
        f'  <rect width="{canvas_w}" height="{canvas_h}" fill="{BG}"/>\n'
        f'{body}\n'
        f'</svg>\n'
    )


def main() -> None:
    """Write piece.svg (q<=60) and thumbnail.svg (q<=40) to this directory."""
    here = pathlib.Path(__file__).parent
    piece = generate_svg()
    thumb = generate_svg(max_q=40, canvas_w=300, canvas_h=187)
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    print(
        f"piece.svg: {len(piece):,} chars | "
        f"thumbnail.svg: {len(thumb):,} chars"
    )


if __name__ == "__main__":
    main()
