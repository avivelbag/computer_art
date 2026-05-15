#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 176 — one representative 12-fold radiolarian."""

import math
import pathlib

W = H = 480
CX = CY = 240.0
R = 110.0
BG = "#070d1a"
BONE = "#e8e0d0"
ACCENT = "#4dd9c0"

N, M = 12, 6
A, B, C = 0.55, 0.30, 0.15
SHELLS = 3
SPINES = 12
STEPS = 720


def polar_pts(cx: float, cy: float, radius: float, n: int, m: int,
              a: float, b: float, c: float, steps: int) -> list[tuple[float, float]]:
    """Sample the polar curve r(θ) = radius*(a + b*sin(n*θ) + c*sin(m*θ)).

    Returns a list of (x, y) Cartesian points for one full revolution.
    """
    pts = []
    for i in range(steps):
        th = (i / steps) * 2 * math.pi
        r = radius * (a + b * math.sin(n * th) + c * math.sin(m * th))
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    return pts


def path_d(pts: list[tuple[float, float]]) -> str:
    """Convert (x, y) pairs to a closed SVG path data string."""
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return d + "Z"


def main() -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    ]

    # Concentric shells at evenly-spaced fractions of R
    for s in range(1, SHELLS + 1):
        scale = s / (SHELLS + 1)
        pts = polar_pts(CX, CY, R * scale, N, M, A, B, C, STEPS)
        sw = 0.8 if s == SHELLS else 0.5
        lines.append(
            f'<path d="{path_d(pts)}" stroke="{BONE}" fill="none"'
            f' stroke-width="{sw}" stroke-linejoin="round"/>'
        )

    # Outer body outline
    pts = polar_pts(CX, CY, R, N, M, A, B, C, STEPS)
    lines.append(
        f'<path d="{path_d(pts)}" stroke="{BONE}" fill="none"'
        f' stroke-width="1.4" stroke-linejoin="round"/>'
    )

    # Spines: radial lines from 0.75R to 1.25R with small diamond tips
    for k in range(SPINES):
        th = (2 * math.pi * k) / SPINES
        co, si = math.cos(th), math.sin(th)
        x1, y1 = CX + R * 0.75 * co, CY + R * 0.75 * si
        x2, y2 = CX + R * 1.25 * co, CY + R * 1.25 * si
        lines.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"'
            f' stroke="{BONE}" stroke-width="0.7" stroke-linecap="round"/>'
        )
        tip = R * 0.055
        tx, ty = x2 + tip * co, y2 + tip * si
        lx, ly = x2 + tip * 0.5 * (-si), y2 + tip * 0.5 * co
        rx, ry = x2 - tip * 0.5 * (-si), y2 - tip * 0.5 * co
        bx, by = x2 - tip * 0.35 * co, y2 - tip * 0.35 * si
        dpts = f"{tx:.2f},{ty:.2f} {lx:.2f},{ly:.2f} {bx:.2f},{by:.2f} {rx:.2f},{ry:.2f}"
        lines.append(
            f'<polygon points="{dpts}" stroke="{BONE}" fill="{BONE}" stroke-width="0.4"/>'
        )

    # Inner lattice: 2N fine radial spokes + 2 concentric rings
    lat_spokes = N * 2
    for k in range(lat_spokes):
        th = (2 * math.pi * k) / lat_spokes
        x2 = CX + R * 0.38 * math.cos(th)
        y2 = CY + R * 0.38 * math.sin(th)
        lines.append(
            f'<line x1="{CX:.2f}" y1="{CY:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"'
            f' stroke="{BONE}" stroke-width="0.3" stroke-linecap="round"/>'
        )
    lines.append(
        f'<circle cx="{CX:.2f}" cy="{CY:.2f}" r="{R * 0.38:.2f}"'
        f' stroke="{BONE}" fill="none" stroke-width="0.35"/>'
    )
    lines.append(
        f'<circle cx="{CX:.2f}" cy="{CY:.2f}" r="{R * 0.25:.2f}"'
        f' stroke="{BONE}" fill="none" stroke-width="0.3"/>'
    )

    # Nucleus: accent ring + filled dot
    lines.append(
        f'<circle cx="{CX:.2f}" cy="{CY:.2f}" r="{R * 0.13:.2f}"'
        f' stroke="{ACCENT}" fill="none" stroke-width="0.9"/>'
    )
    lines.append(
        f'<circle cx="{CX:.2f}" cy="{CY:.2f}" r="{R * 0.06:.2f}"'
        f' stroke="none" fill="{ACCENT}"/>'
    )

    lines.append("</svg>")

    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
