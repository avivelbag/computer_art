#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 136 — Fourier Epicycles: Drawing with Circles.

Samples a 5-pointed star polygon at N points, computes DFT coefficients, and
renders the epicycle chain at t=π/3 (one-sixth of the way through the
animation) together with the partial trace from t=0 to t=π/3 as a 400×400 SVG.
"""

import math
import pathlib

N = 64
N_EPICYCLES = 64  # use all DFT coefficients
W, H = 400, 400
CX, CY = W / 2, H / 2
SCALE = 90
PATH_SAMPLES = 200
BG = "#06101e"
CIRCLE_STROKE = "#2a5080"
ARM_STROKE = "#3d78bf"
TRACE_COLOR = "#f5b942"


def sample_star(n: int, r_outer: float = 1.0, r_inner: float = 0.38) -> list[tuple[float, float]]:
    """Return n equidistant (x, y) samples along the perimeter of a 5-pointed star.

    Vertices alternate between outer radius r_outer and inner radius r_inner,
    starting at the top (-π/2), spaced 36° apart.  Points are distributed
    proportionally to arc length so the sampling is uniform around the polygon.
    """
    verts = []
    for i in range(10):
        angle = 2 * math.pi * i / 10 - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        verts.append((r * math.cos(angle), r * math.sin(angle)))

    segs = []
    for i in range(10):
        a, b = verts[i], verts[(i + 1) % 10]
        segs.append(math.hypot(b[0] - a[0], b[1] - a[1]))
    total = sum(segs)

    pts = []
    for i in range(n):
        target = (i / n) * total
        accum = 0.0
        for j in range(10):
            if accum + segs[j] >= target or j == 9:
                frac = min((target - accum) / segs[j], 1.0)
                a, b = verts[j], verts[(j + 1) % 10]
                pts.append((a[0] + frac * (b[0] - a[0]), a[1] + frac * (b[1] - a[1])))
                break
            accum += segs[j]
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
    """Return the (x, y) position of the final epicycle tip at parameter t."""
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
    """Return SVG showing epicycles at t=π/3 with partial trace from t=0 to t=π/3."""
    pts = sample_star(N)
    coeffs = dft(pts)[:N_EPICYCLES]
    t_snap = math.pi / 3

    trace = []
    for i in range(PATH_SAMPLES + 1):
        t = t_snap * i / PATH_SAMPLES
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
            f' fill="none" stroke="{TRACE_COLOR}" stroke-width="1.8"'
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
            f' fill="none" stroke="{CIRCLE_STROKE}" stroke-width="0.8" opacity="0.7"/>'
        )
        lines.append(
            f'  <line x1="{scx:.1f}" y1="{scy:.1f}" x2="{snx:.1f}" y2="{sny:.1f}"'
            f' stroke="{ARM_STROKE}" stroke-width="1.0" opacity="0.85"/>'
        )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    svg = generate_svg()
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg, encoding="utf-8")
    circle_count = svg.count("<circle")
    print(f"Wrote {out} ({circle_count} circles, {out.stat().st_size} bytes)")
