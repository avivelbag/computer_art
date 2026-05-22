#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 278 — the loom remembers."""
import pathlib

OUT = pathlib.Path(__file__).parent / "thumbnail.svg"

W, H = 400, 400
N = 30   # warp threads
M = 30   # weft threads
CELL = W / N
GAP = 1.0
THREAD = CELL - GAP

# Warm palette for warp threads: terracotta → ochre → cream
WARP_PAL = [(194, 113, 79), (201, 154, 58), (240, 224, 192)]

# Cool palette for weft threads: indigo → slate → sky
WEFT_PAL = [(59, 48, 120), (107, 123, 164), (168, 196, 212)]


def lerp(a, b, t):
    return a + (b - a) * t


def sample_palette(pal, t):
    t = max(0.0, min(1.0, t))
    n = len(pal) - 1
    i = min(n - 1, int(t * n))
    f = t * n - i
    return tuple(lerp(pal[i][k], pal[i + 1][k], f) for k in range(3))


def hex_color(c):
    return "#{:02x}{:02x}{:02x}".format(int(c[0]), int(c[1]), int(c[2]))


# 2/2 twill threading draft (4×4 repeat)
TWILL_CELLS = [
    1, 1, 0, 0,
    0, 1, 1, 0,
    0, 0, 1, 1,
    1, 0, 0, 1,
]


def is_warp_over(r, c):
    """Return True when warp thread c passes over weft thread r (2/2 twill)."""
    ri = r % 4
    ci = c % 4
    return TWILL_CELLS[ri * 4 + ci] == 1


lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    (
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
    ),
    f'  <rect width="{W}" height="{H}" fill="#110a05"/>',
]

for r in range(M):
    for c in range(N):
        t_c = c / (N - 1)
        t_r = r / (M - 1)
        over = is_warp_over(r, c)
        color = hex_color(
            sample_palette(WARP_PAL, t_c) if over
            else sample_palette(WEFT_PAL, t_r)
        )
        x = c * CELL + GAP * 0.5
        y = r * CELL + GAP * 0.5
        lines.append(
            f'  <rect x="{x:.2f}" y="{y:.2f}"'
            f' width="{THREAD:.2f}" height="{THREAD:.2f}"'
            f' fill="{color}"/>'
        )
        if over:
            # Highlight top/left edge to suggest the raised warp thread
            lines.append(
                f'  <rect x="{x:.2f}" y="{y:.2f}"'
                f' width="{THREAD:.2f}" height="1.5"'
                f' fill="rgba(255,255,255,0.10)"/>'
            )
            lines.append(
                f'  <rect x="{x:.2f}" y="{y:.2f}"'
                f' width="1.5" height="{THREAD:.2f}"'
                f' fill="rgba(255,255,255,0.10)"/>'
            )

lines.append('</svg>')

OUT.write_text('\n'.join(lines), encoding='utf-8')
print(f"Written {OUT} ({OUT.stat().st_size:,} bytes, {N}×{M} grid, 2/2 twill)")
