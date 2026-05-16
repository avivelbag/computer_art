#!/usr/bin/env python3
"""Generate thumbnail.png for Piece 240 — Orbital Memory: N-Body Gravity in Slow Time.

Uses only the Python standard library (math, struct, zlib).
Produces a 400×400 RGB PNG of the solar-system configuration after the trail
ring buffers are fully populated (~300 frames / 5 s at 60 fps), showing
concentric glowing orbital arcs in the piece's warm-to-cool palette.
"""
import math
import pathlib
import struct
import zlib

W, H = 400, 400
CX, CY = W // 2, H // 2
SCALE = 125          # simulation units → pixels (tuned for 400×400 square crop)
G = 1.0
EPS = 0.01           # softening in simulation units (= 1.25 px ≥ 1 px)
TRAIL_LEN = 300
DT = 0.05
SUBS = 4
WARMUP_FRAMES = 400  # ~6.7 s at 60 fps — trails fully populated, orbits developed

BG = (10, 10, 20)

COLORS_HEX = ['#f4a261', '#e76f51', '#e9c46a', '#52b3c8', '#a8dadc', '#9b5de5']


def hex_to_rgb(h):
    """Parse '#rrggbb' into an (r, g, b) int tuple."""
    n = int(h.lstrip('#'), 16)
    return (n >> 16, (n >> 8) & 255, n & 255)


COLORS = [hex_to_rgb(h) for h in COLORS_HEX]


def to_screen(x, y):
    """Map simulation coordinates to pixel coordinates (y-axis flipped)."""
    return (int(CX + x * SCALE), int(CY - y * SCALE))


def compute_accel(bodies):
    """Return per-body (ax, ay) under softened Newtonian gravity.

    Force law: a_i += G * m_j * (r_j - r_i) / (|r_ij|^2 + ε^2)^(3/2).
    Softening ε prevents the denominator from reaching zero at close approach.
    """
    n = len(bodies)
    ax = [0.0] * n
    ay = [0.0] * n
    for i in range(n):
        for j in range(i + 1, n):
            dx = bodies[j]['x'] - bodies[i]['x']
            dy = bodies[j]['y'] - bodies[i]['y']
            denom = (dx * dx + dy * dy + EPS * EPS) ** 1.5
            f = G / denom
            ax[i] += f * bodies[j]['m'] * dx
            ay[i] += f * bodies[j]['m'] * dy
            ax[j] -= f * bodies[i]['m'] * dx
            ay[j] -= f * bodies[i]['m'] * dy
    return ax, ay


def leapfrog(bodies, dt):
    """Advance bodies by one kick-drift-kick leapfrog step of duration dt.

    Leapfrog (velocity Verlet) is a symplectic integrator: it conserves a
    slightly perturbed Hamiltonian exactly, preventing secular energy drift
    that would destabilize long-running orbital simulations.
    """
    ax, ay = compute_accel(bodies)
    for i, b in enumerate(bodies):
        b['vx'] += 0.5 * dt * ax[i]
        b['vy'] += 0.5 * dt * ay[i]
    for b in bodies:
        b['x'] += dt * b['vx']
        b['y'] += dt * b['vy']
    ax, ay = compute_accel(bodies)
    for i, b in enumerate(bodies):
        b['vx'] += 0.5 * dt * ax[i]
        b['vy'] += 0.5 * dt * ay[i]


def make_solar():
    """Return the hand-tuned solar system configuration (5 bodies).

    One dominant central body (m=3) plus four planets in circular Keplerian
    orbits at increasing radii. Planet masses are ≤0.2% of M_sun so
    planet-planet perturbations stay orders of magnitude below solar gravity,
    keeping all orbits stable for 30+ s. M_sun=3 gives inner-planet angular
    frequency ω≈3.7 rad/sim at r=0.6, so ω·dt_sub≈0.047 — within the
    leapfrog's stable zone for 1800+ frame integrations.

    Each planet's speed is set to v = sqrt(G·M_sun/r) (Keplerian circular
    velocity). The sun's velocity is then adjusted so total momentum is zero,
    keeping the center of mass fixed throughout the simulation.
    """
    Msun = 3.0
    bodies = [{'x': 0, 'y': 0, 'vx': 0.0, 'vy': 0.0, 'm': Msun}]
    planets = [
        {'r': 0.60, 'm': 0.005, 'phase': 0.5},
        {'r': 0.90, 'm': 0.004, 'phase': 2.1},
        {'r': 1.20, 'm': 0.003, 'phase': 4.3},
        {'r': 1.50, 'm': 0.002, 'phase': 1.0},
    ]
    for p in planets:
        v = math.sqrt(G * Msun / p['r'])
        ph = p['phase']
        bodies.append({
            'x':  p['r'] * math.cos(ph),
            'y':  p['r'] * math.sin(ph),
            'vx': -v * math.sin(ph),
            'vy':  v * math.cos(ph),
            'm':  p['m'],
        })
    # Zero total momentum: give the sun the velocity that cancels planet momenta.
    total_px = sum(b['m'] * b['vx'] for b in bodies)
    total_py = sum(b['m'] * b['vy'] for b in bodies)
    bodies[0]['vx'] = -total_px / Msun
    bodies[0]['vy'] = -total_py / Msun
    return bodies



def make_figure8():
    """Return the Chenciner-Montgomery figure-8 initial conditions.

    Three equal masses (m=1, G=1) in a choreographic figure-8 orbit.
    Period T ≈ 6.3259 simulation time units. Net momentum is near-zero
    (residual ~1e-8 from limited precision of published constants).
    """
    IC = [
        (-0.97000436,  0.24308753,  0.46620369,  0.43236573),
        ( 0.0,         0.0,         0.46620369,  0.43236573),
        ( 0.97000436, -0.24308753, -0.93240737, -0.86473146),
    ]
    return [
        {'x': x, 'y': y, 'vx': vx, 'vy': vy, 'm': 1.0}
        for (x, y, vx, vy) in IC
    ]


def assign_colors(bodies):
    """Rank bodies by mass descending and assign palette colors (warm = heavy)."""
    ranked = sorted(range(len(bodies)), key=lambda i: -bodies[i]['m'])
    for rank, i in enumerate(ranked):
        bodies[i]['color'] = COLORS[rank % len(COLORS)]


def blend(base, color, alpha):
    """Alpha-composite *color* over *base* at opacity *alpha* ∈ [0, 1]."""
    return (
        int(base[0] * (1 - alpha) + color[0] * alpha),
        int(base[1] * (1 - alpha) + color[1] * alpha),
        int(base[2] * (1 - alpha) + color[2] * alpha),
    )


def draw_line(pixels, x0, y0, x1, y1, color, alpha):
    """Bresenham line segment from (x0,y0) to (x1,y1), alpha-blended into pixels."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < W and 0 <= y0 < H:
            idx = y0 * W + x0
            pixels[idx] = blend(pixels[idx], color, alpha)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def render():
    """Simulate the solar configuration for WARMUP_FRAMES and return raw W×H RGB pixels.

    Maintains a 300-position ring buffer per body (matching index.html) and
    renders fading trails with alpha growing linearly from 0 (oldest) to 0.85 (newest).
    Returns a bytes object with one filter byte (0x00) per scanline followed by
    W*3 RGB bytes — the format expected by write_png.
    """
    bodies = make_solar()
    assign_colors(bodies)
    trails = [[] for _ in bodies]
    pixels = [list(BG) for _ in range(W * H)]
    dt_sub = DT / SUBS

    for _frame in range(WARMUP_FRAMES):
        for _ in range(SUBS):
            leapfrog(bodies, dt_sub)
        for i, b in enumerate(bodies):
            sx, sy = to_screen(b['x'], b['y'])
            trails[i].append((sx, sy))
            if len(trails[i]) > TRAIL_LEN:
                trails[i].pop(0)

    for i, b in enumerate(bodies):
        t = trails[i]
        n = len(t)
        for j in range(1, n):
            alpha = (j / n) * 0.85
            draw_line(pixels, t[j-1][0], t[j-1][1], t[j][0], t[j][1],
                      b['color'], alpha)

    for b in bodies:
        sx, sy = to_screen(b['x'], b['y'])
        r = max(2, int(2.5 + math.sqrt(b['m']) * 2))
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    px, py = sx + dx, sy + dy
                    if 0 <= px < W and 0 <= py < H:
                        pixels[py * W + px] = list(b['color'])

    raw = bytes(
        v
        for row in range(H)
        for v in ([0] + [c for px in pixels[row * W:(row + 1) * W] for c in px])
    )
    return raw


def write_png(path, data):
    """Write raw scanline data (filter byte + W*3 RGB bytes per row) as a PNG file."""
    def chunk(name, body):
        crc_data = name + body
        return (
            struct.pack('>I', len(body))
            + crc_data
            + struct.pack('>I', zlib.crc32(crc_data) & 0xFFFFFFFF)
        )

    sig  = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    out  = (
        sig
        + chunk(b'IHDR', ihdr)
        + chunk(b'IDAT', zlib.compress(data, 6))
        + chunk(b'IEND', b'')
    )
    pathlib.Path(path).write_bytes(out)


if __name__ == '__main__':
    out = pathlib.Path(__file__).parent / 'thumbnail.png'
    print('Simulating solar system configuration…')
    data = render()
    write_png(out, data)
    print(f'Written {out}')
