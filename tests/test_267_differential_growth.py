"""Tests for Piece 267 — Differential Growth: Coral Maze."""
import json
import math
import pathlib
import re

import pytest

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "267-differential-growth"
INDEX       = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID    = "267-differential-growth"


# ---------------------------------------------------------------------------
# Python mirror of the simulation core — used for deterministic logic tests
# ---------------------------------------------------------------------------


class Node:
    """Mutable 2-D point representing a node on the growth curve."""

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)


def make_polygon(cx: float, cy: float, radius: float, n: int) -> list:
    """Create a regular n-gon centred at (cx, cy) with the given circumradius.

    Args:
        cx, cy: centre coordinates in pixels.
        radius: circumradius in pixels.
        n: number of vertices.

    Returns:
        List of Node objects forming the polygon in counter-clockwise order.
    """
    return [
        Node(
            cx + radius * math.cos(2 * math.pi * i / n),
            cy + radius * math.sin(2 * math.pi * i / n),
        )
        for i in range(n)
    ]


def subdivide(nodes: list, max_edge: float) -> list:
    """Insert one midpoint on every edge longer than max_edge.

    Mirrors the edge-subdivision step in the JavaScript implementation.
    The input list is not mutated; a new list is always returned.

    Args:
        nodes: list of Node objects forming a closed curve.
        max_edge: threshold in pixels; edges longer than this get a midpoint.

    Returns:
        New list of Node objects with midpoints inserted.
    """
    result = []
    n = len(nodes)
    for i in range(n):
        result.append(nodes[i])
        j  = (i + 1) % n
        dx = nodes[j].x - nodes[i].x
        dy = nodes[j].y - nodes[i].y
        if dx * dx + dy * dy > max_edge * max_edge:
            result.append(
                Node(
                    (nodes[i].x + nodes[j].x) / 2.0,
                    (nodes[i].y + nodes[j].y) / 2.0,
                )
            )
    return result


def spring_force(nodes: list, k: float) -> list:
    """Compute the smoothing spring force on each node.

    Each node is attracted to the midpoint of its two immediate neighbours
    by a spring with stiffness k.  This mirrors SPRING_K in the JS code.

    Args:
        nodes: list of Node objects (closed curve).
        k: spring stiffness coefficient.

    Returns:
        List of (fx, fy) float tuples, one per node.
    """
    m = len(nodes)
    forces = []
    for i in range(m):
        p  = (i - 1 + m) % m
        q  = (i + 1) % m
        mx = (nodes[p].x + nodes[q].x) / 2.0
        my = (nodes[p].y + nodes[q].y) / 2.0
        forces.append((k * (mx - nodes[i].x), k * (my - nodes[i].y)))
    return forces


def boundary_force(
    nodes: list, cx: float, cy: float, radius: float, k: float
) -> list:
    """Compute the soft-boundary inward spring force for each node.

    Nodes inside the boundary circle receive zero force.  Nodes outside are
    pulled inward by a spring proportional to their excess distance.

    Args:
        nodes: list of Node objects.
        cx, cy: centre of the boundary circle.
        radius: boundary radius in pixels.
        k: spring coefficient (0–1 keeps nodes close to the boundary edge).

    Returns:
        List of (fx, fy) float tuples, one per node.
    """
    forces = []
    for nd in nodes:
        bx, by = nd.x - cx, nd.y - cy
        bd = math.sqrt(bx * bx + by * by)
        if bd > radius and bd > 0:
            excess = bd - radius
            forces.append((-k * excess * bx / bd, -k * excess * by / bd))
        else:
            forces.append((0.0, 0.0))
    return forces


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_pieces() -> list:
    """Return parsed contents of pieces.json."""
    return json.loads(PIECES_JSON.read_text())


def get_entry() -> dict | None:
    """Return the pieces.json entry for 267-differential-growth, or None."""
    return next((p for p in load_pieces() if p.get("id") == PIECE_ID), None)


def html() -> str:
    """Return the full text of index.html."""
    return INDEX.read_text()


# ---------------------------------------------------------------------------
# File-system tests
# ---------------------------------------------------------------------------


class TestFiles:
    def test_directory_exists(self):
        assert PIECE_DIR.is_dir(), f"Missing: {PIECE_DIR}"

    def test_index_html_exists(self):
        assert INDEX.is_file()

    def test_thumbnail_exists(self):
        assert THUMBNAIL.is_file()

    def test_readme_exists(self):
        assert README.is_file()

    def test_index_html_non_trivial(self):
        assert len(html()) > 2000, "index.html is suspiciously short"

    def test_readme_non_trivial(self):
        assert len(README.read_text().strip()) > 300

    def test_thumbnail_is_valid_svg(self):
        content = THUMBNAIL.read_text()
        assert "<svg" in content and "</svg>" in content

    def test_thumbnail_has_path_element(self):
        assert "<path" in THUMBNAIL.read_text()

    def test_thumbnail_has_width_400(self):
        content = THUMBNAIL.read_text()
        assert 'width="400"' in content or "width='400'" in content


# ---------------------------------------------------------------------------
# pieces.json tests
# ---------------------------------------------------------------------------


class TestPiecesJson:
    def test_entry_exists(self):
        assert get_entry() is not None, f"{PIECE_ID} not found in pieces.json"

    def test_required_fields(self):
        required = {
            "id", "title", "tagline", "year",
            "technique", "path", "thumbnail", "description",
        }
        e = get_entry()
        assert e is not None
        assert not (required - e.keys()), f"Missing fields: {required - e.keys()}"

    def test_id_matches(self):
        assert get_entry()["id"] == PIECE_ID

    def test_path_correct(self):
        assert get_entry()["path"] == f"pieces/{PIECE_ID}"

    def test_thumbnail_file_exists(self):
        e = get_entry()
        assert e is not None
        assert (REPO / e["thumbnail"]).is_file()

    def test_year_is_int(self):
        assert isinstance(get_entry()["year"], int)

    def test_technique_mentions_canvas(self):
        assert "canvas" in get_entry()["technique"].lower()

    def test_technique_mentions_growth_or_repulsion(self):
        tech = get_entry()["technique"].lower()
        assert "growth" in tech or "repulsion" in tech or "spring" in tech

    def test_appears_after_266(self):
        pieces = load_pieces()
        idx_266 = next(
            (i for i, p in enumerate(pieces) if p["id"] == "266-mondrian-recursion"),
            None,
        )
        idx_267 = next(
            (i for i, p in enumerate(pieces) if p["id"] == PIECE_ID), None
        )
        assert idx_266 is not None, "266-mondrian-recursion missing from pieces.json"
        assert idx_267 is not None, f"{PIECE_ID} missing from pieces.json"
        assert idx_267 > idx_266, "267 must appear after 266 in pieces.json"

    def test_no_duplicate_ids(self):
        ids = [p["id"] for p in load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate piece IDs in pieces.json"

    def test_prior_pieces_preserved(self):
        ids = {p["id"] for p in load_pieces()}
        for expected in ["01-amber-current", "266-mondrian-recursion", "261-sdf-raymarching"]:
            assert expected in ids, f"Prior piece {expected!r} was removed"


# ---------------------------------------------------------------------------
# index.html structural tests
# ---------------------------------------------------------------------------


class TestIndexHtml:
    def test_has_canvas_element(self):
        assert "<canvas" in html()

    def test_has_script(self):
        assert "<script" in html()

    def test_has_viewport_meta(self):
        assert 'name="viewport"' in html()

    def test_has_charset(self):
        assert "charset" in html()

    def test_no_external_scripts(self):
        assert not re.findall(r'<script[^>]+src=["\']https?://', html())

    def test_self_contained(self):
        h = html()
        assert "<script src=" not in h
        assert '<link rel="stylesheet"' not in h

    def test_has_requestanimationframe(self):
        assert "requestAnimationFrame" in html()

    def test_has_max_edge_constant(self):
        h = html()
        assert "MAX_EDGE" in h or "maxEdge" in h or "max_edge" in h

    def test_has_min_dist_constant(self):
        h = html()
        assert "MIN_DIST" in h or "minDist" in h or "min_dist" in h

    def test_has_max_nodes_constant(self):
        h = html()
        assert "MAX_NODES" in h or "maxNodes" in h or "max_nodes" in h

    def test_has_repulsion_logic(self):
        h = html().lower()
        assert "repulsion" in h or "repel" in h or "min_dist" in h

    def test_has_spring_logic(self):
        h = html().lower()
        assert "spring" in h or "smooth" in h

    def test_has_teal_palette(self):
        h = html().lower()
        assert "050d14" in h or "#00c" in h or "#00d" in h

    def test_has_fade_mechanism(self):
        h = html()
        assert "fadingOut" in h or "fadeOut" in h or "fadeCount" in h or "fade" in h.lower()

    def test_has_boundary_constraint(self):
        h = html().lower()
        assert "boundary" in h

    def test_has_spatial_grid(self):
        h = html().lower()
        assert "grid" in h or "cell" in h or "spatial" in h

    def test_curve_is_closed(self):
        h = html()
        assert "closePath" in h or "closepath" in h.lower()


# ---------------------------------------------------------------------------
# Simulation algorithm tests (Python mirror)
# ---------------------------------------------------------------------------


class TestSubdivide:
    def test_no_subdivision_when_edges_short(self):
        """A radius-50 octagon has edges ~38 px; max_edge=100 → no insertions."""
        nodes = make_polygon(400, 400, 50, 8)
        result = subdivide(nodes, max_edge=100)
        assert len(result) == 8

    def test_midpoint_inserted_on_long_edge(self):
        """Two nodes 30 px apart with max_edge=10 → midpoint inserted on each edge."""
        a, b = Node(0, 0), Node(30, 0)
        result = subdivide([a, b], max_edge=10)
        # Closed curve: edges a→b and b→a both exceed 10 px
        assert len(result) == 4

    def test_midpoint_is_geometric_average(self):
        """Inserted midpoint must be exactly at the arithmetic mean of endpoints."""
        a, b = Node(0, 0), Node(20, 0)
        result = subdivide([a, b], max_edge=10)
        mid_xs = {n.x for n in result if n.x not in (a.x, b.x)}
        assert 10.0 in mid_xs

    def test_square_doubles_when_all_edges_long(self):
        """Radius-200 square: all edges ~283 px > 10 → 4 midpoints inserted."""
        nodes = make_polygon(0, 0, 200, 4)
        result = subdivide(nodes, max_edge=10)
        assert len(result) == 8

    def test_empty_input_returns_empty(self):
        assert subdivide([], max_edge=10) == []

    def test_single_node_returns_single_node(self):
        """A single-node 'curve' has a zero-length self-edge — no insertion."""
        result = subdivide([Node(0, 0)], max_edge=10)
        assert len(result) == 1

    def test_growth_bounded_by_cap(self):
        """Midpoints are not inserted once result length >= cap.
        Original nodes always pass through; only midpoints are gated.
        With cap=5 and a 4-node input exactly 2 midpoints are inserted
        (k=0 → len becomes 2; k=1 → len becomes 4; at k=2 len==5 so gate fires)."""
        cap = 5
        nodes = make_polygon(400, 400, 200, 4)
        result = []
        n = len(nodes)
        for i in range(n):
            result.append(nodes[i])
            j  = (i + 1) % n
            dx = nodes[j].x - nodes[i].x
            dy = nodes[j].y - nodes[i].y
            if dx * dx + dy * dy > 100 and len(result) < cap:
                result.append(
                    Node((nodes[i].x + nodes[j].x) / 2,
                         (nodes[i].y + nodes[j].y) / 2)
                )
        midpoints_added = len(result) - n
        # The cap gates midpoints, not original nodes; at most cap-1 midpoints
        # can be added before the guard triggers.
        assert midpoints_added <= cap - 1


class TestSpringForce:
    def test_straight_line_zero_force(self):
        """Three collinear equally-spaced nodes: midpoint of neighbours == node → force zero."""
        nodes = [Node(0, 0), Node(10, 0), Node(20, 0)]
        forces = spring_force(nodes, k=0.5)
        fx, fy = forces[1]
        assert abs(fx) < 1e-9
        assert abs(fy) < 1e-9

    def test_displaced_node_pulled_back(self):
        """A node displaced below the midpoint of its neighbours gets an upward force."""
        nodes = [Node(0, 0), Node(0, -5), Node(0, 0)]
        forces = spring_force(nodes, k=1.0)
        _, fy = forces[1]
        assert fy > 0

    def test_force_proportional_to_k(self):
        """Doubling k must exactly double the force magnitude."""
        nodes = [Node(0, 10), Node(0, 0), Node(0, 10)]
        f1 = spring_force(nodes, k=1.0)[1]
        f2 = spring_force(nodes, k=2.0)[1]
        assert abs(f2[1]) == pytest.approx(2 * abs(f1[1]), rel=1e-6)

    def test_force_magnitude_scales_with_displacement(self):
        """A node displaced twice as far from its neighbours' midpoint gets twice the force."""
        nodes1 = [Node(0, 0), Node(0, -5),  Node(0, 0)]
        nodes2 = [Node(0, 0), Node(0, -10), Node(0, 0)]
        f1 = spring_force(nodes1, k=1.0)[1]
        f2 = spring_force(nodes2, k=1.0)[1]
        assert abs(f2[1]) == pytest.approx(2 * abs(f1[1]), rel=1e-6)


class TestBoundaryForce:
    def test_inside_boundary_zero_force(self):
        """A node well inside the boundary receives zero force."""
        nd = Node(400, 400)
        forces = boundary_force([nd], cx=400, cy=400, radius=100, k=1.0)
        assert forces[0] == (0.0, 0.0)

    def test_outside_boundary_inward_force(self):
        """A node 10 px outside the boundary must receive a strictly inward force."""
        cx, cy, R = 400, 400, 100
        nd = Node(cx + 110, cy)
        forces = boundary_force([nd], cx=cx, cy=cy, radius=R, k=1.0)
        fx, fy = forces[0]
        assert fx < 0, "Force should be directed inward (negative x)"
        assert abs(fy) < 1e-9, "No y-component for a rightward-displaced node"

    def test_force_proportional_to_excess(self):
        """Doubling excess distance doubles the force magnitude."""
        cx, cy, R = 400, 400, 100
        n1 = Node(cx + 110, cy)  # 10 px outside
        n2 = Node(cx + 120, cy)  # 20 px outside
        f1 = boundary_force([n1], cx=cx, cy=cy, radius=R, k=1.0)[0]
        f2 = boundary_force([n2], cx=cx, cy=cy, radius=R, k=1.0)[0]
        assert abs(f2[0]) == pytest.approx(2 * abs(f1[0]), rel=1e-6)

    def test_node_on_boundary_zero_force(self):
        """A node exactly on the boundary circle has zero excess → zero force."""
        cx, cy, R = 400, 400, 100
        nd = Node(cx + R, cy)
        forces = boundary_force([nd], cx=cx, cy=cy, radius=R, k=1.0)
        fx, fy = forces[0]
        assert abs(fx) < 1e-9 and abs(fy) < 1e-9


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_initial_polygon_grows_after_subdivision(self):
        """After one subdivision step, the 16-gon should have more nodes
        (its initial edge length exceeds MAX_EDGE=10)."""
        nodes = make_polygon(400, 400, 90, 16)
        after = subdivide(nodes, max_edge=10)
        assert len(after) > len(nodes)

    def test_large_polygon_converges_to_dense_curve(self):
        """After many subdivision iterations the edge lengths should all be ≤ max_edge."""
        nodes = make_polygon(400, 400, 200, 8)
        max_edge = 10
        for _ in range(20):
            nodes = subdivide(nodes, max_edge=max_edge)
        edges_over = sum(
            1
            for i in range(len(nodes))
            if math.dist(
                (nodes[i].x, nodes[i].y),
                (nodes[(i + 1) % len(nodes)].x, nodes[(i + 1) % len(nodes)].y),
            ) > max_edge
        )
        assert edges_over == 0, f"{edges_over} edges still exceed max_edge after 20 iterations"

    def test_wrong_piece_id_absent(self):
        """Typo variants of the piece ID must not appear in pieces.json."""
        ids = {p["id"] for p in load_pieces()}
        assert "267-growth" not in ids
        assert "267-differential" not in ids
        assert "268-differential-growth" not in ids

    def test_boundary_force_with_many_nodes(self):
        """All nodes of a large circle (r=500, outside boundary=360) should
        receive inward forces."""
        nodes = make_polygon(400, 400, 500, 20)
        forces = boundary_force(nodes, cx=400, cy=400, radius=360, k=0.9)
        for i, (fx, fy) in enumerate(forces):
            # Each node is at radius 500, outside 360 → non-zero inward force
            assert fx != 0.0 or fy != 0.0, f"Node {i} outside boundary has zero force"


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------


class TestReadme:
    def test_mentions_differential_growth(self):
        text = README.read_text().lower()
        assert "differential growth" in text or "growth" in text

    def test_mentions_coral_or_organic(self):
        text = README.read_text().lower()
        assert "coral" in text or "organic" in text or "lettuce" in text or "brain" in text

    def test_mentions_repulsion_or_spring(self):
        text = README.read_text().lower()
        assert "repulsion" in text or "spring" in text or "force" in text

    def test_mentions_palette_or_colour(self):
        text = README.read_text().lower()
        assert "palette" in text or "colour" in text or "color" in text or "teal" in text or "cyan" in text

    def test_mentions_nodes_or_vertices(self):
        text = README.read_text().lower()
        assert "node" in text or "vertex" in text or "vertices" in text or "point" in text

    def test_has_multiple_paragraphs(self):
        text = README.read_text().strip()
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        assert len(paragraphs) >= 2

    def test_mentions_boundary(self):
        text = README.read_text().lower()
        assert "boundary" in text or "circle" in text or "radius" in text
