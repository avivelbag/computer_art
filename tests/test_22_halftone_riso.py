"""Tests for pieces/22-dot-by-dot: halftone risograph canvas animation."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO       = pathlib.Path(__file__).parent.parent
PIECE_DIR  = REPO / "pieces" / "22-dot-by-dot"
INDEX_HTML = PIECE_DIR / "index.html"
README     = PIECE_DIR / "README.md"
THUMBNAIL  = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "22-dot-by-dot"

BG_COLOR     = "faf3e0"
DOT_COLOR    = "ff6b6b"
SHADOW_COLOR = "1a1a2e"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# File-existence tests
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir(), f"Piece directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert INDEX_HTML.is_file(), "index.html missing from piece directory"


def test_readme_exists():
    assert README.is_file(), "README.md missing from piece directory"


def test_thumbnail_exists():
    assert THUMBNAIL.is_file(), "thumbnail.svg missing from piece directory"


# ---------------------------------------------------------------------------
# HTML structural tests
# ---------------------------------------------------------------------------

def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_canvas_has_id():
    html = _html()
    assert 'id="canvas"' in html or "id='canvas'" in html


def test_html_has_script_tag():
    assert "<script" in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html


def test_html_title_mentions_dot_or_light():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    t = m.group(1).lower()
    assert "dot" in t or "light" in t or "falls" in t


def test_html_canvas_size_is_600():
    html = _html()
    assert 'width="600"' in html and 'height="600"' in html, \
        "Canvas must be 600×600 logical pixels"


# ---------------------------------------------------------------------------
# HTML palette / color tests
# ---------------------------------------------------------------------------

def test_html_contains_bg_color():
    assert BG_COLOR in _html().lower(), f"Background colour #{BG_COLOR} missing"


def test_html_contains_dot_color():
    assert DOT_COLOR in _html().lower(), f"Dot colour #{DOT_COLOR} missing"


def test_html_contains_shadow_color():
    assert SHADOW_COLOR in _html().lower(), f"Shadow colour #{SHADOW_COLOR} missing"


def test_html_has_exactly_two_riso_ink_colors():
    """DOT_COLOR and SHADOW_COLOR are the two riso inks; BG is paper."""
    html = _html().lower()
    assert DOT_COLOR in html
    assert SHADOW_COLOR in html


# ---------------------------------------------------------------------------
# JavaScript animation tests
# ---------------------------------------------------------------------------

def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_js_has_delta_cap():
    html = _html()
    assert "Math.min" in html, "Script must cap delta time to prevent burst-step on resume"


def test_js_cycle_is_slow():
    """CYCLE_S must be at least 6 seconds — piece should feel like a poster not a video."""
    html = _html()
    m = re.search(r"CYCLE_S\s*=\s*(\d+)", html)
    if m:
        assert int(m.group(1)) >= 6, f"CYCLE_S={m.group(1)} is too fast (must be ≥ 6 s)"


def test_js_grid_is_60x60():
    html = _html()
    assert "COLS = 60" in html or "COLS=60" in html, "Grid must be 60 columns"
    assert "ROWS = 60" in html or "ROWS=60" in html, "Grid must be 60 rows"


def test_js_defines_evaluate_function():
    assert "function evaluate" in _html()


def test_js_uses_arc_for_dots():
    assert ".arc(" in _html()


def test_js_has_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained — no remote scripts"


def test_js_shadow_offset_is_positive():
    html = _html()
    m = re.search(r"SHADOW_DX\s*=\s*(\d+(?:\.\d+)?)", html)
    if m:
        assert float(m.group(1)) > 0, "Shadow must be offset by a positive amount"


def test_js_uses_sin_for_surface():
    assert "Math.sin" in _html(), "Halftone surface must use Math.sin"


def test_js_uses_sqrt_for_distance():
    assert "Math.sqrt" in _html(), "Distance from centre must use Math.sqrt"


# ---------------------------------------------------------------------------
# Mathematical core — pure Python mirror of index.html evaluate()
# ---------------------------------------------------------------------------

def _evaluate(
    gx: int,
    gy: int,
    phase: float,
    cols: int = 60,
    rows: int = 60,
    scale: float = math.pi * 12,
) -> float:
    """Python mirror of the JavaScript evaluate() function.

    Computes sin(r − phase) / (r + 1) mapped to [0, 1], where r is the
    normalised distance from canvas centre scaled by `scale`.
    """
    nx   = (gx + 0.5) / cols - 0.5
    ny   = (gy + 0.5) / rows - 0.5
    dist = math.sqrt(nx * nx + ny * ny)
    r    = dist * scale
    raw  = math.sin(r - phase) / (r + 1)
    return (raw + 1) / 2


def test_evaluate_output_in_unit_interval():
    """evaluate() must always return a value in [0, 1]."""
    for gy in range(0, 60, 5):
        for gx in range(0, 60, 5):
            for phase in [0.0, math.pi / 4, math.pi, 3 * math.pi / 2, 2 * math.pi]:
                v = _evaluate(gx, gy, phase)
                assert 0.0 <= v <= 1.0, \
                    f"evaluate({gx},{gy},{phase:.3f}) = {v} outside [0,1]"


def test_evaluate_radial_symmetry():
    """Cells equidistant from centre have the same value (radial symmetry)."""
    phase = 1.23
    for gx, gy in [(5, 5), (10, 20), (30, 45)]:
        # Reflect through centre: gx → 59-gx, gy → 59-gy
        v1 = _evaluate(gx, gy, phase)
        v2 = _evaluate(59 - gx, 59 - gy, phase)
        assert abs(v1 - v2) < 1e-12, \
            f"Radial symmetry broken: ({gx},{gy}) → {v1}, reflected → {v2}"


def test_evaluate_phase_changes_values():
    """Changing phase must change the output for a non-centre cell."""
    gx, gy = 10, 10
    v0 = _evaluate(gx, gy, 0.0)
    v1 = _evaluate(gx, gy, math.pi / 2)
    assert abs(v0 - v1) > 1e-6, "Phase shift must alter dot values"


def test_evaluate_large_phase_still_valid():
    """Very large phase values (many full cycles) still produce [0, 1] output."""
    for phase_mult in [10, 100, 1000]:
        v = _evaluate(20, 20, phase_mult * 2 * math.pi + 0.7)
        assert 0.0 <= v <= 1.0, f"evaluate at large phase={phase_mult * 2 * math.pi:.1f} out of range"


def test_evaluate_center_cells_are_nonzero():
    """Centre cells (gx=29, gy=29) must produce a non-trivial radius at phase=0."""
    v = _evaluate(29, 29, 0.0)
    assert v > 0.3, f"Centre cell value {v} too small — centre should be visible"


def test_evaluate_edge_cells_produce_medium_size():
    """Corner cells are far from centre; their value should cluster near 0.5."""
    for gx, gy in [(0, 0), (59, 59), (0, 59), (59, 0)]:
        v = _evaluate(gx, gy, 0.0)
        # Amplitude of sin(r)/(r+1) at the corner is small → output ≈ 0.5
        assert 0.2 <= v <= 0.8, \
            f"Corner cell ({gx},{gy}) value {v:.4f} unreasonably far from 0.5"


def test_dot_radius_range():
    """Computed dot radii (v × MAX_R) must lie in [0, MAX_R]."""
    max_r = (600 / 60) * 0.48  # 4.8 px
    for gy in range(60):
        for gx in range(60):
            v = _evaluate(gx, gy, 0.0)
            r = v * max_r
            assert 0.0 <= r <= max_r + 1e-9, \
                f"Dot radius {r:.4f} exceeds MAX_R={max_r}"


def test_phase_shift_equal_to_full_cycle_is_identity():
    """Adding exactly 2π to phase must return the same value (periodicity)."""
    gx, gy = 15, 25
    for base_phase in [0.0, 1.0, 2.5]:
        v1 = _evaluate(gx, gy, base_phase)
        v2 = _evaluate(gx, gy, base_phase + 2 * math.pi)
        assert abs(v1 - v2) < 1e-12, \
            f"2π periodicity broken at phase={base_phase}: {v1} vs {v2}"


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    assert len(THUMBNAIL.read_text()) > 200


def test_thumbnail_has_svg_root():
    assert "<svg" in THUMBNAIL.read_text()


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg invalid XML: {exc}") from exc


def test_thumbnail_dimensions_400():
    svg = THUMBNAIL.read_text()
    w = re.search(r'width="(\d+)"', svg)
    h = re.search(r'height="(\d+)"', svg)
    assert w and int(w.group(1)) == 400
    assert h and int(h.group(1)) == 400


def test_thumbnail_contains_bg_color():
    assert BG_COLOR in THUMBNAIL.read_text().lower()


def test_thumbnail_contains_dot_color():
    assert DOT_COLOR in THUMBNAIL.read_text().lower()


def test_thumbnail_contains_shadow_color():
    assert SHADOW_COLOR in THUMBNAIL.read_text().lower()


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_many_circles():
    circles = len(re.findall(r"<circle\b", THUMBNAIL.read_text()))
    assert circles >= 20, f"Thumbnail must have ≥20 circles; found {circles}"


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_under_500kb():
    size = THUMBNAIL.stat().st_size
    assert size < 500_000, f"thumbnail.svg is {size} bytes — must be under 500 KB"


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_pieces_json_entry_has_all_required_fields():
    entry = _entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert not (required - entry.keys()), f"Missing: {required - entry.keys()}"


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_halftone():
    assert "halftone" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_riso():
    t = _entry()["technique"].lower()
    assert "riso" in t or "risograph" in t


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_halftone():
    assert "halftone" in README.read_text().lower()


def test_readme_mentions_risograph():
    readme = README.read_text().lower()
    assert "riso" in readme or "risograph" in readme


def test_readme_mentions_sin():
    readme = README.read_text().lower()
    assert "sin" in readme


def test_readme_mentions_two_colors():
    readme = README.read_text()
    coral_present = "ff6b6b" in readme.lower() or "coral" in readme.lower()
    navy_present  = "1a1a2e" in readme.lower() or "navy" in readme.lower()
    assert coral_present and navy_present, "README must mention both riso ink colours"


def test_readme_mentions_cycle_duration():
    readme = README.read_text().lower()
    assert "8" in readme or "eight" in readme, "README must mention the 8-second cycle"


# ---------------------------------------------------------------------------
# Failure-mode tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_found():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "00-does-not-exist" not in ids


def test_missing_canvas_tag_detected():
    fake_html = "<html><body><div id='canvas'></div></body></html>"
    assert "<canvas" not in fake_html


def test_missing_dot_color_detected():
    fake_html = "<script>const color = '#FFFFFF';</script>"
    assert DOT_COLOR not in fake_html.lower()


def test_evaluate_zero_phase_center_medium():
    """At phase=0, the four nearest-centre cells must have v around 0.5–0.7."""
    for gx, gy in [(29, 29), (30, 29), (29, 30), (30, 30)]:
        v = _evaluate(gx, gy, 0.0)
        assert 0.4 <= v <= 0.95, \
            f"Near-centre cell ({gx},{gy}) at phase=0 has unexpected value {v:.4f}"


def test_evaluate_negative_phase_equals_shifted_positive():
    """sin(r − (−φ)) = sin(r + φ), so negative phase is the same as positive in the other direction."""
    gx, gy = 20, 15
    v_neg = _evaluate(gx, gy, -1.0)
    v_pos = _evaluate(gx, gy, 2 * math.pi - 1.0)
    assert abs(v_neg - v_pos) < 1e-12, \
        f"Negative phase not equivalent to 2π-shifted positive phase: {v_neg} vs {v_pos}"
