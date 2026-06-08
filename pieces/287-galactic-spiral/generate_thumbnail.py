"""Generate thumbnail.svg for piece 287-galactic-spiral."""
import math
import pathlib
import random

W, H = 800, 450
CX, CY = W // 2, H // 2
A, B = 14, 0.22
ARMS = 3
MAX_R = min(CY, CX) - 30


def spiral_xy(r: float, arm_offset: float) -> tuple[float, float]:
    """Return canvas (x, y) for a point on the logarithmic spiral r=A·e^(B·θ)."""
    theta = math.log(r / A) / B + arm_offset
    return CX + r * math.cos(theta), CY + r * math.sin(theta)


def approx_gauss(rng: random.Random) -> float:
    """Approximate standard-normal variate via sum of two uniform samples."""
    return (rng.random() + rng.random() - 1.0) * 1.4142


lines: list[str] = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
lines.append(f'<rect width="{W}" height="{H}" fill="#04040c"/>')

lines.append("""<defs>
  <radialGradient id="core" cx="50%" cy="50%" r="50%">
    <stop offset="0%"   stop-color="#fffcf0" stop-opacity="0.95"/>
    <stop offset="8%"   stop-color="#f5a623" stop-opacity="0.80"/>
    <stop offset="25%"  stop-color="#b05010" stop-opacity="0.25"/>
    <stop offset="55%"  stop-color="#3d1a0a" stop-opacity="0.07"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
  </radialGradient>
</defs>""")
lines.append(f'<circle cx="{CX}" cy="{CY}" r="130" fill="url(#core)"/>')

# Wide glow strokes along each arm path
for arm in range(ARMS):
    arm_offset = arm * 2 * math.pi / ARMS
    pts = []
    for r in range(22, MAX_R + 1, 3):
        x, y = spiral_xy(r, arm_offset)
        pts.append(f"{x:.1f},{y:.1f}")
    d = "M " + " L ".join(pts)
    color = "#80d4d4" if arm == 1 else "#c8d0ff"
    lines.append(
        f'<path d="{d}" stroke="{color}" stroke-width="12" fill="none"'
        f' stroke-opacity="0.13" stroke-linecap="round"/>'
    )

# Star dots biased toward arms
rng = random.Random(42)
for _ in range(420):
    arm = rng.randint(0, ARMS - 1)
    r = rng.random() ** 0.55 * (MAX_R - 22) + 22
    arm_offset = arm * 2 * math.pi / ARMS
    theta_arm = math.log(r / A) / B + arm_offset
    theta = theta_arm + approx_gauss(rng) * 0.32
    r2 = max(12, min(MAX_R, r + approx_gauss(rng) * MAX_R * 0.035))
    x = CX + r2 * math.cos(theta)
    y = CY + r2 * math.sin(theta)
    if 0 < x < W and 0 < y < H:
        alpha = rng.uniform(0.4, 0.9)
        rad = 1.5 if rng.random() < 0.05 else 1.0
        col = "#80d4d4" if rng.random() < 0.15 else "#f0f4ff"
        lines.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}"'
            f' fill="{col}" fill-opacity="{alpha:.2f}"/>'
        )

# Sparse background stars
for _ in range(90):
    x = rng.uniform(0, W)
    y = rng.uniform(0, H)
    alpha = rng.uniform(0.07, 0.22)
    lines.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0.7"'
        f' fill="#f0f4ff" fill-opacity="{alpha:.2f}"/>'
    )

lines.append("</svg>")

outfile = pathlib.Path(__file__).parent / "thumbnail.svg"
outfile.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {outfile}")
