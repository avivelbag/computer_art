"""Generate a Gothic rose window SVG with D12 dihedral symmetry."""

import math
import pathlib

CX = CY = 400
LEAD = "#222222"
LEAD_W = 2

RUBY    = "#8b0000"
COBALT  = "#1a237e"
GOLD    = "#f9a825"
EMERALD = "#1b5e20"
VIOLET  = "#4a148c"
AMBER   = "#e65100"

R_CENTER              = 60
R1_IN, R1_OUT         = 60,  160
R2_IN, R2_OUT         = 160, 280
R3_IN, R3_MID, R3_OUT = 280, 320, 400

# Ring 1: 12 petals, alternating ruby/cobalt
RING1_COLORS = [RUBY, COBALT]
# Ring 2: 24 lobes, cycling through emerald/violet/amber
RING2_COLORS = [EMERALD, VIOLET, AMBER]
# Ring 3 slivers and bodies use a 4-color scheme offset by 2 so sliver ≠ body
RING3_SLIVER = [RUBY, COBALT, GOLD,   EMERALD]
RING3_BODY   = [GOLD, EMERALD, RUBY,  COBALT]


def _pt(r: float, theta: float) -> tuple:
    """Convert polar coords to SVG Cartesian (y-down) relative to (CX, CY)."""
    return (CX + r * math.cos(theta), CY + r * math.sin(theta))


def _f(xy: tuple) -> str:
    return f"{xy[0]:.3f},{xy[1]:.3f}"


def _annular(r1: float, r2: float, a0: float, a1: float) -> str:
    """Return SVG path string for an annular sector.

    Draws clockwise along the inner arc (sweep=1) then counterclockwise along
    the outer arc (sweep=0) to form a filled pie-slice-with-hole shape.
    """
    large = 1 if (a1 - a0) > math.pi else 0
    p_i0 = _pt(r1, a0);  p_i1 = _pt(r1, a1)
    p_o1 = _pt(r2, a1);  p_o0 = _pt(r2, a0)
    return (
        f"M {_f(p_i0)} A {r1:.1f} {r1:.1f} 0 {large} 1 {_f(p_i1)} "
        f"L {_f(p_o1)} A {r2:.1f} {r2:.1f} 0 {large} 0 {_f(p_o0)} Z"
    )


def _lancet(r1: float, r2: float, a0: float, a1: float) -> str:
    """Return SVG path for a Gothic lancet arch shape.

    The base is a circular arc at r1; the two straight sides converge on a
    pointed tip at (r2, sector-mid-angle), mimicking a lancet arch profile.
    Dark gap between adjacent lancet tips is intentional — it reads as the
    mortar/caming between arches.
    """
    a_mid = (a0 + a1) / 2
    large = 1 if (a1 - a0) > math.pi else 0
    p0  = _pt(r1, a0)
    p1  = _pt(r1, a1)
    tip = _pt(r2, a_mid)
    return f"M {_f(p0)} A {r1:.1f} {r1:.1f} 0 {large} 1 {_f(p1)} L {_f(tip)} Z"


def _path(d: str, fill: str) -> str:
    """Return an SVG <path> element with the standard lead stroke."""
    return (
        f'<path d="{d}" fill="{fill}" stroke="{LEAD}" '
        f'stroke-width="{LEAD_W}" stroke-linejoin="round"/>'
    )


def generate_svg(display_size: int = 800) -> str:
    """Generate the rose window SVG as a string.

    Computes geometry on a fixed 800×800 internal grid (viewBox 0 0 800 800)
    and scales only the width/height attributes for display_size.

    Layout:
    - Background: near-black rectangle
    - Center disc (r=60): gold
    - Ring 1 (r 60–160): 12 annular sectors, ruby/cobalt alternating
    - Ring 2 (r 160–280): 24 annular sectors, emerald/violet/amber cycling
    - Ring 3 slivers (r 280–320): 12 full annular sectors, 4-color scheme
    - Ring 3 bodies (r 320–400): 12 lancet arches, 4-color scheme (offset +2)
    - Outer lead ring at r=400 (4 px stroke)

    Adjacent regions within each ring always differ in color: Ring 1 alternates
    2 colors, Ring 2 cycles 3 colors, Ring 3 cycles 4 colors with sliver/body
    offset ensuring no same-color adjacency across the sliver-body boundary.
    """
    els: list = [
        '<rect width="800" height="800" fill="#050508"/>',
        (
            f'<circle cx="{CX}" cy="{CY}" r="{R_CENTER}" fill="{GOLD}" '
            f'stroke="{LEAD}" stroke-width="{LEAD_W}"/>'
        ),
    ]

    step1 = 2 * math.pi / 12
    for i in range(12):
        a0, a1 = i * step1, (i + 1) * step1
        els.append(_path(_annular(R1_IN, R1_OUT, a0, a1), RING1_COLORS[i % 2]))

    step2 = 2 * math.pi / 24
    for i in range(24):
        a0, a1 = i * step2, (i + 1) * step2
        els.append(_path(_annular(R2_IN, R2_OUT, a0, a1), RING2_COLORS[i % 3]))

    step3 = 2 * math.pi / 12
    for i in range(12):
        a0, a1 = i * step3, (i + 1) * step3
        els.append(_path(_annular(R3_IN, R3_MID, a0, a1), RING3_SLIVER[i % 4]))
        els.append(_path(_lancet(R3_MID, R3_OUT, a0, a1), RING3_BODY[i % 4]))

    # Outer lead boundary ring
    els.append(
        f'<circle cx="{CX}" cy="{CY}" r="400" fill="none" '
        f'stroke="{LEAD}" stroke-width="4"/>'
    )

    inner = "\n  ".join(els)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 800 800" '
        f'width="{display_size}" height="{display_size}">\n'
        f'  {inner}\n'
        f'</svg>\n'
    )


def main() -> None:
    """Write piece.svg (800×800) and thumbnail.svg (400×400) next to this script."""
    here = pathlib.Path(__file__).parent
    piece = generate_svg(800)
    thumb = generate_svg(400)
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    print(f"piece.svg: {len(piece):,} bytes | thumbnail.svg: {len(thumb):,} bytes")


if __name__ == "__main__":
    main()
