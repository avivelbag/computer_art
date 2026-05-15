"""Generate a Delaunay triangulation stained-glass SVG via Bowyer-Watson (pure stdlib)."""

import pathlib
import random

SEED = 42
N_POINTS = 400
WIDTH = 800
HEIGHT = 800
STROKE_WIDTH = 0.5
STROKE_COLOR = "#1a1214"

# Rose → Amber → Slate (3-stop gradient, RGB tuples)
GRADIENT = [
    (220, 100, 130),  # rose
    (210, 148, 55),   # amber
    (90, 110, 145),   # slate
]

BG_COLOR = "#0f0e12"


def circumcircle(ax, ay, bx, by, cx, cy):
    """Return (ux, uy, r_squared) of the circumcircle of triangle ABC.

    Derived from the perpendicular-bisector intersection formula. The
    circumcenter (ux, uy) is equidistant from all three vertices; r_squared
    is the squared circumradius so we can compare distances without sqrt.
    Returns None when the three points are collinear (degenerate triangle).
    """
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-10:
        return None
    a2 = ax * ax + ay * ay
    b2 = bx * bx + by * by
    c2 = cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    r2 = (ax - ux) ** 2 + (ay - uy) ** 2
    return ux, uy, r2


def bowyer_watson(points, width, height):
    """Compute the Delaunay triangulation of points using the Bowyer-Watson algorithm.

    Algorithm outline:
    1. Seed with a super-triangle large enough to contain every input point.
    2. For each point p, find all "bad" triangles whose circumcircle contains p.
    3. Identify the boundary polygon of the cavity left after removing the bad
       triangles (edges shared by exactly one bad triangle).
    4. Re-fill the cavity by connecting p to every boundary edge.
    5. After all points are inserted, discard any triangle that shares a vertex
       with the super-triangle.

    Returns a list of (i, j, k) index triples into `points`.
    """
    if len(points) < 3:
        return []

    # Super-triangle vertices appended after real points
    M = max(width, height) * 3
    super_pts = [(-M, -M), (3 * M, -M), (-M, 3 * M)]
    pts = list(points) + super_pts
    n_real = len(points)
    sup = (n_real, n_real + 1, n_real + 2)

    triangles = {sup}

    for i, (px, py) in enumerate(points):
        # Find bad triangles: circumcircle strictly contains the new point.
        # The -1e-10 tolerance guards against precision-induced false exclusions.
        bad = set()
        for tri in triangles:
            ax, ay = pts[tri[0]]
            bx, by = pts[tri[1]]
            cx, cy = pts[tri[2]]
            cc = circumcircle(ax, ay, bx, by, cx, cy)
            if cc is None:
                continue
            ux, uy, r2 = cc
            if (px - ux) ** 2 + (py - uy) ** 2 < r2 - 1e-10:
                bad.add(tri)

        # Collect edges on the boundary of the removed cavity.
        # An edge is a boundary edge iff it belongs to exactly one bad triangle.
        boundary = []
        for tri in bad:
            for edge in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
                shared = any(
                    edge[0] in other and edge[1] in other
                    for other in bad
                    if other != tri
                )
                if not shared:
                    boundary.append(edge)

        triangles -= bad

        for e0, e1 in boundary:
            triangles.add((i, e0, e1))

    return [tri for tri in triangles if all(v < n_real for v in tri)]


def lerp3(t, stops):
    """Linearly interpolate through a 3-stop gradient at parameter t ∈ [0, 1].

    t=0 → stops[0], t=0.5 → stops[1], t=1 → stops[2].
    Values outside [0, 1] are clamped. Returns an integer RGB tuple.
    """
    t = max(0.0, min(1.0, t))
    if t <= 0.5:
        a, b, s = stops[0], stops[1], t * 2
    else:
        a, b, s = stops[1], stops[2], (t - 0.5) * 2
    return tuple(int(a[k] + (b[k] - a[k]) * s) for k in range(3))


def generate_svg(
    n_points: int = N_POINTS,
    width: int = WIDTH,
    height: int = HEIGHT,
    seed: int = SEED,
    gradient: list = None,
    stroke_width: float = STROKE_WIDTH,
    stroke_color: str = STROKE_COLOR,
    bg_color: str = BG_COLOR,
) -> str:
    """Generate a self-contained Delaunay triangulation SVG with stained-glass coloring.

    Scatters n_points random seeds inside the canvas with a small margin to
    avoid edge-clipping artifacts, computes the Bowyer-Watson triangulation,
    then colors each triangle by mapping its centroid through a 3-stop gradient
    (rose → amber → slate). A small Gaussian jitter on t gives organic palette
    variation without losing overall gradient discipline.

    Returns the SVG source as a string.
    """
    if gradient is None:
        gradient = GRADIENT

    rng = random.Random(seed)
    margin = 20
    points = [
        (rng.uniform(margin, width - margin), rng.uniform(margin, height - margin))
        for _ in range(n_points)
    ]

    triangles = bowyer_watson(points, width, height)

    polygons = []
    for i, j, k in triangles:
        ax, ay = points[i]
        bx, by = points[j]
        cx, cy = points[k]

        centroid_x = (ax + bx + cx) / 3
        centroid_y = (ay + by + cy) / 3

        # Diagonal gradient: top-left (rose) → bottom-right (slate) via amber mid.
        # Gaussian jitter breaks the strict linearity for an organic stained-glass feel.
        t = (centroid_x / width + centroid_y / height) / 2
        t += rng.gauss(0, 0.04)
        t = max(0.0, min(1.0, t))

        r, g, b = lerp3(t, gradient)
        fill = f"rgb({r},{g},{b})"
        pts_str = f"{ax:.1f},{ay:.1f} {bx:.1f},{by:.1f} {cx:.1f},{cy:.1f}"
        polygons.append(
            f'  <polygon points="{pts_str}" fill="{fill}" '
            f'stroke="{stroke_color}" stroke-width="{stroke_width}" '
            f'stroke-linejoin="round"/>'
        )

    body = "\n".join(polygons)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
        f'  <rect width="{width}" height="{height}" fill="{bg_color}"/>\n'
        f"{body}\n</svg>"
    )


def main() -> None:
    """Write piece.svg (800×800) and thumbnail.svg (400×400) next to this script."""
    here = pathlib.Path(__file__).parent
    piece = generate_svg()
    # Thumbnail uses a 400×400 canvas with fewer points for a lighter file.
    thumb = generate_svg(n_points=200, width=400, height=400)
    (here / "piece.svg").write_text(piece)
    (here / "thumbnail.svg").write_text(thumb)
    print(f"piece.svg: {len(piece):,} bytes | thumbnail.svg: {len(thumb):,} bytes")


if __name__ == "__main__":
    main()
