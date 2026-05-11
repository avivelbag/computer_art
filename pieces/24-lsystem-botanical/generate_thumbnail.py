#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 24 — L-system botanical.

Uses 5 iterations (633 segments) rather than the full 6 to keep the SVG
lightweight while still showing the full plant silhouette.
"""

import math
import pathlib

W, H       = 400, 400
PADDING    = 20
AXIOM      = 'X'
RULES      = {'X': 'F+[[X]-X]-F[-FX]+X', 'F': 'FF'}
ANGLE_DEG  = 25
ITERATIONS = 5

BG = '#f5f0e8'
C0 = '#2d6a4f'  # trunk / depth 0–1
C1 = '#74c69d'  # branches / depth 2–3
C2 = '#d8f3dc'  # leaf tips / depth 4+


def expand(axiom: str, rules: dict, n: int) -> str:
    """Expand axiom by applying rules n times."""
    s = axiom
    for _ in range(n):
        s = ''.join(rules.get(c, c) for c in s)
    return s


def turtle_walk(s: str, angle_deg: float) -> list[tuple]:
    """Interpret L-system string; return list of (x1, y1, x2, y2, depth) tuples.

    F: draw forward; +/-: rotate; [/]: push/pop stack with depth tracking.
    """
    da    = angle_deg * math.pi / 180
    stack: list[tuple] = []
    x, y, a, depth = 0.0, 0.0, -math.pi / 2, 0
    segs: list[tuple] = []

    for c in s:
        if c == 'F':
            nx, ny = x + math.cos(a), y + math.sin(a)
            segs.append((x, y, nx, ny, depth))
            x, y = nx, ny
        elif c == '+':
            a -= da
        elif c == '-':
            a += da
        elif c == '[':
            stack.append((x, y, a, depth))
            depth += 1
        elif c == ']':
            x, y, a, depth = stack.pop()

    return segs


def color_for_depth(d: int) -> str:
    if d <= 1:
        return C0
    if d <= 3:
        return C1
    return C2


def width_for_depth(d: int) -> float:
    if d == 0:
        return 2.5
    if d <= 2:
        return 1.2
    return 0.6


lsys     = expand(AXIOM, RULES, ITERATIONS)
raw_segs = turtle_walk(lsys, ANGLE_DEG)

xs = [v for s in raw_segs for v in (s[0], s[2])]
ys = [v for s in raw_segs for v in (s[1], s[3])]
min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
tree_w = max_x - min_x
tree_h = max_y - min_y

scale = min((W - 2 * PADDING) / tree_w, (H - 2 * PADDING) / tree_h)
off_x = (W - tree_w * scale) / 2 - min_x * scale
off_y = H - PADDING - max_y * scale


def tx(v: float) -> float:
    return v * scale + off_x


def ty(v: float) -> float:
    return v * scale + off_y


lines: list[str] = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
    f'  <rect width="{W}" height="{H}" fill="{BG}"/>',
]

for x1, y1, x2, y2, depth in raw_segs:
    c = color_for_depth(depth)
    w = width_for_depth(depth)
    lines.append(
        f'  <line x1="{tx(x1):.2f}" y1="{ty(y1):.2f}"'
        f' x2="{tx(x2):.2f}" y2="{ty(y2):.2f}"'
        f' stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
    )

lines.append('</svg>')

out = pathlib.Path(__file__).parent / 'thumbnail.svg'
out.write_text('\n'.join(lines) + '\n')
print(f'Wrote {out} ({len(raw_segs)} segments, {out.stat().st_size} bytes)')
