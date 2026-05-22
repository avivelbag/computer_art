"""Generate thumbnail.svg for piece 271 — Sorted Light.

Computes a 50-column downsampled preview of the pixel-sorted interference
field and writes it as an SVG with per-column linear gradients that capture
the sorted state (bright at top, dark at bottom).
"""
import math
import pathlib

W, H = 800, 800        # matches canvas dimensions in index.html
THUMB_W, THUMB_H = 400, 400
NUM_COLS = 50          # vertical gradient strips
COL_W = THUMB_W // NUM_COLS  # 8 px per strip
SAMPLES = THUMB_H      # one sample point per output row

C_DARK   = (10, 10, 20)
C_MID    = (124, 58, 237)
C_BRIGHT = (251, 191, 36)


def lerp3(a, b, t):
    """Linearly interpolate between two RGB tuples, returning integer components."""
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def value_to_color(v):
    """Map a scalar in [0, 1] to RGB: 0 → dark navy, 0.5 → violet, 1 → amber gold."""
    v = max(0.0, min(1.0, v))
    if v < 0.5:
        return lerp3(C_DARK, C_MID, v * 2)
    return lerp3(C_MID, C_BRIGHT, (v - 0.5) * 2)


def source_value(x, y):
    """Three-wave sinusoidal interference field value at canvas pixel (x, y).

    Mirrors the JS sourceValue function exactly so the thumbnail matches
    the animation's source image.
    """
    nx, ny = x / W, y / H
    v = (math.sin(nx * math.pi * 8) * math.cos(ny * math.pi * 5) * 0.40
       + math.sin((nx + ny) * math.pi * 6) * 0.35
       + math.cos((nx - ny) * math.pi * 9) * 0.25)
    return (v + 1.0) * 0.5


def main():
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg"',
        f'     width="{THUMB_W}" height="{THUMB_H}">',
        '<defs>',
    ]

    for ci in range(NUM_COLS):
        cx = int((ci + 0.5) * (W / NUM_COLS))
        vals = sorted(
            [source_value(cx, int(row * (H / SAMPLES))) for row in range(SAMPLES)],
            reverse=True,
        )
        stops = [
            vals[0],
            vals[SAMPLES // 4],
            vals[SAMPLES // 2],
            vals[3 * SAMPLES // 4],
            vals[-1],
        ]
        lines.append(
            f'  <linearGradient id="g{ci}" x1="0" y1="0" x2="0" y2="1"'
            f' gradientUnits="objectBoundingBox">'
        )
        for si, v in enumerate(stops):
            r, g, b = value_to_color(v)
            lines.append(f'    <stop offset="{si * 25}%" stop-color="rgb({r},{g},{b})"/>')
        lines.append('  </linearGradient>')

    lines.append('</defs>')

    for ci in range(NUM_COLS):
        x = ci * COL_W
        lines.append(
            f'<rect x="{x}" y="0" width="{COL_W}" height="{THUMB_H}"'
            f' fill="url(#g{ci})"/>'
        )

    lines.append('</svg>')

    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text('\n'.join(lines))
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
