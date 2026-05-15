#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 139 — greedy circle packing."""

import math
import pathlib
import random

W, H = 300, 300
MIN_R = 3
N_CANDIDATES = 100
SEED = 2026
BG = "#0a0a14"
PAL = [(13, 59, 79), (232, 160, 32), (245, 240, 200)]


def clearance(cx: float, cy: float, circles: list) -> float:
    """Return the largest circle radius that fits at (cx, cy).

    Clearance is the minimum of:
    - distance to each canvas edge
    - distance to the nearest already-placed circle's perimeter
    """
    r = min(cx, cy, W - cx, H - cy)
    for ox, oy, or_ in circles:
        d = math.sqrt((cx - ox) ** 2 + (cy - oy) ** 2) - or_
        if d < r:
            r = d
    return r


def lerp_color(t: float, pal: list) -> tuple:
    """Interpolate through a 3-stop palette at parameter t in [0, 1].

    t=0 maps to pal[0], t=0.5 to pal[1], t=1 to pal[2].
    """
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        a, b, s = pal[0], pal[1], t * 2
    else:
        a, b, s = pal[1], pal[2], (t - 0.5) * 2
    return tuple(round(a[i] + (b[i] - a[i]) * s) for i in range(3))


def circle_t(r: float, max_r: float) -> float:
    """Map log(r) linearly to [0,1] where 0=smallest circles, 1=largest."""
    log_min = math.log(MIN_R)
    log_max = math.log(max_r)
    if log_max <= log_min:
        return 1.0
    return (math.log(r) - log_min) / (log_max - log_min)


def pack(seed: int) -> list:
    """Run the greedy largest-empty-circle algorithm and return placed circles."""
    rng = random.Random(seed)
    placed = []
    max_r = float(MIN_R)

    while True:
        best_r, best_x, best_y = 0.0, W / 2.0, H / 2.0
        for _ in range(N_CANDIDATES):
            cx = rng.random() * W
            cy = rng.random() * H
            r = clearance(cx, cy, placed)
            if r > best_r:
                best_r, best_x, best_y = r, cx, cy
        if best_r < MIN_R:
            break
        if best_r > max_r:
            max_r = best_r
        placed.append((best_x, best_y, best_r))

    return placed, max_r


def main() -> None:
    circles, max_r = pack(SEED)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    ]
    for cx, cy, r in circles:
        t = circle_t(r, max_r)
        col = lerp_color(t, PAL)
        fill = f"rgb({col[0]},{col[1]},{col[2]})"
        lines.append(
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}"/>'
        )
    lines.append("</svg>")

    out_path = pathlib.Path(__file__).parent / "thumbnail.svg"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(circles)} circles → {out_path}")


if __name__ == "__main__":
    main()
