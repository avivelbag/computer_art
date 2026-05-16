"""Generate thumbnail.svg for the quasicrystal piece at t=0."""
import math
import pathlib

W, H  = 400, 400
GRID  = 40          # 40×40 cells → 10×10 px each
N     = 5
K     = 2 * math.pi / 80   # wavelength = 80 px in 400-px space

cos_theta = [math.cos(i * 2 * math.pi / N) for i in range(N)]
sin_theta = [math.sin(i * 2 * math.pi / N) for i in range(N)]


def field(px: float, py: float) -> float:
    """Return quasicrystal field value in [-1, 1] at pixel (px, py), t=0."""
    x = px - W / 2
    y = py - H / 2
    return sum(math.cos(K * (x * cos_theta[i] + y * sin_theta[i]))
               for i in range(N)) / N


def value_to_rgb(v: float) -> tuple[int, int, int]:
    """Map field value v ∈ [-1, 1] to RGB; mirrors the JS palette."""
    t = (v + 1) * 0.5
    if t < 0.5:
        s = t * 2
        r = int(6  + s * 54)
        g = int(4  + s * 16)
        b = int(15 + s * 85)
    else:
        s = (t - 0.5) * 2
        r = int(60  + s * 195)
        g = int(20  + s * 220)
        b = int(100 - s * 20)
    return r, g, b


cell_w = W / GRID
cell_h = H / GRID

rects = []
for row in range(GRID):
    for col in range(GRID):
        cx = (col + 0.5) * cell_w
        cy = (row + 0.5) * cell_h
        v  = field(cx, cy)
        r, g, b = value_to_rgb(v)
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
    f'<rect width="{W}" height="{H}" fill="#06040f"/>\n'
    + '\n'.join(rects)
    + '\n</svg>\n'
)

out = pathlib.Path(__file__).parent / 'thumbnail.svg'
out.write_text(svg)
print(f'Wrote {out} ({len(svg):,} bytes, {GRID*GRID} cells)')
