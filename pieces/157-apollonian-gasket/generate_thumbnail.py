#!/usr/bin/env python3
"""Generates thumbnail.svg: a 400×400 static Apollonian gasket (depth 0–5)."""

import math
from pathlib import Path

MIN_R = 1.0
MAX_DEPTH = 5
OUTER_R = 190  # scaled for 400×400 canvas

PALETTE = [
    (232, 160,  32),
    (212,  90,  64),
    (180,  60, 120),
    (130,  70, 190),
    ( 80,  90, 220),
    ( 50, 120, 220),
    ( 60, 150, 210),
]


def depth_alpha(depth):
    return max(0.4, 1 - depth * 0.08)


def circle_key(x, y, r):
    return (round(x * 10), round(y * 10), round(r * 10))


def build_gasket():
    """Return list of (k, x, y, r, depth) tuples using the Apollonian reflection formula."""
    k0 = -1 / OUTER_R
    r1 = OUTER_R * math.sqrt(3) / (2 + math.sqrt(3))
    k1 = 1 / r1
    d1 = OUTER_R - r1

    C0 = (k0, 0.0,                   0.0,  OUTER_R, -1)
    C1 = (k1, 0.0,                   -d1,  r1,       0)
    C2 = (k1,  d1 * math.sqrt(3)/2,  d1/2, r1,       0)
    C3 = (k1, -d1 * math.sqrt(3)/2,  d1/2, r1,       0)

    circles = [C1, C2, C3]
    seen = {circle_key(c[1], c[2], c[3]) for c in circles}

    queue = [
        (C1, C2, C3, C0, 1),
        (C0, C2, C3, C1, 1),
        (C0, C1, C3, C2, 1),
        (C0, C1, C2, C3, 1),
    ]

    qi = 0
    while qi < len(queue):
        a, b, c, p, depth = queue[qi]
        qi += 1
        if depth > MAX_DEPTH:
            continue
        kn = 2 * (a[0] + b[0] + c[0]) - p[0]
        if kn <= 0:
            continue
        rn = 1 / kn
        if rn < MIN_R:
            continue
        xn = (2 * (a[1]*a[0] + b[1]*b[0] + c[1]*c[0]) - p[1]*p[0]) / kn
        yn = (2 * (a[2]*a[0] + b[2]*b[0] + c[2]*c[0]) - p[2]*p[0]) / kn
        key = circle_key(xn, yn, rn)
        if key in seen:
            continue
        seen.add(key)
        cn = (kn, xn, yn, rn, depth)
        circles.append(cn)
        queue.append((b, c, cn, a, depth + 1))
        queue.append((a, c, cn, b, depth + 1))
        queue.append((a, b, cn, c, depth + 1))

    return circles


def main():
    circles = build_gasket()
    CX = CY = 200

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">',
        '<rect width="400" height="400" fill="#050A1A"/>',
        f'<defs><clipPath id="bc"><circle cx="{CX}" cy="{CY}" r="{OUTER_R}"/></clipPath></defs>',
        '<g clip-path="url(#bc)">',
    ]

    for k, x, y, r, depth in circles:
        if depth < 0:
            continue
        rc, gc, bc = PALETTE[min(depth, len(PALETTE) - 1)]
        alpha = depth_alpha(depth)
        lines.append(
            f'<circle cx="{CX+x:.1f}" cy="{CY+y:.1f}" r="{r:.1f}" '
            f'fill="rgb({rc},{gc},{bc})" fill-opacity="{alpha:.2f}"/>'
        )

    lines += [
        '</g>',
        f'<circle cx="{CX}" cy="{CY}" r="{OUTER_R}" fill="none" stroke="#1a2a4a" stroke-width="1.5"/>',
        '</svg>',
    ]

    out = Path(__file__).parent / 'thumbnail.svg'
    out.write_text('\n'.join(lines))
    print(f"Wrote {out} ({len(circles)} circles)")


if __name__ == '__main__':
    main()
