"""Generate a static thumbnail SVG for Piece 94 — Penrose P3 tiling.

Uses substitution deflation starting from a 10-triangle sun, producing
Robinson triangles that fill the thumbnail canvas. Thick rhombus halves
(acute triangles, type 'A') use terracotta; thin rhombus halves (obtuse
triangles, type 'B') use dusty sage. Palette evokes Islamic tilework.
"""

import cmath
import math
import pathlib

PHI = (1 + math.sqrt(5)) / 2

BG_COLOR = "#f5f0e8"
THICK_COLOR = "#c84b31"
THIN_COLOR = "#7a9e7e"
STROKE_COLOR = "#3d2b1f"

THUMB_SIZE = 400
THUMB_GENERATIONS = 4


def make_sun(radius: float) -> list[tuple]:
    """Return 10 acute Robinson triangles arranged in a decagonal sun around the origin.

    Each triangle has its 36-degree apex at the origin; B and C lie on a
    circle of the given radius. Alternating chirality ensures adjacent
    triangles share edges correctly.
    """
    tris = []
    for i in range(10):
        B = cmath.rect(radius, (2 * i - 1) * math.pi / 10)
        C = cmath.rect(radius, (2 * i + 1) * math.pi / 10)
        if i % 2 == 0:
            B, C = C, B
        tris.append(("A", 0 + 0j, B, C))
    return tris


def deflate(tris: list[tuple]) -> list[tuple]:
    """Apply one P3 Penrose substitution deflation step.

    Convention: first vertex is always the special apex.

    'A' (acute, 36-degree apex): P = A + (B-A)/phi
        yields acute(C, P, B) and obtuse(P, C, A).

    'B' (obtuse, 108-degree apex): Q = B+(A-B)/phi, R = B+(C-B)/phi
        yields obtuse(R,C,A), obtuse(Q,R,B), and acute(R,Q,A).

    Each step scales edge lengths by 1/phi.
    """
    out = []
    for kind, A, B, C in tris:
        if kind == "A":
            P = A + (B - A) / PHI
            out.append(("A", C, P, B))
            out.append(("B", P, C, A))
        else:
            Q = B + (A - B) / PHI
            R = B + (C - B) / PHI
            out.append(("B", R, C, A))
            out.append(("B", Q, R, B))
            out.append(("A", R, Q, A))
    return out


def _fmt(v: float) -> str:
    return f"{v:.1f}"


def _pts(A: complex, B: complex, C: complex, cx: float, cy: float) -> str:
    """Return SVG polygon points string for three vertices, translated to viewport centre."""
    return (
        f"{_fmt(A.real + cx)},{_fmt(A.imag + cy)} "
        f"{_fmt(B.real + cx)},{_fmt(B.imag + cy)} "
        f"{_fmt(C.real + cx)},{_fmt(C.imag + cy)}"
    )


def _render(tris: list[tuple], size: int, stroke_width: str) -> str:
    """Render Robinson triangles as SVG polygon elements grouped by type."""
    cx = cy = size / 2
    acute_elems: list[str] = []
    obtuse_elems: list[str] = []
    for kind, A, B, C in tris:
        p = _pts(A, B, C, cx, cy)
        elem = f'<polygon points="{p}"/>'
        if kind == "A":
            acute_elems.append(elem)
        else:
            obtuse_elems.append(elem)

    g_thick = (
        f'<g fill="{THICK_COLOR}" stroke="{STROKE_COLOR}" '
        f'stroke-width="{stroke_width}" stroke-linejoin="round">\n'
        + "\n".join(acute_elems)
        + "\n</g>"
    )
    g_thin = (
        f'<g fill="{THIN_COLOR}" stroke="{STROKE_COLOR}" '
        f'stroke-width="{stroke_width}" stroke-linejoin="round">\n'
        + "\n".join(obtuse_elems)
        + "\n</g>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size}" width="{size}" height="{size}">\n'
        f'<rect width="{size}" height="{size}" fill="{BG_COLOR}"/>\n'
        f'{g_thick}\n{g_thin}\n</svg>'
    )


def generate_svg(generations: int = THUMB_GENERATIONS, size: int = THUMB_SIZE) -> str:
    """Return a complete SVG string of the Penrose P3 tiling thumbnail.

    Builds the tiling by deflating a 10-triangle sun `generations` times.
    Acute-triangle halves use THICK_COLOR (terracotta); obtuse halves use
    THIN_COLOR (dusty sage). The two groups are written as separate <g>
    elements so fill and stroke attributes are not repeated per polygon.
    """
    tris = make_sun(size * 0.52)
    for _ in range(generations):
        tris = deflate(tris)
    return _render(tris, size, "0.8")


def main() -> None:
    """Write thumbnail.svg next to this script."""
    here = pathlib.Path(__file__).parent
    svg = generate_svg()
    (here / "thumbnail.svg").write_text(svg)
    print(f"thumbnail.svg: {len(svg.encode()):,} bytes  ({svg.count('<polygon')} triangles)")


if __name__ == "__main__":
    main()
