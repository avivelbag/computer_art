"""Generate a static SVG thumbnail for Piece 129 — Ghost Frequencies: A Moiré Study.

The SVG renders two concentric ring systems at a fixed offset, using
CSS mix-blend-mode:difference on the second group so that where both
ring systems coincide the pixel cancels to black — the moiré fringe.
"""
import math
import pathlib

SIZE = 480
CX = SIZE / 2
CY = SIZE / 2
RING_SPACING = 10
LINE_WIDTH = 1.2
BG_COLOR = "#0d0d0d"
RING_COLOR = "#ffffff"
# Fixed offset chosen to place the moiré eye clearly in the frame
B_OFFSET_X = 30
B_OFFSET_Y = 15


def max_radius() -> int:
    """Radius sufficient to cover the full canvas diagonal from any offset center."""
    return int(math.ceil(math.sqrt(SIZE ** 2 + SIZE ** 2))) + RING_SPACING


def ring_circles(cx: float, cy: float, max_r: int, spacing: int) -> list:
    """Return SVG <circle> element strings for concentric rings up to max_r."""
    elements = []
    for r in range(spacing, max_r + 1, spacing):
        elements.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" '
            f'fill="none" stroke="{RING_COLOR}" stroke-width="{LINE_WIDTH}"/>'
        )
    return elements


def generate_svg() -> str:
    """Build the SVG thumbnail string showing the moiré beat pattern.

    Ring system A is centered at (CX, CY).  Ring system B is offset by
    (B_OFFSET_X, B_OFFSET_Y) and drawn into a group with
    mix-blend-mode:difference so overlapping rings cancel to black.
    """
    max_r = max_radius()
    cx_b = CX + B_OFFSET_X
    cy_b = CY + B_OFFSET_Y

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">',
        f'<rect width="{SIZE}" height="{SIZE}" fill="{BG_COLOR}"/>',
        '<g id="ring-a">',
    ]
    parts.extend(ring_circles(CX, CY, max_r, RING_SPACING))
    parts.append('</g>')

    # The inner <rect> paints all non-ring pixels inside this group the same
    # dark color as the backdrop so difference compositing works correctly:
    # |backdrop_ring(255) - group_ring(255)| = 0 (dark interference band).
    parts.append('<g id="ring-b" style="mix-blend-mode:difference">')
    parts.append(f'<rect width="{SIZE}" height="{SIZE}" fill="{BG_COLOR}"/>')
    parts.extend(ring_circles(cx_b, cy_b, max_r, RING_SPACING))
    parts.append('</g>')
    parts.append('</svg>')
    return '\n'.join(parts)


if __name__ == "__main__":
    svg = generate_svg()
    out = pathlib.Path(__file__).parent / "thumbnail.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg):,} bytes)")
