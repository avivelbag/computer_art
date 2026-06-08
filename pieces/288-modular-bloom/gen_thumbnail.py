#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 288 — Modular Bloom.

Renders the K=2 snapshot (pure cardioid) as 200 chord lines on a near-black
background. Point i on the unit circle connects to point (i×2 mod 200) so the
200 chords together envelope an exact cardioid — the same geometry shown in the
animated piece at the start of each loop.
"""

import math
import pathlib

N = 200
K = 2
W, H = 400, 400
CX, CY = W / 2, H / 2
R = 170
BG = "#0a0a0f"


def compute_pts(n: int, cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    """Return n equally-spaced points on a circle of radius r centred at (cx, cy).

    Points are ordered counter-clockwise starting at angle 0 (rightmost point).
    Used both for thumbnail generation and unit tests.
    """
    return [
        (cx + r * math.cos(2 * math.pi * i / n),
         cy + r * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]


def gen_svg(pts: list[tuple[float, float]], k: float, w: int, h: int, bg: str) -> str:
    """Return an SVG string of the chord diagram for multiplier k.

    Each point i connects to point round(i*k) mod len(pts). Lines are drawn at
    15% opacity in hsl(0, 80%, 65%) which matches the animated K=2 frame colour
    (hue=0 in the full 0..360 rainbow sweep).
    """
    n = len(pts)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f'  <rect width="{w}" height="{h}" fill="{bg}"/>',
    ]
    for i in range(n):
        j = round(i * k) % n
        x1, y1 = pts[i]
        x2, y2 = pts[j]
        lines.append(
            f'  <line x1="{x1:.2f}" y1="{y1:.2f}"'
            f' x2="{x2:.2f}" y2="{y2:.2f}"'
            f' stroke="hsl(0,80%,65%)" stroke-width="0.7" opacity="0.15"/>'
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    pts = compute_pts(N, CX, CY, R)
    svg = gen_svg(pts, K, W, H, BG)
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes, {svg.count('<line')} chords)")
