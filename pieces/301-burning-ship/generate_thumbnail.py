"""
Generate thumbnail.png for piece 301 — The Wreck Below (Burning Ship fractal).

Renders the Burning Ship set at the default view (Re ∈ [−2.0, 1.0], Im ∈ [−1.8, 0.1])
using the same algorithm as the WebGL fragment shader:
  z_{n+1} = (|Re z| + i|Im z|)² + c   (Burning Ship iteration)
  smooth count  nu = n − log₂(log₂|z|)
  colour        3-stop gradient: deep indigo → amber → pale cream
  interior      near-black #050008

Produces a 400×400 PNG encoded entirely with stdlib (struct + zlib).
"""

import math
import pathlib
import struct
import zlib

INDIGO = (0.051, 0.008, 0.129)   # #0d0221
AMBER  = (0.878, 0.482, 0.0)     # #e07b00
CREAM  = (1.0,   0.973, 0.906)   # #fff8e7
INTERIOR_RGB = (5, 0, 8)         # #050008


def _smoothstep(a: float, b: float, x: float) -> float:
    """GLSL smoothstep in [a, b]."""
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def palette(t: float) -> tuple[int, int, int]:
    """Map smooth iteration count t ∈ [0, 1] to RGB via the 3-stop gradient."""
    if t < 0.3:
        s = _smoothstep(0.0, 1.0, t / 0.3)
        r = INDIGO[0] + s * (AMBER[0] - INDIGO[0])
        g = INDIGO[1] + s * (AMBER[1] - INDIGO[1])
        b = INDIGO[2] + s * (AMBER[2] - INDIGO[2])
    else:
        s = _smoothstep(0.0, 1.0, (t - 0.3) / 0.7)
        r = AMBER[0] + s * (CREAM[0] - AMBER[0])
        g = AMBER[1] + s * (CREAM[1] - AMBER[1])
        b = AMBER[2] + s * (CREAM[2] - AMBER[2])
    return (int(r * 255), int(g * 255), int(b * 255))


def burning_ship_color(cr: float, ci: float, max_iter: int = 256) -> tuple[int, int, int]:
    """Compute Burning Ship iteration colour for complex constant c = cr + i·ci.

    Returns an 8-bit RGB tuple; interior points (non-escaping) get INTERIOR_RGB.
    """
    zr, zi = 0.0, 0.0
    for i in range(max_iter):
        zr = abs(zr)
        zi = abs(zi)
        zr2 = zr * zr - zi * zi + cr
        zi  = 2.0 * zr * zi     + ci
        zr  = zr2
        if zr * zr + zi * zi > 4.0:
            mag = math.sqrt(zr * zr + zi * zi)
            nu  = i - math.log2(math.log2(max(mag, 1.0 + 1e-10)))
            t   = max(0.0, min(1.0, nu / max_iter))
            return palette(t)
    return INTERIOR_RGB


def make_png(pixels: list[list[tuple[int, int, int]]]) -> bytes:
    """Encode a 2D list of (R,G,B) tuples as a minimal PNG bytestring."""
    size = len(pixels)

    def chunk(tag: bytes, data: bytes) -> bytes:
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    raw_rows = b""
    for row in pixels:
        raw_rows += b"\x00" + bytes(v for rgb in row for v in rgb)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", header)
    png += chunk(b"IDAT", zlib.compress(raw_rows, 9))
    png += chunk(b"IEND", b"")
    return png


def generate(size: int = 400) -> list[list[tuple[int, int, int]]]:
    """Render the Burning Ship at default view; returns pixel rows top-to-bottom.

    View: Re ∈ [−2.0, 1.0], Im ∈ [−1.8, 0.1]  (y flipped so ship is upright)
    """
    re_min, re_max = -2.0,  1.0
    im_min, im_max = -1.8,  0.1
    pixels = []
    for py in range(size):
        row = []
        for px in range(size):
            cr = re_min + (px / size) * (re_max - re_min)
            # y flipped: row 0 → im_max, row size-1 → im_min
            ci = im_max - (py / size) * (im_max - im_min)
            row.append(burning_ship_color(cr, ci))
        pixels.append(row)
    return pixels


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.png"
    pixels = generate()
    out.write_bytes(make_png(pixels))
    print(f"wrote {out} ({out.stat().st_size} bytes)")
