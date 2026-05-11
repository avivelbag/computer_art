"""Tests for pieces/21-frequencies-in-common/generate.py."""

import importlib.util
import math
import pathlib

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "21-frequencies-in-common"

_spec = importlib.util.spec_from_file_location("gen21", PIECE_DIR / "generate.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)


def path_lines(svg: str) -> list[str]:
    """Return lines of svg that contain a <path element."""
    return [line for line in svg.splitlines() if "<path" in line]


class TestLissajousPath:
    def test_returns_string_starting_with_M(self):
        """Path data must start with an M move command."""
        d = gen._lissajous_path(1, 2, 0.0, 10, 400.0, 400.0, 360.0, 360.0)
        assert d.startswith("M ")

    def test_n_plus_one_coordinate_pairs(self):
        """Path samples n_points+1 positions (closed loop), yielding n_points L segments."""
        d = gen._lissajous_path(1, 2, 0.0, 20, 400.0, 400.0, 360.0, 360.0)
        segments = d.split(" L ")
        assert len(segments) == 21

    def test_delta_zero_starts_at_center_x(self):
        """With a=1, b=1, delta=0, t=0: sin(0)=0 so x=cx."""
        cx, cy, rx, ry = 400.0, 400.0, 360.0, 360.0
        d = gen._lissajous_path(1, 1, 0.0, 5, cx, cy, rx, ry)
        first = d.split("M ")[1].split(" L ")[0]
        x, y = map(float, first.split(","))
        assert abs(x - cx) < 0.01
        assert abs(y - cy) < 0.01

    def test_phase_shifts_first_point(self):
        """delta=π/2 causes sin(a*0+delta)=1 so x=cx+rx."""
        cx, cy, rx, ry = 400.0, 400.0, 360.0, 360.0
        d = gen._lissajous_path(1, 1, math.pi / 2, 5, cx, cy, rx, ry)
        first = d.split("M ")[1].split(" L ")[0]
        x, _ = map(float, first.split(","))
        assert abs(x - (cx + rx)) < 0.01


class TestGenerateSVG:
    def test_default_path_count(self):
        """Default call produces len(FREQUENCY_PAIRS) * DELTAS_PER_PAIR paths."""
        svg = gen.generate_svg()
        expected = len(gen.FREQUENCY_PAIRS) * gen.DELTAS_PER_PAIR
        assert len(path_lines(svg)) == expected

    def test_custom_frequency_pairs(self):
        """Passing a single pair with 2 deltas yields exactly 2 paths."""
        svg = gen.generate_svg(frequency_pairs=[(1, 2)], deltas_per_pair=2)
        assert len(path_lines(svg)) == 2

    def test_empty_frequency_pairs(self):
        """No frequency pairs → valid SVG with no path elements."""
        svg = gen.generate_svg(frequency_pairs=[], deltas_per_pair=4)
        assert len(path_lines(svg)) == 0
        assert "<svg" in svg
        assert "<rect" in svg

    def test_svg_namespace(self):
        """Output must carry the SVG namespace declaration."""
        svg = gen.generate_svg(frequency_pairs=[(1, 1)], deltas_per_pair=1)
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_background_rect(self):
        """SVG must contain a background <rect."""
        svg = gen.generate_svg(frequency_pairs=[(1, 2)], deltas_per_pair=1)
        assert "<rect" in svg

    def test_background_color_appears(self):
        """Supplied bg color must appear in the background rect."""
        svg = gen.generate_svg(
            frequency_pairs=[(1, 1)], deltas_per_pair=1, bg="#aabbcc"
        )
        assert "#aabbcc" in svg

    def test_ink_color_in_paths(self):
        """Supplied ink color must appear in at least one path element."""
        svg = gen.generate_svg(
            frequency_pairs=[(1, 1)], deltas_per_pair=1, ink="#ff0000"
        )
        assert "#ff0000" in svg

    def test_stroke_width_in_output(self):
        """stroke-width value must appear in path attributes."""
        svg = gen.generate_svg(
            frequency_pairs=[(1, 2)], deltas_per_pair=1, stroke_width=1.23
        )
        assert "1.23" in svg

    def test_viewbox_matches_size(self):
        """viewBox must reflect the requested canvas size."""
        svg = gen.generate_svg(
            size=500, frequency_pairs=[(1, 2)], deltas_per_pair=1
        )
        assert 'viewBox="0 0 500 500"' in svg

    def test_paths_are_fill_none(self):
        """All path elements must have fill="none" (plotter style, not filled)."""
        svg = gen.generate_svg(frequency_pairs=[(1, 2)], deltas_per_pair=2)
        for line in path_lines(svg):
            assert 'fill="none"' in line

    def test_thumbnail_size_smaller_than_piece(self):
        """Thumbnail SVG (400px) must be smaller in bytes than piece SVG (800px)."""
        piece = gen.generate_svg()
        thumb = gen.generate_svg(size=gen.THUMB_SIZE, margin=20)
        assert len(thumb) < len(piece)

    def test_large_call_completes(self):
        """Full default call (56 curves × 800 points) must complete without error."""
        svg = gen.generate_svg()
        assert len(svg) > 0

    def test_single_delta_produces_one_path_per_pair(self):
        """deltas_per_pair=1 yields exactly one path per frequency pair."""
        pairs = [(1, 2), (3, 4)]
        svg = gen.generate_svg(frequency_pairs=pairs, deltas_per_pair=1)
        assert len(path_lines(svg)) == len(pairs)

    def test_coordinates_within_canvas(self):
        """All path coordinates must lie within the canvas bounds [0, size]."""
        size = 800
        svg = gen.generate_svg(
            size=size,
            frequency_pairs=[(1, 2), (3, 5)],
            deltas_per_pair=2,
        )
        import re
        coords = re.findall(r"([\d.]+),([\d.]+)", svg)
        for xs, ys in coords:
            x, y = float(xs), float(ys)
            assert 0 <= x <= size, f"x={x} out of range"
            assert 0 <= y <= size, f"y={y} out of range"


class TestCommittedFiles:
    def test_piece_svg_exists(self):
        """piece.svg must be committed alongside generate.py."""
        assert (PIECE_DIR / "piece.svg").is_file()

    def test_thumbnail_svg_exists(self):
        """thumbnail.svg must be committed alongside piece.svg."""
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        """README.md must exist in the piece directory."""
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_py_exists(self):
        """generate.py must be present in the piece directory."""
        assert (PIECE_DIR / "generate.py").is_file()

    def test_piece_svg_has_background(self):
        """Committed piece.svg must contain a background rect."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert "<rect" in content

    def test_piece_svg_has_paths(self):
        """Committed piece.svg must contain at least 40 path elements."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert len(path_lines(content)) >= 40

    def test_thumbnail_smaller_than_piece(self):
        """thumbnail.svg must be smaller in bytes than piece.svg."""
        piece = (PIECE_DIR / "piece.svg").read_text()
        thumb = (PIECE_DIR / "thumbnail.svg").read_text()
        assert len(thumb) < len(piece)

    def test_piece_svg_correct_viewbox(self):
        """Committed piece.svg must have an 800x800 viewBox."""
        content = (PIECE_DIR / "piece.svg").read_text()
        assert 'viewBox="0 0 800 800"' in content

    def test_thumbnail_svg_correct_viewbox(self):
        """Committed thumbnail.svg must have a 400x400 viewBox."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert 'viewBox="0 0 400 400"' in content


class TestSmokeRun:
    def test_generate_svg_runs_without_error(self):
        """generate_svg() must complete without exceptions and return non-empty SVG."""
        svg = gen.generate_svg()
        assert len(svg) > 0
        assert "<svg" in svg

    def test_main_writes_both_svgs(self):
        """main() writes both piece.svg and thumbnail.svg to the piece directory."""
        gen.main()
        assert (PIECE_DIR / "piece.svg").is_file()
        assert (PIECE_DIR / "thumbnail.svg").is_file()
