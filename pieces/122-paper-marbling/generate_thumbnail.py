#!/usr/bin/env python3
"""Generate thumbnail.png for Piece 122 — Ink Dropped in Still Water: Paper Marbling.

Renders the final marbled surface (after all stone drops and comb passes) at
400×400 using pure Python standard library. The algorithm mirrors the canvas
animation: stone drops apply the classic Ebru circular-displacement warp;
horizontal and vertical comb drags apply Gaussian-falloff per-tine warps.
"""
import math
import pathlib
import struct
import zlib

W, H = 400, 400

BG         = (242, 230, 200)
TERRACOTTA = (192,  82,  42)
COBALT     = ( 58,  95, 168)
SAFFRON    = (232, 160,  32)
FGREEN     = ( 45,  96,  64)
WINE       = (150,  55,  95)

# Stone drop parameters: (cx, cy, R, color, n_rings) — coords/radii scaled ×0.5
DROPS = [
    (115, 135,  57, TERRACOTTA, 6),
    (280, 115,  50, COBALT,     5),
    (190, 270,  60, SAFFRON,    6),
    (320, 260,  45, FGREEN,     5),
    ( 75, 280,  40, WINE,       4),
]

# Horizontal comb: (ty, direction) pairs; amt and sigma scaled ×0.5
H_TINES  = [(35,1),(95,-1),(155,1),(215,-1),(275,1),(335,-1),(372,1)]
H_AMT    = 65
H_SIGMA  = 17.5

# Vertical comb: (tx, direction) pairs
V_TINES  = [(40,1),(110,1),(180,1),(250,1),(320,1),(375,1)]
V_AMT    = -50
V_SIGMA  = 17.5


def _mk_buf():
    """Create a flat bytearray of W*H*3 bytes filled with the background colour."""
    r, g, b = BG
    buf = bytearray(W * H * 3)
    for i in range(W * H):
        buf[i*3] = r
        buf[i*3+1] = g
        buf[i*3+2] = b
    return buf


def _bilinear(buf, sx, sy):
    """Bilinear sample from flat RGB bytearray *buf* at float position (sx, sy).

    Returns an (r, g, b) tuple. Falls back to the background colour when the
    sample coordinates land outside the canvas boundary.
    """
    ix, iy = int(sx), int(sy)
    if ix < 0 or ix >= W-1 or iy < 0 or iy >= H-1:
        return BG
    fx, fy = sx - ix, sy - iy
    i00 = (iy * W + ix) * 3
    i10 = i00 + 3
    i01 = i00 + W * 3
    i11 = i01 + 3
    s = (1 - fx) * (1 - fy)
    t = fx * (1 - fy)
    u = (1 - fx) * fy
    v = fx * fy
    return (
        int(buf[i00]*s + buf[i10]*t + buf[i01]*u + buf[i11]*v),
        int(buf[i00+1]*s + buf[i10+1]*t + buf[i01+1]*u + buf[i11+1]*v),
        int(buf[i00+2]*s + buf[i10+2]*t + buf[i01+2]*u + buf[i11+2]*v),
    )


def _stone_drop(buf, cx, cy, R, color, n_rings):
    """Apply a classic Ebru stone drop to *buf* in-place.

    Pixels within 2R of (cx, cy) receive concentric alternating rings of
    *color* and the background. Pixels outside 2R are read from their
    pre-drop position via the inverse of r_new = r_old + R²/r_old:

        r_old = (r_new − √(r_new² − 4R²)) / 2

    This pushes all existing ink radially outward while preserving its pattern.
    """
    tmp = bytes(buf)
    R4 = 4.0 * R * R
    cr, cg, cb = color
    bgr, bgg, bgb = BG
    for y in range(H):
        for x in range(W):
            dx = x - cx
            dy = y - cy
            d2 = float(dx*dx + dy*dy)
            idx = (y * W + x) * 3
            if d2 < 0.25:
                buf[idx] = cr
                buf[idx+1] = cg
                buf[idx+2] = cb
                continue
            d = math.sqrt(d2)
            if d2 < R4:
                ring = int(d * n_rings / (2.0 * R))
                if ring % 2 == 0:
                    buf[idx] = cr
                    buf[idx+1] = cg
                    buf[idx+2] = cb
                else:
                    buf[idx] = bgr
                    buf[idx+1] = bgg
                    buf[idx+2] = bgb
            else:
                src_r = (d - math.sqrt(d2 - R4)) * 0.5
                r, g, b = _bilinear_from_bytes(tmp, cx + dx/d * src_r, cy + dy/d * src_r)
                buf[idx] = r
                buf[idx+1] = g
                buf[idx+2] = b


def _bilinear_from_bytes(buf, sx, sy):
    """Bilinear sample from a bytes object *buf* (immutable flat RGB).

    Identical logic to _bilinear() but accepts an immutable bytes snapshot
    taken at the start of each deformation pass.
    """
    ix, iy = int(sx), int(sy)
    if ix < 0 or ix >= W-1 or iy < 0 or iy >= H-1:
        return BG
    fx, fy = sx - ix, sy - iy
    i00 = (iy * W + ix) * 3
    i10 = i00 + 3
    i01 = i00 + W * 3
    i11 = i01 + 3
    s = (1 - fx) * (1 - fy)
    t = fx * (1 - fy)
    u = (1 - fx) * fy
    v = fx * fy
    return (
        int(buf[i00]*s + buf[i10]*t + buf[i01]*u + buf[i11]*v),
        int(buf[i00+1]*s + buf[i10+1]*t + buf[i01+1]*u + buf[i11+1]*v),
        int(buf[i00+2]*s + buf[i10+2]*t + buf[i01+2]*u + buf[i11+2]*v),
    )


def _comb_h(buf, tines, amt, sigma):
    """Apply a horizontal comb drag to *buf* in-place.

    Each tine at row *ty* displaces pixels in the x direction by
    dir * amt * exp(-(y−ty)² / sigma²). All tines act simultaneously
    (their displacements are summed), as in the physical Ebru rake.
    """
    tmp = bytes(buf)
    sig2 = sigma * sigma
    for y in range(H):
        disp = sum(
            direction * amt * math.exp(-(y - ty) ** 2 / sig2)
            for ty, direction in tines
        )
        for x in range(W):
            r, g, b = _bilinear_from_bytes(tmp, x - disp, y)
            idx = (y * W + x) * 3
            buf[idx] = r
            buf[idx+1] = g
            buf[idx+2] = b


def _comb_v(buf, tines, amt, sigma):
    """Apply a vertical comb drag to *buf* in-place.

    Each tine at column *tx* displaces pixels in the y direction by
    dir * amt * exp(-(x−tx)² / sigma²).
    """
    tmp = bytes(buf)
    sig2 = sigma * sigma
    for x in range(W):
        disp = sum(
            direction * amt * math.exp(-(x - tx) ** 2 / sig2)
            for tx, direction in tines
        )
        for y in range(H):
            r, g, b = _bilinear_from_bytes(tmp, x, y - disp)
            idx = (y * W + x) * 3
            buf[idx] = r
            buf[idx+1] = g
            buf[idx+2] = b


def render():
    """Render the fully marbled surface and return raw PNG row data.

    Applies all stone drops followed by horizontal and vertical comb passes.
    Returns bytes in PNG filter-byte format: one 0x00 filter byte per row
    followed by W × 3 RGB bytes, ready to be passed to write_png().
    """
    buf = _mk_buf()
    for cx, cy, R, color, n_rings in DROPS:
        _stone_drop(buf, cx, cy, R, color, n_rings)
    _comb_h(buf, H_TINES, H_AMT, H_SIGMA)
    _comb_v(buf, V_TINES, V_AMT, V_SIGMA)

    raw = bytearray()
    for row in range(H):
        raw.append(0)
        start = row * W * 3
        raw.extend(buf[start:start + W * 3])
    return bytes(raw)


def write_png(path, data):
    """Write raw filter+RGB pixel data *data* to a PNG file at *path*."""
    def chunk(name, body):
        crc_data = name + body
        return (
            struct.pack(">I", len(body))
            + crc_data
            + struct.pack(">I", zlib.crc32(crc_data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    out = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(data, 6))
        + chunk(b"IEND", b"")
    )
    pathlib.Path(path).write_bytes(out)


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "thumbnail.png"
    write_png(str(out), render())
    print(f"Written {out}")
