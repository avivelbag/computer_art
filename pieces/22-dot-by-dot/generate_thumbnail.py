#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 22 — halftone risograph.

Evaluates the same damped radial ripple used in index.html on a 20×20 grid
at phase=0, then writes each dot (shadow pass + coral pass) as SVG circles.
"""

import math
import pathlib

W, H   = 400, 400
COLS   = 20
ROWS   = 20
CELL_W = W / COLS
CELL_H = H / ROWS
MAX_R  = CELL_W * 0.48

BG     = "#FAF3E0"
DOT    = "#FF6B6B"
SHADOW = "#1A1A2E"
SHADOW_DX    = 1.5
SHADOW_DY    = 1.5
SHADOW_ALPHA = 0.35

SCALE = math.pi * 12
PHASE = 0.0


def evaluate(gx: int, gy: int) -> float:
    """Return dot-size value in [0, 1] for grid cell (gx, gy) at PHASE.

    Mirrors the JavaScript evaluate() in index.html: computes the normalised
    distance from canvas centre, applies sin(r − phase)/(r+1), then shifts
    the result to [0, 1].
    """
    nx   = (gx + 0.5) / COLS - 0.5
    ny   = (gy + 0.5) / ROWS - 0.5
    dist = math.sqrt(nx * nx + ny * ny)
    r    = dist * SCALE
    raw  = math.sin(r - PHASE) / (r + 1)
    return (raw + 1) / 2


dots: list[tuple[float, float, float]] = []
for gy in range(ROWS):
    for gx in range(COLS):
        v = evaluate(gx, gy)
        radius = v * MAX_R
        if radius < 0.4:
            continue
        cx = (gx + 0.5) * CELL_W
        cy = (gy + 0.5) * CELL_H
        dots.append((cx, cy, radius))

lines: list[str] = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
    f'  <rect width="{W}" height="{H}" fill="{BG}"/>',
]

for cx, cy, r in dots:
    lines.append(
        f'  <circle cx="{cx + SHADOW_DX:.1f}" cy="{cy + SHADOW_DY:.1f}"'
        f' r="{r:.2f}" fill="{SHADOW}" opacity="{SHADOW_ALPHA}"/>'
    )

for cx, cy, r in dots:
    lines.append(
        f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" fill="{DOT}"/>'
    )

lines.append("</svg>")

out = pathlib.Path(__file__).parent / "thumbnail.svg"
out.write_text("\n".join(lines) + "\n")
print(f"Wrote {out} ({len(dots)} dots, {out.stat().st_size} bytes)")
