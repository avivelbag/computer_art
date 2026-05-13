#!/usr/bin/env python3
"""Generate thumbnail.png for Piece 115 — The Field Remembers.

Uses only the Python standard library (math, random, struct, zlib).
Writes a 400×250 RGB PNG showing simulated particle trails on a cream
background, faithfully representing the flow field palette.
"""
import math
import pathlib
import random
import struct
import zlib

W, H = 400, 250
SEED = 42
NOISE_SCALE = 0.006
TIME_OFFSET = 0.3
SPEED = 1.5
BG = (242, 237, 228)
INK_COLORS = [
    (26, 39, 68),    # #1a2744 navy
    (192, 57, 43),   # #c0392b rust
    (74, 124, 89),   # #4a7c59 sage
]

_F2 = 0.5 * (math.sqrt(3) - 1)
_G2 = (3 - math.sqrt(3)) / 6
_GRAD2 = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]


def build_perm(seed):
    """Return a 512-entry permutation table seeded deterministically."""
    rng = random.Random(seed)
    p = list(range(256))
    rng.shuffle(p)
    return [p[i & 255] for i in range(512)]


def noise2d(xin, yin, perm):
    """2D simplex noise in [-1, 1] using *perm* as the permutation table.

    Based on Stefan Gustavson's public-domain implementation.
    """
    s = (xin + yin) * _F2
    i = math.floor(xin + s)
    j = math.floor(yin + s)
    t = (i + j) * _G2
    x0 = xin - (i - t)
    y0 = yin - (j - t)
    i1, j1 = (1, 0) if x0 > y0 else (0, 1)
    x1 = x0 - i1 + _G2
    y1 = y0 - j1 + _G2
    x2 = x0 - 1 + 2 * _G2
    y2 = y0 - 1 + 2 * _G2
    ii = i & 255
    jj = j & 255
    g0 = perm[ii + perm[jj]] % 8
    g1 = perm[ii + i1 + perm[jj + j1]] % 8
    g2 = perm[ii + 1 + perm[jj + 1]] % 8
    n = 0.0
    t0 = 0.5 - x0 * x0 - y0 * y0
    if t0 >= 0:
        t0 *= t0
        n += t0 * t0 * (_GRAD2[g0][0] * x0 + _GRAD2[g0][1] * y0)
    t1 = 0.5 - x1 * x1 - y1 * y1
    if t1 >= 0:
        t1 *= t1
        n += t1 * t1 * (_GRAD2[g1][0] * x1 + _GRAD2[g1][1] * y1)
    t2 = 0.5 - x2 * x2 - y2 * y2
    if t2 >= 0:
        t2 *= t2
        n += t2 * t2 * (_GRAD2[g2][0] * x2 + _GRAD2[g2][1] * y2)
    return 70 * n


def _blend(base, color, alpha):
    """Alpha-blend *color* over *base* at *alpha* in [0, 1], return new RGB tuple."""
    return (
        int(base[0] * (1 - alpha) + color[0] * alpha),
        int(base[1] * (1 - alpha) + color[1] * alpha),
        int(base[2] * (1 - alpha) + color[2] * alpha),
    )


def render():
    """Simulate particle trails and return raw W×H×3 RGB bytes.

    Uses a fixed seed for deterministic output. Particles follow the same
    simplex-noise flow field as the live canvas animation but at a smaller
    canvas scale and with a reduced particle count suitable for a thumbnail.
    """
    perm = build_perm(SEED)
    pixels = [list(BG) for _ in range(W * H)]

    rng = random.Random(SEED)
    n_particles = 600
    steps = 350
    trail_alpha = 0.18

    for _ in range(n_particles):
        x = rng.random() * W
        y = rng.random() * H
        color = INK_COLORS[rng.randint(0, 2)]

        for s in range(steps):
            t = TIME_OFFSET + s * 0.001
            angle = noise2d(x * NOISE_SCALE, y * NOISE_SCALE + t, perm) * math.pi * 2
            x = (x + math.cos(angle) * SPEED) % W
            y = (y + math.sin(angle) * SPEED) % H
            xi, yi = int(x) % W, int(y) % H
            idx = yi * W + xi
            r, g, b = pixels[idx]
            blended = _blend((r, g, b), color, trail_alpha)
            pixels[idx] = list(blended)

    raw = bytes(v for row in range(H) for v in ([0] + [c for px in pixels[row * W:(row + 1) * W] for c in px]))
    return raw


def write_png(path, data):
    """Write raw RGB pixel data *data* (W×H×3) to a PNG file at *path*."""
    def chunk(name, body):
        crc_data = name + body
        return (
            struct.pack('>I', len(body))
            + crc_data
            + struct.pack('>I', zlib.crc32(crc_data) & 0xFFFFFFFF)
        )

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    out = (
        sig
        + chunk(b'IHDR', ihdr)
        + chunk(b'IDAT', zlib.compress(data, 9))
        + chunk(b'IEND', b'')
    )
    pathlib.Path(path).write_bytes(out)


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.png'
    write_png(out, render())
    print(f'Written {out}')
