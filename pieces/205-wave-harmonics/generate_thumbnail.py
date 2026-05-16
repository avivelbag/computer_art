"""Generate thumbnail.svg for piece 205-wave-harmonics."""
import math
import pathlib

W, H = 400, 300
N = 200

UPPER_H = H // 2       # 150
LOWER_H = H - UPPER_H  # 150

CY_UPPER = UPPER_H // 2      # 75
CY_LOWER = UPPER_H + LOWER_H // 2  # 225

AMP_SCALE = UPPER_H * 0.35   # ~52.5 px per unit amplitude

COLORS = ["#00d4ff", "#ff6b9d", "#ffb347", "#7fff6b",
          "#b47fff", "#6bb8ff", "#ff8c6b", "#a0e67f"]


def svg_polyline(n_harmonic, amplitude, center_y, scale, n_pts=N):
    """Return an SVG polyline points string for the given harmonic."""
    pts = []
    for i in range(n_pts + 1):
        x = W * i / n_pts
        t = i / n_pts
        y = center_y - scale * amplitude * math.sin(2 * math.pi * n_harmonic * t)
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def svg_sum_polyline(preset_amps, center_y, n_pts=N):
    """Return an SVG polyline points string for the summed wave."""
    # Scale so the sum fits in the lower panel
    max_sum = max(
        abs(sum(a * math.sin(2 * math.pi * (idx + 1) * t)
                for idx, a in enumerate(preset_amps)))
        for t in (i / 500 for i in range(500))
    ) or 1.0
    scale = LOWER_H * 0.4 / max_sum
    pts = []
    for i in range(n_pts + 1):
        x = W * i / n_pts
        t = i / n_pts
        y_val = sum(
            a * math.sin(2 * math.pi * (idx + 1) * t)
            for idx, a in enumerate(preset_amps)
        )
        pts.append(f"{x:.1f},{(center_y - scale * y_val):.1f}")
    return " ".join(pts)


# Square-wave approximation using 4 odd harmonics
AMPS = [1.0, 0.0, 1/3, 0.0, 1/5, 0.0, 1/7, 0.0]

lines = [
    f'<rect width="{W}" height="{H}" fill="#0d0d14"/>',
    # Divider between upper and lower panels
    f'<line x1="0" y1="{UPPER_H}" x2="{W}" y2="{UPPER_H}" stroke="#1a1a2e" stroke-width="1"/>',
    # Center axes (subtle)
    f'<line x1="0" y1="{CY_UPPER}" x2="{W}" y2="{CY_UPPER}" stroke="#191924" stroke-width="0.5"/>',
    f'<line x1="0" y1="{CY_LOWER}" x2="{W}" y2="{CY_LOWER}" stroke="#191924" stroke-width="0.5"/>',
]

# Draw individual harmonics in upper panel
for idx, (n, amp, lw, alpha) in enumerate([
    (1, AMPS[0], 1.5, 0.85),
    (3, AMPS[2], 1.1, 0.70),
    (5, AMPS[4], 0.9, 0.60),
    (7, AMPS[6], 0.8, 0.55),
]):
    pts = svg_polyline(n, amp, CY_UPPER, AMP_SCALE)
    color = COLORS[(n - 1) % len(COLORS)]
    lines.append(
        f'<polyline points="{pts}" stroke="{color}" stroke-width="{lw}" '
        f'fill="none" opacity="{alpha}"/>'
    )

# Draw summed wave in lower panel
sum_pts = svg_sum_polyline(AMPS, CY_LOWER)
lines.append(
    f'<polyline points="{sum_pts}" stroke="#ffffff" stroke-width="2.5" fill="none"/>'
)

# Labels
lines.append(
    f'<text x="6" y="12" font-family="system-ui,sans-serif" font-size="9" fill="#555">harmonics</text>'
)
lines.append(
    f'<text x="6" y="{UPPER_H + 12}" font-family="system-ui,sans-serif" font-size="9" fill="#555">sum</text>'
)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
    + "\n".join(f"  {l}" for l in lines)
    + "\n</svg>\n"
)

out = pathlib.Path(__file__).parent / "thumbnail.svg"
out.write_text(svg)
print(f"Wrote {out}")
