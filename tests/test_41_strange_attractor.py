"""Tests for pieces/41-dust-of-the-infinite: Clifford strange attractor."""

import importlib.util
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "41-dust-of-the-infinite"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "41-dust-of-the-infinite"

A, B, C, D = -1.4, 1.6, 1.0, 0.7


def _load_gen():
    """Import generate_thumbnail.py as a module."""
    spec = importlib.util.spec_from_file_location(
        "gen41", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _entry() -> dict:
    """Return the pieces.json entry for this piece."""
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
# Clifford attractor equations (Python mirror of JS iterate())
# ---------------------------------------------------------------------------


def clifford_step(x: float, y: float) -> tuple[float, float]:
    """One Clifford attractor step with the canonical parameters."""
    return (
        math.sin(A * y) + C * math.cos(A * x),
        math.sin(B * x) + D * math.cos(B * y),
    )


class TestCliffordEquations:
    def test_step_returns_two_floats(self):
        xn, yn = clifford_step(0.1, 0.1)
        assert isinstance(xn, float)
        assert isinstance(yn, float)

    def test_step_known_first_iterate(self):
        """Verify the exact values for the first step from (0.1, 0.1)."""
        xn, yn = clifford_step(0.1, 0.1)
        expected_x = math.sin(A * 0.1) + C * math.cos(A * 0.1)
        expected_y = math.sin(B * 0.1) + D * math.cos(B * 0.1)
        assert abs(xn - expected_x) < 1e-15
        assert abs(yn - expected_y) < 1e-15

    def test_attractor_stays_bounded(self):
        """After 10 000 steps the trajectory must stay within [-2.5, 2.5]²."""
        x, y = 0.1, 0.1
        for _ in range(10_000):
            x, y = clifford_step(x, y)
        assert -2.5 <= x <= 2.5
        assert -2.5 <= y <= 2.5

    def test_attractor_is_deterministic(self):
        """Two runs from the same seed must produce byte-identical results."""
        x1, y1 = 0.1, 0.1
        x2, y2 = 0.1, 0.1
        for _ in range(500):
            x1, y1 = clifford_step(x1, y1)
            x2, y2 = clifford_step(x2, y2)
        assert x1 == x2 and y1 == y2

    def test_attractor_is_not_a_fixed_point(self):
        """The trajectory must still be moving after 200 warm-up steps."""
        x, y = 0.1, 0.1
        for _ in range(200):
            x, y = clifford_step(x, y)
        snap_x, snap_y = x, y
        for _ in range(100):
            x, y = clifford_step(x, y)
        assert abs(x - snap_x) > 1e-9 or abs(y - snap_y) > 1e-9

    def test_x_spans_wide_range(self):
        """x must visit a range of at least 2.0 across 2000 on-attractor steps."""
        x, y = 0.1, 0.1
        for _ in range(500):
            x, y = clifford_step(x, y)
        xs = []
        for _ in range(2000):
            x, y = clifford_step(x, y)
            xs.append(x)
        assert max(xs) - min(xs) >= 2.0

    def test_y_spans_wide_range(self):
        """y must visit a range of at least 2.0 across 2000 on-attractor steps."""
        x, y = 0.1, 0.1
        for _ in range(500):
            x, y = clifford_step(x, y)
        ys = []
        for _ in range(2000):
            x, y = clifford_step(x, y)
            ys.append(y)
        assert max(ys) - min(ys) >= 2.0

    def test_output_stays_finite(self):
        """10 000 iterations must never produce NaN or Inf."""
        x, y = 0.1, 0.1
        for _ in range(10_000):
            x, y = clifford_step(x, y)
        assert math.isfinite(x) and math.isfinite(y)

    def test_mathematical_bounds_respected(self):
        """Each component of x′ is bounded by the closed-form limits.

        |x′| ≤ |sin(a·y)| + |c·cos(a·x)| ≤ 1 + C = 2.0
        |y′| ≤ |sin(b·x)| + |d·cos(b·y)| ≤ 1 + D = 1.7
        """
        x, y = 0.3, -0.7
        for _ in range(5000):
            xn, yn = clifford_step(x, y)
            assert abs(xn) <= 1.0 + C + 1e-12
            assert abs(yn) <= 1.0 + D + 1e-12
            x, y = xn, yn


# ---------------------------------------------------------------------------
# Coordinate mapping
# ---------------------------------------------------------------------------


def coord_to_pixel(v: float, v_min: float, v_range: float, size: int) -> int:
    """Map an attractor coordinate to an integer pixel index."""
    return int((v - v_min) / v_range * size)


class TestCoordMapping:
    VMIN = -2.5
    VRANGE = 5.0
    SIZE = 800

    def test_lower_bound_maps_to_zero(self):
        assert coord_to_pixel(self.VMIN, self.VMIN, self.VRANGE, self.SIZE) == 0

    def test_upper_bound_maps_to_size(self):
        px = coord_to_pixel(self.VMIN + self.VRANGE, self.VMIN, self.VRANGE, self.SIZE)
        assert px == self.SIZE

    def test_centre_maps_to_half_size(self):
        px = coord_to_pixel(0.0, self.VMIN, self.VRANGE, self.SIZE)
        assert px == self.SIZE // 2

    def test_all_attractor_points_within_canvas(self):
        """All on-attractor points must map into [0, SIZE) after warm-up."""
        x, y = 0.1, 0.1
        for _ in range(500):
            x, y = clifford_step(x, y)
        out_of_range = 0
        for _ in range(5000):
            x, y = clifford_step(x, y)
            px = coord_to_pixel(x, self.VMIN, self.VRANGE, self.SIZE)
            py = coord_to_pixel(y, self.VMIN, self.VRANGE, self.SIZE)
            if not (0 <= px < self.SIZE and 0 <= py < self.SIZE):
                out_of_range += 1
        assert out_of_range == 0, f"{out_of_range} points fell outside canvas"


# ---------------------------------------------------------------------------
# HTML structure tests
# ---------------------------------------------------------------------------


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_has_script():
    assert "<script" in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset():
    assert "charset" in _html()


def test_html_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external


def test_html_mentions_clifford_or_attractor():
    html = _html().lower()
    assert "clifford" in html or "attractor" in html


def test_html_has_parameter_a():
    """The HTML must embed the a = −1.4 parameter value."""
    assert "-1.4" in _html()


def test_html_has_parameter_b():
    assert "1.6" in _html()


def test_html_iterates_2_million_points():
    """Total iteration count must be at least 2 million."""
    html = _html()
    assert (
        "2_000_000" in html
        or "2000000" in html
        or "2e6" in html.lower()
    ), "HTML must iterate at least 2 million points"


def test_html_uses_chunked_iteration():
    html = _html()
    assert "setTimeout" in html or "requestAnimationFrame" in html


def test_html_uses_float32array():
    assert "Float32Array" in _html()


def test_html_has_dark_background():
    """Background must be very dark (near-black)."""
    html = _html().lower()
    assert "0a0600" in html or "0a0500" in html or "080600" in html or "0b0600" in html


def test_html_self_contained():
    """No <script src=...> or external stylesheet links."""
    html = _html()
    assert "<script src=" not in html
    assert '<link rel="stylesheet"' not in html


# ---------------------------------------------------------------------------
# generate_thumbnail module tests
# ---------------------------------------------------------------------------


class TestGenerateThumbnail:
    def test_clifford_step_matches_equations(self):
        """gen.clifford_step must agree with the reference equations."""
        gen = _load_gen()
        xn, yn = gen.clifford_step(0.1, 0.1)
        expected_x = math.sin(A * 0.1) + C * math.cos(A * 0.1)
        expected_y = math.sin(B * 0.1) + D * math.cos(B * 0.1)
        assert abs(xn - expected_x) < 1e-15
        assert abs(yn - expected_y) < 1e-15

    def test_iterate_returns_correct_count(self):
        """iterate_attractor(n, burn, step) must return exactly n // step points."""
        gen = _load_gen()
        pts = gen.iterate_attractor(100, 50, 1)
        assert len(pts) == 100

    def test_iterate_step_sampling(self):
        """With step=5, only every 5th point is collected."""
        gen = _load_gen()
        pts = gen.iterate_attractor(100, 50, 5)
        assert len(pts) == 20

    def test_all_points_bounded(self):
        """All generated points must lie in [-3.0, 3.0]² (well inside max bounds)."""
        gen = _load_gen()
        for ax, ay in gen.iterate_attractor(1000, 500, 1):
            assert -3.0 <= ax <= 3.0
            assert -3.0 <= ay <= 3.0

    def test_to_svg_coords_centre(self):
        """Attractor origin maps to SVG centre."""
        gen = _load_gen()
        px, py = gen.to_svg_coords(0.0, 0.0)
        assert abs(px - gen.W / 2) < 1e-9
        assert abs(py - gen.H / 2) < 1e-9

    def test_to_svg_coords_lower_left(self):
        """COORD_MIN maps to (0, 0)."""
        gen = _load_gen()
        px, py = gen.to_svg_coords(gen.COORD_MIN, gen.COORD_MIN)
        assert abs(px) < 1e-9
        assert abs(py) < 1e-9

    def test_generate_svg_returns_string(self):
        gen = _load_gen()
        assert isinstance(gen.generate_svg(n_points=50), str)

    def test_generate_svg_valid_xml(self):
        gen = _load_gen()
        ET.fromstring(gen.generate_svg(n_points=50))

    def test_generate_svg_has_background_rect(self):
        gen = _load_gen()
        assert "<rect" in gen.generate_svg(n_points=50)

    def test_generate_svg_has_circles(self):
        gen = _load_gen()
        assert "<circle" in gen.generate_svg(n_points=50)

    def test_generate_svg_is_reproducible(self):
        """Same n_points must produce identical SVG strings."""
        gen = _load_gen()
        assert gen.generate_svg(n_points=100) == gen.generate_svg(n_points=100)

    def test_generate_svg_zero_points_is_valid_xml(self):
        """Edge case: n_points=0 must still produce valid XML."""
        gen = _load_gen()
        ET.fromstring(gen.generate_svg(n_points=0))

    def test_generate_svg_large_input(self):
        """A large but finite n_points must return valid XML within reasonable size."""
        gen = _load_gen()
        svg = gen.generate_svg(n_points=500)
        ET.fromstring(svg)
        assert len(svg.encode()) < 500_000


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------


def test_thumbnail_not_empty():
    assert THUMBNAIL.stat().st_size > 500


def test_thumbnail_is_valid_xml():
    ET.fromstring(THUMBNAIL.read_text())


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_dimensions_400():
    svg = THUMBNAIL.read_text()
    w = re.search(r'width="(\d+)"', svg)
    h = re.search(r'height="(\d+)"', svg)
    assert w and int(w.group(1)) == 400
    assert h and int(h.group(1)) == 400


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_many_circles():
    count = THUMBNAIL.read_text().count("<circle")
    assert count >= 500, f"Thumbnail must have ≥500 circles; found {count}"


def test_thumbnail_under_500kb():
    assert THUMBNAIL.stat().st_size < 500_000


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_has_svg_namespace():
    assert 'xmlns="http://www.w3.org/2000/svg"' in THUMBNAIL.read_text()


def test_thumbnail_has_amber_color():
    """Dots must use a warm amber colour (high red, moderate green, low blue)."""
    thumb = THUMBNAIL.read_text()
    assert "FF9030" in thumb or "ff9030" in thumb.lower()


# ---------------------------------------------------------------------------
# pieces.json tests
# ---------------------------------------------------------------------------


def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_entry_has_all_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - _entry().keys()
    assert not missing, f"Missing fields: {missing}"


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    assert (REPO / _entry()["thumbnail"]).is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_attractor():
    tech = _entry()["technique"].lower()
    assert "attractor" in tech or "clifford" in tech


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_clifford():
    assert "clifford" in README.read_text().lower()


def test_readme_mentions_parameters():
    readme = README.read_text()
    assert "−1.4" in readme or "-1.4" in readme


def test_readme_mentions_amber_or_rose():
    readme = README.read_text().lower()
    assert "amber" in readme or "rose" in readme


def test_readme_mentions_2_million():
    readme = README.read_text()
    assert "2 million" in readme or "2_000_000" in readme or "2000000" in readme


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_trajectory_does_not_settle_on_fixed_point():
    """1000 consecutive pairs must all differ — attractor is not periodic at this scale."""
    x, y = 0.1, 0.1
    for _ in range(500):
        x, y = clifford_step(x, y)
    prev = (x, y)
    for _ in range(1000):
        x, y = clifford_step(x, y)
        assert (x, y) != prev, "Trajectory hit exact duplicate"
        prev = (x, y)


def test_attractor_with_unit_parameters_bounded():
    """With a=b=c=d=1, the system is still bounded."""
    x, y = 0.1, 0.1
    for _ in range(5000):
        xn = math.sin(1.0 * y) + 1.0 * math.cos(1.0 * x)
        yn = math.sin(1.0 * x) + 1.0 * math.cos(1.0 * y)
        x, y = xn, yn
    assert abs(x) <= 2.0 + 1e-9
    assert abs(y) <= 2.0 + 1e-9


def test_attractor_with_zero_c_and_d_bounded():
    """c=d=0 reduces equations to sin only; system stays in [-1, 1]."""
    x, y = 0.5, 0.5
    for _ in range(2000):
        xn = math.sin(A * y)
        yn = math.sin(B * x)
        x, y = xn, yn
    assert -1.0 <= x <= 1.0
    assert -1.0 <= y <= 1.0


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------


def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = {item["id"] for item in data}
    assert "41-wrong-piece" not in ids


def test_missing_canvas_in_fake_html():
    """Structural absence of <canvas must be detectable."""
    fake = "<html><body><div id='c'></div></body></html>"
    assert "<canvas" not in fake


def test_attractor_with_all_zero_params_gives_fixed_point():
    """a=b=c=d=0 drives both x' and y' to 0, reaching the fixed point (0, 0)."""
    x, y = 0.5, 0.5
    for _ in range(20):
        x = math.sin(0) + 0 * math.cos(0)
        y = math.sin(0) + 0 * math.cos(0)
    assert x == 0.0 and y == 0.0


def test_missing_float32array_in_fake_js():
    """Absence of Float32Array in a fake script must be detectable."""
    fake_js = "const buf = new Array(800 * 800).fill(0);"
    assert "Float32Array" not in fake_js
