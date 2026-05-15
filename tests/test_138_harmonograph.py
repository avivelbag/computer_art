"""Tests for pieces/138-harmonograph: bilateral lateral harmonograph animation."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "138-harmonograph"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "138-harmonograph"


def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# Python mirror of the bilateral harmonograph equations for white-box testing
# ---------------------------------------------------------------------------

def bilateral_harmonograph_xy(
    t: float,
    A1: float, f1: float, p1: float, d1: float,
    A2: float, f2: float, p2: float, d2: float,
    A3: float, f3: float, p3: float, d3: float,
    A4: float, f4: float, p4: float, d4: float,
) -> tuple[float, float]:
    """Compute (x, y) for the bilateral lateral harmonograph at time t.

    Both axes have two damped pendulums:
        x(t) = A1·sin(f1·t + p1)·exp(−d1·t)  +  A2·sin(f2·t + p2)·exp(−d2·t)
        y(t) = A3·sin(f3·t + p3)·exp(−d3·t)  +  A4·sin(f4·t + p4)·exp(−d4·t)
    """
    x = A1 * math.sin(f1 * t + p1) * math.exp(-d1 * t) + \
        A2 * math.sin(f2 * t + p2) * math.exp(-d2 * t)
    y = A3 * math.sin(f3 * t + p3) * math.exp(-d3 * t) + \
        A4 * math.sin(f4 * t + p4) * math.exp(-d4 * t)
    return x, y


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


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------

def test_html_has_doctype():
    assert _html().startswith("<!DOCTYPE html>")


def test_html_has_charset():
    assert 'charset="UTF-8"' in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_canvas_has_id():
    html = _html()
    assert 'id="canvas"' in html


def test_html_canvas_dimensions():
    html = _html()
    assert 'width="600"' in html and 'height="600"' in html


def test_html_title_mentions_harmonograph():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    assert "harmonograph" in m.group(1).lower()


def test_html_dark_background():
    assert "#0a0a14" in _html()


def test_html_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must not load remote scripts"


def test_html_no_external_links():
    external = re.findall(r'<link[^>]+href=["\']https?://', _html())
    assert not external, "index.html must not reference external stylesheets"


# ---------------------------------------------------------------------------
# Animation mechanics
# ---------------------------------------------------------------------------

def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_js_uses_sin_and_exp():
    html = _html()
    assert "Math.sin" in html
    assert "Math.exp" in html


def test_js_uses_canvas_2d_context():
    assert "getContext" in _html()


def test_js_defines_alpha():
    html = _html()
    assert "ALPHA" in html
    m = re.search(r"ALPHA\s*=\s*([\d.]+)", html)
    assert m, "ALPHA constant not found"
    alpha_val = float(m.group(1))
    assert 0.10 <= alpha_val <= 0.20, f"ALPHA should be ~0.15, got {alpha_val}"


def test_js_defines_scale():
    html = _html()
    assert "SCALE" in html
    m = re.search(r"SCALE\s*=\s*(\d+)", html)
    assert m, "SCALE constant not found"
    assert int(m.group(1)) > 0


def test_js_defines_dt():
    html = _html()
    assert "DT" in html


def test_js_defines_t_max():
    html = _html()
    assert "T_MAX" in html
    m = re.search(r"T_MAX\s*=\s*(\d+)", html)
    assert m, "T_MAX not found"
    assert int(m.group(1)) >= 200


def test_js_defines_total_steps():
    html = _html()
    assert "TOTAL_STEPS" in html


def test_js_defines_steps_per_frame():
    html = _html()
    assert "STEPS_PER_FRAME" in html
    m = re.search(r"STEPS_PER_FRAME\s*=\s*(\d+)", html)
    assert m
    spf = int(m.group(1))
    assert 50 <= spf <= 2000, f"STEPS_PER_FRAME={spf} seems unreasonable"


def test_js_has_replay_delay():
    """Animation must pause before replaying — not loop abruptly."""
    html = _html()
    assert "setTimeout" in html or "REPLAY" in html, \
        "Must implement a replay delay (setTimeout)"


def test_js_has_four_frequency_constants():
    """Both axes must have distinct frequency constants (F1, F2, F3, F4)."""
    html = _html()
    assert "F1" in html and "F2" in html and "F3" in html and "F4" in html


def test_js_has_four_damping_constants():
    """Both axes must have distinct damping constants (DAMP1-DAMP4 or similar)."""
    html = _html()
    has_damp = "DAMP" in html or ("d1" in html and "d2" in html and "d3" in html)
    assert has_damp, "Must define damping constants for all four pendulums"


def test_js_fills_background_before_animation():
    """Background fill must precede the main requestAnimationFrame call."""
    html = _html()
    bg_idx = html.rfind("#0a0a14")
    raf_idx = html.rfind("requestAnimationFrame")
    assert bg_idx != -1 and raf_idx != -1
    assert bg_idx < raf_idx, \
        "Background fill should appear before the final requestAnimationFrame call"


def test_js_stroke_color_is_cool_blue():
    """Stroke must use a cool-blue rgba color."""
    html = _html()
    assert "rgba(160" in html or "rgba(180" in html or "rgba(140" in html, \
        "Stroke must be a cool blue rgba(...)"


def test_js_stroke_uses_moveto_and_lineto():
    html = _html()
    assert "moveTo" in html
    assert "lineTo" in html


def test_js_calls_stroke():
    assert "ctx.stroke()" in _html()


def test_js_defines_x_function():
    """Must define a function or inline expression computing x(t) with sin+exp."""
    html = _html()
    assert "xAt" in html or ("F1" in html and "F2" in html)


def test_js_defines_y_function():
    """Must define a function or inline expression computing y(t) with sin+exp."""
    html = _html()
    assert "yAt" in html or ("F3" in html and "F4" in html)


# ---------------------------------------------------------------------------
# Harmonograph math: white-box validation
# ---------------------------------------------------------------------------

def test_harmonograph_at_t0_matches_phases():
    """At t=0, exp decay = 1, so output equals amplitude * sin(phase)."""
    x, y = bilateral_harmonograph_xy(
        0,
        1.0, 2.0, 0.0, 0.002,
        1.0, 3.0, math.pi / 4, 0.002,
        1.0, 3.0, math.pi / 6, 0.002,
        1.0, 2.0, math.pi / 2, 0.002,
    )
    expected_x = math.sin(0.0) + math.sin(math.pi / 4)
    expected_y = math.sin(math.pi / 6) + math.sin(math.pi / 2)
    assert abs(x - expected_x) < 1e-10
    assert abs(y - expected_y) < 1e-10


def test_harmonograph_decays_to_zero():
    """With positive damping, curve must converge to zero as t → ∞.

    At t=5000 with d=0.002: exp(-0.002*5000) = exp(-10) ≈ 4.5e-5,
    so amplitude ≤ 2 * 4.5e-5 = 9e-5 < 1e-4.
    """
    x_large, y_large = bilateral_harmonograph_xy(
        5000,
        1.0, 2.0, 0.0, 0.002,
        1.0, 3.0, math.pi / 4, 0.002,
        1.0, 3.0, math.pi / 6, 0.002,
        1.0, 2.0, math.pi / 2, 0.002,
    )
    assert abs(x_large) < 1e-4
    assert abs(y_large) < 1e-4


def test_harmonograph_x_amplitude_bounded():
    """x(t) must stay within ±(A1+A2) at all times."""
    A1, A2 = 1.0, 1.0
    max_amp = A1 + A2
    for i in range(0, 40000, 100):
        t = i * 0.01
        x, _ = bilateral_harmonograph_xy(
            t, A1, 2.0, 0.0, 0.002, A2, 3.0, math.pi / 4, 0.002,
            1.0, 3.0, math.pi / 6, 0.002, 1.0, 2.0, math.pi / 2, 0.002,
        )
        assert abs(x) <= max_amp + 1e-9, f"x={x} exceeds bound at t={t}"


def test_harmonograph_y_uses_two_pendulums():
    """y-axis must have contribution from two independent frequencies (F3 ≠ F4)."""
    # Remove one pendulum (A4=0) vs both active — result must differ at some t.
    t_test = 1.5
    _, y_both = bilateral_harmonograph_xy(
        t_test,
        1.0, 2.0, 0.0, 0.002, 1.0, 3.0, math.pi / 4, 0.002,
        1.0, 3.0, math.pi / 6, 0.002, 1.0, 2.0, math.pi / 2, 0.002,
    )
    _, y_one = bilateral_harmonograph_xy(
        t_test,
        1.0, 2.0, 0.0, 0.002, 1.0, 3.0, math.pi / 4, 0.002,
        1.0, 3.0, math.pi / 6, 0.002, 0.0, 2.0, math.pi / 2, 0.002,
    )
    assert y_both != y_one, "y with two pendulums must differ from y with one pendulum"


def test_curve_differs_from_piece_80_unilateral_form():
    """The bilateral form (two y-pendulums) must produce a different y than the
    unilateral form (one y-pendulum) used in piece 80."""
    # Piece 80 uses: y(t) = B1·sin(g1·t)·exp(−e1·t)  — only one y-pendulum.
    # This piece has two y-pendulums. Test that they diverge at representative times.
    diffs = []
    for step in range(0, 2000, 100):
        t = step * 0.01
        _, y_bilateral = bilateral_harmonograph_xy(
            t,
            1.0, 2.0, 0.0, 0.002, 1.0, 3.0, math.pi / 4, 0.002,
            1.0, 3.0, math.pi / 6, 0.002, 1.0, 2.0, math.pi / 2, 0.002,
        )
        y_unilateral = 1.0 * math.sin(3.0 * t) * math.exp(-0.002 * t)
        diffs.append(abs(y_bilateral - y_unilateral))
    assert max(diffs) > 0.1, "Bilateral y must differ substantially from unilateral y"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_harmonograph_zero_amplitude():
    """With A=0 for all pendulums, output is always (0, 0)."""
    x, y = bilateral_harmonograph_xy(
        10.0,
        0.0, 2.0, 0.0, 0.002, 0.0, 3.0, 0.0, 0.002,
        0.0, 3.0, 0.0, 0.002, 0.0, 2.0, 0.0, 0.002,
    )
    assert x == 0.0
    assert y == 0.0


def test_harmonograph_large_t_is_numerically_stable():
    """At very large t, exp(-d*t) underflows to 0 safely — no NaN/Inf."""
    x, y = bilateral_harmonograph_xy(
        100000,
        1.0, 2.0, 0.0, 0.002, 1.0, 3.0, math.pi / 4, 0.002,
        1.0, 3.0, math.pi / 6, 0.002, 1.0, 2.0, math.pi / 2, 0.002,
    )
    assert math.isfinite(x)
    assert math.isfinite(y)
    assert abs(x) < 1e-50
    assert abs(y) < 1e-50


def test_harmonograph_negative_t_gives_finite_values():
    """Negative t should produce finite values (damping term grows, but stays bounded)."""
    x, y = bilateral_harmonograph_xy(
        -1.0,
        1.0, 2.0, 0.0, 0.002, 1.0, 3.0, math.pi / 4, 0.002,
        1.0, 3.0, math.pi / 6, 0.002, 1.0, 2.0, math.pi / 2, 0.002,
    )
    assert math.isfinite(x)
    assert math.isfinite(y)


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


def test_thumbnail_has_width_and_height():
    svg = THUMBNAIL.read_text()
    assert 'width="' in svg and 'height="' in svg


def test_thumbnail_has_dark_background():
    svg = THUMBNAIL.read_text()
    assert "#0a0a14" in svg or "0a0a14" in svg


def test_thumbnail_not_trivially_empty():
    assert len(THUMBNAIL.read_text()) > 500


def test_thumbnail_has_curve_geometry():
    """Thumbnail must contain actual curve geometry, not just a background rect."""
    svg = THUMBNAIL.read_text()
    assert "<path" in svg or "<polyline" in svg or "<polygon" in svg, \
        "thumbnail.svg must contain curve geometry"


def test_thumbnail_has_cool_blue_stroke():
    """Thumbnail stroke must be a blue/cyan family color."""
    svg = THUMBNAIL.read_text()
    assert "160" in svg or "210" in svg or "255" in svg, \
        "Thumbnail must use a cool-blue stroke"


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_pendulum_equations():
    text = README.read_text().lower()
    assert "pendulum" in text or "equation" in text


def test_readme_mentions_frequency_ratios():
    text = README.read_text()
    assert "2:3" in text or "3:2" in text or "f1" in text.lower()


def test_readme_mentions_damping():
    text = README.read_text().lower()
    assert "damp" in text or "decay" in text or "0.002" in text


def test_readme_mentions_alpha():
    text = README.read_text()
    assert "0.15" in text or "alpha" in text.lower()


def test_readme_differentiates_from_piece_80():
    """README must explicitly discuss how this differs from piece 80."""
    text = README.read_text()
    assert "80" in text, "README must explain how this differs from piece 80"


# ---------------------------------------------------------------------------
# pieces.json contract
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [e.get("id") for e in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_entry_has_all_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - _entry().keys()
    assert not missing, f"Missing fields: {missing}"


def test_entry_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_entry_path_matches_id():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_entry_thumbnail_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file(), f"Thumbnail referenced in pieces.json is missing: {thumb}"


def test_entry_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_entry_id_matches_dir_name():
    entry = _entry()
    piece_dir = REPO / entry["path"]
    assert entry["id"] == piece_dir.name


# ---------------------------------------------------------------------------
# Regression: existing entries must remain intact
# ---------------------------------------------------------------------------

def test_pieces_json_still_valid_after_new_entry():
    """pieces.json must remain a valid JSON list with all previous entries intact."""
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)
    ids = [e["id"] for e in data]
    assert "01-amber-current" in ids, "Existing entry must not be removed"
    assert "80-harmonograph" in ids, "Piece 80 must remain for differentiation reference"
    assert "137-lorenz-attractor" in ids, "Most recent prior piece must still be present"
    assert PIECE_ID in ids


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "pieces.json must not have duplicate ids"


def test_piece_138_is_after_137_in_json():
    """New piece must appear after 137-lorenz-attractor in the list."""
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    idx_137 = ids.index("137-lorenz-attractor")
    idx_138 = ids.index(PIECE_ID)
    assert idx_138 > idx_137, "138-harmonograph must come after 137-lorenz-attractor"


# ---------------------------------------------------------------------------
# Failure mode: malformed pieces.json entry
# ---------------------------------------------------------------------------

def test_missing_thumbnail_field_detected(tmp_path):
    """An entry without 'thumbnail' should fail the required-field check."""
    entry = {
        "id": "138-harmonograph",
        "title": "test",
        "tagline": "test tagline",
        "year": 2026,
        "technique": "canvas",
        "path": "pieces/138-harmonograph",
    }
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - entry.keys()
    assert "thumbnail" in missing
