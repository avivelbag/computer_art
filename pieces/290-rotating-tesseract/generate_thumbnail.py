"""Generate a static SVG thumbnail for piece 290 — Through the Fourth Wall.

Renders a single frame of a tesseract (4D hypercube) projected through two
perspective stages to 2D. Edge colour encodes w-depth after rotation: bright
cyan (#00e5ff) for edges near the viewer in w, deep indigo (#1a0050) for far.
Edge opacity is also modulated by w-depth.
"""

import math
import pathlib

D4 = 2.0   # 4D → 3D perspective viewing distance
D3 = 3.0   # 3D → 2D perspective viewing distance

VERTICES = [
    (x, y, z, w)
    for x in (-1.0, 1.0)
    for y in (-1.0, 1.0)
    for z in (-1.0, 1.0)
    for w in (-1.0, 1.0)
]

EDGES = [
    (i, j)
    for i in range(16)
    for j in range(i + 1, 16)
    if sum(VERTICES[i][k] != VERTICES[j][k] for k in range(4)) == 1
]


def _rot_xw(v, theta):
    """Rotate 4D vertex v in the XW plane by theta radians."""
    c, s = math.cos(theta), math.sin(theta)
    x, y, z, w = v
    return (x * c - w * s, y, z, x * s + w * c)


def _rot_yz(v, phi):
    """Rotate 4D vertex v in the YZ plane by phi radians."""
    c, s = math.cos(phi), math.sin(phi)
    x, y, z, w = v
    return (x, y * c - z * s, y * s + z * c, w)


def _proj4to3(v):
    """Perspective-project 4D vertex to 3D via w-depth; return (x3,y3,z3,w)."""
    x, y, z, w = v
    f = D4 / (D4 - w)
    return (x * f, y * f, z * f, w)


def _proj3to2(v, scale, cx, cy):
    """Perspective-project 3D vertex to 2D screen coordinates."""
    x, y, z = v[0], v[1], v[2]
    f = D3 / (D3 - z)
    return (cx + x * f * scale, cy - y * f * scale)


def _edge_color(t):
    """Return (r, g, b, opacity) for edge depth t in [0, 1]; t=1 = near/cyan."""
    t = max(0.0, min(1.0, t))
    r = round(0x1a * (1.0 - t))
    g = round(0xe5 * t)
    b = round(0x50 * (1.0 - t) + 0xff * t)
    opacity = 0.2 + 0.8 * t
    return r, g, b, opacity


def generate_svg(
    size: int = 400,
    frame: int = 42,
    bg: str = "#000000",
    xw_speed: float = 0.007,
    yz_speed: float = 0.011,
) -> str:
    """Return an SVG string for one frame of the rotating tesseract.

    Parameters
    ----------
    size:      Square canvas size in SVG user units.
    frame:     Animation frame index; drives rotation angles via speed params.
    bg:        Background fill colour hex string.
    xw_speed:  Angular velocity of XW-plane rotation in rad/frame.
    yz_speed:  Angular velocity of YZ-plane rotation in rad/frame.

    Returns
    -------
    str
        Complete SVG document.
    """
    theta_xw = xw_speed * frame
    theta_yz = yz_speed * frame

    rotated = [_rot_yz(_rot_xw(v, theta_xw), theta_yz) for v in VERTICES]
    proj3 = [_proj4to3(v) for v in rotated]
    scale = size * 0.28
    cx = size / 2.0
    cy = size / 2.0
    proj2 = [_proj3to2(v, scale, cx, cy) for v in proj3]

    svg_lines: list[str] = []
    for i, j in EDGES:
        w_avg = (rotated[i][3] + rotated[j][3]) / 2.0
        t = (w_avg + 1.0) / 2.0
        r, g, b, opacity = _edge_color(t)
        x1, y1 = proj2[i]
        x2, y2 = proj2[j]
        svg_lines.append(
            f'  <line x1="{x1:.2f}" y1="{y1:.2f}"'
            f' x2="{x2:.2f}" y2="{y2:.2f}"'
            f' stroke="rgb({r},{g},{b})"'
            f' stroke-opacity="{opacity:.3f}"'
            f' stroke-width="1.2"/>'
        )

    body = "\n".join(svg_lines)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' viewBox="0 0 {size} {size}" width="{size}" height="{size}">\n'
        f'  <rect width="{size}" height="{size}" fill="{bg}"/>\n'
        f'{body}\n'
        f'</svg>'
    )


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(generate_svg())
    print(f"Written {out}")
