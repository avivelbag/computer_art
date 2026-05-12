"""Generate a P3 Penrose tiling (rhombus variant) via substitution deflation."""

import cmath
import math
import pathlib

PHI = (1 + math.sqrt(5)) / 2

THICK_COLOR = "#2d1b69"
THIN_COLOR = "#e8b84b"
STROKE_COLOR = "#f8f4ec"
BG_COLOR = "#0f0a1e"

SIZE = 800
GENERATIONS = 6
THUMB_SIZE = 400
THUMB_GENERATIONS = 4


def make_sun(radius: float) -> list[tuple]:
    """Return 10 acute Robinson triangles arranged in a decagonal sun around the origin.

    Each triangle has its 36° apex at the origin; B and C lie on a circle of the given
    radius. Alternating chirality ensures adjacent triangles share edges correctly.
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
    """Apply one P3 Penrose deflation step, returning the next generation of triangles.

    Convention: first vertex is always the special apex.
      'A' (acute, 36° apex): P = A + (B-A)/phi
          → acute(C, P, B) with apex C  +  obtuse(P, C, A) with apex P
      'B' (obtuse, 108° apex): Q = B+(A-B)/phi, R = B+(C-B)/phi
          → obtuse(R,C,A) + obtuse(Q,R,B) + acute(R,Q,A) with respective apices

    Each deflation scales triangle edge lengths by 1/phi.
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
    """Render triangles as SVG polygon elements grouped by type for compact output."""
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


def generate_svg(generations: int = GENERATIONS, size: int = SIZE) -> str:
    """Generate a self-contained SVG of a P3 Penrose tiling.

    Builds the tiling by deflating a 10-triangle sun `generations` times.
    Acute triangles (half of thick rhombi) use THICK_COLOR;
    obtuse triangles (half of thin rhombi) use THIN_COLOR.
    Polygons are grouped by type so fill/stroke attributes are written once.
    """
    tris = make_sun(size * 0.52)
    for _ in range(generations):
        tris = deflate(tris)
    return _render(tris, size, "0.5")


def generate_thumbnail(
    size: int = THUMB_SIZE, generations: int = THUMB_GENERATIONS
) -> str:
    """Generate a smaller thumbnail SVG using fewer deflation generations."""
    tris = make_sun(size * 0.52)
    for _ in range(generations):
        tris = deflate(tris)
    return _render(tris, size, "0.8")


def main() -> None:
    """Write piece.svg and thumbnail.svg next to this script."""
    here = pathlib.Path(__file__).parent
    piece = generate_svg()
    thumb = generate_thumbnail()
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    print(f"piece.svg:     {len(piece.encode()):,} bytes  ({piece.count('<polygon')} triangles)")
    print(f"thumbnail.svg: {len(thumb.encode()):,} bytes  ({thumb.count('<polygon')} triangles)")


if __name__ == "__main__":
    main()
