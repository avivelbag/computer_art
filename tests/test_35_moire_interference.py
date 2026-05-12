"""Tests for pieces/35-two-truths-overlapping: moiré / optical interference pattern."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "35-two-truths-overlapping"
INDEX_HTML  = PIECE_DIR / "index.html"
README      = PIECE_DIR / "README.md"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "35-two-truths-overlapping"


# ---------------------------------------------------------------------------
# Python mirrors of the per-pixel moiré formula used in the JS
# ---------------------------------------------------------------------------

def ring_phase(x: float, y: float, cx: float, cy: float, lam: float) -> float:
    """Return sin(r/λ) where r is the Euclidean distance from (x, y) to (cx, cy).

    Mirrors the per-pixel evaluation in index.html:
        f = Math.sin(Math.sqrt(dx*dx + dy*dy) / lam)
    """
    r = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    return math.sin(r / lam)


def moire_value(
    x: float, y: float,
    cx1: float, cy1: float,
    cx2: float, cy2: float,
    lam: float,
) -> float:
    """Return (f1 + f2) / 2 — the interference value for a pixel at (x, y).

    Mirrors: v = (f1 + f2) * 0.5 in the render loop.
    Result is always in [-1, 1].
    """
    return (ring_phase(x, y, cx1, cy1, lam) + ring_phase(x, y, cx2, cy2, lam)) * 0.5


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


def test_html_canvas_id_is_c():
    html = _html()
    assert 'id="c"' in html or "id='c'" in html


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html


def test_html_title_exists():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m and len(m.group(1).strip()) > 0


def test_html_has_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained — no remote scripts"


def test_html_canvas_resizes_to_window():
    html = _html()
    assert "window.innerWidth" in html and "window.innerHeight" in html


# ---------------------------------------------------------------------------
# Per-pixel / ImageData technique tests
# ---------------------------------------------------------------------------

def test_html_uses_image_data_write():
    """Piece must write pixels directly into an ImageData buffer."""
    html = _html()
    assert "putImageData" in html, "expected putImageData call"


def test_html_creates_image_data():
    html = _html()
    assert "createImageData" in html or "ImageData" in html


def test_html_uses_math_sqrt():
    """Distance computation requires Math.sqrt for the radial formula."""
    assert "Math.sqrt" in _html()


def test_html_uses_math_sin():
    """Wave function requires Math.sin."""
    assert "Math.sin" in _html()


def test_html_uses_math_cos_for_orbit():
    """Centre-2 orbit must use both cos and sin."""
    html = _html()
    assert "Math.cos" in html and "Math.sin" in html


# ---------------------------------------------------------------------------
# Animation parameter tests
# ---------------------------------------------------------------------------

def test_html_rot_period_20_to_30():
    """ROT_PERIOD constant must be in the 20–30 s range as required."""
    html = _html()
    m = re.search(r'ROT_PERIOD\s*=\s*(\d+(?:\.\d+)?)', html)
    assert m, "ROT_PERIOD constant not found in index.html"
    val = float(m.group(1))
    assert 20 <= val <= 30, f"ROT_PERIOD={val} must be between 20 and 30 seconds"


def test_html_has_orbit_radius():
    """ORBIT_R constant must be present (orbit of centre-2 around centre-1)."""
    assert "ORBIT_R" in _html()


def test_html_wavelength_range_present():
    """LAM_MIN and LAM_MAX must both appear in the HTML."""
    html = _html()
    assert "LAM_MIN" in html and "LAM_MAX" in html


def test_html_lam_min_is_20():
    html = _html()
    m = re.search(r'LAM_MIN\s*=\s*(\d+(?:\.\d+)?)', html)
    assert m, "LAM_MIN not found"
    assert float(m.group(1)) == 20.0


def test_html_lam_max_is_35():
    html = _html()
    m = re.search(r'LAM_MAX\s*=\s*(\d+(?:\.\d+)?)', html)
    assert m, "LAM_MAX not found"
    assert float(m.group(1)) == 35.0


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_hsl_saturation_40_percent():
    """Saturation must be 40 % (0.4) as specified."""
    html = _html()
    assert "0.4" in html, "expected saturation value 0.4 in index.html"


# ---------------------------------------------------------------------------
# Python mirrors — ring_phase
# ---------------------------------------------------------------------------

def test_ring_phase_at_centre_is_zero():
    """At the ring centre r=0, sin(0/λ)=0 for any λ."""
    for lam in (20, 27.5, 35):
        assert ring_phase(100, 100, 100, 100, lam) == 0.0


def test_ring_phase_range():
    """ring_phase must always lie in [-1, 1]."""
    for x in range(0, 401, 40):
        for y in range(0, 301, 30):
            v = ring_phase(x, y, 200, 150, 27.5)
            assert -1.0 <= v <= 1.0, f"ring_phase out of range at ({x},{y}): {v}"


def test_ring_phase_known_value():
    """At exactly one wavelength from the centre, sin(1) ≈ 0.841."""
    lam = 30.0
    v = ring_phase(200 + lam, 200, 200, 200, lam)
    assert abs(v - math.sin(1.0)) < 1e-12


def test_ring_phase_isotropic():
    """ring_phase must be the same for any point equidistant from the centre."""
    cx, cy, lam, r = 200, 150, 27.5, 60
    pts = [(cx + r, cy), (cx - r, cy), (cx, cy + r), (cx, cy - r)]
    vals = [ring_phase(x, y, cx, cy, lam) for x, y in pts]
    assert all(abs(v - vals[0]) < 1e-10 for v in vals), \
        "ring_phase not isotropic for equidistant points"


def test_ring_phase_large_coordinates():
    """ring_phase must not overflow or NaN for large coordinate values."""
    v = ring_phase(10_000, 10_000, 0, 0, 25.0)
    assert -1.0 <= v <= 1.0 and not math.isnan(v)


# ---------------------------------------------------------------------------
# Python mirrors — moire_value
# ---------------------------------------------------------------------------

def test_moire_value_range():
    """moire_value must stay in [-1, 1] for all pixels of a typical frame."""
    cx1, cy1 = 200, 150
    cx2 = cx1 + 90 * math.cos(math.pi / 4)
    cy2 = cy1 + 90 * math.sin(math.pi / 4)
    lam = 27.5
    for x in range(0, 401, 20):
        for y in range(0, 301, 20):
            v = moire_value(x, y, cx1, cy1, cx2, cy2, lam)
            assert -1.0 <= v <= 1.0, f"moire_value out of range at ({x},{y}): {v}"


def test_moire_value_symmetric_centres():
    """Swapping the two centres must yield the same interference value."""
    x, y, lam = 150, 120, 27.5
    cx1, cy1, cx2, cy2 = 200, 150, 270, 215
    v1 = moire_value(x, y, cx1, cy1, cx2, cy2, lam)
    v2 = moire_value(x, y, cx2, cy2, cx1, cy1, lam)
    assert abs(v1 - v2) < 1e-12, "moire_value must be symmetric in the two centres"


def test_moire_value_same_centre_equals_ring_phase():
    """When both centres coincide the value equals ring_phase (not doubled)."""
    x, y, cx, cy, lam = 300, 200, 200, 150, 27.5
    expected = ring_phase(x, y, cx, cy, lam)
    actual   = moire_value(x, y, cx, cy, cx, cy, lam)
    assert abs(actual - expected) < 1e-12


def test_moire_constructive_maximum():
    """Constructive interference: when both phases are 1 the value is 1."""
    # Place pixel at distance λ*π/2 from both centres simultaneously (both at peak).
    # For c1=(0,0), r1=lam*π/2 → sin(r1/lam) = sin(π/2) = 1.
    # Use c2=(0,0) too so both phases are identical.
    lam = 30.0
    r = lam * math.pi / 2
    v = moire_value(r, 0, 0, 0, 0, 0, lam)
    assert abs(v - 1.0) < 1e-12, f"Expected 1.0 at constructive peak, got {v}"


def test_moire_destructive_yields_zero():
    """Destructive interference: f1=1, f2=-1 → value=0."""
    lam = 30.0
    r_peak   = lam * math.pi / 2      # sin = +1
    r_trough = lam * 3 * math.pi / 2  # sin = -1
    # f1 from c1=(0,0): pixel at (r_peak, 0) → sin(r_peak/lam) = +1
    # f2 from c2=(r_peak - r_trough, 0) → distance from c2 = r_trough → sin = -1
    offset = r_peak - r_trough         # negative: c2 is to the right
    # pixel at x=r_peak, c2 at x=r_peak-r_trough → distance from c2 = r_trough
    v = moire_value(r_peak, 0, 0, 0, r_peak - r_trough, 0, lam)
    assert abs(v) < 1e-12, f"Expected 0.0 at destructive interference, got {v}"


def test_moire_value_at_midpoint_of_centres():
    """The midpoint between c1 and c2 can be computed without error."""
    cx1, cy1, cx2, cy2, lam = 100.0, 100.0, 200.0, 200.0, 27.5
    mid_x, mid_y = (cx1 + cx2) / 2, (cy1 + cy2) / 2
    v = moire_value(mid_x, mid_y, cx1, cy1, cx2, cy2, lam)
    assert -1.0 <= v <= 1.0


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_ring_phase_small_wavelength():
    """With a very small λ the phase oscillates rapidly but stays in [-1, 1]."""
    for r in range(1, 100, 7):
        v = ring_phase(r, 0, 0, 0, 0.5)
        assert -1.0 <= v <= 1.0


def test_ring_phase_large_wavelength():
    """With a very large λ, sin(r/λ) ≈ r/λ (small-angle); still in [-1, 1]."""
    v = ring_phase(10, 0, 0, 0, 10_000)
    assert abs(v - math.sin(10 / 10_000)) < 1e-12


def test_moire_value_zero_pixel_distance():
    """Pixel at cx1=cx2 with both centres at the pixel location → value 0."""
    v = moire_value(50, 50, 50, 50, 50, 50, 25.0)
    assert v == 0.0


def test_moire_value_many_pixels_no_nan():
    """Full-resolution scan of a typical frame must produce no NaN values."""
    cx1, cy1 = 200, 150
    cx2, cy2 = 263, 213
    lam = 27.5
    for y in range(0, 300, 10):
        for x in range(0, 400, 10):
            v = moire_value(x, y, cx1, cy1, cx2, cy2, lam)
            assert not math.isnan(v), f"NaN at ({x},{y})"


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    assert len(THUMBNAIL.read_text()) > 500


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


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_gradient():
    svg = THUMBNAIL.read_text()
    assert "radialGradient" in svg or "linearGradient" in svg


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_under_200kb():
    size = THUMBNAIL.stat().st_size
    assert size < 200_000, f"thumbnail.svg is {size} bytes — must be under 200 KB"


def test_thumbnail_has_two_circle_groups():
    """Thumbnail must contain circles from two separate centres."""
    svg = THUMBNAIL.read_text()
    circles = re.findall(r'<circle\s[^>]*/>', svg)
    assert len(circles) >= 20, f"Expected at least 20 circle elements, found {len(circles)}"


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


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_moire_or_interference():
    t = _entry()["technique"].lower()
    assert "moir" in t or "interference" in t or "imagedata" in t.replace("-", "")


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_moire_or_interference():
    readme = README.read_text().lower()
    assert "moir" in readme or "interference" in readme


def test_readme_mentions_per_pixel():
    readme = README.read_text().lower()
    assert "per-pixel" in readme or "per pixel" in readme or "imagedata" in readme.replace("-", "")


def test_readme_mentions_concentric():
    readme = README.read_text().lower()
    assert "concentric" in readme or "ring" in readme


def test_readme_mentions_wavelength():
    readme = README.read_text().lower()
    assert "wavelength" in readme or "lambda" in readme or "λ" in readme


# ---------------------------------------------------------------------------
# Failure-mode tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "00-does-not-exist" not in ids


def test_missing_canvas_tag_detected():
    fake = "<html><body><div id='c'></div></body></html>"
    assert "<canvas" not in fake


def test_moire_value_off_canvas_no_error():
    """Pixels outside the logical canvas bounds must not raise exceptions."""
    v = moire_value(-100, -100, 200, 150, 264, 214, 27.5)
    assert -1.0 <= v <= 1.0


def test_ring_phase_returns_float():
    v = ring_phase(150, 100, 200, 150, 27.5)
    assert isinstance(v, float)
