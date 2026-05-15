#!/usr/bin/env python3
"""Generates thumbnail.svg: a 400×400 static snapshot of the ASCII scalar field at t=2.5."""

import math
from pathlib import Path

RAMP = [' ', '.', '·', ':', '-', '=', '+', 'o', 'O', '#', '@']

# Same four plane waves as index.html: [freq_x, freq_y, speed, phase_offset]
WAVES = [
    (0.08, 0.05, 0.9, 0.0),
    (0.04, 0.09, 0.7, 1.2),
    (0.10, 0.03, 1.1, 2.4),
    (0.06, 0.07, 0.6, 3.7),
]

W, H = 400, 400
CELL_W = 8
CELL_H = 10
COLS = W // CELL_W   # 50
ROWS = H // CELL_H   # 40
T = 2.5              # snapshot time chosen for interesting interference pattern


def scalar(cx: int, cy: int) -> float:
    """Normalised plane-wave superposition at snapshot time T, cell (cx, cy)."""
    val = sum(math.sin(cx * fx + cy * fy + T * sp + ph) for fx, fy, sp, ph in WAVES)
    return (val / len(WAVES) + 1) / 2


def hsl_bg(val: float) -> str:
    h = 200 + val * 60
    l = max(3.0, 8 + val * 10)
    return f"hsl({h:.0f},70%,{l:.0f}%)"


def hsl_fg(val: float) -> str:
    h = 200 + val * 60
    l = 20 + val * 60
    return f"hsl({h:.0f},80%,{l:.0f}%)"


def build_svg() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">',
        '<rect width="400" height="400" fill="#020810"/>',
    ]

    for row in range(ROWS):
        for col in range(COLS):
            val = scalar(col, row)
            char_idx = min(len(RAMP) - 1, int(val * len(RAMP)))
            ch = RAMP[char_idx]

            x = col * CELL_W
            y = row * CELL_H

            lines.append(
                f'<rect x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" fill="{hsl_bg(val)}"/>'
            )
            if ch != ' ':
                # Escape XML-special chars; none appear in RAMP, but be defensive
                safe_ch = ch.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                lines.append(
                    f'<text x="{x}" y="{y + CELL_H - 1}" '
                    f'font-family="monospace" font-size="{CELL_H}" fill="{hsl_fg(val)}">'
                    f'{safe_ch}</text>'
                )

    lines.append('</svg>')
    return '\n'.join(lines)


def main() -> None:
    svg = build_svg()
    out = Path(__file__).parent / 'thumbnail.svg'
    out.write_text(svg, encoding='utf-8')
    print(f"Wrote {out} ({COLS}×{ROWS} cells)")


if __name__ == '__main__':
    main()
