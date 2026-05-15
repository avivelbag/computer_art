"""Generate SVG thumbnail for Piece 133 — SDF Raymarcher: Infinite Folded Space.

Projects an infinite grid of tori (cell size 2.0, major radius 0.4, minor 0.15)
onto a 400×400 canvas from the same camera angle used in the live shader.
Each torus cross-section is drawn as a perspective-foreshortened ellipse with a
warm-gold stroke that fades to deep indigo via an exponential fog factor.
"""

import math
import pathlib

SIZE      = 400
SCALE_FOV = 240.0   # pixels × world-units at unit depth (controls FOV)

CAM       = (3.0, 2.0, 3.0)
R_MAJOR   = 0.4
R_MINOR   = 0.15

BG_COLOR  = "#080618"
GOLD      = (234, 184, 46)   # warm gold RGB
FOG_RGB   = (8, 4, 24)       # deep indigo RGB


def _normalize(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _setup_camera():
    """Compute the orthonormal camera basis (fwd, rgt, up)."""
    fwd = _normalize((-CAM[0], -CAM[1], -CAM[2]))
    rgt = _normalize(_cross(fwd, (0.0, 1.0, 0.0)))
    up  = _cross(rgt, fwd)
    return fwd, rgt, up


def _project(wx, wy, wz, fwd, rgt, up):
    """Perspective-project world point onto screen.

    Returns (screen_x, screen_y, depth) or None if the point is behind camera.
    """
    dx, dy, dz = wx - CAM[0], wy - CAM[1], wz - CAM[2]
    depth = _dot((dx, dy, dz), fwd)
    if depth <= 0.1:
        return None
    sx = SIZE / 2 + _dot((dx, dy, dz), rgt) * SCALE_FOV / depth
    sy = SIZE / 2 - _dot((dx, dy, dz), up)  * SCALE_FOV / depth
    return sx, sy, depth


def _lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB tuples; returns a hex string."""
    t = max(0.0, min(1.0, t))
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def generate_svg() -> str:
    """Build the SVG string: perspective torus grid with fog and glow overlays."""
    fwd, rgt, up = _setup_camera()

    # How much the torus ellipse is squashed by the camera elevation angle.
    # A torus in XZ plane (axis = Y) is compressed by |up · Y|.
    compress = abs(_dot((0.0, 1.0, 0.0), up))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">',
        "<defs>",
        '<radialGradient id="fog" cx="50%" cy="50%" r="62%">',
        f'  <stop offset="0%"   stop-color="{BG_COLOR}" stop-opacity="0"/>',
        f'  <stop offset="100%" stop-color="{BG_COLOR}" stop-opacity="0.90"/>',
        "</radialGradient>",
        '<radialGradient id="glow" cx="50%" cy="50%" r="38%">',
        '  <stop offset="0%"   stop-color="#c88010" stop-opacity="0.22"/>',
        '  <stop offset="100%" stop-color="#c88010" stop-opacity="0"/>',
        "</radialGradient>",
        "</defs>",
        f'<rect width="{SIZE}" height="{SIZE}" fill="{BG_COLOR}"/>',
    ]

    rings = []
    for ix in range(-6, 7):
        for iz in range(-6, 7):
            res = _project(ix * 2.0, 0.0, iz * 2.0, fwd, rgt, up)
            if res is None:
                continue
            sx, sy, depth = res
            margin = 80
            if not (-margin < sx < SIZE + margin and -margin < sy < SIZE + margin):
                continue
            # Exponential fog matching the shader: 1 - exp(-0.07 * t)
            fog = 1.0 - math.exp(-0.07 * depth)
            fog = min(1.0, fog ** 0.55)       # gamma for artistic control
            opacity = max(0.04, 1.0 - fog * 0.96)
            color   = _lerp_color(GOLD, FOG_RGB, fog)
            rx  = R_MAJOR * SCALE_FOV / depth
            ry  = rx * compress
            sw  = max(1.0, R_MINOR * 2.0 * SCALE_FOV / depth)
            rings.append((depth, sx, sy, rx, ry, sw, color, opacity))

    # Painter's algorithm: far first, near on top
    rings.sort(key=lambda r: -r[0])

    for _, sx, sy, rx, ry, sw, color, opacity in rings:
        parts.append(
            f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" '
            f'rx="{max(rx, 2.0):.1f}" ry="{max(ry, 1.0):.1f}" '
            f'fill="none" stroke="{color}" '
            f'stroke-width="{sw:.1f}" opacity="{opacity:.2f}"/>'
        )

    parts.extend([
        f'<rect width="{SIZE}" height="{SIZE}" fill="url(#glow)"/>',
        f'<rect width="{SIZE}" height="{SIZE}" fill="url(#fog)"/>',
        "</svg>",
    ])
    return "\n".join(parts)


if __name__ == "__main__":
    svg = generate_svg()
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg):,} bytes)")
