#!/usr/bin/env python3
"""Generate thumbnail.png for Piece 285 — The Sifting Hour (sand pendulum).

Simulates 800 frames of a 3:2 Lissajous sand pendulum on a 400×400 grid,
accumulates grain density, tone-maps to the ochre-cream palette, and writes
a PNG using only stdlib (zlib + struct).
"""
import math
import pathlib
import struct
import zlib

W, H = 400, 400
CX, CY = W / 2, H / 2

FX, FY = 3, 2
INIT_AMP = 160.0
DECAY = 0.9995
DT = 0.04
GRAINS = 35
PHASE_X = math.pi / 6
N_FRAMES = 800

BG_R, BG_G, BG_B = 26, 15, 6


def _make_rand():
    """Return a zero-argument callable that produces [0,1) floats via a simple LCG.

    Using a deterministic LCG rather than random.random() makes the output
    fully reproducible without seeding the global random state.
    """
    state = [12345]

    def rand():
        state[0] = (state[0] * 1664525 + 1013904223) & 0xFFFFFFFF
        return state[0] / 0x100000000

    return rand


def simulate(n_frames: int = N_FRAMES) -> list[int]:
    """Run the sand pendulum and return a flat W*H density grid.

    Each grain increments the integer pixel it falls on by 1.  The pendulum
    follows x(t) = ax·cos(FX·t + PHASE_X), y(t) = ay·sin(FY·t) with both
    amplitudes decaying by DECAY per frame.
    """
    density = [0] * (W * H)
    ax = ay = INIT_AMP
    t = 0.0
    rand = _make_rand()

    for _ in range(n_frames):
        px = CX + ax * math.cos(FX * t + PHASE_X)
        py = CY + ay * math.sin(FY * t)

        for _ in range(GRAINS):
            # Polar Box-Muller for Gaussian radius
            while True:
                u = rand() * 2 - 1
                v = rand() * 2 - 1
                s = u * u + v * v
                if 0 < s < 1:
                    break
            r = abs(u * math.sqrt(-2 * math.log(s) / s)) * 2.2
            angle = rand() * 2 * math.pi
            gx = int(px + r * math.cos(angle))
            gy = int(py + r * math.sin(angle))
            if 0 <= gx < W and 0 <= gy < H:
                density[gy * W + gx] += 1

        ax *= DECAY
        ay *= DECAY
        t += DT

    return density


def density_to_pixels(density: list[int]) -> list[tuple[int, int, int]]:
    """Convert raw density counts to RGB pixels via log-density tone mapping.

    Maps 0 → deep umber background, low density → ochre, high density → warm cream.
    Log scaling prevents overexposure along the densely-hit trace intersections.
    """
    max_d = max(density) if any(density) else 1
    log_max = math.log(max_d + 1)
    pixels = []
    for d in density:
        if d == 0:
            pixels.append((BG_R, BG_G, BG_B))
            continue
        t = math.log(d + 1) / log_max
        if t < 0.5:
            u = t * 2
            R = int(BG_R + u * (180 - BG_R))
            G = int(BG_G + u * (130 - BG_G))
            B = int(BG_B + u * (55 - BG_B))
        else:
            u = (t - 0.5) * 2
            R = int(180 + u * (245 - 180))
            G = int(130 + u * (234 - 130))
            B = int(55 + u * (208 - 55))
        pixels.append((R, G, B))
    return pixels


def write_png(path: pathlib.Path, pixels: list[tuple[int, int, int]]) -> None:
    """Write a W×H list of (r, g, b) tuples as a PNG file using only stdlib.

    Uses raw (filter-type 0) scanlines and zlib DEFLATE compression.
    """
    def chunk(tag: bytes, data: bytes) -> bytes:
        payload = tag + data
        return (
            struct.pack(">I", len(data))
            + payload
            + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        for x in range(W):
            r, g, b = pixels[y * W + x]
            raw.extend((r, g, b))

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def generate_thumbnail(n_frames: int = N_FRAMES) -> list[tuple[int, int, int]]:
    """Return W*H list of (r, g, b) pixels for the sand pendulum density thumbnail."""
    return density_to_pixels(simulate(n_frames))


if __name__ == "__main__":
    pixels = generate_thumbnail()
    out = pathlib.Path(__file__).parent / "thumbnail.png"
    write_png(out, pixels)
    non_bg = sum(1 for p in pixels if p != (BG_R, BG_G, BG_B))
    print(f"Wrote {out} ({out.stat().st_size} bytes, {non_bg} non-background pixels)")
