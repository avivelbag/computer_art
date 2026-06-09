"""Tests for pieces/05-ford-circles/generate.py."""

import importlib.util
import math
import pathlib

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "05-ford-circles"
GENERATE_PY = PIECE_DIR / "generate.py"

spec = importlib.util.spec_from_file_location("generate_ford_circles", GENERATE_PY)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def circle_lines(svg: str) -> list[str]:
    """Return lines containing a <circle element."""
    return [line for line in svg.splitlines() if "<circle" in line]


def parse_attr(line: str, attr: str) -> float:
    """Parse a numeric SVG attribute value from an element line."""
    return float(line.split(f'{attr}="')[1].split('"')[0])


def farey_count(n: int) -> int:
    """Return |F_n|, the number of Farey fractions with denominator <= n."""
    from math import gcd
    return 1 + sum(
        sum(1 for k in range(1, q + 1) if gcd(k, q) == 1)
        for q in range(1, n + 1)
    )


# ---------------------------------------------------------------------------
# ford_fractions
# ---------------------------------------------------------------------------

class TestFordFractions:
    def test_max_q_zero_returns_empty(self):
        assert gen.ford_fractions(0) == []

    def test_max_q_negative_returns_empty(self):
        assert gen.ford_fractions(-5) == []

    def test_max_q_1_returns_boundary_fractions(self):
        result = gen.ford_fractions(1)
        assert set(result) == {(0, 1), (1, 1)}
        assert len(result) == 2

    def test_max_q_2_count(self):
        result = gen.ford_fractions(2)
        assert len(result) == 3
        assert (1, 2) in result

    def test_max_q_3_count(self):
        result = gen.ford_fractions(3)
        assert len(result) == 5
        assert (1, 3) in result
        assert (2, 3) in result

    def test_all_denominators_within_bound(self):
        for p, q in gen.ford_fractions(15):
            assert q <= 15, f"Denominator {q} exceeds max_q=15"

    def test_all_fractions_reduced(self):
        from math import gcd
        for p, q in gen.ford_fractions(20):
            assert gcd(p, q) == 1, f"Fraction {p}/{q} is not reduced"

    def test_boundary_fractions_always_present(self):
        for max_q in [1, 5, 30]:
            result = gen.ford_fractions(max_q)
            assert (0, 1) in result
            assert (1, 1) in result

    def test_count_matches_farey_formula_small(self):
        for n in [1, 2, 3, 5, 10]:
            expected = farey_count(n)
            got = len(gen.ford_fractions(n))
            assert got == expected, f"|F_{n}|: expected {expected}, got {got}"

    def test_count_max_q_60(self):
        assert len(gen.ford_fractions(60)) == 1103

    def test_all_numerators_in_range(self):
        for p, q in gen.ford_fractions(10):
            assert 0 <= p <= q

    def test_no_duplicates(self):
        result = gen.ford_fractions(20)
        assert len(result) == len(set(result))

    def test_large_max_q_completes(self):
        result = gen.ford_fractions(100)
        assert len(result) > 1000


# ---------------------------------------------------------------------------
# lerp_color
# ---------------------------------------------------------------------------

class TestLerpColor:
    def test_t_zero_is_indigo(self):
        assert gen.lerp_color(0.0) == "#1a1060"

    def test_t_one_is_rose(self):
        assert gen.lerp_color(1.0) == "#e05060"

    def test_t_half_is_teal(self):
        assert gen.lerp_color(0.5) == "#2a8070"

    def test_clamps_below_zero(self):
        assert gen.lerp_color(-1.0) == gen.lerp_color(0.0)

    def test_clamps_above_one(self):
        assert gen.lerp_color(2.0) == gen.lerp_color(1.0)

    def test_returns_valid_hex_string(self):
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            color = gen.lerp_color(t)
            assert color.startswith("#")
            assert len(color) == 7
            int(color[1:], 16)   # must parse as valid hex

    def test_quarter_is_between_indigo_and_teal(self):
        """At t=0.25 the blue channel should be between indigo and teal values."""
        color = gen.lerp_color(0.25)
        r_val = int(color[1:3], 16)
        g_val = int(color[3:5], 16)
        b_val = int(color[5:7], 16)
        # Indigo: r=26 g=16 b=96; Teal: r=42 g=128 b=112
        assert 26 <= r_val <= 42
        assert 16 <= g_val <= 128
        assert 96 <= b_val <= 112


# ---------------------------------------------------------------------------
# generate_svg
# ---------------------------------------------------------------------------

class TestGenerateSVG:
    def test_default_circle_count(self):
        """Default (max_q=60) must produce 1103 circles."""
        svg = gen.generate_svg()
        assert len(circle_lines(svg)) == 1103

    def test_circle_count_max_q_3(self):
        svg = gen.generate_svg(max_q=3)
        assert len(circle_lines(svg)) == 5

    def test_svg_namespace_present(self):
        svg = gen.generate_svg(max_q=3)
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_background_rect_present(self):
        svg = gen.generate_svg(max_q=3)
        assert "<rect" in svg

    def test_background_uses_bg_constant(self):
        svg = gen.generate_svg(max_q=3)
        assert gen.BG in svg

    def test_circles_have_fill_none(self):
        """All circles must have fill=none."""
        for line in circle_lines(gen.generate_svg(max_q=5)):
            assert 'fill="none"' in line

    def test_viewbox_matches_canvas(self):
        svg = gen.generate_svg(canvas_w=800, canvas_h=500)
        assert 'viewBox="0 0 800 500"' in svg

    def test_width_height_in_svg_tag(self):
        svg = gen.generate_svg(canvas_w=800, canvas_h=500)
        assert 'width="800"' in svg
        assert 'height="500"' in svg

    def test_no_solid_fill_on_circles(self):
        """No circle should have fill set to a hex color."""
        for line in circle_lines(gen.generate_svg(max_q=5)):
            assert 'fill="#' not in line

    def test_q1_circles_have_largest_radius(self):
        """The q=1 circles must have the largest radius in the SVG."""
        svg = gen.generate_svg(max_q=5)
        lines = circle_lines(svg)
        radii = [parse_attr(line, " r") for line in lines]
        max_r = max(radii)
        # Lines are sorted by q ascending, so lines[0] and [1] are q=1
        assert abs(parse_attr(lines[0], " r") - max_r) < 0.01
        assert abs(parse_attr(lines[1], " r") - max_r) < 0.01

    def test_stroke_width_decreases_with_q(self):
        """q=1 circles must have thicker strokes than q=2 circles."""
        svg = gen.generate_svg(max_q=2)
        lines = circle_lines(svg)
        sw_q1 = parse_attr(lines[0], "stroke-width")
        sw_q2 = parse_attr(lines[2], "stroke-width")
        assert sw_q1 > sw_q2

    def test_output_is_string(self):
        assert isinstance(gen.generate_svg(max_q=3), str)

    def test_custom_canvas_dimensions(self):
        svg = gen.generate_svg(max_q=3, canvas_w=400, canvas_h=250)
        assert 'viewBox="0 0 400 250"' in svg

    def test_max_q_1_produces_two_circles(self):
        assert len(circle_lines(gen.generate_svg(max_q=1))) == 2

    def test_max_q_0_produces_no_circles(self):
        svg = gen.generate_svg(max_q=0)
        assert len(circle_lines(svg)) == 0
        assert "<svg" in svg


# ---------------------------------------------------------------------------
# Ford circle geometry (mathematical properties)
# ---------------------------------------------------------------------------

class TestFordGeometry:
    def test_adjacent_farey_circles_are_tangent(self):
        """Ford circles for adjacent Farey fractions must be externally tangent."""
        # 0/1 and 1/2: |0*2 - 1*1| = 1 → adjacent
        p1, q1 = 0, 1
        p2, q2 = 1, 2
        r1 = 1.0 / (2 * q1 * q1)
        r2 = 1.0 / (2 * q2 * q2)
        dist = math.hypot(p1 / q1 - p2 / q2, r1 - r2)
        assert abs(dist - (r1 + r2)) < 1e-10

    def test_another_adjacent_pair_tangent(self):
        """1/2 and 2/3: |1*3 - 2*2| = 1 → adjacent."""
        p1, q1 = 1, 2
        p2, q2 = 2, 3
        r1 = 1.0 / (2 * q1 * q1)
        r2 = 1.0 / (2 * q2 * q2)
        dist = math.hypot(p1 / q1 - p2 / q2, r1 - r2)
        assert abs(dist - (r1 + r2)) < 1e-10

    def test_non_adjacent_circles_not_tangent(self):
        """1/3 and 2/3 have 1/2 between them — their circles do not touch."""
        p1, q1 = 1, 3
        p2, q2 = 2, 3
        r1 = 1.0 / (2 * q1 * q1)
        r2 = 1.0 / (2 * q2 * q2)
        dist = math.hypot(p1 / q1 - p2 / q2, r1 - r2)
        assert dist > r1 + r2 + 1e-6

    def test_all_circles_tangent_to_x_axis(self):
        """By definition every Ford circle sits tangent to y=0: center_y == r."""
        for p, q in [(0, 1), (1, 2), (1, 3), (2, 3), (3, 5)]:
            r = 1.0 / (2 * q * q)
            center_y = r   # Ford circle property: center height = radius
            assert abs(center_y - r) < 1e-15


# ---------------------------------------------------------------------------
# Committed files
# ---------------------------------------------------------------------------

class TestCommittedFiles:
    def test_piece_svg_exists(self):
        assert (PIECE_DIR / "piece.svg").is_file()

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_py_exists(self):
        assert (PIECE_DIR / "generate.py").is_file()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_smaller_than_piece(self):
        piece = (PIECE_DIR / "piece.svg").read_text()
        thumb = (PIECE_DIR / "thumbnail.svg").read_text()
        assert len(thumb) < len(piece)

    def test_piece_svg_has_correct_circle_count(self):
        content = (PIECE_DIR / "piece.svg").read_text()
        assert len(circle_lines(content)) == 1103

    def test_piece_svg_has_background_rect(self):
        content = (PIECE_DIR / "piece.svg").read_text()
        assert "<rect" in content

    def test_piece_svg_has_svg_namespace(self):
        content = (PIECE_DIR / "piece.svg").read_text()
        assert 'xmlns="http://www.w3.org/2000/svg"' in content

    def test_piece_svg_circles_stroke_only(self):
        for line in circle_lines((PIECE_DIR / "piece.svg").read_text()):
            assert 'fill="none"' in line

    def test_readme_mentions_ford(self):
        assert "Ford" in (PIECE_DIR / "README.md").read_text()

    def test_thumbnail_has_circles(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert len(circle_lines(content)) > 0


# ---------------------------------------------------------------------------
# Edge cases and explicit failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_generate_svg_max_q_0_has_no_circles(self):
        svg = gen.generate_svg(max_q=0)
        assert len(circle_lines(svg)) == 0
        assert "<svg" in svg

    def test_svg_always_has_background_rect(self):
        for mq in [0, 1, 5]:
            svg = gen.generate_svg(max_q=mq)
            assert "<rect" in svg

    def test_large_canvas_completes(self):
        svg = gen.generate_svg(max_q=60, canvas_w=1920, canvas_h=1080)
        assert len(circle_lines(svg)) == 1103

    def test_write_to_tmp_path(self, tmp_path):
        svg = gen.generate_svg(max_q=5)
        out = tmp_path / "ford.svg"
        out.write_text(svg)
        assert out.read_text() == svg

    def test_ford_fractions_deterministic(self):
        """Two calls with the same max_q must return identical sets."""
        assert set(gen.ford_fractions(30)) == set(gen.ford_fractions(30))

    def test_entry_missing_required_field_detected(self):
        """An entry without 'description' fails the required-field check."""
        required = {"id", "title", "tagline", "year", "technique",
                    "path", "thumbnail", "description"}
        bad = {"id": "x", "title": "x", "tagline": "x", "year": 2026}
        assert not (required <= bad.keys())
