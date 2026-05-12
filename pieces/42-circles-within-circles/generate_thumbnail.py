#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 42 — Fourier epicycles tracing a heart.

Samples a heart curve at N points, computes DFT coefficients, and renders
the epicycle chain at t=π (mid-animation) together with the partial trace
from t=0 to t=π as a 400×400 SVG.
"""

import math
import pathlib

N = 64
N_EPICYCLES = 50
W, H = 400, 400
CX, CY = W / 2, H / 2
SCALE = 8
PATH_SAMPLES = 300
BG = "#07070f"
CIRCLE_STROKE = "#2a58a0"
ARM_STROKE = "#4488cc"
TRACE_COLOR = "#00e5ff"


def sample_heart(n: int) -> list[tuple[float, float]]:
    """Return n equidistant (x, y) samples around the parametric heart curve."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        s = math.sin(t)
        pts.append((
            16 * s * s * s,
            -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        ))
    return pts


def dft(pts: list[tuple[float, float]]) -> list[dict]:
    """DFT of complex signal encoded as (re, im) pairs.

    Returns coefficient dicts {freq, amp, phase} sorted by amplitude descending.
    Each coefficient k represents a circle rotating at integer frequency k.
    """
    n = len(pts)
    result = []
    for k in range(n):
        re = 0.0
        im = 0.0
        for j in range(n):
            angle = 2 * math.pi * k * j / n
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            re += pts[j][0] * cos_a + pts[j][1] * sin_a
            im += -pts[j][0] * sin_a + pts[j][1] * cos_a
        amp = math.sqrt(re * re + im * im) / n
        phase = math.atan2(im, re)
        result.append({"freq": k, "amp": amp, "phase": phase})
    result.sort(key=lambda c: -c["amp"])
    return result


def tip_at(coeffs: list[dict], t: float) -> tuple[float, float]:
    """Return the (x, y) position of the final epicycle tip at time t."""
    x = 0.0
    y = 0.0
    for c in coeffs:
        angle = c["freq"] * t + c["phase"]
        x += c["amp"] * SCALE * math.cos(angle)
        y += c["amp"] * SCALE * math.sin(angle)
    return x, y


def epicycles_at(coeffs: list[dict], t: float) -> list[tuple[float, float, float, float, float]]:
    """Return (cx, cy, r, tip_x, tip_y) for each epicycle in the chain at time t."""
    circles = []
    x = 0.0
    y = 0.0
    for c in coeffs:
        r = c["amp"] * SCALE
        angle = c["freq"] * t + c["phase"]
        nx = x + r * math.cos(angle)
        ny = y + r * math.sin(angle)
        circles.append((x, y, r, nx, ny))
        x, y = nx, ny
    return circles


def generate_svg() -> str:
    """Return SVG string showing epicycles at t=π with partial trace from t=0 to t=π."""
    pts = sample_heart(N)
    coeffs = dft(pts)[:N_EPICYCLES]
    t_snap = math.pi

    trace = []
    for i in range(PATH_SAMPLES + 1):
        t = math.pi * i / PATH_SAMPLES
        tx, ty = tip_at(coeffs, t)
        trace.append((CX + tx, CY + ty))

    circles = epicycles_at(coeffs, t_snap)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f'  <rect width="{W}" height="{H}" fill="{BG}"/>',
    ]

    if len(trace) > 1:
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in trace)
        lines.append(
            f'  <polyline points="{pts_str}"'
            f' fill="none" stroke="{TRACE_COLOR}" stroke-width="1.5"'
            f' stroke-linejoin="round" stroke-linecap="round"/>'
        )

    for cx, cy, r, nx, ny in circles:
        if r < 0.4:
            continue
        scx = CX + cx
        scy = CY + cy
        snx = CX + nx
        sny = CY + ny
        lines.append(
            f'  <circle cx="{scx:.1f}" cy="{scy:.1f}" r="{r:.1f}"'
            f' fill="none" stroke="{CIRCLE_STROKE}" stroke-width="0.8" opacity="0.75"/>'
        )
        lines.append(
            f'  <line x1="{scx:.1f}" y1="{scy:.1f}" x2="{snx:.1f}" y2="{sny:.1f}"'
            f' stroke="{ARM_STROKE}" stroke-width="1.0" opacity="0.9"/>'
        )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    svg = generate_svg()
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg)
    circle_count = svg.count("<circle")
    print(f"Wrote {out} ({circle_count} circles, {out.stat().st_size} bytes)")
