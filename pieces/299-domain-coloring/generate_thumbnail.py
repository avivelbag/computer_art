"""
Generate thumbnail.png for piece 299 — Complex Portrait (domain coloring).

Renders z³−1 at the default view Re/Im ∈ [−3, 3] using the same domain-coloring
formula as the WebGL fragment shader:
  hue       = (atan2(Im f(z), Re f(z)) + π) / (2π)
  brightness = 0.5 + 0.5·sin(2π·log₂|f(z)|)   ← isochromatic rings
  saturation = 0.85

Produces a 400×400 PNG encoded entirely with stdlib (struct + zlib).
"""

import math
import pathlib
import struct
import zlib


def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    """Convert HSV (all [0,1]) to 8-bit RGB tuple."""
    if s == 0.0:
        b = int(v * 255)
        return (b, b, b)
    i = int(h * 6.0) % 6
    f = h * 6.0 - math.floor(h * 6.0)
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    palette = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    r, g, b = palette[i]
    return (int(r * 255), int(g * 255), int(b * 255))


def domain_color(fz_re: float, fz_im: float) -> tuple[int, int, int]:
    """Map a single f(z) value to an 8-bit RGB color via domain coloring."""
    arg = math.atan2(fz_im, fz_re)
    hue = (arg + math.pi) / (2.0 * math.pi)
    mag = math.hypot(fz_re, fz_im)
    bri = 0.5 + 0.5 * math.sin(2.0 * math.pi * math.log2(mag + 1e-10))
    return hsv_to_rgb(hue % 1.0, 0.85, max(0.0, min(1.0, bri)))


def eval_z3_minus_1(re: float, im: float) -> tuple[float, float]:
    """Evaluate z³ − 1 at z = re + im·i."""
    z2_re = re * re - im * im
    z2_im = 2.0 * re * im
    z3_re = z2_re * re - z2_im * im
    z3_im = z2_re * im + z2_im * re
    return (z3_re - 1.0, z3_im)


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


def generate(size: int = 400, view: float = 3.0) -> list[list[tuple[int, int, int]]]:
    """Render z³−1 domain coloring at the default ±view view, returning pixel rows."""
    pixels = []
    for py in range(size):
        row = []
        for px in range(size):
            re = (px / size - 0.5) * (2.0 * view)
            im = (0.5 - py / size) * (2.0 * view)   # y flipped so +Im is up
            fz_re, fz_im = eval_z3_minus_1(re, im)
            row.append(domain_color(fz_re, fz_im))
        pixels.append(row)
    return pixels


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.png"
    pixels = generate()
    out.write_bytes(make_png(pixels))
    print(f"wrote {out} ({out.stat().st_size} bytes)")
