"""Generate a static SVG thumbnail for Piece 171 — Conformal Grid.

Shows the Joukowski-distorted grid (z → z + 1/z) at full distortion (λ=1),
with horizontal lines in rose/coral and vertical lines in sky blue,
matching the palette used by the live canvas animation.
"""
import math
import pathlib

SIZE = 400
CX = SIZE / 2
CY = SIZE / 2
SCALE = 55          # pixels per unit (−3..3 → ±165 px = 35..365 on 400 px canvas)
GRID_MIN = -3.0
GRID_MAX = 3.0
N_LINES = 20
N_SAMPLES = 200
MAX_MAG = 8.0
MIN_Z_MAG = 0.05
JUMP_THRESH = 80    # screen-pixel gap indicating a discontinuity
LAM = 1.0           # full Joukowski distortion for the thumbnail


def cdiv(a, b):
    """Divide complex number a by b, returning None if b is near zero."""
    d = b[0] ** 2 + b[1] ** 2
    if d < 1e-12:
        return None
    return ((a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d)


def cmag(z):
    """Return |z| for complex z = (re, im)."""
    return math.sqrt(z[0] ** 2 + z[1] ** 2)


def joukowski(z, lam):
    """Apply the blended Joukowski transform z → z + lam/z, returning None near the pole."""
    if cmag(z) < MIN_Z_MAG:
        return None
    inv = cdiv((1.0, 0.0), z)
    if inv is None:
        return None
    return (z[0] + lam * inv[0], z[1] + lam * inv[1])


def to_screen(w):
    """Map complex w to SVG pixel coordinates."""
    return (CX + w[0] * SCALE, CY - w[1] * SCALE)


def line_positions():
    """Return the N_LINES evenly spaced values from GRID_MIN to GRID_MAX."""
    return [GRID_MIN + (GRID_MAX - GRID_MIN) * i / (N_LINES - 1) for i in range(N_LINES)]


def sample_mapped_line(const_val, is_horizontal, lam):
    """Sample a grid line through the Joukowski map, split at poles and large jumps.

    Returns a list of segments; each segment is a list of (x, y) screen points.
    is_horizontal=True → constant imaginary part (const_val), varying real part.
    """
    segments = []
    current = []
    last_pt = None

    for i in range(N_SAMPLES):
        t = GRID_MIN + (GRID_MAX - GRID_MIN) * i / (N_SAMPLES - 1)
        z = (t, const_val) if is_horizontal else (const_val, t)
        w = joukowski(z, lam)
        if w is None or cmag(w) > MAX_MAG:
            if current:
                segments.append(current)
                current = []
            last_pt = None
            continue
        s = to_screen(w)
        if last_pt and (abs(s[0] - last_pt[0]) > JUMP_THRESH or
                        abs(s[1] - last_pt[1]) > JUMP_THRESH):
            if current:
                segments.append(current)
                current = []
        current.append(s)
        last_pt = s

    if current:
        segments.append(current)
    return segments


def polyline_points(pts):
    """Format a list of (x, y) tuples as an SVG points string."""
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def generate_svg():
    """Build the thumbnail SVG: light base grid + Joukowski-mapped bold lines."""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">',
        f'<rect width="{SIZE}" height="{SIZE}" fill="#0d0d18"/>',
    ]

    positions = line_positions()

    # Light base grid (w-plane, identity)
    for v in positions:
        y = CY - v * SCALE
        x0 = CX + GRID_MIN * SCALE
        x1 = CX + GRID_MAX * SCALE
        parts.append(
            f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" '
            f'stroke="rgba(255,130,160,0.18)" stroke-width="0.4"/>'
        )
        x = CX + v * SCALE
        y0 = CY - GRID_MAX * SCALE
        y1 = CY - GRID_MIN * SCALE
        parts.append(
            f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}" '
            f'stroke="rgba(100,190,255,0.18)" stroke-width="0.4"/>'
        )

    # Joukowski-mapped horizontal lines (rose/coral)
    for v in positions:
        for seg in sample_mapped_line(v, True, LAM):
            if len(seg) >= 2:
                parts.append(
                    f'<polyline points="{polyline_points(seg)}" fill="none" '
                    f'stroke="rgba(255,100,140,0.75)" stroke-width="1.2" '
                    f'stroke-linejoin="round" stroke-linecap="round"/>'
                )

    # Joukowski-mapped vertical lines (sky blue)
    for v in positions:
        for seg in sample_mapped_line(v, False, LAM):
            if len(seg) >= 2:
                parts.append(
                    f'<polyline points="{polyline_points(seg)}" fill="none" '
                    f'stroke="rgba(80,195,255,0.75)" stroke-width="1.2" '
                    f'stroke-linejoin="round" stroke-linecap="round"/>'
                )

    parts.append('</svg>')
    return '\n'.join(parts)


if __name__ == "__main__":
    svg = generate_svg()
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg):,} bytes)")
