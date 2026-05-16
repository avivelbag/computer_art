"""Generate thumbnail.svg for Piece 194 — Chladni Figures, showing mode (3, 4)."""
import math
import pathlib

W, H  = 400, 400
GRID  = 60   # 60×60 cells → ~6.7×6.7 px each

K_SHARP = 40.0

BG_R, BG_G, BG_B   = 10,  10,  15
AU_R, AU_G, AU_B   = 242, 201, 76
WH_R, WH_G, WH_B   = 255, 255, 255


def field_abs(m: int, n: int, px: float, py: float) -> float:
    """Return |sin(m·π·x)·sin(n·π·y)| for pixel (px, py) in [0, W-1]×[0, H-1]."""
    x = px / (W - 1)
    y = py / (H - 1)
    return abs(math.sin(m * math.pi * x) * math.sin(n * math.pi * y))


def field_to_rgb(v: float) -> tuple[int, int, int]:
    """Map |field| value v ∈ [0, 1] to RGB; mirrors the JS colour logic."""
    t = math.exp(-v * v * K_SHARP)
    if t < 0.4:
        s = t / 0.4
        r = int(BG_R + (AU_R - BG_R) * s)
        g = int(BG_G + (AU_G - BG_G) * s)
        b = int(BG_B + (AU_B - BG_B) * s)
    else:
        s = (t - 0.4) / 0.6
        r = int(AU_R + (WH_R - AU_R) * s)
        g = int(AU_G + (WH_G - AU_G) * s)
        b = int(AU_B + (WH_B - AU_B) * s)
    return r, g, b


def main() -> None:
    M, N = 3, 4  # mode to render in thumbnail
    cell_w = W / GRID
    cell_h = H / GRID

    rects = []
    for row in range(GRID):
        for col in range(GRID):
            cx = (col + 0.5) * cell_w
            cy = (row + 0.5) * cell_h
            v = field_abs(M, N, cx, cy)
            r, g, b = field_to_rgb(v)
            x = col * cell_w
            y = row * cell_h
            rects.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" '
                f'width="{cell_w:.2f}" height="{cell_h:.2f}" '
                f'fill="rgb({r},{g},{b})"/>'
            )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n'
        f'<rect width="{W}" height="{H}" fill="#0a0a0f"/>\n'
        + '\n'.join(rects)
        + '\n</svg>\n'
    )

    out = pathlib.Path(__file__).parent / 'thumbnail.svg'
    out.write_text(svg)
    print(f'Wrote {out} ({len(svg):,} bytes, {GRID * GRID} cells, mode ({M},{N}))')


if __name__ == '__main__':
    main()
