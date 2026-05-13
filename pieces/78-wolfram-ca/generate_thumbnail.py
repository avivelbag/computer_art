#!/usr/bin/env python3
"""Generate thumbnail.svg for pieces/78-wolfram-ca — Rule 30 on 100×100 grid.

Uses a single <path> element for all live cells to keep file size under 200 KB.
"""
import pathlib

W = 100
H = 100
CELL = 4
RULE = 30
BG_COLOR = "#0a080f"
FG_COLOR = "#ffb000"


def next_gen(row: list[int], rule: int) -> list[int]:
    """Return the next CA generation using periodic boundary conditions."""
    n = len(row)
    result = []
    for i in range(n):
        pat = (row[(i - 1) % n] << 2) | (row[i] << 1) | row[(i + 1) % n]
        result.append((rule >> pat) & 1)
    return result


def generate() -> None:
    row: list[int] = [0] * W
    row[W // 2] = 1
    rows = [list(row)]
    for _ in range(H - 1):
        row = next_gen(row, RULE)
        rows.append(list(row))

    total_w = W * CELL
    total_h = H * CELL

    # Encode all live cells as a single compact SVG path (Mxy hCELL vCELL h-CELL z).
    # This is ~3× smaller than individual <rect> elements.
    segments: list[str] = []
    for y, r in enumerate(rows):
        for x, cell in enumerate(r):
            if cell:
                segments.append(f"M{x * CELL},{y * CELL}h{CELL}v{CELL}h-{CELL}z")

    path_d = "".join(segments)

    svg = "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {total_w} {total_h}" '
        f'width="{total_w}" height="{total_h}">',
        f'  <rect width="{total_w}" height="{total_h}" fill="{BG_COLOR}"/>',
        f'  <path fill="{FG_COLOR}" d="{path_d}"/>',
        "</svg>",
    ])

    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg, encoding="utf-8")
    live = sum(cell for r in rows for cell in r)
    print(f"Written {out} ({out.stat().st_size} bytes, {live} live cells)")


if __name__ == "__main__":
    generate()
