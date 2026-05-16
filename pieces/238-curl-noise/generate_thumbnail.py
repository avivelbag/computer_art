#!/usr/bin/env python3
"""Generate thumbnail.png for Piece 238 — Curl Noise: The River That Doesn't Repeat.

Uses only the Python standard library (math, random, struct, zlib).
Writes a 400×250 RGB PNG that captures the canvas at a moment when trails
are fully developed, showing the ink-in-water look of divergence-free curl noise.
"""
import math
import pathlib
import random
import struct
import zlib

W, H = 400, 250
SEED = 7
NOISE_SCALE = 0.003
TIME_SCALE = 0.0003
CURL_EPS = 0.0001
STEP = 1.5

# Palette: deep violet (#2d0a50) → electric cyan (#00c8dc) → pale gold (#ffdc82)
PALETTE = [
    (45,  10,  80),
    (0,  200, 220),
    (255, 220, 130),
]
MAX_SPEED = 4.0
BG = (10, 0, 16)


def _build_perm(seed):
    """Return a 512-entry permutation table seeded deterministically."""
    rng = random.Random(seed)
    p = list(range(256))
    rng.shuffle(p)
    return [p[i & 255] for i in range(512)]


def _fade(t):
    """Quintic Hermite smoothstep giving C2 continuity across lattice boundaries."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def value_noise3(x, y, z, perm):
    """Evaluate 3D value noise at (x, y, z) using *perm*.

    Returns a value in [-1, 1]. Uses a tricubic lattice interpolation
    with quintic fade curves for smooth gradients.
    """
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    zi = int(math.floor(z)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    zf = z - math.floor(z)
    u, v, w = _fade(xf), _fade(yf), _fade(zf)

    aaa = perm[perm[perm[xi    ] + yi    ] + zi    ]
    aba = perm[perm[perm[xi    ] + yi + 1] + zi    ]
    aab = perm[perm[perm[xi    ] + yi    ] + zi + 1]
    abb = perm[perm[perm[xi    ] + yi + 1] + zi + 1]
    baa = perm[perm[perm[xi + 1] + yi    ] + zi    ]
    bba = perm[perm[perm[xi + 1] + yi + 1] + zi    ]
    bab = perm[perm[perm[xi + 1] + yi    ] + zi + 1]
    bbb = perm[perm[perm[xi + 1] + yi + 1] + zi + 1]

    def lerp(a, b, t):
        return a + t * (b - a)

    def val(h):
        return (h / 127.5) - 1.0

    return lerp(
        lerp(lerp(val(aaa), val(baa), u), lerp(val(aba), val(bba), u), v),
        lerp(lerp(val(aab), val(bab), u), lerp(val(abb), val(bbb), u), v),
        w,
    )


def curl_velocity(wx, wy, t, perm):
    """Return the 2D curl-noise velocity at world position (wx, wy) at time t.

    Derives velocity from a scalar potential P(x,y,t) via:
        vx = ∂P/∂y,   vy = −∂P/∂x
    Partial derivatives are approximated by central finite differences in
    noise space. Divergence-free by construction — particles never pile up.
    """
    nx = wx * NOISE_SCALE
    ny = wy * NOISE_SCALE
    nz = t * TIME_SCALE
    dPdy = (value_noise3(nx, ny + CURL_EPS, nz, perm) -
            value_noise3(nx, ny - CURL_EPS, nz, perm)) / (2 * CURL_EPS)
    dPdx = (value_noise3(nx + CURL_EPS, ny, nz, perm) -
            value_noise3(nx - CURL_EPS, ny, nz, perm)) / (2 * CURL_EPS)
    return dPdy, -dPdx


def speed_color(speed):
    """Map particle speed to an RGB tuple using the 3-stop violet→cyan→gold palette."""
    t = min(speed / MAX_SPEED, 1.0)
    if t < 0.5:
        s = t * 2
        p0, p1 = PALETTE[0], PALETTE[1]
    else:
        s = (t - 0.5) * 2
        p0, p1 = PALETTE[1], PALETTE[2]
    return (
        int(p0[0] + s * (p1[0] - p0[0])),
        int(p0[1] + s * (p1[1] - p0[1])),
        int(p0[2] + s * (p1[2] - p0[2])),
    )


def _blend(base, color, alpha):
    """Alpha-blend *color* over *base* at *alpha* in [0, 1], return new RGB tuple."""
    return (
        int(base[0] * (1 - alpha) + color[0] * alpha),
        int(base[1] * (1 - alpha) + color[1] * alpha),
        int(base[2] * (1 - alpha) + color[2] * alpha),
    )


def render():
    """Simulate curl-noise particle trails and return raw W×H×3 RGB bytes.

    Uses a fixed seed for deterministic output. Simulates ~600 frames
    (~10 seconds at 60 fps) to capture fully-developed trails, matching the
    acceptance criterion that the thumbnail captures the canvas ~10 s in.
    """
    perm = _build_perm(SEED)
    pixels = [list(BG) for _ in range(W * H)]

    rng = random.Random(SEED)
    n_particles = 500
    warmup_frames = 600
    trail_alpha = 0.25

    x_pos = [rng.random() * W for _ in range(n_particles)]
    y_pos = [rng.random() * H for _ in range(n_particles)]

    for frame in range(warmup_frames):
        # Fade background slightly each frame to simulate low-alpha compositing.
        if frame % 20 == 0:
            for k in range(W * H):
                r, g, b = pixels[k]
                pixels[k] = [
                    int(r * 0.97 + BG[0] * 0.03),
                    int(g * 0.97 + BG[1] * 0.03),
                    int(b * 0.97 + BG[2] * 0.03),
                ]

        for i in range(n_particles):
            vx, vy = curl_velocity(x_pos[i], y_pos[i], frame, perm)
            speed = math.sqrt(vx * vx + vy * vy)

            new_x = (x_pos[i] + vx * STEP) % W
            new_y = (y_pos[i] + vy * STEP) % H

            # Only paint if particle didn't wrap across canvas.
            if abs(new_x - x_pos[i]) < W * 0.4 and abs(new_y - y_pos[i]) < H * 0.4:
                xi = int(new_x) % W
                yi = int(new_y) % H
                idx = yi * W + xi
                r, g, b = pixels[idx]
                color = speed_color(speed)
                pixels[idx] = list(_blend((r, g, b), color, trail_alpha))

            x_pos[i] = new_x
            y_pos[i] = new_y

    raw = bytes(
        v
        for row in range(H)
        for v in ([0] + [c for px in pixels[row * W:(row + 1) * W] for c in px])
    )
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
