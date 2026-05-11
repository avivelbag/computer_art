"""Tests for pieces/10-the-room-divides-itself/generate.py."""

import importlib.util
import pathlib
import re

import pytest

PIECE_DIR = (
    pathlib.Path(__file__).parent.parent / "pieces" / "10-the-room-divides-itself"
)

# Load by file path to avoid sys.modules collision with other pieces' generate.py
_spec = importlib.util.spec_from_file_location("gen10", PIECE_DIR / "generate.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)


def parse_rects(svg: str) -> list[dict]:
    """Return a list of attribute dicts for every <rect element in the SVG."""
    rects = []
    for m in re.finditer(r"<rect ([^/]+)/>", svg):
        attrs = {}
        for km in re.finditer(r'([\w-]+)="([^"]*)"', m.group(1)):
            attrs[km.group(1)] = km.group(2)
        rects.append(attrs)
    return rects


class TestGenerateSVG:
    def test_svg_namespace_present(self):
        """SVG must carry the standard XML namespace declaration."""
        svg = gen.generate_svg()
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_viewbox_is_square(self):
        """viewBox must equal '0 0 size size' for a square composition."""
        svg = gen.generate_svg(size=400)
        assert 'viewBox="0 0 400 400"' in svg

    def test_deterministic_same_seed(self):
        """Two calls with the same seed must produce identical SVG output."""
        assert gen.generate_svg(seed=42) == gen.generate_svg(seed=42)

    def test_different_seeds_differ(self):
        """Different seeds must produce different SVG compositions."""
        assert gen.generate_svg(seed=42) != gen.generate_svg(seed=99)

    def test_max_depth_zero_one_leaf(self):
        """max_depth=0 prevents any split, producing exactly one leaf rect."""
        rects = parse_rects(gen.generate_svg(size=200, max_depth=0))
        assert len(rects) == 1
        assert float(rects[0]["x"]) == pytest.approx(0.0)
        assert float(rects[0]["y"]) == pytest.approx(0.0)
        assert float(rects[0]["width"]) == pytest.approx(200.0)
        assert float(rects[0]["height"]) == pytest.approx(200.0)

    def test_total_area_equals_canvas(self):
        """Leaf rects tile the canvas — area sums to size×size within rounding."""
        size = 400
        rects = parse_rects(gen.generate_svg(size=size, seed=42))
        total = sum(float(r["width"]) * float(r["height"]) for r in rects)
        assert total == pytest.approx(size * size, abs=1.0)

    def test_subdivide_exact_area(self):
        """_subdivide produces leaves whose float areas sum exactly to size×size."""
        import random
        size = 400.0
        rng = random.Random(42)
        leaves = gen._subdivide(
            0.0, 0.0, size, size, 0, rng,
            gen.MAX_DEPTH, gen.MIN_SIZE, gen.SPLIT_PROB_BASE,
        )
        total = sum(w * h for _, _, w, h in leaves)
        assert total == pytest.approx(size * size, rel=1e-10)

    def test_no_rect_outside_bounds(self):
        """Every leaf rect must lie entirely within [0, size]×[0, size]."""
        size = 400
        rects = parse_rects(gen.generate_svg(size=size, seed=42))
        for r in rects:
            x, y = float(r["x"]), float(r["y"])
            w, h = float(r["width"]), float(r["height"])
            assert x >= -0.01
            assert y >= -0.01
            assert x + w <= size + 0.01
            assert y + h <= size + 0.01

    def test_stroke_width_consistent(self):
        """All rects must carry the stroke-width supplied to generate_svg."""
        rects = parse_rects(gen.generate_svg(seed=42, stroke_width=2.5))
        assert rects, "expected at least one rect"
        for r in rects:
            assert r["stroke-width"] == "2.5"

    def test_white_fraction_zero_no_white(self):
        """white_fraction=0 must exclude all white/cream colours."""
        svg = gen.generate_svg(seed=42, white_fraction=0.0)
        for color in gen.WHITE_COLORS:
            assert color not in svg

    def test_white_fraction_one_all_white(self):
        """white_fraction=1.0 must give every leaf a white/cream fill."""
        rects = parse_rects(gen.generate_svg(seed=42, white_fraction=1.0))
        assert rects
        for r in rects:
            assert r["fill"] in gen.WHITE_COLORS

    def test_palette_colors_appear(self):
        """All palette colours must appear when white_fraction=0 and depth is high."""
        svg = gen.generate_svg(
            size=800, seed=42, max_depth=8, split_prob_base=0.99, white_fraction=0.0
        )
        for color in gen.PALETTE:
            assert color in svg, f"Palette colour {color!r} absent from SVG"

    def test_min_rect_dimension_not_below_half_min_size(self):
        """No leaf min-dimension should fall below min_size/2 (sliver guard)."""
        min_size = 40.0
        rects = parse_rects(gen.generate_svg(size=800, seed=42, min_size=min_size))
        for r in rects:
            assert min(float(r["width"]), float(r["height"])) >= min_size / 2 - 0.01

    def test_higher_depth_more_or_equal_leaves(self):
        """Deeper recursion must produce >= as many leaves as shallower."""
        shallow = parse_rects(gen.generate_svg(size=800, seed=42, max_depth=2))
        deep = parse_rects(gen.generate_svg(size=800, seed=42, max_depth=8))
        assert len(deep) >= len(shallow)

    def test_large_canvas_completes(self):
        """Full 800×800 generation must complete without error."""
        svg = gen.generate_svg(size=800, seed=42)
        assert "<svg" in svg
        assert len(parse_rects(svg)) > 0

    def test_custom_palette_replaces_default(self):
        """A custom palette is used and the default palette colours are absent."""
        custom = ["#aabbcc", "#ddeeff"]
        svg = gen.generate_svg(seed=42, palette=custom, white_fraction=0.0)
        for color in gen.PALETTE:
            assert color not in svg


class TestEdgeCases:
    def test_very_large_min_size_one_leaf(self):
        """min_size exceeding the canvas prevents all splits → one leaf."""
        rects = parse_rects(
            gen.generate_svg(size=200, min_size=300.0, split_prob_base=1.0)
        )
        assert len(rects) == 1

    def test_area_preserved_across_seeds(self):
        """Total leaf area stays within 0.1% of size×size for any seed.

        2-decimal-place SVG formatting introduces per-leaf rounding error;
        the bound is generous enough to survive that while still ruling out
        real tiling bugs (overlaps or gaps).
        """
        size = 300
        for seed in [0, 1, 12345, 99999]:
            rects = parse_rects(gen.generate_svg(size=size, seed=seed))
            total = sum(float(r["width"]) * float(r["height"]) for r in rects)
            assert total == pytest.approx(size * size, rel=0.001), (
                f"Area mismatch for seed={seed}"
            )

    def test_single_color_palette(self):
        """A single-colour palette still produces a valid SVG."""
        rects = parse_rects(
            gen.generate_svg(seed=42, palette=["#ff0000"], white_fraction=0.0)
        )
        assert len(rects) > 0
        for r in rects:
            assert r["fill"] == "#ff0000"

    def test_empty_palette_raises(self):
        """An empty palette raises IndexError when rng.choice is called."""
        with pytest.raises(IndexError):
            gen.generate_svg(seed=42, palette=[], white_fraction=0.0)

    def test_size_one_no_splits(self):
        """A 1×1 canvas cannot be split further; one leaf is returned."""
        rects = parse_rects(gen.generate_svg(size=1, split_prob_base=1.0))
        assert len(rects) == 1


class TestCommittedFiles:
    def test_piece_svg_exists(self):
        """piece.svg must be committed alongside generate.py."""
        assert (PIECE_DIR / "piece.svg").is_file()

    def test_thumbnail_svg_exists(self):
        """thumbnail.svg must be committed alongside piece.svg."""
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_generate_py_exists(self):
        """generate.py must be committed in the piece directory."""
        assert (PIECE_DIR / "generate.py").is_file()

    def test_readme_exists(self):
        """README.md must exist in the piece directory."""
        assert (PIECE_DIR / "README.md").is_file()

    def test_piece_svg_is_valid_svg(self):
        """Committed piece.svg must carry the SVG namespace."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert 'xmlns="http://www.w3.org/2000/svg"' in content

    def test_piece_svg_has_rects(self):
        """Committed piece.svg must contain at least one rect element."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert "<rect" in content

    def test_piece_svg_has_800_viewbox(self):
        """Committed piece.svg must have an 800×800 viewBox."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert 'viewBox="0 0 800 800"' in content

    def test_thumbnail_has_200_viewbox(self):
        """thumbnail.svg must have a 200×200 viewBox."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert 'viewBox="0 0 200 200"' in content

    def test_thumbnail_smaller_than_piece(self):
        """thumbnail.svg must be smaller in bytes than piece.svg."""
        piece = (PIECE_DIR / "piece.svg").read_text()
        thumb = (PIECE_DIR / "thumbnail.svg").read_text()
        assert len(thumb) < len(piece)

    def test_piece_svg_matches_deterministic_generation(self):
        """Committed piece.svg must exactly match what generate_svg() produces."""
        committed = (PIECE_DIR / "piece.svg").read_text()
        generated = gen.generate_svg()
        assert committed == generated

    def test_readme_mentions_seed(self):
        """README.md must document the random seed used."""
        content = (PIECE_DIR / "README.md").read_text()
        assert "seed" in content.lower() or "42" in content

    def test_readme_mentions_algorithm(self):
        """README.md must describe the splitting algorithm."""
        content = (PIECE_DIR / "README.md").read_text()
        lower = content.lower()
        assert "split" in lower or "subdivis" in lower or "recursiv" in lower
