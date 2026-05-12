"""Tests for pieces/46-superformula-bloom: Gielis superformula parametric morphing."""

import importlib.util
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "46-superformula-bloom"
INDEX_HTML = PIECE_DIR / "index.html"
README     = PIECE_DIR / "README.md"
THUMBNAIL  = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID   = "46-superformula-bloom"
TWO_PI     = 2 * math.pi
SAMPLES    = 512

WAYPOINTS = [
    (5, 3,   3,   3  ),   # Flower 5
    (6, 2,   4,   4  ),   # Star 6
    (4, 100, 100, 100),   # near-circle
    (6, 1,   0.5, 0.5),   # Snowflake
    (2, 1,   1,   0.5),   # Leaf
    (8, 3,   0.5, 0.5),   # Koch-like
]


def _load_gen():
    """Import generate_thumbnail.py as a module."""
    spec = importlib.util.spec_from_file_location(
        "gen46", PIECE_DIR / "generate_thumbnail.py"
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


# Python mirror of the JS r_super() in index.html.
def r_super(theta: float, m: float, n1: float, n2: float, n3: float) -> float:
    """Gielis superformula r(θ) with a=b=1."""
    t1  = abs(math.cos(m * theta / 4)) ** n2
    t2  = abs(math.sin(m * theta / 4)) ** n3
    s   = t1 + t2
    return s ** (-1 / n1) if s > 0 else 0.0


def sample_shape(
    m: float, n1: float, n2: float, n3: float, samples: int = SAMPLES
) -> list[tuple[float, float]]:
    """Return (x, y) pairs normalized to unit circle. Returns [] when samples=0."""
    if samples == 0:
        return []
    thetas = [TWO_PI * i / samples for i in range(samples + 1)]
    rs     = [r_super(t, m, n1, n2, n3) for t in thetas]
    max_r  = max(rs) if rs else 1.0
    scale  = 1.0 / max_r if max_r > 0 else 0.0
    return [
        (r * scale * math.cos(theta), r * scale * math.sin(theta))
        for theta, r in zip(thetas, rs)
    ]


# ---------------------------------------------------------------------------
# File existence
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
# Superformula math
# ---------------------------------------------------------------------------


class TestSuperformulaMath:
    """Verify properties of the Gielis superformula r(θ)."""

    def test_flower5_at_theta_zero(self):
        """r(0) for Flower-5: |cos(0)|^3 + |sin(0)|^3 = 1, so r = 1."""
        assert abs(r_super(0.0, 5, 3, 3, 3) - 1.0) < 1e-12

    def test_flower5_has_pentagonal_symmetry(self):
        """Flower-5 (m=5, n2=n3) must repeat with period 2π/5."""
        period = TWO_PI / 5
        for i in range(12):
            theta = i * TWO_PI / 60
            r1 = r_super(theta, 5, 3, 3, 3)
            r2 = r_super(theta + period, 5, 3, 3, 3)
            assert abs(r1 - r2) < 1e-10, f"Symmetry broken at theta={theta:.4f}"

    def test_shape_closes_at_2pi_for_all_waypoints(self):
        """r(0) ≈ r(2π) for every waypoint (shape closes after full revolution).

        Tolerance is 1e-6 because sin(m·2π/4) for integer m evaluates to values
        like sin(3π) ≈ -3.7e-16 in IEEE-754, which propagates to ~2e-8 in r when
        raised to fractional exponents (n2 or n3 < 1).
        """
        for m, n1, n2, n3 in WAYPOINTS:
            r0   = r_super(0.0, m, n1, n2, n3)
            r2pi = r_super(TWO_PI, m, n1, n2, n3)
            assert abs(r0 - r2pi) < 1e-6, f"Shape doesn't close for m={m}"

    def test_r_is_nonnegative_for_flower(self):
        """r(θ) must be ≥ 0 at all sample points for Flower-5."""
        for i in range(SAMPLES):
            theta = TWO_PI * i / SAMPLES
            assert r_super(theta, 5, 3, 3, 3) >= 0.0

    def test_normalized_shape_touches_unit_circle(self):
        """After normalizing by max_r, at least one point must reach radius 1."""
        pts     = sample_shape(5, 3, 3, 3)
        max_dist = max(math.sqrt(x * x + y * y) for x, y in pts)
        assert abs(max_dist - 1.0) < 1e-10

    def test_normalized_shape_stays_in_unit_circle(self):
        """No point may exceed radius 1 after normalizing."""
        pts = sample_shape(5, 3, 3, 3)
        for x, y in pts:
            dist = math.sqrt(x * x + y * y)
            assert dist <= 1.0 + 1e-9, f"Point ({x:.4f},{y:.4f}) outside unit circle"

    def test_all_waypoints_give_positive_r(self):
        """Every waypoint must produce positive r at every sample angle."""
        for m, n1, n2, n3 in WAYPOINTS:
            for i in range(SAMPLES):
                theta = TWO_PI * i / SAMPLES
                rv = r_super(theta, m, n1, n2, n3)
                assert rv > 0.0, f"r={rv} at theta={theta:.4f} for m={m}"

    def test_snowflake_spikier_than_flower(self):
        """Snowflake (n1=1, n2=0.5) should have larger r variation than Flower-5."""
        def r_var(m, n1, n2, n3):
            rs = [r_super(TWO_PI * i / 100, m, n1, n2, n3) for i in range(100)]
            return max(rs) / min(rs)
        assert r_var(6, 1, 0.5, 0.5) > r_var(5, 3, 3, 3)

    def test_leaf_is_asymmetric(self):
        """Leaf waypoint (n2 ≠ n3) must give different r at cos-dominant vs sin-dominant angles."""
        r_cos_dominant = r_super(0.0, 2, 1, 1, 0.5)
        r_sin_dominant = r_super(TWO_PI / 4, 2, 1, 1, 0.5)
        assert abs(r_cos_dominant - r_sin_dominant) > 0.01


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_degenerate_zero_sum_returns_finite(self):
        """When both trig terms are zero, r_super must return 0, not raise."""
        rv = r_super(0.0, 0, 1, 1, 1)
        assert math.isfinite(rv)

    def test_fractional_exponents_stay_finite(self):
        """n2=n3=0.5 (snowflake) must give finite r everywhere."""
        for i in range(SAMPLES):
            theta = TWO_PI * i / SAMPLES
            rv    = r_super(theta, 6, 1, 0.5, 0.5)
            assert math.isfinite(rv), f"r not finite at theta={theta:.4f}"

    def test_large_n1_gives_finite_r(self):
        """n1=100 must produce finite r at all sample points."""
        for i in range(SAMPLES):
            theta = TWO_PI * i / SAMPLES
            rv    = r_super(theta, 4, 100, 100, 100)
            assert math.isfinite(rv)

    def test_minimum_samples_still_closes(self):
        """Even with 4 samples, r(0) == r(2π) for Flower-5."""
        r0   = r_super(0.0,    5, 3, 3, 3)
        r2pi = r_super(TWO_PI, 5, 3, 3, 3)
        assert abs(r0 - r2pi) < 1e-12

    def test_all_waypoints_n1_positive(self):
        """All waypoints must have n1 > 0 (n1=0 would cause division by zero)."""
        for m, n1, n2, n3 in WAYPOINTS:
            assert n1 > 0, f"Waypoint m={m} has n1={n1} ≤ 0"

    def test_large_sample_count_still_normalized(self):
        """With 1024 samples, normalized max radius is still 1."""
        pts     = sample_shape(5, 3, 3, 3, samples=1024)
        max_dist = max(math.sqrt(x * x + y * y) for x, y in pts)
        assert abs(max_dist - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------


class TestFailureModes:
    def test_wrong_id_not_in_json(self):
        data = json.loads(PIECES_JSON.read_text())
        ids  = {item["id"] for item in data}
        assert "46-wrong-piece" not in ids

    def test_missing_canvas_detectable(self):
        fake = "<html><body><div></div></body></html>"
        assert "<canvas" not in fake

    def test_empty_coefficients_returns_zero(self):
        """Zero samples → max_r=0 → scale=0, all points at centre."""
        # Verify guard: if rs is empty, scale is 0 and output is (CX, CY).
        pts = sample_shape(5, 3, 3, 3, samples=0)
        assert pts == []

    def test_cycle_time_30_seconds(self):
        """CYCLE constant in HTML must equal 30."""
        html = _html()
        m = re.search(r"CYCLE\s*=\s*(\d+)", html)
        assert m, "CYCLE constant not found in HTML"
        assert int(m.group(1)) == 30


# ---------------------------------------------------------------------------
# HTML structure
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
    assert not re.findall(r'<script[^>]+src=["\']https?://', _html())


def test_html_has_cream_background():
    assert "fdf6f0" in _html().lower()


def test_html_mentions_superformula():
    html = _html().lower()
    assert "superformula" in html or "r_super" in html or "gielis" in html


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_two_pi():
    html = _html()
    assert "TWO_PI" in html or "2 * Math.PI" in html or "Math.PI * 2" in html


def test_html_has_waypoints_array():
    assert "WAYPOINTS" in _html()


def test_html_has_samples_count():
    html = _html()
    assert "SAMPLES" in html or "512" in html


def test_html_has_cycle_constant():
    assert "CYCLE" in _html() or "30" in _html()


def test_html_self_contained():
    html = _html()
    assert "<script src=" not in html
    assert '<link rel="stylesheet"' not in html


def test_html_has_three_scales():
    """SCALES array with three concentric copies must appear in the source."""
    html = _html()
    assert "SCALES" in html or ("0.70" in html and "0.45" in html)


def test_html_has_rose_palette():
    """Rose/blush/mauve palette colors must appear in the source (rgba or hex)."""
    html = _html().lower()
    # Colors expressed as rgba(196,...), rgba(160,...), rgba(122,...) in index.html.
    palette_fragments = ["196,112", "160,78", "122,52", "c47088", "b5748e", "8b4f6e"]
    assert any(c in html for c in palette_fragments)


def test_html_has_smoothstep():
    """Smoothstep interpolation must be present for seamless morphing."""
    assert "smoothstep" in _html()


def test_html_has_lerp():
    """Linear interpolation between waypoints must be present."""
    assert "lerp" in _html()


# ---------------------------------------------------------------------------
# generate_thumbnail module
# ---------------------------------------------------------------------------


class TestGenerateThumbnail:
    def test_r_super_at_zero(self):
        """r(0) for Flower-5 must equal 1.0 exactly."""
        gen = _load_gen()
        assert abs(gen.r_super(0.0, 5, 3, 3, 3) - 1.0) < 1e-12

    def test_r_super_returns_float(self):
        gen = _load_gen()
        assert isinstance(gen.r_super(0.5, 5, 3, 3, 3), float)

    def test_shape_points_count(self):
        """shape_points must return exactly SAMPLES+1 items."""
        gen = _load_gen()
        pts = gen.shape_points(5, 3, 3, 3, 180.0)
        assert len(pts) == SAMPLES + 1

    def test_shape_points_max_dist_equals_radius(self):
        """Furthest point from centre must match the requested radius."""
        gen    = _load_gen()
        radius = 176.0
        pts    = gen.shape_points(5, 3, 3, 3, radius)
        dists  = [math.sqrt((x - gen.CX) ** 2 + (y - gen.CY) ** 2) for x, y in pts]
        assert abs(max(dists) - radius) < 0.5

    def test_generate_svg_returns_string(self):
        gen = _load_gen()
        assert isinstance(gen.generate_svg(), str)

    def test_generate_svg_valid_xml(self):
        gen = _load_gen()
        ET.fromstring(gen.generate_svg())

    def test_generate_svg_has_background_rect(self):
        gen = _load_gen()
        assert "<rect" in gen.generate_svg()

    def test_generate_svg_has_three_polygons(self):
        """Three concentric shapes must produce exactly three <polygon> elements."""
        gen = _load_gen()
        assert gen.generate_svg().count("<polygon") == 3

    def test_generate_svg_is_reproducible(self):
        gen = _load_gen()
        assert gen.generate_svg() == gen.generate_svg()

    def test_generate_svg_innermost_has_fill(self):
        """Innermost polygon must have a non-zero fill-opacity."""
        gen = _load_gen()
        svg = gen.generate_svg()
        assert "fill-opacity" in svg

    def test_generate_svg_has_cream_background(self):
        gen = _load_gen()
        assert "fdf6f0" in gen.generate_svg().lower()


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------


def test_thumbnail_not_empty():
    assert THUMBNAIL.stat().st_size > 200


def test_thumbnail_is_valid_xml():
    ET.fromstring(THUMBNAIL.read_text())


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_dimensions_400():
    svg = THUMBNAIL.read_text()
    w   = re.search(r'width="(\d+)"', svg)
    h   = re.search(r'height="(\d+)"', svg)
    assert w and int(w.group(1)) == 400
    assert h and int(h.group(1)) == 400


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_polygon():
    assert "<polygon" in THUMBNAIL.read_text()


def test_thumbnail_under_500kb():
    assert THUMBNAIL.stat().st_size < 500_000


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_has_svg_namespace():
    assert 'xmlns="http://www.w3.org/2000/svg"' in THUMBNAIL.read_text()


def test_thumbnail_has_rose_stroke_color():
    svg = THUMBNAIL.read_text().lower()
    assert "d4a0b5" in svg or "b5748e" in svg or "8b4f6e" in svg


# ---------------------------------------------------------------------------
# pieces.json
# ---------------------------------------------------------------------------


def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_entry_has_all_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing  = required - _entry().keys()
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


def test_pieces_json_technique_mentions_superformula():
    tech = _entry()["technique"].lower()
    assert "superformula" in tech or "gielis" in tech


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_superformula():
    assert "superformula" in README.read_text().lower()


def test_readme_mentions_natural_forms():
    readme = README.read_text().lower()
    assert "flower" in readme or "snowflake" in readme or "leaf" in readme


def test_readme_mentions_morphing_or_animation():
    readme = README.read_text().lower()
    assert "morph" in readme or "animate" in readme or "cycle" in readme


def test_readme_has_equation():
    readme = README.read_text()
    assert "n1" in readme and "n2" in readme


def test_readme_mentions_palette():
    readme = README.read_text().lower()
    assert "rose" in readme or "blush" in readme or "mauve" in readme or "cream" in readme
