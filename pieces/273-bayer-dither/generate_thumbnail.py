"""Generate thumbnail.png for piece 273 — The Grain of Light.

Computes the Bayer-dithered plasma snapshot at t=5.0 seconds at 400×400
resolution and writes it as a PNG using only stdlib (zlib + struct).
The resulting file is a pixel-exact representation of what the canvas
animation looks like at that time.
"""

import math
import pathlib
import struct
import zlib

THUMB_W, THUMB_H = 400, 400
T = 5.0

BAYER8 = [
     0, 32,  8, 40,  2, 34, 10, 42,
    48, 16, 56, 24, 50, 18, 58, 26,
    12, 44,  4, 36, 14, 46,  6, 38,
    60, 28, 52, 20, 62, 30, 54, 22,
     3, 35, 11, 43,  1, 33,  9, 41,
    51, 19, 59, 27, 49, 17, 57, 25,
    15, 47,  7, 39, 13, 45,  5, 37,
    63, 31, 55, 23, 61, 29, 53, 21,
]

BG = (13, 13, 13)     # #0d0d0d — near-black
FG = (232, 201, 122)  # #e8c97a — sand gold

P3 = math.pi * 3
P4 = math.pi * 4
P5 = math.pi * 5 / THUMB_W


def plasma(x, y, t):
    """Four-term plasma field value at pixel (x, y) at time t.

    Mirrors the JavaScript render() function exactly so the thumbnail
    represents a real frame of the animation.  Each of the four sine
    terms lies in [-1, 1]; their sum lies in [-4, 4].  Adding 4 and
    multiplying by 0.125 maps the result to [0, 1].
    """
    nx, ny = x / THUMB_W, y / THUMB_H
    dx, dy = nx - 0.5, ny - 0.5
    rd = math.sqrt(dx * dx + dy * dy) * 12 * math.pi
    return (
        math.sin(nx * P3 + t * 0.7)
        + math.sin(ny * P4 + t * 0.5)
        + math.sin((x + y) * P5 + t * 0.3)
        + math.sin(rd + t * 0.9)
        + 4
    ) * 0.125


def write_png(path, w, h, rows):
    """Write an RGB PNG file from a list of rows of (R, G, B) tuples.

    Uses only zlib and struct from the Python standard library.
    """
    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter type None — no per-row prediction
        for r, g, b in row:
            raw += bytes([r, g, b])

    body = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(body)


def main():
    out = pathlib.Path(__file__).parent / "thumbnail.png"
    rows = []
    for y in range(THUMB_H):
        brow = (y & 7) * 8
        row = []
        for x in range(THUMB_W):
            v = plasma(x, y, T)
            on = v > BAYER8[brow + (x & 7)] / 64
            row.append(FG if on else BG)
        rows.append(row)
    write_png(out, THUMB_W, THUMB_H, rows)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
