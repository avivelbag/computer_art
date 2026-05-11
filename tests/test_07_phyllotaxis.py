"""Tests for pieces/07-every-seed-knows/generate.py."""

import math
import pathlib
import sys

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "07-every-seed-knows"
sys.path.insert(0, str(PIECE_DIR))
import generate as gen  # noqa: E402


def circle_lines(svg: str) -> list[str]:
    """Return the lines of svg that contain a <circle element."""
    return [line for line in svg.splitlines() if "<circle" in line]


def parse_attr(line: str, attr: str) -> float:
    """Parse a numeric SVG attribute value from a single element line."""
    return float(line.split(f'{attr}="')[1].split('"')[0])


class TestGenerateSVG:
    def test_default_circle_count(self):
        """Default call must produce exactly N_SEEDS circles."""
        svg = gen.generate_svg()
        assert len(circle_lines(svg)) == gen.N_SEEDS

    def test_custom_n_seeds(self):
        """Passing n_seeds=10 produces exactly 10 circle elements."""
        svg = gen.generate_svg(n_seeds=10)
        assert len(circle_lines(svg)) == 10

    def test_zero_seeds_no_circles(self):
        """n_seeds=0 produces a valid SVG shell with no circles."""
        svg = gen.generate_svg(n_seeds=0)
        assert len(circle_lines(svg)) == 0
        assert "<svg" in svg
        assert "<rect" in svg

    def test_svg_namespace(self):
        """Output must carry the SVG namespace declaration."""
        svg = gen.generate_svg(n_seeds=1)
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_background_rect_present(self):
        """SVG must contain a background <rect for the dark fill."""
        svg = gen.generate_svg(n_seeds=5)
        assert "<rect" in svg

    def test_palette_cycles_every_five(self):
        """Seeds n and n+5 share the same color because palette length is 5."""
        svg = gen.generate_svg(n_seeds=10)
        lines = circle_lines(svg)
        color_0 = lines[0].split('fill="')[1].split('"')[0]
        color_5 = lines[5].split('fill="')[1].split('"')[0]
        assert color_0 == color_5

    def test_first_dot_at_center(self):
        """n=0 has r=sqrt(0)*scale=0, so cx=cy=size/2."""
        svg = gen.generate_svg(n_seeds=1, size=600, scale=10.0)
        lines = circle_lines(svg)
        assert len(lines) == 1
        cx = parse_attr(lines[0], "cx")
        cy = parse_attr(lines[0], "cy")
        assert abs(cx - 300.0) < 0.01
        assert abs(cy - 300.0) < 0.01

    def test_golden_angle_placement(self):
        """n=1 must land at the golden angle from center, at radius=scale."""
        size, scale = 600, 10.0
        svg = gen.generate_svg(n_seeds=2, size=size, scale=scale)
        lines = circle_lines(svg)
        cx = parse_attr(lines[1], "cx")
        cy = parse_attr(lines[1], "cy")
        center = size / 2
        expected_x = center + scale * math.cos(gen.GOLDEN_ANGLE_RAD)
        expected_y = center + scale * math.sin(gen.GOLDEN_ANGLE_RAD)
        assert abs(cx - expected_x) < 0.01
        assert abs(cy - expected_y) < 0.01

    def test_dot_radius_increases_toward_edge(self):
        """Outer dots must have a strictly larger radius than the innermost dot."""
        svg = gen.generate_svg(n_seeds=50)
        lines = circle_lines(svg)
        r_first = parse_attr(lines[0], " r")
        r_last = parse_attr(lines[-1], " r")
        assert r_last > r_first

    def test_dot_radius_bounds(self):
        """The first dot uses dot_r_min and the last dot uses dot_r_max."""
        dot_r_min, dot_r_max = 2.0, 6.0
        svg = gen.generate_svg(n_seeds=100, dot_r_min=dot_r_min, dot_r_max=dot_r_max)
        lines = circle_lines(svg)
        assert abs(parse_attr(lines[0], " r") - dot_r_min) < 0.01
        assert abs(parse_attr(lines[-1], " r") - dot_r_max) < 0.01

    def test_single_seed_uses_r_min(self):
        """With n_seeds=1 the division guard fires: dot gets dot_r_min."""
        svg = gen.generate_svg(n_seeds=1, dot_r_min=3.0, dot_r_max=8.0)
        lines = circle_lines(svg)
        assert abs(parse_attr(lines[0], " r") - 3.0) < 0.01

    def test_large_n_seeds_completes(self):
        """Generating 800 dots must complete without error."""
        svg = gen.generate_svg(n_seeds=800)
        assert len(circle_lines(svg)) == 800

    def test_custom_background_color(self):
        """The supplied bg color must appear in the background rect."""
        svg = gen.generate_svg(n_seeds=5, bg="#ff0000")
        assert '#ff0000' in svg


class TestCommittedFiles:
    def test_piece_svg_exists(self):
        """piece.svg must be committed alongside generate.py."""
        assert (PIECE_DIR / "piece.svg").is_file()

    def test_thumbnail_svg_exists(self):
        """thumbnail.svg must be committed alongside piece.svg."""
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_piece_svg_has_correct_circle_count(self):
        """Committed piece.svg must contain exactly N_SEEDS circles."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert len(circle_lines(content)) == gen.N_SEEDS

    def test_piece_svg_has_background(self):
        """Committed piece.svg must contain a background rect."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert "<rect" in content

    def test_thumbnail_smaller_than_piece(self):
        """thumbnail.svg must be smaller in bytes than piece.svg."""
        piece = (PIECE_DIR / "piece.svg").read_text()
        thumb = (PIECE_DIR / "thumbnail.svg").read_text()
        assert len(thumb) < len(piece)

    def test_readme_exists(self):
        """README.md must exist in the piece directory."""
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_py_exists(self):
        """generate.py must be committed in the piece directory."""
        assert (PIECE_DIR / "generate.py").is_file()


class TestWriteToDirectory:
    def test_generate_svg_output_is_writable(self, tmp_path):
        """generate_svg output can be written to a file and read back intact."""
        svg = gen.generate_svg(n_seeds=5)
        out = tmp_path / "test.svg"
        out.write_text(svg)
        assert out.read_text() == svg

    def test_thumbnail_parameters_produce_smaller_viewbox(self, tmp_path):
        """Thumbnail SVG with size=200 has a 200x200 viewBox."""
        thumb = gen.generate_svg(size=200, scale=3.2, dot_r_min=1.0, dot_r_max=2.5)
        assert 'viewBox="0 0 200 200"' in thumb

    def test_all_palette_colors_appear(self):
        """Each of the 5 palette colors must appear at least once in the SVG."""
        svg = gen.generate_svg(n_seeds=5)
        for color in gen.PALETTE:
            assert color in svg
