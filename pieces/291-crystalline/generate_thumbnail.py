#!/usr/bin/env python3
"""Generate thumbnail.svg for piece 291 — Crystalline (hexagonal DLA snowflake)."""

import math
import pathlib

W, H = 400, 400
CX, CY = 200, 200
HEX_SIZE = 5.0
BG = "#080c18"
MAX_R = 22


def hex_to_pixel(q: int, r: int) -> tuple[float, float]:
    """Convert axial hex coordinates to pixel coordinates (pointy-top orientation)."""
    px = CX + HEX_SIZE * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
    py = CY + HEX_SIZE * 1.5 * r
    return px, py


def hex_radius(q: int, r: int) -> int:
    """Return the Chebyshev distance from the origin in cube hex coordinates."""
    return max(abs(q), abs(r), abs(q + r))


def symmetry_set(q: int, r: int) -> list[tuple[int, int]]:
    """Return all 12 cells in the D6 orbit of (q, r).

    The dihedral group D6 has six rotations (60° each) and six reflections.
    In axial hex coordinates the six 60° rotations are:
      R^k(q,r) for k=0..5
    and six more reflected variants R^k(S(q,r)) where S(q,r) = (q, -q-r).
    """
    s = -q - r
    return [
        (q, r),    (q + r, -q),  (r, s),      (-q, -r),  (s, q),    (-r, q + r),
        (q, s),    (q + r, -r),  (r, q),      (-q, -s),  (s, r),    (-r, -q),
    ]


def hex_polygon_points(px: float, py: float, size: float) -> str:
    """Return SVG polygon points string for a pointy-top hexagon centered at (px, py)."""
    pts = []
    for i in range(6):
        a = math.pi / 3 * i
        pts.append(f"{px + size * math.cos(a):.2f},{py + size * math.sin(a):.2f}")
    return " ".join(pts)


def build_snowflake() -> set[tuple[int, int]]:
    """Construct a deterministic hex snowflake cell set for the thumbnail.

    Adds main arm cells along each of the 6 hex axes, then periodic
    side branches and shorter tertiary sub-branches, exploiting symmetry_set
    so only one 'canonical' arm needs to be specified.
    """
    cells: set[tuple[int, int]] = set()

    def add(q: int, r: int) -> None:
        for cell in symmetry_set(q, r):
            cells.add(cell)

    # Main six arms: (k, 0) for k=0..MAX_R.  symmetry_set mirrors to all 6.
    for k in range(MAX_R + 1):
        add(k, 0)

    # Side branches off the main arm at every 4th cell, growing outward.
    for k in range(4, MAX_R, 4):
        max_branch = min(k // 2, 6)
        for j in range(1, max_branch + 1):
            add(k, -j)
            add(k + j, -j)

    # Shorter tertiary nubs on the largest branches.
    for k in range(8, MAX_R, 8):
        for j in range(1, 3):
            add(k + 1, -j)

    return cells


def main() -> None:
    cells = build_snowflake()
    max_r = max(hex_radius(q, r) for q, r in cells)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    ]

    for q, r in sorted(cells):
        px, py = hex_to_pixel(q, r)
        if not (0 <= px <= W and 0 <= py <= H):
            continue
        hr = hex_radius(q, r)
        t = min(1.0, hr / max_r)
        opacity = round(0.35 + 0.65 * t, 2)
        pts = hex_polygon_points(px, py, HEX_SIZE - 0.4)
        lines.append(
            f'<polygon points="{pts}" fill="rgb(222,238,255)" fill-opacity="{opacity:.2f}"/>'
        )

    lines.append("</svg>")

    out_path = pathlib.Path(__file__).parent / "thumbnail.svg"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(cells)} cells → {out_path}")


if __name__ == "__main__":
    main()
