"""
Tests for pieces/295-lichtenberg-dbm/generate.py.

Covers the happy path described in the acceptance criteria plus edge cases
for the DBM algorithm helpers and SVG output.
"""
import importlib.util
import pathlib
import sys
import math
import random

import pytest

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "295-lichtenberg-dbm"


def load_generate():
    """Import generate.py from the piece directory as a module."""
    spec = importlib.util.spec_from_file_location(
        "generate_lichtenberg", PIECE_DIR / "generate.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return load_generate()


# ── File existence ────────────────────────────────────────────────────────────

class TestFileExists:
    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_py_exists(self):
        assert (PIECE_DIR / "generate.py").is_file()


# ── make_phi ─────────────────────────────────────────────────────────────────

class TestMakePhi:
    def test_edge_cells_are_one(self, gen):
        """Every cell on the grid boundary must be initialised to 1."""
        w, h, cx, cy = 20, 20, 10, 10
        phi = gen.make_phi(w, h, cx, cy)
        for x in range(w):
            assert phi[0 * w + x] == 1.0, f"top edge (x={x})"
            assert phi[(h - 1) * w + x] == 1.0, f"bottom edge (x={x})"
        for y in range(h):
            assert phi[y * w + 0] == 1.0, f"left edge (y={y})"
            assert phi[y * w + (w - 1)] == 1.0, f"right edge (y={y})"

    def test_centre_cell_is_zero(self, gen):
        """The seed cell at (cx, cy) must start at phi = 0."""
        w, h, cx, cy = 20, 20, 10, 10
        phi = gen.make_phi(w, h, cx, cy)
        assert phi[cy * w + cx] == 0.0

    def test_phi_monotonically_increasing_radially(self, gen):
        """Interior phi should increase from centre toward edge (rough check)."""
        w, h = 40, 40
        cx, cy = w // 2, h // 2
        phi = gen.make_phi(w, h, cx, cy)
        # Centre tile
        centre = phi[cy * w + cx]
        # Mid-radius sample
        mid = phi[cy * w + (cx + 10)]
        # Near-edge sample
        near = phi[cy * w + (w - 2)]
        assert centre <= mid <= near

    def test_interior_values_in_unit_interval(self, gen):
        """All phi values must lie in [0, 1]."""
        phi = gen.make_phi(30, 30, 15, 15)
        assert all(0.0 <= v <= 1.0 for v in phi)

    def test_1x1_grid_all_edges(self, gen):
        """A 1×1 grid is all edge — the single cell must be 1."""
        phi = gen.make_phi(1, 1, 0, 0)
        assert phi[0] == 1.0


# ── add_to_tree ───────────────────────────────────────────────────────────────

class TestAddToTree:
    def _make_state(self, gen, w=10, h=10):
        phi = gen.make_phi(w, h, w // 2, h // 2)
        tree = [False] * (w * h)
        frontier: set = set()
        parent_of: dict = {}
        return phi, tree, frontier, parent_of

    def test_cell_marked_as_tree(self, gen):
        w, h = 10, 10
        phi, tree, frontier, parent_of = self._make_state(gen, w, h)
        gen.add_to_tree(5, 5, None, phi, tree, frontier, parent_of, w, h)
        assert tree[5 * w + 5] is True

    def test_phi_set_to_zero(self, gen):
        w, h = 10, 10
        phi, tree, frontier, parent_of = self._make_state(gen, w, h)
        gen.add_to_tree(5, 5, None, phi, tree, frontier, parent_of, w, h)
        assert phi[5 * w + 5] == 0.0

    def test_neighbours_added_to_frontier(self, gen):
        w, h = 10, 10
        phi, tree, frontier, parent_of = self._make_state(gen, w, h)
        gen.add_to_tree(5, 5, None, phi, tree, frontier, parent_of, w, h)
        expected = {4 * w + 5, 6 * w + 5, 5 * w + 4, 5 * w + 6}
        assert expected <= frontier

    def test_cell_itself_not_in_frontier(self, gen):
        w, h = 10, 10
        phi, tree, frontier, parent_of = self._make_state(gen, w, h)
        gen.add_to_tree(5, 5, None, phi, tree, frontier, parent_of, w, h)
        assert (5 * w + 5) not in frontier

    def test_parent_recorded(self, gen):
        w, h = 10, 10
        phi, tree, frontier, parent_of = self._make_state(gen, w, h)
        gen.add_to_tree(5, 5, None, phi, tree, frontier, parent_of, w, h)
        gen.add_to_tree(5, 6, 5 * w + 5, phi, tree, frontier, parent_of, w, h)
        assert parent_of[6 * w + 5] == 5 * w + 5


# ── pick_frontier ─────────────────────────────────────────────────────────────

class TestPickFrontier:
    def test_returns_a_frontier_member(self, gen):
        frontier = {10, 20, 30}
        phi = [0.0] * 50
        for i in frontier:
            phi[i] = 0.5
        rng = random.Random(0)
        result = gen.pick_frontier(frontier, phi, eta=1.5, rng=rng)
        assert result in frontier

    def test_deterministic_with_fixed_seed(self, gen):
        frontier = {5, 10, 15, 20}
        phi = [0.0] * 25
        for i, v in zip(sorted(frontier), [0.1, 0.5, 0.8, 0.3]):
            phi[i] = v
        r1 = gen.pick_frontier(frontier, phi, eta=1.5, rng=random.Random(7))
        r2 = gen.pick_frontier(frontier, phi, eta=1.5, rng=random.Random(7))
        assert r1 == r2

    def test_high_eta_biases_toward_highest_phi(self, gen):
        """With very high eta the highest-phi cell should dominate overwhelmingly."""
        frontier = {0, 1, 2}
        phi = [0.0] * 3
        phi[0] = 0.1
        phi[1] = 0.5
        phi[2] = 0.99  # dominates at eta=10: 0.99^10 >> 0.5^10 >> 0.1^10
        rng = random.Random(0)
        counts = [0, 0, 0]
        for _ in range(200):
            picked = gen.pick_frontier(frontier, phi, eta=10.0, rng=rng)
            counts[picked] += 1
        # Cell 2 must win the vast majority; cells 0 and 1 may both be 0
        assert counts[2] > 150
        assert counts[2] >= counts[1] + counts[0]

    def test_zero_phi_falls_back_to_uniform(self, gen):
        """When all weights are zero the function must still return a frontier cell."""
        frontier = {3, 7, 11}
        phi = [0.0] * 15
        rng = random.Random(42)
        result = gen.pick_frontier(frontier, phi, eta=1.5, rng=rng)
        assert result in frontier

    def test_single_cell_frontier(self, gen):
        frontier = {5}
        phi = [0.0] * 10
        phi[5] = 0.7
        rng = random.Random(0)
        assert gen.pick_frontier(frontier, phi, eta=1.5, rng=rng) == 5


# ── relax_around ──────────────────────────────────────────────────────────────

class TestRelaxAround:
    def test_boundary_cells_unchanged(self, gen):
        """Edge cells (phi=1) must never be modified by the relaxation."""
        w, h = 20, 20
        phi = gen.make_phi(w, h, 10, 10)
        tree = [False] * (w * h)
        tree[10 * w + 10] = True
        phi[10 * w + 10] = 0.0
        original_edges = [phi[y * w + x] for x in range(w) for y in [0, h - 1]]
        original_edges += [phi[y * w + x] for y in range(h) for x in [0, w - 1]]
        gen.relax_around(10, 10, phi, tree, w, h, local_r=5, relax_n=20)
        after_edges = [phi[y * w + x] for x in range(w) for y in [0, h - 1]]
        after_edges += [phi[y * w + x] for y in range(h) for x in [0, w - 1]]
        assert original_edges == after_edges

    def test_tree_cells_unchanged(self, gen):
        """Tree cells must retain phi=0 after relaxation."""
        w, h = 20, 20
        phi = gen.make_phi(w, h, 10, 10)
        tree = [False] * (w * h)
        tree[10 * w + 10] = True
        phi[10 * w + 10] = 0.0
        gen.relax_around(10, 10, phi, tree, w, h, local_r=5, relax_n=50)
        assert phi[10 * w + 10] == 0.0

    def test_interior_phi_remains_bounded(self, gen):
        """After relaxation interior phi must still be in [0, 1]."""
        w, h = 30, 30
        phi = gen.make_phi(w, h, 15, 15)
        tree = [False] * (w * h)
        gen.relax_around(15, 15, phi, tree, w, h, local_r=8, relax_n=30)
        for i in range(w * h):
            assert 0.0 <= phi[i] <= 1.0 + 1e-9


# ── grow_tree (happy path and edge cases) ────────────────────────────────────

class TestGrowTree:
    def test_returns_nonempty_parent_map(self, gen):
        parent_of = gen.grow_tree(
            30, 30, 15, 15, eta=1.5, local_r=5, relax_n=10, max_steps=50, seed=0
        )
        assert len(parent_of) > 0

    def test_deterministic_with_same_seed(self, gen):
        kwargs = dict(w=40, h=40, cx=20, cy=20, eta=1.5,
                      local_r=6, relax_n=10, max_steps=80, seed=99)
        p1 = gen.grow_tree(**kwargs)
        p2 = gen.grow_tree(**kwargs)
        assert p1 == p2

    def test_different_seeds_differ(self, gen):
        kwargs = dict(w=40, h=40, cx=20, cy=20, eta=1.5,
                      local_r=6, relax_n=10, max_steps=150)
        p1 = gen.grow_tree(**kwargs, seed=1)
        p2 = gen.grow_tree(**kwargs, seed=2)
        assert p1 != p2

    def test_zero_max_steps_returns_empty(self, gen):
        """max_steps=0 should stop before a single growth step."""
        parent_of = gen.grow_tree(
            20, 20, 10, 10, eta=1.5, local_r=4, relax_n=5, max_steps=0, seed=0
        )
        assert len(parent_of) == 0

    def test_tree_stays_within_grid(self, gen):
        """Every cell index in parent_of must be valid for the given grid."""
        w, h = 30, 30
        parent_of = gen.grow_tree(
            w, h, 15, 15, eta=1.5, local_r=5, relax_n=10, max_steps=200, seed=7
        )
        for idx in parent_of:
            assert 0 <= idx < w * h

    def test_parent_is_adjacent(self, gen):
        """Each cell's parent must be exactly one step away (orthogonal adjacency)."""
        w, h = 40, 40
        parent_of = gen.grow_tree(
            w, h, 20, 20, eta=1.5, local_r=6, relax_n=10, max_steps=100, seed=3
        )
        for child, par in parent_of.items():
            cx_c, cy_c = child % w, child // w
            cx_p, cy_p = par % w, par // w
            dist = abs(cx_c - cx_p) + abs(cy_c - cy_p)
            assert dist == 1, f"non-adjacent parent: child={child}, par={par}"

    def test_high_eta_still_grows(self, gen):
        """Even with very high eta (η=5) the tree must produce segments."""
        parent_of = gen.grow_tree(
            30, 30, 15, 15, eta=5.0, local_r=5, relax_n=10, max_steps=80, seed=0
        )
        assert len(parent_of) > 0

    def test_eta_zero_uniform_growth(self, gen):
        """eta=0 ⟹ all weights equal 1 ⟹ uniform random walk; tree still grows."""
        parent_of = gen.grow_tree(
            30, 30, 15, 15, eta=0.0, local_r=5, relax_n=10, max_steps=80, seed=0
        )
        assert len(parent_of) > 0


# ── render_svg ────────────────────────────────────────────────────────────────

class TestRenderSvg:
    def test_returns_string(self, gen):
        parent_of = {10: 5, 20: 10}
        svg = gen.render_svg(parent_of, 30, 30, 100, 100)
        assert isinstance(svg, str)

    def test_svg_root_element(self, gen):
        parent_of = {10: 5}
        svg = gen.render_svg(parent_of, 20, 20, 100, 100)
        assert svg.strip().startswith("<svg ")
        assert "</svg>" in svg

    def test_background_rect_present(self, gen):
        parent_of = {10: 5}
        svg = gen.render_svg(parent_of, 20, 20, 100, 100)
        assert "#08071a" in svg

    def test_correct_dimensions_in_output(self, gen):
        parent_of = {10: 5}
        svg = gen.render_svg(parent_of, 20, 20, 300, 400)
        assert 'width="300"' in svg
        assert 'height="400"' in svg

    def test_empty_tree_produces_valid_svg(self, gen):
        """An empty parent_of map must still yield a valid SVG file."""
        svg = gen.render_svg({}, 20, 20, 100, 100)
        assert "<svg " in svg
        assert "</svg>" in svg

    def test_glow_filter_present(self, gen):
        parent_of = {10: 5}
        svg = gen.render_svg(parent_of, 20, 20, 100, 100)
        assert "feGaussianBlur" in svg

    def test_branch_colours_present(self, gen):
        parent_of = {10: 5}
        svg = gen.render_svg(parent_of, 20, 20, 100, 100)
        assert "#6040c0" in svg   # outer glow
        assert "#d0c8ff" in svg   # bright core


# ── thumbnail regeneration (integration) ─────────────────────────────────────

class TestThumbnailIntegration:
    def test_main_writes_thumbnail(self, gen, tmp_path, monkeypatch):
        """gen.main() must create thumbnail.svg inside the piece directory."""
        monkeypatch.chdir(PIECE_DIR)
        out = PIECE_DIR / "thumbnail.svg"
        if out.exists():
            out.unlink()
        gen.main()
        assert out.is_file()
        content = out.read_text()
        assert "<svg " in content
        assert "#08071a" in content

    def test_thumbnail_has_segments(self, gen):
        """The committed thumbnail.svg must contain at least one path element."""
        svg = (PIECE_DIR / "thumbnail.svg").read_text()
        assert '<path d="' in svg
