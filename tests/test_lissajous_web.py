"""Tests for Piece 145 — Frequencies in Resonance: Lissajous Web."""
import json
import math
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "145-lissajous-web"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def load_pieces():
    return json.loads(PIECES_JSON.read_text())


def get_entry():
    return next((p for p in load_pieces() if p["id"] == PIECE_ID), None)


# ---------------------------------------------------------------------------
# Directory / file existence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), f"Directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_exists():
    thumb = PIECE_DIR / "thumbnail.svg"
    assert thumb.is_file(), "thumbnail.svg must exist"


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

def test_entry_present_in_pieces_json():
    assert get_entry() is not None, f"{PIECE_ID} not found in pieces.json"


def test_entry_required_fields():
    entry = get_entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= entry.keys(), f"Missing fields: {required - entry.keys()}"


def test_entry_id_matches_directory():
    entry = get_entry()
    assert entry["id"] == pathlib.Path(entry["path"]).name


def test_entry_thumbnail_file_exists():
    entry = get_entry()
    assert (REPO / entry["thumbnail"]).is_file()


def test_entry_path_is_directory():
    entry = get_entry()
    assert (REPO / entry["path"]).is_dir()


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def _html():
    return (PIECE_DIR / "index.html").read_text()


def test_html_uses_canvas():
    assert "<canvas" in _html()


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_uses_global_alpha_or_hsla():
    """The animation must use low-alpha strokes for additive glow."""
    html = _html()
    assert "hsla" in html or "globalAlpha" in html, (
        "index.html must use hsla() or globalAlpha for the fading-trail effect"
    )


def test_html_lissajous_formula_present():
    """Both sin(a·τ + δ) for x and sin(b·τ) for y must appear."""
    html = _html()
    assert "Math.sin" in html, "Lissajous formula requires Math.sin"


def test_html_b_wraps_back():
    """b must wrap back to re-enter the low ratio range."""
    html = _html()
    assert re.search(r'b\s*=\s*0\.9[0-9]', html), (
        "b must reset to ~0.98 when it exceeds the upper limit"
    )


def test_html_background_near_black():
    html = _html()
    assert "#08080f" in html, "Background must be near-black #08080f"


def test_html_no_external_dependencies():
    """Piece must be self-contained — no <script src=> or <link stylesheet>."""
    html = _html()
    assert '<script src' not in html
    assert '<link rel="stylesheet"' not in html


# ---------------------------------------------------------------------------
# Mathematical sanity checks (pure Python, no browser)
# ---------------------------------------------------------------------------

def lissajous_point(a, b, tau, delta, R=270):
    """Return (x, y) for a Lissajous figure at parameter tau."""
    return R * math.sin(a * tau + delta), R * math.sin(b * tau)


def test_lissajous_closed_at_integer_ratio():
    """At integer ratio a=3, b=3 the curve closes: point at tau=0 reappears."""
    a, b, delta = 3, 3, 0.0
    period = 2 * math.pi  # both frequencies are equal so period is 2π/gcd=2π
    p0 = lissajous_point(a, b, 0.0, delta)
    p_period = lissajous_point(a, b, period, delta)
    assert abs(p0[0] - p_period[0]) < 1e-9
    assert abs(p0[1] - p_period[1]) < 1e-9


def test_lissajous_amplitude_bounded():
    """All points must stay within radius R."""
    a, b, delta, R = 3, 2.0, 0.5, 270
    for i in range(1000):
        x, y = lissajous_point(a, b, i * 0.02, delta, R)
        assert abs(x) <= R + 1e-9, f"|x|={abs(x)} exceeds R={R}"
        assert abs(y) <= R + 1e-9, f"|y|={abs(y)} exceeds R={R}"


def test_lissajous_origin_at_zero_phase():
    """With delta=0, tau=0 yields x=0, y=0 for any frequencies."""
    for b_val in [1.0, 2.0, 3.14, 4.99]:
        x, y = lissajous_point(3, b_val, 0.0, 0.0, 270)
        assert abs(x) < 1e-9, f"x should be 0 at tau=0 with delta=0, got {x}"
        assert abs(y) < 1e-9, f"y should be 0 at tau=0, got {y}"


def test_hue_mapping_full_range():
    """hue = ((b/a) % 1) * 360 must stay within [0, 360) for all b in range."""
    a = 3
    for b_val in [0.98, 1.5, 2.0, 2.5, 3.0, 3.7, 4.0, 5.02]:
        frac = (b_val / a) % 1
        hue = frac * 360
        assert 0.0 <= hue < 360.0, f"hue {hue} out of range for b={b_val}"


def test_b_drift_cycles_through_ratios():
    """After enough steps b should cross every integer ratio 1 through 5."""
    b = 0.98
    B_STEP = 0.00008
    crossed = set()
    for _ in range(int((5.02 - 0.98) / B_STEP) + 10):
        for integer in range(1, 6):
            # ratio b/3 crosses integer when b/3 crosses integer, i.e. b = integer*3
            # More relevant: b crosses integer values 1..5
            if int(b) == integer and integer not in crossed:
                crossed.add(integer)
        b += B_STEP
        if b > 5.02:
            break
    assert crossed == {1, 2, 3, 4, 5}, f"b failed to cross integer values: {crossed}"


# ---------------------------------------------------------------------------
# Edge cases / failure modes
# ---------------------------------------------------------------------------

def test_thumbnail_is_valid_svg():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert content.strip().startswith("<svg"), "thumbnail.svg must be a valid SVG file"
    assert "</svg>" in content


def test_readme_mentions_lissajous():
    readme = (PIECE_DIR / "README.md").read_text().lower()
    assert "lissajous" in readme


def test_readme_mentions_frequency():
    readme = (PIECE_DIR / "README.md").read_text().lower()
    assert "frequenc" in readme


def test_pieces_json_still_valid_after_addition():
    """Ensure pieces.json didn't get corrupted by the new entry."""
    data = load_pieces()
    assert isinstance(data, list)
    assert len(data) > 0
    ids = [p["id"] for p in data]
    assert ids.count(PIECE_ID) == 1, "Duplicate entry in pieces.json"
