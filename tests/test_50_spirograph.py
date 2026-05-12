"""Tests for pieces/50-spirograph: Hypotrochoid roulette curve animation."""

import importlib.util
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "50-spirograph"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID    = "50-spirograph"
TWO_PI      = 2 * math.pi


# ---------------------------------------------------------------------------
# Python mirror of the JS math in index.html
# ---------------------------------------------------------------------------


def gcd(a: int, b: int) -> int:
    """Euclidean GCD for positive integers."""
    return a if b == 0 else gcd(b, a % b)


def n_turns(R: int, r: int) -> int:
    """Return the number of revolutions of the inner-circle centre before closure.

    Equals r / gcd(R, r) — the smallest positive integer n such that
    2π·n is a full period for both cos(t) and cos((R-r)/r · t).
    """
    return r // gcd(R, r)


def hypotrochoid_pt(t: float, R: int, r: int, d: float) -> tuple[float, float]:
    """Return (x, y) in normalised units (centre at origin) for parameter t.

    Equations:
        x(t) = (R−r)·cos(t) + d·cos((R−r)/r · t)
        y(t) = (R−r)·sin(t) − d·sin((R−r)/r · t)
    """
    Rr = R - r
    k  = Rr / r
    return (Rr * math.cos(t) + d * math.cos(k * t),
            Rr * math.sin(t) - d * math.sin(k * t))


def curve_closes(R: int, r: int, d: float, tol: float = 1e-9) -> bool:
    """Return True iff the hypotrochoid returns to its starting point after one period."""
    period = TWO_PI * n_turns(R, r)
    p0 = hypotrochoid_pt(0.0, R, r, d)
    p1 = hypotrochoid_pt(period, R, r, d)
    return abs(p0[0] - p1[0]) < tol and abs(p0[1] - p1[1]) < tol


def _entry() -> dict:
    """Return the pieces.json entry for this piece, raising if absent."""
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


def _html() -> str:
    return INDEX_HTML.read_text()


def _load_gen():
    """Import generate_thumbnail.py as a module without executing __main__ block."""
    spec = importlib.util.spec_from_file_location(
        "gen50", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# File existence — happy path
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
# Hypotrochoid math — closure property
# ---------------------------------------------------------------------------


class TestHypotrochoidClosure:
    """Verify that each preset closes exactly after n_turns·2π."""

    PRESETS = [
        (5,  3, 0.90),
        (7,  2, 0.85),
        (8,  3, 1.10),
        (11, 4, 0.75),
        (13, 5, 0.95),
        (9,  4, 1.20),
    ]

    def test_r5_r3_closes(self):
        """R=5, r=3: the classic rose-petal spirograph closes after 3 turns."""
        assert curve_closes(5, 3, 0.90 * 3)

    def test_r7_r2_closes(self):
        assert curve_closes(7, 2, 0.85 * 2)

    def test_r8_r3_closes(self):
        assert curve_closes(8, 3, 1.10 * 3)

    def test_r11_r4_closes(self):
        assert curve_closes(11, 4, 0.75 * 4)

    def test_r13_r5_closes(self):
        assert curve_closes(13, 5, 0.95 * 5)

    def test_r9_r4_closes(self):
        assert curve_closes(9, 4, 1.20 * 4)

    def test_all_presets_close(self):
        """Every preset must produce a closed curve."""
        for R, r, dr in self.PRESETS:
            assert curve_closes(R, r, dr * r), f"Preset R={R} r={r} did not close"


# ---------------------------------------------------------------------------
# Hypotrochoid math — n_turns
# ---------------------------------------------------------------------------


class TestNTurns:
    def test_5_3_gives_3_turns(self):
        """R=5, r=3 → gcd=1 → 3 turns to close."""
        assert n_turns(5, 3) == 3

    def test_7_2_gives_2_turns(self):
        assert n_turns(7, 2) == 2

    def test_8_3_gives_3_turns(self):
        assert n_turns(8, 3) == 3

    def test_11_4_gives_4_turns(self):
        assert n_turns(11, 4) == 4

    def test_13_5_gives_5_turns(self):
        assert n_turns(13, 5) == 5

    def test_9_4_gives_4_turns(self):
        assert n_turns(9, 4) == 4

    def test_coprime_ratio_gives_r_turns(self):
        """When gcd(R,r)=1 the number of turns equals r."""
        assert n_turns(7, 3) == 3

    def test_shared_factor_reduces_turns(self):
        """R=10, r=4, gcd=2 → 4/2 = 2 turns (not 4)."""
        assert n_turns(10, 4) == 2


# ---------------------------------------------------------------------------
# Hypotrochoid math — point properties
# ---------------------------------------------------------------------------


class TestHypotrochoidPoints:
    def test_at_t0_y_is_zero(self):
        """At t=0 the sine terms vanish and y must be exactly 0."""
        _, y = hypotrochoid_pt(0.0, 5, 3, 2.7)
        assert abs(y) < 1e-15

    def test_at_t0_x_equals_Rr_plus_d(self):
        """At t=0 both cosines are 1, so x = (R-r) + d."""
        x, _ = hypotrochoid_pt(0.0, 5, 3, 2.7)
        assert abs(x - (5 - 3 + 2.7)) < 1e-12

    def test_max_radius_does_not_exceed_Rr_plus_d(self):
        """Triangle inequality: |point| ≤ (R-r) + d at all times."""
        R, r, dr = 5, 3, 0.9
        d = dr * r
        period = TWO_PI * n_turns(R, r)
        for i in range(1000):
            t   = (i / 999) * period
            px, py = hypotrochoid_pt(t, R, r, d)
            dist = math.hypot(px, py)
            assert dist <= (R - r) + d + 1e-10

    def test_curve_has_multiple_lobes_r5_r3(self):
        """R=5/r=3 preset must produce points that span at least two quadrants."""
        d      = 0.9 * 3
        period = TWO_PI * n_turns(5, 3)
        xs     = [hypotrochoid_pt((i / 500) * period, 5, 3, d)[0] for i in range(501)]
        assert min(xs) < -0.5
        assert max(xs) > 0.5


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_d_zero_gives_circle(self):
        """With d=0 the pen sits at the inner circle's centre and traces a circle."""
        R, r = 5, 3
        Rr   = R - r
        period = TWO_PI * n_turns(R, r)
        for i in range(100):
            t    = (i / 99) * period
            x, y = hypotrochoid_pt(t, R, r, 0.0)
            assert abs(math.hypot(x, y) - Rr) < 1e-10, f"Not a circle at t={t:.3f}"

    def test_large_d_still_closes(self):
        """Even with d much larger than r the curve must still close."""
        assert curve_closes(5, 3, 10.0)

    def test_r_equals_R_minus_1(self):
        """Degenerate ratio R/r = (r+1)/r: gcd=1 → r turns."""
        R, r = 6, 5
        assert n_turns(R, r) == r

    def test_gcd_of_equal_values(self):
        assert gcd(7, 7) == 7

    def test_gcd_commutative(self):
        assert gcd(12, 8) == gcd(8, 12)


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------


class TestFailureModes:
    def test_wrong_id_not_in_pieces_json(self):
        """A made-up piece id must not appear in pieces.json."""
        data = json.loads(PIECES_JSON.read_text())
        ids  = {item["id"] for item in data}
        assert "50-wrong-piece" not in ids

    def test_missing_piece_dir_detectable(self, tmp_path):
        assert not (tmp_path / "50-spirograph-ghost").is_dir()

    def test_curve_does_not_close_at_half_period(self):
        """Sampling at half-period must NOT return to the start (for non-trivial curves)."""
        R, r, d = 5, 3, 2.7
        half = TWO_PI * n_turns(R, r) / 2
        p0   = hypotrochoid_pt(0.0, R, r, d)
        p_half = hypotrochoid_pt(half, R, r, d)
        dist = math.hypot(p_half[0] - p0[0], p_half[1] - p0[1])
        assert dist > 0.1, "Curve closed at half-period — unexpected for R=5/r=3"


# ---------------------------------------------------------------------------
# generate_thumbnail.py module
# ---------------------------------------------------------------------------


class TestGenerateThumbnail:
    def test_gcd_in_module(self):
        gen = _load_gen()
        assert gen.gcd(12, 8) == 4

    def test_hypotrochoid_points_count(self):
        """hypotrochoid_points returns steps+1 points."""
        gen = _load_gen()
        pts = gen.hypotrochoid_points(5, 3, 2.7, 200.0, 200.0, 40.0, 300)
        assert len(pts) == 301

    def test_hypotrochoid_points_closes(self):
        """First and last points must coincide (closed curve)."""
        gen = _load_gen()
        pts = gen.hypotrochoid_points(5, 3, 2.7, 0.0, 0.0, 1.0, 3000)
        x0, y0 = pts[0]
        xf, yf = pts[-1]
        assert abs(x0 - xf) < 1e-6 and abs(y0 - yf) < 1e-6

    def test_generate_svg_returns_string(self):
        gen = _load_gen()
        svg = gen.generate_svg()
        assert isinstance(svg, str)
        assert "<svg" in svg

    def test_generate_svg_valid_xml(self):
        gen = _load_gen()
        ET.fromstring(gen.generate_svg())

    def test_generate_svg_has_polyline(self):
        gen = _load_gen()
        assert "<polyline" in gen.generate_svg()

    def test_generate_svg_to_tmp(self, tmp_path):
        """Writing the SVG to a tmp file produces a valid, non-empty file."""
        gen = _load_gen()
        out = tmp_path / "thumb.svg"
        out.write_text(gen.generate_svg(), encoding="utf-8")
        assert out.stat().st_size > 500
        ET.fromstring(out.read_text())


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


def test_html_self_contained():
    html = _html()
    assert "<script src=" not in html
    assert '<link rel="stylesheet"' not in html


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_canvas_800x800():
    html = _html()
    assert 'width="800"' in html and 'height="800"' in html


def test_html_has_draw_secs_constant():
    """The animation must declare an explicit draw-duration constant."""
    html = _html()
    assert "DRAW_SECS" in html or re.search(r"draw.*secs?", html, re.I)


def test_html_has_fade_secs_constant():
    assert "FADE_SECS" in _html()


def test_html_has_hypotrochoid_formula():
    """The parametric formula variables must appear in the JS source."""
    html = _html()
    assert "cos(t)" in html or "Math.cos" in html


def test_html_has_gcd_function():
    """GCD computation is needed for determining curve closure; must be present."""
    assert "gcd" in _html()


def test_html_has_presets_array():
    html = _html()
    assert "PRESETS" in html


def test_html_has_enough_presets():
    """Must define 5–8 presets (acceptance criterion)."""
    html  = _html()
    m     = re.search(r"PRESETS\s*=\s*\[(.+?)\]", html, re.S)
    assert m, "PRESETS array not found"
    count = m.group(1).count("{")
    assert 5 <= count <= 8, f"Expected 5–8 presets, found {count}"


def test_html_presets_have_distinct_palettes():
    """Each preset object must include bg and fg color fields."""
    html = _html()
    assert html.count("bg:") >= 5
    assert html.count("fg:") >= 5


def test_html_has_steps_per_turn():
    assert "STEPS_PER_TURN" in _html()


def test_html_has_fade_logic():
    html = _html()
    assert "fading" in html or "fade" in html.lower()


def test_html_has_all_six_palette_backgrounds():
    """The six preset background colours must all appear in the source."""
    html   = _html().lower()
    colors = ["fdf6f0", "0d2240", "1c1c1c", "1a0a2e", "0f2210", "18000f"]
    for c in colors:
        assert c in html, f"Background colour #{c} not found in HTML"


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


def test_thumbnail_has_polyline():
    assert "<polyline" in THUMBNAIL.read_text()


def test_thumbnail_polyline_has_many_points():
    """The polyline must have at least 300 coordinate pairs (smooth curve)."""
    svg  = THUMBNAIL.read_text()
    m    = re.search(r'<polyline[^>]+points="([^"]+)"', svg)
    assert m, "<polyline points=...> not found in thumbnail"
    coords = m.group(1).strip().split()
    assert len(coords) >= 300, f"Only {len(coords)} coordinate values found"


def test_thumbnail_has_cream_background():
    assert "fdf6f0" in THUMBNAIL.read_text().lower()


def test_thumbnail_has_rose_stroke():
    assert "c4706a" in THUMBNAIL.read_text().lower()


def test_thumbnail_under_500kb():
    assert THUMBNAIL.stat().st_size < 500_000


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_has_svg_namespace():
    assert 'xmlns="http://www.w3.org/2000/svg"' in THUMBNAIL.read_text()


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


def test_pieces_json_technique_mentions_hypotrochoid_or_spirograph():
    tech = _entry()["technique"].lower()
    assert "hypotrochoid" in tech or "spirograph" in tech or "roulette" in tech


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_parametric():
    assert "parametric" in _entry()["technique"].lower()


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_hypotrochoid():
    readme = README.read_text().lower()
    assert "hypotrochoid" in readme


def test_readme_mentions_closure():
    readme = README.read_text().lower()
    assert "clos" in readme


def test_readme_mentions_parametric_equations():
    readme = README.read_text()
    assert "x(t)" in readme or "parametric" in readme.lower()


def test_readme_mentions_all_six_presets():
    readme = README.read_text()
    for r_val in ("5", "7", "8", "11", "13", "9"):
        assert r_val in readme, f"Preset R={r_val} not mentioned in README"


def test_readme_mentions_animation():
    readme = README.read_text().lower()
    assert "animat" in readme or "draw" in readme or "stroke" in readme


def test_readme_lists_files():
    readme = README.read_text().lower()
    assert "index.html" in readme


def test_readme_has_palette_section():
    readme = README.read_text().lower()
    assert "palette" in readme or "colour" in readme or "color" in readme
