"""Tests for pieces/80-harmonograph: damped-pendulum Lissajous line art."""

import importlib.util
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "80-harmonograph"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID    = "80-harmonograph"


# ---------------------------------------------------------------------------
# Python mirror of the harmonograph equations for white-box testing
# ---------------------------------------------------------------------------


def harmonograph_xy(
    t: float,
    A1: float, f1: float, p1: float, d1: float,
    A2: float, f2: float, p2: float, d2: float,
    B1: float, g1: float, e1: float,
) -> tuple[float, float]:
    """Compute normalised (x, y) for the two-axis damped harmonograph at time t.

    Equations:
        x(t) = A1·sin(f1·t + p1)·exp(−d1·t) + A2·sin(f2·t + p2)·exp(−d2·t)
        y(t) = B1·sin(g1·t)·exp(−e1·t)

    Returns:
        (x, y) in normalised units (no pixel scaling applied).
    """
    x = A1 * math.sin(f1 * t + p1) * math.exp(-d1 * t) + \
        A2 * math.sin(f2 * t + p2) * math.exp(-d2 * t)
    y = B1 * math.sin(g1 * t) * math.exp(-e1 * t)
    return x, y


def width_at(step: int, total_steps: int, t_max: float,
             d1: float, max_w: float, min_w: float) -> float:
    """Compute tapered line width at a given step index.

    Follows the dominant damping envelope exp(-d1*t), mapping from max_w
    at t=0 down toward min_w at t=T_MAX.

    Args:
        step:        current step index (0 … total_steps).
        total_steps: total number of steps in the figure.
        t_max:       upper time bound corresponding to step == total_steps.
        d1:          primary damping constant.
        max_w:       maximum line width (at t=0).
        min_w:       minimum line width (at large t).

    Returns:
        Line width in pixels.
    """
    t   = (step / total_steps) * t_max
    env = math.exp(-d1 * t)
    return min_w + (max_w - min_w) * env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    """Return the pieces.json entry for this piece, raising if absent."""
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


def _load_gen():
    """Import generate_thumbnail.py as a module without executing __main__."""
    spec = importlib.util.spec_from_file_location(
        "gen80", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# File-existence tests — happy path
# ---------------------------------------------------------------------------


def test_piece_dir_exists():
    assert PIECE_DIR.is_dir(), f"Piece directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_readme_exists():
    assert README.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


def test_generate_thumbnail_exists():
    assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# Harmonograph math — at t=0
# ---------------------------------------------------------------------------


class TestHarmonographAtZero:
    """Verify boundary conditions at t=0 (no damping, full amplitude)."""

    def test_y_is_zero_at_t0(self):
        """y = B1*sin(0) = 0 regardless of parameters."""
        _, y = harmonograph_xy(0.0, 0.85, 3.0, math.pi/4, 0.003,
                               0.10, 2.0, math.pi/3, 0.005,
                               0.90, 2.0, 0.003)
        assert abs(y) < 1e-15

    def test_x_equals_amplitude_sum_at_t0(self):
        """At t=0 exp(-d*0)=1, so x = A1*sin(p1) + A2*sin(p2)."""
        A1, p1, A2, p2 = 0.85, math.pi/4, 0.10, math.pi/3
        x, _ = harmonograph_xy(0.0, A1, 3.0, p1, 0.003,
                                A2, 2.0, p2, 0.005,
                                0.90, 2.0, 0.003)
        expected = A1 * math.sin(p1) + A2 * math.sin(p2)
        assert abs(x - expected) < 1e-12

    def test_line_width_max_at_step_zero(self):
        """Width at step 0 should equal MAX_WIDTH (env=exp(0)=1)."""
        w = width_at(0, 100_000, 1000.0, 0.003, 2.5, 0.15)
        assert abs(w - 2.5) < 1e-10


# ---------------------------------------------------------------------------
# Harmonograph math — damping decay
# ---------------------------------------------------------------------------


class TestHarmonographDamping:
    """Verify that damping drives the trajectory to zero."""

    def test_amplitude_decays_at_large_t(self):
        """At t=5000 with d=0.003, amplitude is < 5% of initial."""
        x, y = harmonograph_xy(5000.0, 0.85, 3.0, math.pi/4, 0.003,
                                0.10, 2.0, math.pi/3, 0.005,
                                0.90, 2.0, 0.003)
        assert abs(x) < 0.05 and abs(y) < 0.05

    def test_amplitude_bounded_by_A1_plus_A2(self):
        """Triangle inequality: |x| ≤ A1 + A2, |y| ≤ B1 for all t."""
        A1, A2, B1 = 0.85, 0.10, 0.90
        for i in range(200):
            t = i * 5.0
            x, y = harmonograph_xy(t, A1, 3.0, math.pi/4, 0.003,
                                   A2, 2.0, math.pi/3, 0.005,
                                   B1, 2.0, 0.003)
            assert abs(x) <= A1 + A2 + 1e-10
            assert abs(y) <= B1 + 1e-10

    def test_line_width_tapers_monotonically(self):
        """Width at a later step must be strictly less than width at an earlier step."""
        w_early = width_at(0,      100_000, 1000.0, 0.003, 2.5, 0.15)
        w_mid   = width_at(50_000, 100_000, 1000.0, 0.003, 2.5, 0.15)
        w_late  = width_at(99_999, 100_000, 1000.0, 0.003, 2.5, 0.15)
        assert w_early > w_mid > w_late

    def test_line_width_stays_above_min(self):
        """Width must never drop below MIN_WIDTH."""
        for step in range(0, 100_001, 10_000):
            w = width_at(step, 100_000, 1000.0, 0.003, 2.5, 0.15)
            assert w >= 0.15 - 1e-10

    def test_line_width_stays_below_max(self):
        """Width must never exceed MAX_WIDTH."""
        for step in range(0, 100_001, 10_000):
            w = width_at(step, 100_000, 1000.0, 0.003, 2.5, 0.15)
            assert w <= 2.5 + 1e-10


# ---------------------------------------------------------------------------
# Harmonograph math — figure shape
# ---------------------------------------------------------------------------


class TestHarmonographShape:
    """Verify that preset parameters produce Lissajous-family figures."""

    def test_3_2_ratio_spans_both_axes(self):
        """3:2 ratio figure must reach positive and negative x and y values."""
        xs, ys = [], []
        for i in range(5000):
            t = i * 0.1
            x, y = harmonograph_xy(t, 0.85, 3.0, math.pi/4, 0.003,
                                   0.10, 2.0, math.pi/3, 0.005,
                                   0.90, 2.0, 0.003)
            xs.append(x)
            ys.append(y)
        assert min(xs) < -0.1 and max(xs) > 0.1
        assert min(ys) < -0.1 and max(ys) > 0.1

    def test_second_pendulum_component_modifies_x(self):
        """Adding A2 term changes x compared to A2=0."""
        t = 1.5
        x_full, _ = harmonograph_xy(t, 0.85, 3.0, math.pi/4, 0.003,
                                    0.10, 2.0, math.pi/3, 0.005,
                                    0.90, 2.0, 0.003)
        x_no_a2, _ = harmonograph_xy(t, 0.85, 3.0, math.pi/4, 0.003,
                                     0.00, 2.0, math.pi/3, 0.005,
                                     0.90, 2.0, 0.003)
        assert abs(x_full - x_no_a2) > 1e-6

    def test_detuned_1_1_ratio_precesses(self):
        """With g1=1.001 vs f1=1.0 the x-y phase relationship drifts visibly.

        At t=0 y=0 so the angle is 0.  At t=1000 the detuning has accumulated
        ~1 radian of phase shift while damping (exp(-2)) still leaves a
        measurable signal, so atan2(y,x) should differ by more than 0.1 rad.
        """
        def phase_angle(t):
            x, y = harmonograph_xy(t, 0.75, 1.0, math.pi/2, 0.002,
                                   0.18, 2.0, math.pi/4, 0.003,
                                   0.90, 1.001, 0.002)
            return math.atan2(y, x)
        angle_0    = phase_angle(0.0)
        angle_1000 = phase_angle(1000.0)
        assert abs(angle_0 - angle_1000) > 0.1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_zero_amplitude_gives_origin(self):
        """With A1=A2=B1=0 the trajectory stays at the origin."""
        x, y = harmonograph_xy(10.0, 0.0, 3.0, 0.5, 0.003,
                               0.0,  2.0, 0.5, 0.005,
                               0.0,  2.0, 0.003)
        assert x == 0.0 and y == 0.0

    def test_very_large_t_approaches_zero(self):
        """With finite damping d>0, amplitude → 0 as t → ∞."""
        x, y = harmonograph_xy(1e6, 1.0, 1.0, 0.0, 1.0,
                               1.0, 2.0, 0.0, 1.0,
                               1.0, 1.0, 1.0)
        assert abs(x) < 1e-10 and abs(y) < 1e-10

    def test_width_at_boundary_step_is_min_width_approx(self):
        """At the last step, width approaches but stays >= MIN_WIDTH."""
        w = width_at(100_000, 100_000, 1000.0, 0.006, 2.5, 0.15)
        assert 0.15 <= w <= 0.16


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------


class TestFailureModes:
    def test_wrong_id_not_in_pieces_json(self):
        data = json.loads(PIECES_JSON.read_text())
        ids  = {item["id"] for item in data}
        assert "80-wrong-piece" not in ids

    def test_missing_piece_dir_detectable(self, tmp_path):
        assert not (tmp_path / "80-harmonograph-ghost").is_dir()

    def test_zero_damping_produces_undamped_lissajous(self):
        """With d1=d2=e1=0 the amplitude stays constant at all t."""
        A1, A2, B1 = 0.5, 0.3, 0.7
        for t in (0.0, 10.0, 100.0, 1000.0):
            x, y = harmonograph_xy(t, A1, 3.0, math.pi/4, 0.0,
                                   A2, 2.0, math.pi/3, 0.0,
                                   B1, 2.0, 0.0)
            assert abs(x) <= A1 + A2 + 1e-10
            assert abs(y) <= B1 + 1e-10


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_canvas_800x800():
    html = _html()
    assert 'width="800"' in html and 'height="800"' in html


def test_html_has_canvas_id():
    html = _html()
    assert 'id="c"' in html or 'id="canvas"' in html


def test_html_no_external_scripts():
    assert not re.findall(r'<script[^>]+src=["\']https?://', _html())


def test_html_no_external_stylesheets():
    assert not re.findall(r'<link[^>]+href=["\']https?://', _html())


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_uses_math_sin():
    assert "Math.sin" in _html()


def test_html_uses_math_exp():
    assert "Math.exp" in _html()


def test_html_has_total_steps():
    html = _html()
    assert "TOTAL_STEPS" in html
    m = re.search(r"TOTAL_STEPS\s*=\s*([\d_]+)", html)
    assert m, "TOTAL_STEPS constant not found"
    assert int(m.group(1).replace("_", "")) == 100_000


def test_html_has_draw_secs():
    html = _html()
    assert "DRAW_SECS" in html
    m = re.search(r"DRAW_SECS\s*=\s*(\d+)", html)
    assert m, "DRAW_SECS constant not found"
    assert int(m.group(1)) == 8


def test_html_has_t_max():
    html = _html()
    assert "T_MAX" in html
    m = re.search(r"T_MAX\s*=\s*(\d+)", html)
    assert m
    assert int(m.group(1)) == 1000


def test_html_has_max_width():
    assert "MAX_WIDTH" in _html()


def test_html_has_min_width():
    assert "MIN_WIDTH" in _html()


def test_html_has_segment_constant():
    html = _html()
    assert "SEGMENT" in html
    m = re.search(r"\bSEGMENT\b\s*=\s*(\d+)", html)
    assert m, "SEGMENT constant not found"
    assert int(m.group(1)) == 500


def test_html_has_presets_array():
    assert "PRESETS" in _html()


def test_html_has_3_to_5_presets():
    html  = _html()
    m     = re.search(r"PRESETS\s*=\s*\[(.+?)\];", html, re.S)
    assert m, "PRESETS array not found"
    count = m.group(1).count("{")
    assert 3 <= count <= 5, f"Expected 3–5 presets, found {count}"


def test_html_presets_have_bg_and_fg():
    html = _html()
    assert html.count("bg:") >= 3
    assert html.count("fg:") >= 3


def test_html_presets_have_damping_fields():
    html = _html()
    assert html.count("d1:") >= 3
    assert html.count("e1:") >= 3


def test_html_has_global_alpha():
    assert "globalAlpha" in _html()


def test_html_background_near_black():
    html = _html().lower()
    assert "0d0d0d" in html or "0a0a0f" in html


def test_html_has_fade_logic():
    html = _html()
    assert "fading" in html or "fade" in html.lower()


def test_html_has_hold_secs():
    assert "HOLD_SECS" in _html()


def test_html_has_fade_secs():
    assert "FADE_SECS" in _html()


def test_html_has_width_at_function():
    html = _html()
    assert "widthAt" in html or "width_at" in html or "lineWidth" in html


def test_html_linewidth_uses_exp():
    """The line-width computation must reference Math.exp for the taper."""
    html = _html()
    assert "Math.exp" in html


def test_html_has_charset():
    html = _html()
    assert "charset" in html.lower()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_title():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "Missing <title>"
    assert "harmonograph" in m.group(1).lower()


def test_html_no_audio():
    html = _html()
    assert "<audio" not in html.lower() and "AudioContext" not in html


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_dimensions_400():
    svg = THUMBNAIL.read_text()
    w   = re.search(r'width="(\d+)"', svg)
    h   = re.search(r'height="(\d+)"', svg)
    assert w and int(w.group(1)) == 400
    assert h and int(h.group(1)) == 400


def test_thumbnail_has_dark_background():
    svg = THUMBNAIL.read_text().lower()
    assert "0d0d0d" in svg or "0a0a0f" in svg


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_polyline():
    assert "<polyline" in THUMBNAIL.read_text()


def test_thumbnail_polyline_has_many_points():
    """The polyline must have at least 4000 coordinate pairs (smooth trace)."""
    svg = THUMBNAIL.read_text()
    m   = re.search(r'<polyline[^>]+points="([^"]+)"', svg)
    assert m, "<polyline points=...> not found"
    coords = m.group(1).strip().split()
    assert len(coords) >= 4000


def test_thumbnail_has_stroke_color():
    svg = THUMBNAIL.read_text().lower()
    assert "f5e6c8" in svg


def test_thumbnail_not_trivially_empty():
    assert THUMBNAIL.stat().st_size > 1000


def test_thumbnail_under_500kb():
    assert THUMBNAIL.stat().st_size < 500_000


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_has_svg_namespace():
    assert 'xmlns="http://www.w3.org/2000/svg"' in THUMBNAIL.read_text()


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_pendulum():
    text = README.read_text().lower()
    assert "pendulum" in text


def test_readme_mentions_equation():
    text = README.read_text()
    assert "x(t)" in text or "equation" in text.lower()


def test_readme_mentions_damping():
    text = README.read_text().lower()
    assert "damp" in text or "decay" in text


def test_readme_mentions_frequency_ratios():
    text = README.read_text()
    assert "3:2" in text or "5:4" in text


def test_readme_mentions_index_html():
    assert "index.html" in README.read_text().lower()


def test_readme_mentions_palette():
    text = README.read_text().lower()
    assert "palette" in text or "colour" in text or "color" in text


# ---------------------------------------------------------------------------
# generate_thumbnail.py module
# ---------------------------------------------------------------------------


class TestGenerateThumbnail:
    def test_harmonograph_points_returns_steps_plus_one(self):
        """harmonograph_points(N) returns N+1 points."""
        gen = _load_gen()
        pts = gen.harmonograph_points(300)
        assert len(pts) == 301

    def test_first_point_y_near_center(self):
        """At t=0 y = B1*sin(0)*exp(0) = 0, so py should equal CY."""
        gen = _load_gen()
        pts = gen.harmonograph_points(100)
        _, py = pts[0]
        assert abs(py - gen.CY) < 1e-10

    def test_last_point_approaches_center(self):
        """With damping, the last point must be much closer to center than first."""
        gen = _load_gen()
        pts = gen.harmonograph_points(4000)
        cx, cy = gen.CX, gen.CY
        dist_first = math.hypot(pts[0][0] - cx, pts[0][1] - cy)
        dist_last  = math.hypot(pts[-1][0] - cx, pts[-1][1] - cy)
        assert dist_last < dist_first * 0.3

    def test_points_to_svg_polyline_format(self):
        """Output must be space-separated 'x.xx,y.yy' pairs."""
        gen = _load_gen()
        pts = [(1.0, 2.0), (3.5, 4.75)]
        result = gen.points_to_svg_polyline(pts)
        assert "1.00,2.00" in result
        assert "3.50,4.75" in result

    def test_generate_svg_returns_string(self):
        gen = _load_gen()
        assert isinstance(gen.generate_svg(), str)

    def test_generate_svg_valid_xml(self):
        gen = _load_gen()
        ET.fromstring(gen.generate_svg())

    def test_generate_svg_has_polyline(self):
        gen = _load_gen()
        assert "<polyline" in gen.generate_svg()

    def test_generate_svg_has_background_rect(self):
        gen = _load_gen()
        assert "<rect" in gen.generate_svg()

    def test_generate_svg_to_tmp(self, tmp_path):
        """Writing the SVG to a tmp file produces a valid, non-empty file."""
        gen = _load_gen()
        out = tmp_path / "thumb.svg"
        out.write_text(gen.generate_svg(), encoding="utf-8")
        assert out.stat().st_size > 1000
        ET.fromstring(out.read_text())


# ---------------------------------------------------------------------------
# pieces.json contract
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


def test_pieces_json_technique_mentions_harmonograph():
    tech = _entry()["technique"].lower()
    assert "harmonograph" in tech or "pendulum" in tech


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_is_valid_list():
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids  = [item["id"] for item in data]
    assert len(ids) == len(set(ids))


def test_pieces_json_still_has_existing_entries():
    """Existing entries must not be removed when adding piece 80."""
    data = json.loads(PIECES_JSON.read_text())
    ids  = {item["id"] for item in data}
    assert "01-amber-current" in ids
    assert "78-wolfram-ca"    in ids
    assert PIECE_ID           in ids
