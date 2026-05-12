"""Generate thumbnail.svg for piece 59 — String Art.

Renders a static nephroid (multiplier=3) in the same dusty-rose-on-charcoal
palette used by the live canvas piece.  Run from any directory:

    python3 pieces/59-string-art/generate_thumbnail.py
"""

import math
import pathlib

N    = 200
R    = 175
CX   = 200
CY   = 200
SIZE = 400
M    = 3.0  # nephroid — three-lobed envelope

pts = [
    (CX + R * math.cos(2 * math.pi * i / N),
     CY + R * math.sin(2 * math.pi * i / N))
    for i in range(N)
]


def pt_at(j: float, coord: int) -> float:
    """Interpolated coordinate at real-valued circular index j."""
    j0   = int(j) % N
    j1   = (j0 + 1) % N
    frac = j - int(j)
    return pts[j0][coord] * (1 - frac) + pts[j1][coord] * frac


lines = []
for i in range(N):
    j = (i * M) % N
    x1, y1 = pts[i]
    x2 = pt_at(j, 0)
    y2 = pt_at(j, 1)
    lines.append(
        f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
    )

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">\n'
    f'  <rect width="{SIZE}" height="{SIZE}" fill="#111014"/>\n'
    f'  <g stroke="#c97ca3" stroke-width="0.9" opacity="0.55">\n'
    + "\n".join(lines) + "\n"
    f"  </g>\n"
    f"</svg>\n"
)

out = pathlib.Path(__file__).parent / "thumbnail.svg"
out.write_text(svg)
print(f"wrote {out}")
