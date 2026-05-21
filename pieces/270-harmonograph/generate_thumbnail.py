"""Generate thumbnail.svg for Piece 270 — Harmonograph: Where the Pendulums Rest.

Produces a static SVG of the full harmonograph curve at t_max using the same
pendulum parameters as index.html.  Run once; the output is committed.
"""
import math
import pathlib

A1, f1, p1, d1 = 190, 2.001, 0.0,         0.0025
A2, f2, p2, d2 = 190, 3.0,   math.pi / 2, 0.0025
A3, f3, p3, d3 = 190, 3.0,   math.pi / 4, 0.0025
A4, f4, p4, d4 = 190, 2.0,   0.0,         0.0025

T_MAX = 4000
STEPS = 4000          # fewer points in SVG thumbnail keeps file size small
W = H = 800
CX = CY = 400

INK = "#1a1a2e"
BG  = "#f5f0e8"
STROKE_WIDTH = 0.6
STROKE_ALPHA = 0.6


def compute_points():
    """Return (xs, ys) lists of floats for the full curve at T_MAX."""
    xs, ys = [], []
    for i in range(STEPS):
        t = (i / STEPS) * T_MAX
        x = CX + (A1 * math.sin(f1 * t + p1) * math.exp(-d1 * t)
                + A2 * math.sin(f2 * t + p2) * math.exp(-d2 * t))
        y = CY + (A3 * math.sin(f3 * t + p3) * math.exp(-d3 * t)
                + A4 * math.sin(f4 * t + p4) * math.exp(-d4 * t))
        xs.append(x)
        ys.append(y)
    return xs, ys


def points_to_path(xs, ys):
    """Convert parallel coordinate lists to an SVG path d-string."""
    parts = [f"M{xs[0]:.2f},{ys[0]:.2f}"]
    for x, y in zip(xs[1:], ys[1:]):
        parts.append(f"L{x:.2f},{y:.2f}")
    return "".join(parts)


def main():
    xs, ys = compute_points()
    d = points_to_path(xs, ys)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}">\n'
        f'  <rect width="{W}" height="{H}" fill="{BG}"/>\n'
        f'  <path d="{d}" fill="none" stroke="{INK}" '
        f'stroke-width="{STROKE_WIDTH}" stroke-opacity="{STROKE_ALPHA}" '
        f'stroke-linecap="round" stroke-linejoin="round"/>\n'
        f'</svg>\n'
    )
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg)
    size_kb = out.stat().st_size / 1024
    print(f"Wrote {out} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
