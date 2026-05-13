#!/usr/bin/env python3
"""Generate thumbnail.svg for Piece 123 — Torus Knot Curves.

Renders the (2,3) trefoil knot as a static SVG with stroke-width varying
sinusoidally along the curve (via z depth) to fake occlusion. Uses pure
Python standard library; no external dependencies.
"""
import math
import pathlib

W, H = 400, 400
CX, CY = 200, 200
P, Q = 2, 3
R, r = 120, 45
N = 300
TILT = 0.45

BG = "#0d0a14"
COLORS = ["#c8405a", "#e88c1a", "#f5c830"]  # far=rose, mid=amber, near=gold
SW_MIN, SW_MAX = 1.5, 5.5


def point(i: int, tilt: float = TILT) -> tuple[float, float, float]:
    """Return screen-space (x, y, z) for sample index *i* of the (P, Q) torus knot.

    The tilt is a rotation around the x-axis so the z coordinate encodes
    viewer depth (higher z = nearer to the viewer).
    """
    t = i / N * math.pi * 2
    ct, st = math.cos(tilt), math.sin(tilt)
    cp, sp = math.cos(P * t), math.sin(P * t)
    cq, sq = math.cos(Q * t), math.sin(Q * t)
    rho = R + r * cq
    x = rho * cp
    y = rho * sp
    z = r * sq
    return x + CX, y * ct - z * st + CY, y * st + z * ct


def render() -> str:
    """Return a complete SVG document for the (2,3) trefoil as a string.

    Each of the N segments gets its own stroke-width and color determined by
    its z midpoint depth. z = r·sin(Q·t) is sinusoidal in t, so the
    stroke-width is sinusoidal along the curve.
    """
    pts = [point(i) for i in range(N + 1)]

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"'
        f' viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    ]

    for i in range(N):
        x1, y1, z1 = pts[i]
        x2, y2, z2 = pts[i + 1]
        zm = (z1 + z2) * 0.5
        # Normalize z ∈ [-r, r] to depth ∈ [0, 1]
        depth = (zm + r) / (2 * r)
        sw = SW_MIN + (SW_MAX - SW_MIN) * depth
        color = COLORS[min(2, int(depth * 3))]
        lines.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"'
            f' stroke="{color}" stroke-width="{sw:.2f}" stroke-linecap="round"/>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def write_svg(path: str, svg: str) -> None:
    """Write *svg* string to *path* as UTF-8 text."""
    pathlib.Path(path).write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    write_svg(str(out), render())
    print(f"Written {out}")
