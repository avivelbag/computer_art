#!/usr/bin/env python3
"""Generate thumbnail.png for Piece 120 — Celtic Knotwork: Over, Under, Forever.

Renders a (3,5) torus knot projected to 2D with correct over-under crossings
using pure Python standard library (math, struct, zlib, pathlib).

The rendering mirrors the canvas animation:
  - Shadow layer  (wider, dark bronze)
  - Main strand   (warm bronze/gold)
  - Highlight     (thin cream line along strand centre)
  - At each crossing: background-coloured gap over the under-strand,
    then all three layers redrawn for the over-strand.
"""
import math
import pathlib
import struct
import zlib

W, H = 400, 400
CX, CY = W // 2, H // 2
P, Q = 3, 5
R, r = 114, 36        # scaled ~57% from canvas 200/62
N = 300               # curve samples (reduced for static thumbnail)
SKIP = 18             # min index gap for crossing detection
TILT = 0.45           # fixed tilt angle (radians) for the thumbnail

SW = 12               # strand half-width (radius) in pixels
GW = int(SW * 1.85)   # gap half-width
HW = 3                # highlight half-width

BG     = (31, 51, 32)       # #1f3320 deep forest green
SHAD   = (122, 69, 0)       # #7a4500 dark bronze shadow
STRAND = (200, 134, 10)     # #c8860a warm bronze/gold
HILIT  = (245, 230, 176)    # #f5e6b0 cream highlight

CROSS_R2 = (SW * 0.6) ** 2
MERGE_R2 = (SW * 2.8) ** 2


def compute_points(tilt: float) -> list[tuple[float, float, float]]:
    """Return the N+1 screen-space points of the (P,Q) torus knot tilted by *tilt*.

    The tilt is a rotation around the x-axis that gives the viewer a slight
    bird's-eye perspective so over/under depths are clearly differentiated.
    Returns a list of (x, y, z) tuples where x/y are pixel coordinates and
    z is the depth value (higher = in front).
    """
    ct, st = math.cos(tilt), math.sin(tilt)
    pts = []
    for i in range(N + 1):
        t = i / N * math.pi * 2
        cp, sp = math.cos(P * t), math.sin(P * t)
        cq, sq = math.cos(Q * t), math.sin(Q * t)
        rho = R + r * cq
        x = rho * cp
        y = rho * sp
        z = r * sq
        pts.append((x + CX, y * ct - z * st + CY, y * st + z * ct))
    return pts


def detect_crossings(pts: list) -> list[dict]:
    """Find over/under crossing pairs in the projected (x, y) plane.

    Uses midpoint proximity: two segments whose midpoints lie within
    CROSS_R2 (squared pixels) of each other in 2D are a crossing candidate.
    The segment with higher z midpoint is the "over" strand.

    Pairs within SKIP indices are neighbours on the curve (not crossings) and
    are excluded.  Multiple detections of the same physical crossing are merged
    using MERGE_R2.
    """
    mx = [(pts[i][0] + pts[i + 1][0]) * 0.5 for i in range(N)]
    my = [(pts[i][1] + pts[i + 1][1]) * 0.5 for i in range(N)]
    mz = [(pts[i][2] + pts[i + 1][2]) * 0.5 for i in range(N)]

    raw = []
    for i in range(N):
        lim = N - SKIP + i
        for j in range(i + SKIP, N):
            if j >= lim:
                continue
            dx, dy = mx[i] - mx[j], my[i] - my[j]
            if dx * dx + dy * dy <= CROSS_R2:
                if mz[i] >= mz[j]:
                    ov, un = i, j
                else:
                    ov, un = j, i
                raw.append({
                    "ov": ov, "un": un,
                    "cx": (mx[i] + mx[j]) * 0.5,
                    "cy": (my[i] + my[j]) * 0.5,
                })

    merged: list[dict] = []
    for c in raw:
        is_dup = any(
            (m["cx"] - c["cx"]) ** 2 + (m["cy"] - c["cy"]) ** 2 < MERGE_R2
            for m in merged
        )
        if not is_dup:
            merged.append(c)
    return merged


def _blend(base: list, color: tuple, alpha: float) -> list:
    """Alpha-composite *color* over *base* at opacity *alpha* ∈ [0, 1]."""
    return [
        int(base[0] * (1 - alpha) + color[0] * alpha + 0.5),
        int(base[1] * (1 - alpha) + color[1] * alpha + 0.5),
        int(base[2] * (1 - alpha) + color[2] * alpha + 0.5),
    ]


def _paint_disk(pixels: list, cx: float, cy: float, radius: int,
                color: tuple, alpha: float = 1.0) -> None:
    """Stamp a filled circle of *radius* pixels at (*cx*, *cy*) into *pixels*."""
    ix, iy = int(cx + 0.5), int(cy + 0.5)
    r2 = radius * radius
    for dy in range(-radius - 1, radius + 2):
        for dx in range(-radius - 1, radius + 2):
            if dx * dx + dy * dy <= r2:
                px, py = ix + dx, iy + dy
                if 0 <= px < W and 0 <= py < H:
                    idx = py * W + px
                    pixels[idx] = _blend(pixels[idx], color, alpha)


def _draw_segment(pixels: list, pts: list, i: int,
                  radius: int, color: tuple, alpha: float = 1.0) -> None:
    """Rasterise the thick line for segment i → i+1 by stamping disks along it.

    The disk-stamping approach approximates a round-capped stroke: every pixel
    within *radius* of the line centreline gets the blended colour.
    """
    x1, y1 = pts[i][0], pts[i][1]
    x2, y2 = pts[i + 1][0], pts[i + 1][1]
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    steps = max(1, int(length * 1.5))
    for s in range(steps + 1):
        t = s / steps
        _paint_disk(pixels, x1 + dx * t, y1 + dy * t, radius, color, alpha)


def _draw_full_strand(pixels: list, pts: list,
                      radius: int, color: tuple, alpha: float = 1.0) -> None:
    """Draw every segment of the closed curve with the given radius and color."""
    for i in range(N):
        _draw_segment(pixels, pts, i, radius, color, alpha)


def render() -> bytes:
    """Render the Celtic knotwork thumbnail and return raw PNG-filter-byte data.

    The return value is a flat bytes object in the format expected by write_png:
    one filter byte (0x00) per row followed by W×3 RGB bytes.
    """
    pixels = [list(BG) for _ in range(W * H)]
    pts = compute_points(TILT)
    crossings = detect_crossings(pts)

    # Layer 1: full strand (shadow → main colour → highlight)
    _draw_full_strand(pixels, pts, SW + 4, SHAD)
    _draw_full_strand(pixels, pts, SW, STRAND)
    _draw_full_strand(pixels, pts, HW, HILIT)

    # Layer 2: crossings — erase under, overdraw over
    for c in crossings:
        un, ov = c["un"], c["ov"]
        _draw_segment(pixels, pts, un, GW, BG)          # gap
        _draw_segment(pixels, pts, ov, SW + 4, SHAD)    # over shadow
        _draw_segment(pixels, pts, ov, SW, STRAND)      # over main
        _draw_segment(pixels, pts, ov, HW, HILIT)       # over highlight

    raw = bytearray()
    for row in range(H):
        raw.append(0)  # PNG filter byte: None
        for px in pixels[row * W:(row + 1) * W]:
            raw.extend(px)
    return bytes(raw)


def write_png(path: str, data: bytes) -> None:
    """Write raw filter+RGB pixel data *data* to a PNG file at *path*."""
    def chunk(name: bytes, body: bytes) -> bytes:
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
