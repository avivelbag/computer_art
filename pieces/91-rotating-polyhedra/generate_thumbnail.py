"""Generate a static SVG thumbnail of the rotating polyhedra piece.

The thumbnail shows three nested Platonic solids — tetrahedron, icosahedron,
and dodecahedron — frozen at a 45°/25° viewing angle, rendered as perspective-
projected wireframes on a deep-charcoal background.
"""

import math
import pathlib

PHI = (1 + math.sqrt(5)) / 2


def _rot_y(v, c, s):
    return (v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c)


def _rot_x(v, c, s):
    return (v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c)


def _apply_rot(verts, ay, ax):
    """Apply Ry(ay) then Rx(ax) to every vertex in *verts*."""
    cy, sy = math.cos(ay), math.sin(ay)
    cx, sx = math.cos(ax), math.sin(ax)
    return [_rot_x(_rot_y(v, cy, sy), cx, sx) for v in verts]


def _project(v, fov, cam_dist, cx, cy):
    """Perspective-project 3-D vertex *v* onto the 2-D SVG plane.

    Camera is fixed at (0, 0, cam_dist). Returns (sx, sy, vz).
    """
    denom = v[2] + cam_dist
    sx = cx + fov * v[0] / denom
    sy = cy - fov * v[1] / denom
    return sx, sy, v[2]


def _ico_verts():
    norm = math.sqrt(1 + PHI * PHI)
    raw = [
        (0, 1, PHI), (0, -1, PHI), (0, 1, -PHI), (0, -1, -PHI),
        (1, PHI, 0), (-1, PHI, 0), (1, -PHI, 0), (-1, -PHI, 0),
        (PHI, 0, 1), (-PHI, 0, 1), (PHI, 0, -1), (-PHI, 0, -1),
    ]
    return [(x / norm, y / norm, z / norm) for x, y, z in raw]


ICO_EDGES = [
    (0, 1), (0, 4), (0, 5), (0, 8), (0, 9),
    (1, 6), (1, 7), (1, 8), (1, 9),
    (2, 3), (2, 4), (2, 5), (2, 10), (2, 11),
    (3, 6), (3, 7), (3, 10), (3, 11),
    (4, 5), (4, 8), (4, 10),
    (5, 9), (5, 11),
    (6, 7), (6, 8), (6, 10),
    (7, 9), (7, 11),
    (8, 10), (9, 11),
]


def _dod_verts():
    inv_phi = 1 / PHI
    norm = math.sqrt(3)
    raw = [
        ( 1,  1,  1), ( 1,  1, -1), ( 1, -1,  1), ( 1, -1, -1),
        (-1,  1,  1), (-1,  1, -1), (-1, -1,  1), (-1, -1, -1),
        (0,  inv_phi,  PHI), (0, -inv_phi,  PHI),
        (0,  inv_phi, -PHI), (0, -inv_phi, -PHI),
        ( inv_phi,  PHI, 0), (-inv_phi,  PHI, 0),
        ( inv_phi, -PHI, 0), (-inv_phi, -PHI, 0),
        ( PHI, 0,  inv_phi), (-PHI, 0,  inv_phi),
        ( PHI, 0, -inv_phi), (-PHI, 0, -inv_phi),
    ]
    return [(x / norm, y / norm, z / norm) for x, y, z in raw]


DOD_EDGES = [
    (0, 8), (0, 12), (0, 16),
    (1, 10), (1, 12), (1, 18),
    (2, 9), (2, 14), (2, 16),
    (3, 11), (3, 14), (3, 18),
    (4, 8), (4, 13), (4, 17),
    (5, 10), (5, 13), (5, 19),
    (6, 9), (6, 15), (6, 17),
    (7, 11), (7, 15), (7, 19),
    (8, 9), (10, 11),
    (12, 13), (14, 15),
    (16, 18), (17, 19),
]


def _tet_verts():
    norm = math.sqrt(3)
    raw = [(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)]
    return [(x / norm, y / norm, z / norm) for x, y, z in raw]


TET_EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


def generate_svg(
    size: int = 400,
    angle_y: float = math.pi / 4,
    angle_x: float = math.pi / 7,
    bg: str = "#1c1c1e",
    fov: float = 200.0,
    cam_dist: float = 3.5,
) -> str:
    """Return SVG markup for a single frozen frame of the polyhedra animation.

    Parameters
    ----------
    size:      Canvas size in SVG user units (square).
    angle_y:   Base Y-axis rotation in radians; each solid multiplies it by
               its own speed factor (2.1, 1.3, 1.0) to produce visual offset.
    angle_x:   Base X-axis rotation in radians (same speed-factor scaling).
    bg:        Background fill colour hex string.
    fov:       Perspective focal length (SVG user units).
    cam_dist:  Camera distance along +z axis in world units.

    Returns
    -------
    str
        Complete SVG document as a string.
    """
    cx = size / 2
    cy = size / 2

    solids = [
        (_tet_verts(), TET_EDGES, 0.38, 2.1),
        (_ico_verts(), ICO_EDGES, 0.68, 1.3),
        (_dod_verts(), DOD_EDGES, 1.00, 1.0),
    ]

    svg_lines: list[str] = []
    for verts, edges, scale, speed in solids:
        ay = angle_y * speed
        ax = angle_x * speed
        scaled  = [(v[0] * scale, v[1] * scale, v[2] * scale) for v in verts]
        rotated = _apply_rot(scaled, ay, ax)

        zs      = [v[2] for v in rotated]
        z_min   = min(zs)
        z_range = max(zs) - z_min or 1.0
        proj    = [_project(v, fov, cam_dist, cx, cy) for v in rotated]

        for i, j in edges:
            z_avg = (rotated[i][2] + rotated[j][2]) * 0.5
            alpha = 0.15 + 0.75 * (z_avg - z_min) / z_range
            alpha = max(0.05, min(1.0, alpha))
            x1, y1, _ = proj[i]
            x2, y2, _ = proj[j]
            svg_lines.append(
                f'  <line x1="{x1:.2f}" y1="{y1:.2f}"'
                f' x2="{x2:.2f}" y2="{y2:.2f}"'
                f' stroke="rgb(245,240,230)"'
                f' stroke-opacity="{alpha:.3f}"'
                f' stroke-width="0.9"/>'
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
