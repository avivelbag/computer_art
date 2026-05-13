#!/usr/bin/env python3
"""Generate thumbnail.png for Piece 111 — Bifurcation Diagram.

Uses only the Python standard library (struct, zlib) so it runs anywhere.
Writes a 400×400 RGB PNG next to this script.
"""
import pathlib
import struct
import zlib

W, H = 400, 400
R_MIN = 2.5
R_SPAN = 1.5
CHAOS_ONSET = 3.57
WARMUP = 300
PLOT = 300


def lerp(a, b, t):
    """Linear interpolation from a to b by factor t."""
    return a + (b - a) * t


def render():
    """Iterate the logistic map for each column and return raw RGB bytes.

    Background is near-black #050508.  Point colour is a function of r:
    t=0 (r=2.5, stable) → cool blue; t=1 (r=4.0, chaotic) → warm gold.
    A subtle dashed vertical line marks the chaos onset at r≈3.57.
    """
    pixels = bytearray(W * H * 3)
    for i in range(W * H):
        pixels[i * 3]     = 5
        pixels[i * 3 + 1] = 5
        pixels[i * 3 + 2] = 8

    for px in range(W):
        r = R_MIN + (px / W) * R_SPAN
        x = 0.5
        for _ in range(WARMUP):
            x = r * x * (1 - x)
        t = (r - R_MIN) / R_SPAN
        rv = int(lerp(30, 255, t))
        gv = int(lerp(80, 200, t * t))
        bv = int(lerp(200, 30, t))
        for _ in range(PLOT):
            x = r * x * (1 - x)
            py = int((1 - x) * H)
            if 0 <= py < H:
                idx = (py * W + px) * 3
                pixels[idx]     = rv
                pixels[idx + 1] = gv
                pixels[idx + 2] = bv

    cx = round(W * (CHAOS_ONSET - R_MIN) / R_SPAN)
    for py in range(H):
        if (py // 5) % 2 == 0:
            idx = (py * W + cx) * 3
            pixels[idx]     = min(255, pixels[idx]     + 60)
            pixels[idx + 1] = min(255, pixels[idx + 1] + 60)
            pixels[idx + 2] = min(255, pixels[idx + 2] + 60)

    return bytes(pixels)


def write_png(path, data):
    """Write raw RGB bytes *data* (W×H×3) to a PNG file at *path*."""
    def chunk(name, body):
        crc_data = name + body
        return (
            struct.pack('>I', len(body))
            + crc_data
            + struct.pack('>I', zlib.crc32(crc_data) & 0xFFFFFFFF)
        )

    raw = bytearray()
    for y in range(H):
        raw += b'\x00'
        raw += data[y * W * 3: (y + 1) * W * 3]

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    out = (
        sig
        + chunk(b'IHDR', ihdr_data)
        + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
        + chunk(b'IEND', b'')
    )
    pathlib.Path(path).write_bytes(out)


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.png'
    write_png(out, render())
    print(f'Written {out}')
