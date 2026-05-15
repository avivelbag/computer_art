#!/usr/bin/env python3
"""Generate thumbnail.png for Piece 137 — Lorenz Attractor: The Butterfly That Never Lands.

Integrates the Lorenz system with RK4 at dt=0.005, projects the 3D orbit onto a
400×400 density grid using a fixed camera angle (pi/5 ≈ 36°), applies
log(density+1) tone mapping, and writes a PNG using only stdlib (zlib + struct).
"""
import math
import pathlib
import struct
import zlib

W, H = 400, 400
SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
DT = 0.005
DT_2, DT_6 = DT / 2, DT / 6
N_WARMUP = 2000
N_POINTS = 200000

# Camera angle fixed at pi/5 for the thumbnail snapshot
ANGLE = math.pi / 5

# Projection bounds — must match index.html exactly
U_HALF = 38.0
V_MIN, V_MAX = -3.0, 53.0
V_RANGE = V_MAX - V_MIN

# Background: deep indigo
BG_R, BG_G, BG_B = 6, 6, 24


def rk4_step(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Advance the Lorenz system by one RK4 step of size DT.

    The Lorenz equations are:
        dx/dt = sigma * (y - x)
        dy/dt = x * (rho - z) - y
        dz/dt = x * y - beta * z
    """
    def deriv(x, y, z):
        return SIGMA * (y - x), x * (RHO - z) - y, x * y - BETA * z

    dx1, dy1, dz1 = deriv(x, y, z)
    dx2, dy2, dz2 = deriv(x + DT_2 * dx1, y + DT_2 * dy1, z + DT_2 * dz1)
    dx3, dy3, dz3 = deriv(x + DT_2 * dx2, y + DT_2 * dy2, z + DT_2 * dz2)
    dx4, dy4, dz4 = deriv(x + DT * dx3, y + DT * dy3, z + DT * dz3)
    return (
        x + DT_6 * (dx1 + 2 * dx2 + 2 * dx3 + dx4),
        y + DT_6 * (dy1 + 2 * dy2 + 2 * dy3 + dy4),
        z + DT_6 * (dz1 + 2 * dz2 + 2 * dz3 + dz4),
    )


def lorenz_color(t: float) -> tuple[int, int, int]:
    """Map t ∈ [0, 1] to RGB along the indigo → cyan → gold gradient.

    Matches the LUT built in index.html so thumbnail and live rendering use
    an identical palette.
    """
    if t < 0.5:
        u = t * 2
        r = int(BG_R * (1 - u))
        g = int(BG_G + (220 - BG_G) * u)
        b = int(BG_B + (220 - BG_B) * u)
    else:
        u = (t - 0.5) * 2
        r = int(255 * u)
        g = int(220 - 5 * u)
        b = int(220 * (1 - u))
    return r, g, b


def write_png(path: str, pixels: list, width: int, height: int) -> None:
    """Write a flat list of (r, g, b) tuples as a PNG file using only stdlib.

    Uses zlib for DEFLATE compression and struct for binary packing.
    """
    def chunk(tag: bytes, data: bytes) -> bytes:
        payload = tag + data
        return (
            struct.pack(">I", len(data))
            + payload
            + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # PNG filter: none
        for x in range(width):
            r, g, b = pixels[y * width + x]
            raw.extend((r, g, b))

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + chunk(b"IEND", b"")
    )
    pathlib.Path(path).write_bytes(png)


def build_density(n_points: int = N_POINTS) -> list[int]:
    """Integrate the Lorenz system and return a flat W*H density grid.

    Each entry counts how many projected trajectory points fell into that pixel.
    """
    cos_a = math.cos(ANGLE)
    sin_a = math.sin(ANGLE)
    u_scale = W / (2 * U_HALF)
    v_scale = H / V_RANGE

    density = [0] * (W * H)
    x, y, z = 0.1, 0.0, 1.0

    for _ in range(N_WARMUP):
        x, y, z = rk4_step(x, y, z)

    for _ in range(n_points):
        x, y, z = rk4_step(x, y, z)
        u = x * cos_a - y * sin_a
        v = z
        sx = int((u + U_HALF) * u_scale)
        sy = int((V_MAX - v) * v_scale)
        if 0 <= sx < W and 0 <= sy < H:
            density[sy * W + sx] += 1

    return density


def density_to_pixels(density: list[int]) -> list[tuple[int, int, int]]:
    """Convert a raw density grid to RGB pixels via log-density tone mapping."""
    max_d = max(density) if any(density) else 1
    log_max = math.log(max_d + 1)
    pixels = []
    for d in density:
        if d == 0:
            pixels.append((BG_R, BG_G, BG_B))
        else:
            t = math.log(d + 1) / log_max
            pixels.append(lorenz_color(t))
    return pixels


def generate_thumbnail(n_points: int = N_POINTS) -> list[tuple[int, int, int]]:
    """Return W*H list of (r, g, b) for the Lorenz density thumbnail."""
    return density_to_pixels(build_density(n_points))


if __name__ == "__main__":
    pixels = generate_thumbnail()
    out = pathlib.Path(__file__).parent / "thumbnail.png"
    write_png(str(out), pixels, W, H)
    non_bg = sum(1 for p in pixels if p != (BG_R, BG_G, BG_B))
    print(f"Wrote {out} ({out.stat().st_size} bytes, {non_bg} attractor pixels)")
