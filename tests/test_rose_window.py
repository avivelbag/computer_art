"""Tests for the rose window generator (piece 294-rose-window)."""

import importlib.util
import pathlib
import re

import pytest

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "294-rose-window"
GEN_PATH  = PIECE_DIR / "generate.py"


def _load_generate():
    """Dynamically import generate.py from the piece directory."""
    spec = importlib.util.spec_from_file_location("gen294", GEN_PATH)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return _load_generate()


@pytest.fixture(scope="module")
def svg_800(gen):
    return gen.generate_svg(800)


@pytest.fixture(scope="module")
def svg_400(gen):
    return gen.generate_svg(400)


class TestSVGStructure:
    """Verify the SVG has correct structure and dimensions."""

    def test_viewbox_800x800(self, svg_800):
        assert 'viewBox="0 0 800 800"' in svg_800

    def test_display_size_800(self, svg_800):
        assert 'width="800"' in svg_800
        assert 'height="800"' in svg_800

    def test_thumbnail_display_size_400(self, svg_400):
        assert 'width="400"' in svg_400
        assert 'height="400"' in svg_400

    def test_thumbnail_retains_full_viewbox(self, svg_400):
        # Thumbnail still uses the 800×800 geometry (just displayed smaller)
        assert 'viewBox="0 0 800 800"' in svg_400

    def test_is_valid_svg(self, svg_800):
        assert svg_800.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
        assert svg_800.strip().endswith('</svg>')

    def test_lead_stroke_present(self, svg_800):
        assert 'stroke="#222222"' in svg_800

    def test_stroke_width_2_present(self, svg_800):
        assert 'stroke-width="2"' in svg_800

    def test_background_color_present(self, svg_800):
        assert '#050508' in svg_800


class TestColors:
    """Verify all six required stained-glass colors appear in the SVG."""

    REQUIRED = ['#8b0000', '#1a237e', '#f9a825', '#1b5e20', '#4a148c', '#e65100']

    @pytest.mark.parametrize("color", REQUIRED)
    def test_color_present(self, svg_800, color):
        assert color in svg_800, f"Missing required stained-glass color {color}"

    def test_center_disc_is_gold(self, svg_800):
        # The center circle uses gold (#f9a825)
        assert '#f9a825' in svg_800


class TestRegionCounts:
    """Verify the correct number of path elements are generated."""

    def test_path_count_is_60(self, svg_800):
        # 12 Ring-1 + 24 Ring-2 + 12 Ring-3-slivers + 12 Ring-3-bodies = 60
        count = svg_800.count('<path ')
        assert count == 60, f"Expected 60 path elements, got {count}"

    def test_ring2_violet_present(self, svg_800):
        # Ring 2 cycles emerald/violet/amber; violet should appear
        assert '#4a148c' in svg_800

    def test_ring2_amber_present(self, svg_800):
        assert '#e65100' in svg_800


class TestAdjacentColorConstraint:
    """Verify the 4-coloring constraint via the color tables in generate.py."""

    def test_ring1_colors_alternate(self, gen):
        colors = [gen.RING1_COLORS[i % 2] for i in range(12)]
        for i in range(12):
            assert colors[i] != colors[(i + 1) % 12], (
                f"Ring 1 adjacent sectors {i} and {(i+1)%12} share color {colors[i]}"
            )

    def test_ring2_colors_cycle(self, gen):
        colors = [gen.RING2_COLORS[i % 3] for i in range(24)]
        for i in range(24):
            assert colors[i] != colors[(i + 1) % 24], (
                f"Ring 2 adjacent lobes {i} and {(i+1)%24} share color {colors[i]}"
            )

    def test_ring3_slivers_no_adjacent_same_color(self, gen):
        slivers = [gen.RING3_SLIVER[i % 4] for i in range(12)]
        for i in range(12):
            assert slivers[i] != slivers[(i + 1) % 12], (
                f"Ring 3 adjacent slivers {i} and {(i+1)%12} share color {slivers[i]}"
            )

    def test_ring3_bodies_no_adjacent_same_color(self, gen):
        bodies = [gen.RING3_BODY[i % 4] for i in range(12)]
        for i in range(12):
            assert bodies[i] != bodies[(i + 1) % 12], (
                f"Ring 3 adjacent bodies {i} and {(i+1)%12} share color {bodies[i]}"
            )

    def test_ring3_sliver_differs_from_body_same_sector(self, gen):
        for i in range(12):
            s = gen.RING3_SLIVER[i % 4]
            b = gen.RING3_BODY[i % 4]
            assert s != b, (
                f"Ring 3 sector {i}: sliver ({s}) and body ({b}) share the same color"
            )


class TestDeterminism:
    """generate_svg must produce identical output on repeated calls."""

    def test_same_output_on_repeated_calls(self, gen):
        a = gen.generate_svg(800)
        b = gen.generate_svg(800)
        assert a == b

    def test_thumbnail_and_piece_differ_only_in_display_size(self, svg_800, svg_400):
        # Stripping the width/height values should yield identical documents
        norm_800 = re.sub(r'width="\d+" height="\d+"', 'width="X" height="X"', svg_800)
        norm_400 = re.sub(r'width="\d+" height="\d+"', 'width="X" height="X"', svg_400)
        assert norm_800 == norm_400


class TestEdgeCases:
    """Edge cases: small display size, output validity."""

    def test_small_display_size(self, gen):
        svg = gen.generate_svg(100)
        assert 'viewBox="0 0 800 800"' in svg
        assert 'width="100"' in svg

    def test_output_is_non_empty_string(self, gen):
        svg = gen.generate_svg(200)
        assert isinstance(svg, str)
        assert len(svg) > 1000

    def test_no_nan_or_inf_in_output(self, gen):
        svg = gen.generate_svg(800)
        assert 'nan' not in svg.lower()
        assert 'inf' not in svg.lower()

    def test_large_display_size(self, gen):
        svg = gen.generate_svg(2000)
        assert 'width="2000"' in svg
        assert 'viewBox="0 0 800 800"' in svg


class TestPieceFiles:
    """Verify all required piece files are present on disk."""

    def test_piece_svg_exists(self):
        assert (PIECE_DIR / "piece.svg").is_file()

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_generate_py_exists(self):
        assert GEN_PATH.is_file()

    def test_piece_svg_has_correct_viewbox(self):
        content = (PIECE_DIR / "piece.svg").read_text()
        assert 'viewBox="0 0 800 800"' in content

    def test_thumbnail_svg_is_400(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert 'width="400"' in content
