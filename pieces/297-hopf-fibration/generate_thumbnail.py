#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 297 — Hopf fibration."""

import math
import pathlib

W, H = 400, 300
CX, CY = 200, 155
FOV = 200
CAM_D = 3.5
ANGLE = 0.35  # Y-axis rotation angle for thumbnail view

N_LAT = 10
N_LON = 12
N_PTS = 64
PHI_MIN = math.pi / 10   # 18°
PHI_MAX = math.pi * 9 / 10  # 162°

AMBER = (212, 131, 42)
TEAL = (42, 138, 159)


def lerp(a, b, t):
    return a + (b - a) * t


def fiber_color(phi):
    t = abs(math.cos(phi))
    return (
        round(lerp(AMBER[0], TEAL[0], t)),
        round(lerp(AMBER[1], TEAL[1], t)),
        round(lerp(AMBER[2], TEAL[2], t)),
    )


def hopf_fiber(phi, theta, t):
    """S³ fiber over (phi, theta) at parameter t — same formula as index.html."""
    hp, ht = phi / 2, theta / 2
    chp, shp = math.cos(hp), math.sin(hp)
    return (
        chp * math.cos(t + ht),
        chp * math.sin(t + ht),
        shp * math.cos(t - ht),
        shp * math.sin(t - ht),
    )


def stereo_proj(a, b, c, d):
    if d > 0.999:
        return None
    f = 1.0 / (1.0 - d)
    return (a * f, b * f, c * f)


def rot_y(x, y, z, ca, sa):
    return (x * ca + z * sa, y, -x * sa + z * ca)


def project(x, y, z):
    dz = z + CAM_D
    if dz < 0.05:
        return None
    sx = CX + FOV * x / dz
    sy = CY - FOV * y / dz
    if abs(sx - CX) > W * 4 or abs(sy - CY) > H * 4:
        return None
    return (sx, sy)


def main():
    ca, sa = math.cos(ANGLE), math.sin(ANGLE)

    fibers = []
    for li in range(N_LAT):
        phi = PHI_MIN + (PHI_MAX - PHI_MIN) * li / (N_LAT - 1)
        color = fiber_color(phi)
        for lo in range(N_LON):
            theta = 2 * math.pi * lo / N_LON
            pts_3d = []
            for i in range(N_PTS + 1):
                t = 2 * math.pi * i / N_PTS
                a, b, c, d = hopf_fiber(phi, theta, t)
                pts_3d.append(stereo_proj(a, b, c, d))
            fibers.append((pts_3d, color))

    batches = []
    for pts_3d, color in fibers:
        rotated = []
        z_sum = 0
        n = 0
        for p in pts_3d:
            if p is None:
                rotated.append(None)
            else:
                r = rot_y(*p, ca, sa)
                rotated.append(r)
                z_sum += r[2]
                n += 1
        z_avg = z_sum / n if n > 0 else 0
        batches.append((rotated, color, z_avg))

    batches.sort(key=lambda b: b[2])

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="#0a0a12"/>',
    ]

    for rotated, color, z_avg in batches:
        r, g, b = color
        alpha = max(0.08, min(0.55, 0.55 * (0.35 + 0.65 * max(0, min(1, (z_avg + 2) / 4)))))

        path_parts = []
        started = False
        for rv in rotated:
            if rv is None:
                started = False
                continue
            p2 = project(*rv)
            if p2 is None:
                started = False
                continue
            sx, sy = p2
            if not started:
                path_parts.append(f"M{sx:.1f},{sy:.1f}")
                started = True
            else:
                path_parts.append(f"L{sx:.1f},{sy:.1f}")

        if path_parts:
            lines.append(
                f'<path d="{" ".join(path_parts)}" fill="none" '
                f'stroke="rgb({r},{g},{b})" stroke-opacity="{alpha:.3f}" stroke-width="1.2"/>'
            )

    lines.append("</svg>")

    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text("\n".join(lines))
    print(f"Written {out}  ({len(batches)} fibers)")


if __name__ == "__main__":
    main()
