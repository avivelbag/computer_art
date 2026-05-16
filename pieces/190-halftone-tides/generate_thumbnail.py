#!/usr/bin/env python3
"""Generate a static SVG thumbnail for Halftone Tides at snapshot time t=1.2."""

import math
import pathlib

W, H = 400, 400
COLS, ROWS = 40, 40
CELL_W = W / COLS
CELL_H = H / ROWS
MAX_R = min(CELL_W, CELL_H) * 0.45

BG  = '#1a0a2e'
DOT = '#f7c95b'

WAVES = [
    {'kx':  0.08, 'ky':  0.06, 'freq': 1.1, 'phase': 0.0},
    {'kx': -0.05, 'ky':  0.10, 'freq': 0.7, 'phase': 1.2},
    {'kx':  0.12, 'ky': -0.04, 'freq': 1.5, 'phase': 2.4},
    {'kx': -0.07, 'ky': -0.09, 'freq': 0.9, 'phase': 3.7},
]

T_SNAPSHOT = 1.2


def wave_value(cx, cy, t):
    v = 0.0
    for w in WAVES:
        v += math.sin(w['kx'] * cx + w['ky'] * cy + w['freq'] * t + w['phase'])
    return v / len(WAVES)


def dot_radius(cx, cy, t):
    v = wave_value(cx, cy, t)
    norm = max(0.1, min(0.9, v * 0.5 + 0.5))
    return MAX_R * norm


def main():
    circles = []
    for row in range(ROWS):
        for col in range(COLS):
            cx = (col + 0.5) * CELL_W
            cy = (row + 0.5) * CELL_H
            r = dot_radius(cx, cy, T_SNAPSHOT)
            circles.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" fill="{DOT}"/>')

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        *circles,
        '</svg>',
    ]

    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text('\n'.join(lines))
    print(f'Wrote {out} ({len(circles)} circles)')


if __name__ == '__main__':
    main()
