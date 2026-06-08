#!/usr/bin/env python3
"""Generate thumbnail.svg for the loxodrome navigator piece at rotation=0.3 rad."""
import math
import pathlib

W, H, CX, CY, R = 400, 400, 200, 200, 160
ANGLE = 0.3  # globe rotation for the still frame
T_MIN, T_MAX, T_STEPS = -4, 4, 400
N_CURVES = 16


def to3d(lat, lon):
    c = math.cos(lat)
    return c * math.cos(lon), math.sin(lat), c * math.sin(lon)


def rot_y(x, y, z, ca, sa):
    return x * ca + z * sa, y, z * ca - x * sa


def screen(rx, ry):
    return CX + rx * R, CY - ry * R


def path_d(pts):
    """Serialize a list of (px, py) screen points to an SVG path d attribute."""
    if not pts:
        return ""
    parts = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for p in pts[1:]:
        parts.append(f"L{p[0]:.1f},{p[1]:.1f}")
    return " ".join(parts)


def emit_segments(lines, pts, **attrs):
    """Flush accumulated visible segments as <path> elements."""
    if not pts:
        return
    attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    lines.append(f'    <path d="{path_d(pts)}" {attr_str}/>')


ca, sa = math.cos(ANGLE), math.sin(ANGLE)
dt = (T_MAX - T_MIN) / T_STEPS

out_lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'width="{W}" height="{H}">',
    f'  <rect width="{W}" height="{H}" fill="#060a18"/>',
    f'  <defs><clipPath id="g"><circle cx="{CX}" cy="{CY}" r="{R}"/></clipPath></defs>',
]

# ---- Wireframe grid ----
out_lines.append('  <g clip-path="url(#g)" stroke="#2a3550" stroke-width="0.7" '
                 'fill="none" opacity="0.55">')

for lat_deg in range(-60, 61, 30):
    lat = math.radians(lat_deg)
    pts = []
    for i in range(361):
        x, y, z = to3d(lat, math.radians(i))
        rx, ry, rz = rot_y(x, y, z, ca, sa)
        if rz >= 0:
            pts.append(screen(rx, ry))
        elif pts:
            emit_segments(out_lines, pts)
            pts = []
    emit_segments(out_lines, pts)

for lon_deg in range(0, 360, 30):
    lon = math.radians(lon_deg)
    pts = []
    for lat_deg in range(-88, 89):
        x, y, z = to3d(math.radians(lat_deg), lon)
        rx, ry, rz = rot_y(x, y, z, ca, sa)
        if rz >= 0:
            pts.append(screen(rx, ry))
        elif pts:
            emit_segments(out_lines, pts)
            pts = []
    emit_segments(out_lines, pts)

out_lines.append('  </g>')

# Sphere limb
out_lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" '
                 f'stroke="#2a3550" stroke-width="1" opacity="0.4"/>')

# ---- Loxodrome curves ----
out_lines.append('  <g clip-path="url(#g)" fill="none" stroke-width="1.3">')

for k in range(N_CURVES):
    bearing_deg = (k + 0.5) * 11.25
    tan_b = math.tan(math.radians(bearing_deg))
    lon0 = k * math.pi / N_CURVES
    hue = int((bearing_deg * 2) % 360)

    pts = []
    for i in range(T_STEPS + 1):
        t = T_MIN + i * dt
        lat = 2 * math.atan(math.exp(t)) - math.pi / 2
        x, y, z = to3d(lat, lon0 + t * tan_b)
        rx, ry, rz = rot_y(x, y, z, ca, sa)
        if rz >= 0:
            pts.append(screen(rx, ry))
        elif pts:
            emit_segments(out_lines, pts, stroke=f"hsl({hue},90%,65%)")
            pts = []
    if pts:
        emit_segments(out_lines, pts, stroke=f"hsl({hue},90%,65%)")

out_lines.append('  </g>')
out_lines.append('</svg>')

dest = pathlib.Path(__file__).parent / "thumbnail.svg"
dest.write_text("\n".join(out_lines))
print(f"Written {dest} ({dest.stat().st_size} bytes)")
