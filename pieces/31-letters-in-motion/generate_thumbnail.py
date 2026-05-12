#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 31 — Letters in Motion.

Approximates the canvas particle effect in static SVG: a dense hexagonal
grid of circles is clipped to an SVG <text> element, creating the
"particles forming letters" look without requiring any raster library.
Accent dots scatter outside the text at random positions.
"""

import pathlib
import random

W, H = 400, 400
BG = '#f5f0eb'
DARK = '#1a1a2e'
ACCENT = '#e94560'
STEP = 8
DOT_R = 2.5

random.seed(42)


def build_svg() -> str:
    """Construct the SVG source string for the thumbnail.

    Returns a complete SVG document that uses a clipPath with a <text>
    element to mask a hexagonal grid of circles, producing a dot-matrix
    rendering of the word DRIFT.
    """
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        '  <defs>',
        '    <clipPath id="tc">',
        '      <text x="200" y="248" font-family="Arial,sans-serif" font-size="128"',
        '            font-weight="bold" text-anchor="middle">DRIFT</text>',
        '    </clipPath>',
        '  </defs>',
        f'  <rect width="{W}" height="{H}" fill="{BG}"/>',
        f'  <g clip-path="url(#tc)" fill="{DARK}" opacity="0.9">',
    ]

    # Hexagonal dot grid clipped to text shape
    rows = H // STEP + 1
    cols = W // STEP + 2
    for row in range(rows):
        y = row * STEP
        ox = (STEP // 2) if row % 2 == 1 else 0
        for col in range(cols):
            x = col * STEP + ox - STEP
            if 0 <= x <= W:
                lines.append(f'    <circle cx="{x}" cy="{y}" r="{DOT_R}"/>')

    lines.append('  </g>')

    # Scattered accent dots — convey the dispersing phase
    lines.append(f'  <g fill="{ACCENT}" opacity="0.75">')
    for _ in range(70):
        cx = random.randint(10, 390)
        cy = random.randint(10, 390)
        r = round(random.uniform(1.0, 2.5), 1)
        lines.append(f'    <circle cx="{cx}" cy="{cy}" r="{r}"/>')
    lines.append('  </g>')
    lines.append('</svg>')

    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    svg = build_svg()
    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text(svg)
    print(f'Wrote {out} ({out.stat().st_size} bytes)')
