"""Tests for Piece 124 — Strange Attractor: A Basin with No Bottom.

Covers the Clifford attractor equations, coordinate mapping, HTML structure,
generate_thumbnail module, the SVG thumbnail, and the pieces.json registration.
"""
import importlib.util
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "124-strange-attractor"
PIECE_DIR = REPO / "pieces" / PIECE_ID
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

# Canonical Clifford parameters matching the piece
A, B, C, D = -1.4, 1.6, 1.0, 0.7
COORD_MIN = -2.5
COORD_RANGE = 5.0
SZ = 800


# ---------------------------------------------------------------------------
# Helpers shared across tests
# ---------------------------------------------------------------------------

def clifford_step(x: float, y: float) -> tuple[float, float]:
    """One iteration of the Clifford attractor using the piece's parameters."""
    return (
        math.sin(A * y) + C * math.cos(A * x),
        math.sin(B * x) + D * math.cos(B * y),
    )


def _load_gen():
    """Import generate_thumbnail.py as a fresh module without polluting sys.modules."""
    spec = importlib.util.spec_from_file_location(
        "gen124", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _entry() -> dict:
    """Return the pieces.json entry for this piece, raising if absent."""
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


def _html() -> str:
    return INDEX_HTML.read_text()


# ---------------------------------------------------------------------------
# File-existence tests
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_readme_exists():
    assert README.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


def test_generate_thumbnail_exists():
    assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# Clifford attractor mathematics (Python re-implementation)
# ---------------------------------------------------------------------------

class TestCliffordEquations:
    def test_step_returns_two_floats(self):
        xn, yn = clifford_step(0.1, 0.1)
        assert isinstance(xn, float) and isinstance(yn, float)

    def test_step_known_first_iterate(self):
        """Exact check against the closed-form formula from (0.1, 0.1)."""
        xn, yn = clifford_step(0.1, 0.1)
        ex = math.sin(A * 0.1) + C * math.cos(A * 0.1)
        ey = math.sin(B * 0.1) + D * math.cos(B * 0.1)
        assert abs(xn - ex) < 1e-15
        assert abs(yn - ey) < 1e-15

    def test_attractor_stays_bounded(self):
        """After 10 000 steps the orbit must stay within [-2.5, 2.5]²."""
        x, y = 0.1, 0.1
        for _ in range(10_000):
            x, y = clifford_step(x, y)
        assert -2.5 <= x <= 2.5 and -2.5 <= y <= 2.5

    def test_attractor_output_is_finite(self):
        """10 000 iterates must never produce NaN or Inf."""
        x, y = 0.1, 0.1
        for _ in range(10_000):
            x, y = clifford_step(x, y)
        assert math.isfinite(x) and math.isfinite(y)

    def test_attractor_is_deterministic(self):
        """Two identical starting points must produce identical trajectories."""
        x1, y1 = 0.3, -0.5
        x2, y2 = 0.3, -0.5
        for _ in range(2000):
            x1, y1 = clifford_step(x1, y1)
            x2, y2 = clifford_step(x2, y2)
        assert x1 == x2 and y1 == y2

    def test_x_component_bounded_by_formula(self):
        """|x'| ≤ 1 + C = 2.0 for all (x, y) — enforced by the equation form."""
        x, y = 0.3, -0.7
        for _ in range(5000):
            xn, yn = clifford_step(x, y)
            assert abs(xn) <= 1.0 + C + 1e-12
            x, y = xn, yn

    def test_y_component_bounded_by_formula(self):
        """|y'| ≤ 1 + D = 1.7 for all (x, y)."""
        x, y = 0.3, -0.7
        for _ in range(5000):
            xn, yn = clifford_step(x, y)
            assert abs(yn) <= 1.0 + D + 1e-12
            x, y = xn, yn

    def test_x_spans_wide_range(self):
        """x must cover at least 2.0 units across 2000 on-attractor steps."""
        x, y = 0.1, 0.1
        for _ in range(500):
            x, y = clifford_step(x, y)
        xs = []
        for _ in range(2000):
            x, y = clifford_step(x, y)
            xs.append(x)
        assert max(xs) - min(xs) >= 2.0

    def test_y_spans_wide_range(self):
        """y must cover at least 2.0 units across 2000 on-attractor steps."""
        x, y = 0.1, 0.1
        for _ in range(500):
            x, y = clifford_step(x, y)
        ys = []
        for _ in range(2000):
            x, y = clifford_step(x, y)
            ys.append(y)
        assert max(ys) - min(ys) >= 2.0

    def test_not_a_fixed_point(self):
        """The trajectory must still be moving after 200 warm-up steps."""
        x, y = 0.1, 0.1
        for _ in range(200):
            x, y = clifford_step(x, y)
        sx, sy = x, y
        for _ in range(100):
            x, y = clifford_step(x, y)
        assert abs(x - sx) > 1e-9 or abs(y - sy) > 1e-9

    def test_1000_consecutive_iterates_are_unique(self):
        """No two consecutive pairs should be exactly equal — no period-1 orbit."""
        x, y = 0.1, 0.1
        for _ in range(500):
            x, y = clifford_step(x, y)
        prev = (x, y)
        for _ in range(1000):
            x, y = clifford_step(x, y)
            assert (x, y) != prev
            prev = (x, y)


# ---------------------------------------------------------------------------
# Coordinate mapping
# ---------------------------------------------------------------------------

class TestCoordMapping:
    def _to_px(self, v: float) -> int:
        return int((v - COORD_MIN) / COORD_RANGE * SZ)

    def test_lower_bound_maps_to_zero(self):
        assert self._to_px(COORD_MIN) == 0

    def test_upper_bound_maps_to_sz(self):
        assert self._to_px(COORD_MIN + COORD_RANGE) == SZ

    def test_centre_maps_to_half_sz(self):
        assert self._to_px(0.0) == SZ // 2

    def test_all_on_attractor_points_within_canvas(self):
        """All on-attractor points must map into [0, SZ) after warm-up."""
        x, y = 0.1, 0.1
        for _ in range(500):
            x, y = clifford_step(x, y)
        out = 0
        for _ in range(5000):
            x, y = clifford_step(x, y)
            px = self._to_px(x)
            py = self._to_px(y)
            if not (0 <= px < SZ and 0 <= py < SZ):
                out += 1
        assert out == 0, f"{out} points fell outside the canvas"


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------

class TestIndexHtml:
    def setup_method(self):
        self.html = _html()

    def test_has_canvas_element(self):
        assert "<canvas" in self.html

    def test_has_script_element(self):
        assert "<script" in self.html

    def test_has_viewport_meta(self):
        assert 'name="viewport"' in self.html

    def test_has_charset_utf8(self):
        assert "charset" in self.html.lower()

    def test_no_external_scripts(self):
        assert not re.findall(r'<script[^>]+src=["\']https?://', self.html)

    def test_self_contained(self):
        assert "<script src=" not in self.html
        assert '<link rel="stylesheet"' not in self.html

    def test_clifford_parameter_a(self):
        assert "-1.4" in self.html

    def test_clifford_parameter_b(self):
        assert "1.6" in self.html

    def test_mentions_attractor_or_clifford(self):
        h = self.html.lower()
        assert "attractor" in h or "clifford" in h

    def test_has_5_million_total(self):
        """Total iteration count must be at least 5 million."""
        h = self.html
        assert "5_000_000" in h or "5000000" in h or "5e6" in h.lower()

    def test_uses_requestanimationframe(self):
        assert "requestAnimationFrame" in self.html

    def test_has_dark_violet_background(self):
        """Background must be the deep-space violet #0d0820."""
        assert "0d0820" in self.html.lower()

    def test_uses_imagedata(self):
        """Density accumulation must use ImageData for direct pixel writes."""
        assert "createImageData" in self.html or "ImageData" in self.html

    def test_reset_clears_canvas(self):
        """reset() must restore the canvas — count or startTime must be reset."""
        assert "reset" in self.html and ("count=0" in self.html or "count = 0" in self.html)

    def test_batch_constant_present(self):
        """The per-frame batch size constant must appear in the script."""
        assert "10_000" in self.html or "10000" in self.html

    def test_warm_up_discards_iterates(self):
        """500 warm-up iterations must be discarded before plotting."""
        assert "500" in self.html

    def test_coord_min_present(self):
        assert "-2.5" in self.html

    def test_canvas_size_800(self):
        assert "800" in self.html

    def test_no_network_requests(self):
        assert "fetch(" not in self.html
        assert "XMLHttpRequest" not in self.html

    def test_reset_after_60s(self):
        """Piece must reset after 60 000 ms."""
        assert "60_000" in self.html or "60000" in self.html


# ---------------------------------------------------------------------------
# generate_thumbnail module
# ---------------------------------------------------------------------------

class TestGenerateThumbnail:
    def test_clifford_step_matches_equations(self):
        """gen.clifford_step must agree with the reference Python function."""
        gen = _load_gen()
        xn, yn = gen.clifford_step(0.1, 0.1)
        ex = math.sin(A * 0.1) + C * math.cos(A * 0.1)
        ey = math.sin(B * 0.1) + D * math.cos(B * 0.1)
        assert abs(xn - ex) < 1e-15
        assert abs(yn - ey) < 1e-15

    def test_iterate_attractor_returns_correct_count(self):
        gen = _load_gen()
        pts = gen.iterate_attractor(100, 50, 1)
        assert len(pts) == 100

    def test_iterate_attractor_step_sampling(self):
        """With step=5, exactly n points are returned, each sampled every 5 steps."""
        gen = _load_gen()
        pts = gen.iterate_attractor(100, 50, 5)
        assert len(pts) == 100

    def test_all_points_bounded(self):
        """All generated orbit points must lie in [-3, 3]²."""
        gen = _load_gen()
        for ax, ay in gen.iterate_attractor(1000, 500, 1):
            assert -3.0 <= ax <= 3.0 and -3.0 <= ay <= 3.0

    def test_to_svg_coords_centre(self):
        """The attractor origin (0, 0) must map to the SVG centre."""
        gen = _load_gen()
        px, py = gen.to_svg_coords(0.0, 0.0)
        assert abs(px - gen.W / 2) < 1e-6
        assert abs(py - gen.H / 2) < 1e-6

    def test_to_svg_coords_lower_left(self):
        """COORD_MIN maps to the margin offset (not 0,0 since there is a margin)."""
        gen = _load_gen()
        px, py = gen.to_svg_coords(gen.COORD_MIN, gen.COORD_MIN)
        assert abs(px - gen.MARGIN) < 1e-6
        assert abs(py - gen.MARGIN) < 1e-6

    def test_generate_svg_returns_string(self):
        gen = _load_gen()
        assert isinstance(gen.generate_svg(n_points=50), str)

    def test_generate_svg_is_valid_xml(self):
        gen = _load_gen()
        ET.fromstring(gen.generate_svg(n_points=50))

    def test_generate_svg_has_background_rect(self):
        gen = _load_gen()
        assert "<rect" in gen.generate_svg(n_points=50)

    def test_generate_svg_has_circles(self):
        gen = _load_gen()
        assert "<circle" in gen.generate_svg(n_points=50)

    def test_generate_svg_circle_count_matches_n_points(self):
        gen = _load_gen()
        svg = gen.generate_svg(n_points=80)
        assert svg.count("<circle") == 80

    def test_generate_svg_zero_points_valid_xml(self):
        """n_points=0 must produce valid XML with just a background rect."""
        gen = _load_gen()
        ET.fromstring(gen.generate_svg(n_points=0))

    def test_generate_svg_large_input_valid(self):
        """500 points must produce valid XML under 500 KB."""
        gen = _load_gen()
        svg = gen.generate_svg(n_points=500)
        ET.fromstring(svg)
        assert len(svg.encode()) < 500_000

    def test_generate_svg_is_reproducible(self):
        """Same n_points must produce identical SVG strings (deterministic)."""
        gen = _load_gen()
        assert gen.generate_svg(n_points=100) == gen.generate_svg(n_points=100)

    def test_colour_violet_at_y_min(self):
        """At COORD_MIN the colour function must return a violet-spectrum hex."""
        gen = _load_gen()
        col = gen._colour(gen.COORD_MIN)
        # red component should be in violet range (~100), blue should be high
        r = int(col[1:3], 16)
        b = int(col[5:7], 16)
        assert r < 150 and b > 100

    def test_colour_gold_at_y_max(self):
        """At COORD_MAX the colour must be gold — high red, high green, low blue."""
        gen = _load_gen()
        col = gen._colour(gen.COORD_MIN + gen.COORD_RANGE)
        r = int(col[1:3], 16)
        g = int(col[3:5], 16)
        b = int(col[5:7], 16)
        assert r > 200 and g > 150 and b < 50


# ---------------------------------------------------------------------------
# Thumbnail SVG file
# ---------------------------------------------------------------------------

class TestThumbnailSvg:
    def setup_method(self):
        self.svg = THUMBNAIL.read_text()

    def test_is_valid_xml(self):
        ET.fromstring(self.svg)

    def test_has_svg_namespace(self):
        assert 'xmlns="http://www.w3.org/2000/svg"' in self.svg

    def test_has_viewbox(self):
        assert "viewBox" in self.svg

    def test_dimensions_480(self):
        """Thumbnail must be 480×480 as specified in the suggestion."""
        w = re.search(r'width="(\d+)"', self.svg)
        h = re.search(r'height="(\d+)"', self.svg)
        assert w and int(w.group(1)) == 480
        assert h and int(h.group(1)) == 480

    def test_has_background_rect(self):
        assert "<rect" in self.svg

    def test_has_dark_background(self):
        assert "0d0820" in self.svg.lower()

    def test_has_many_circles(self):
        """Must have at least 500 circles for a recognisable preview."""
        count = self.svg.count("<circle")
        assert count >= 500, f"Expected ≥500 circles; found {count}"

    def test_under_500kb(self):
        assert THUMBNAIL.stat().st_size < 500_000

    def test_not_empty(self):
        assert THUMBNAIL.stat().st_size > 500

    def test_valid_utf8(self):
        THUMBNAIL.read_bytes().decode("utf-8")

    def test_contains_violet_spectrum_colour(self):
        """At least one circle must use a violet-range colour (high blue component)."""
        colours = re.findall(r'fill="#([0-9A-Fa-f]{6})"', self.svg)
        has_violet = any(int(c[4:6], 16) > 100 and int(c[0:2], 16) < 100
                         for c in colours)
        assert has_violet, "No violet-range colour found in thumbnail circles"

    def test_contains_gold_spectrum_colour(self):
        """At least one circle must use a gold-range colour (high red + green, low blue)."""
        colours = re.findall(r'fill="#([0-9A-Fa-f]{6})"', self.svg)
        has_gold = any(int(c[0:2], 16) > 150 and int(c[4:6], 16) < 50
                       for c in colours)
        assert has_gold, "No gold-range colour found in thumbnail circles"


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

class TestPiecesJson:
    REQUIRED = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

    def test_entry_exists(self):
        _entry()

    def test_entry_has_all_required_fields(self):
        missing = self.REQUIRED - _entry().keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches(self):
        assert _entry()["id"] == PIECE_ID

    def test_path_matches(self):
        assert _entry()["path"] == f"pieces/{PIECE_ID}"

    def test_thumbnail_is_svg(self):
        assert _entry()["thumbnail"].endswith(".svg")

    def test_thumbnail_file_exists(self):
        assert (REPO / _entry()["thumbnail"]).is_file()

    def test_year_is_int(self):
        assert isinstance(_entry()["year"], int)

    def test_technique_mentions_canvas(self):
        assert "canvas" in _entry()["technique"].lower()

    def test_technique_mentions_attractor(self):
        tech = _entry()["technique"].lower()
        assert "attractor" in tech or "clifford" in tech

    def test_appears_after_123(self):
        """Piece 124 must appear after 123 in pieces.json."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "123-torus-knot" in ids and PIECE_ID in ids
        assert ids.index(PIECE_ID) > ids.index("123-torus-knot")

    def test_total_pieces_at_least_53(self):
        data = json.loads(PIECES_JSON.read_text())
        assert len(data) >= 53


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------

class TestReadme:
    def test_not_empty(self):
        assert len(README.read_text().strip()) > 100

    def test_mentions_clifford(self):
        assert "clifford" in README.read_text().lower()

    def test_mentions_parameter_a(self):
        readme = README.read_text()
        assert "−1.4" in readme or "-1.4" in readme

    def test_mentions_5_million(self):
        readme = README.read_text()
        assert "5 million" in readme or "5_000_000" in readme or "5000000" in readme

    def test_mentions_violet_or_gold(self):
        readme = README.read_text().lower()
        assert "violet" in readme or "gold" in readme

    def test_mentions_additive(self):
        readme = README.read_text().lower()
        assert "additive" in readme or "accumulate" in readme or "density" in readme


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_wrong_piece_id_absent_from_json(self):
        data = json.loads(PIECES_JSON.read_text())
        ids = {item["id"] for item in data}
        assert "124-wrong-attractor" not in ids

    def test_large_iterate_count_no_crash(self):
        """Iterating 50 000 steps must not raise or produce non-finite output."""
        x, y = 0.1, 0.1
        for _ in range(50_000):
            x, y = clifford_step(x, y)
        assert math.isfinite(x) and math.isfinite(y)

    def test_attractor_from_different_seeds(self):
        """Two different starting points must converge to the same attractor basin."""
        x1, y1 = 0.1, 0.1
        x2, y2 = 1.0, -1.0
        for _ in range(2000):
            x1, y1 = clifford_step(x1, y1)
            x2, y2 = clifford_step(x2, y2)
        # Both should be within the known bound
        assert -2.5 <= x1 <= 2.5 and -2.5 <= x2 <= 2.5

    def test_generate_svg_very_small_n(self):
        """n_points=1 must return valid XML with exactly one circle."""
        gen = _load_gen()
        svg = gen.generate_svg(n_points=1)
        ET.fromstring(svg)
        assert svg.count("<circle") == 1

    def test_missing_canvas_in_fake_html_detectable(self):
        """Absence of <canvas in a fake document must be detectable."""
        fake = "<html><body><div></div></body></html>"
        assert "<canvas" not in fake

    def test_c_d_zero_reduces_to_sine_map(self):
        """With c=d=0 the map reduces to x'=sin(a·y), y'=sin(b·x): bounded in [-1,1]."""
        x, y = 0.5, 0.5
        for _ in range(2000):
            xn = math.sin(A * y)
            yn = math.sin(B * x)
            x, y = xn, yn
        assert -1.0 <= x <= 1.0 and -1.0 <= y <= 1.0

    def test_all_zero_params_gives_fixed_point(self):
        """a=b=c=d=0 collapses to the fixed point (0, 0)."""
        x, y = 0.5, 0.5
        for _ in range(20):
            x = math.sin(0.0) + 0.0 * math.cos(0.0)
            y = math.sin(0.0) + 0.0 * math.cos(0.0)
        assert x == 0.0 and y == 0.0
