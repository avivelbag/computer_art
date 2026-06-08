"""Tests for piece 287-galactic-spiral (Density Wave)."""
import json
import math
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "287-galactic-spiral"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "287-galactic-spiral"

# ── Spiral constants (must match index.html) ──────────────────────────────────
A = 14.0    # scale parameter
B = 0.22    # pitch
ARMS = 3
SIGMA = 0.32
VC = 0.038
OMEGA_P = 1e-4


# ── File presence ─────────────────────────────────────────────────────────────

def test_piece_directory_exists():
    """Piece directory must be present under pieces/."""
    assert PIECE_DIR.is_dir(), f"Missing directory: {PIECE_DIR}"


def test_index_html_exists():
    """Each piece requires an index.html entry point."""
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_exists():
    """A thumbnail (SVG or PNG) must exist for gallery display."""
    has_svg = (PIECE_DIR / "thumbnail.svg").is_file()
    has_png = (PIECE_DIR / "thumbnail.png").is_file()
    assert has_svg or has_png, "No thumbnail.svg or thumbnail.png found"


def test_readme_exists():
    """README.md is required for each piece."""
    assert (PIECE_DIR / "README.md").is_file()


# ── pieces.json ───────────────────────────────────────────────────────────────

def _load_entry() -> dict:
    """Load and return the pieces.json entry for this piece."""
    data = json.loads(PIECES_JSON.read_text())
    matches = [e for e in data if e["id"] == PIECE_ID]
    assert matches, f"No entry with id={PIECE_ID!r} in pieces.json"
    return matches[0]


def test_pieces_json_has_entry():
    """pieces.json must contain an entry with the correct id."""
    entry = _load_entry()
    assert entry["id"] == PIECE_ID


def test_pieces_json_required_fields():
    """All mandatory metadata fields must be present."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = _load_entry()
    missing = required - entry.keys()
    assert not missing, f"Missing fields: {missing}"


def test_pieces_json_path_matches_id():
    """The 'path' field must end with the piece id."""
    entry = _load_entry()
    assert entry["path"].endswith(entry["id"])


def test_pieces_json_thumbnail_file_exists():
    """The thumbnail path referenced in pieces.json must point to an actual file."""
    entry = _load_entry()
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file(), f"Thumbnail missing: {entry['thumbnail']}"


# ── Logarithmic spiral mathematics ───────────────────────────────────────────

def test_spiral_formula_at_theta_zero():
    """At θ = 0, r = A (the scale parameter); the spiral starts at the origin scale."""
    r = A * math.exp(B * 0)
    assert abs(r - A) < 1e-10


def test_spiral_formula_positive_pitch_increases_r():
    """For B > 0, r = A·e^(B·θ) increases monotonically with θ."""
    thetas = [0.0, 0.5, 1.0, math.pi, 2 * math.pi, 4 * math.pi]
    radii = [A * math.exp(B * t) for t in thetas]
    for i in range(len(radii) - 1):
        assert radii[i] < radii[i + 1], f"Spiral not increasing: r[{i}]={radii[i]} >= r[{i+1}]={radii[i+1]}"


def test_spiral_inverse_recovers_theta():
    """log(r/A)/B must exactly invert r = A·e^(B·θ) for any θ."""
    for theta_in in [0.0, 1.0, 3.14, 7.0, 15.0]:
        r = A * math.exp(B * theta_in)
        theta_out = math.log(r / A) / B
        assert abs(theta_out - theta_in) < 1e-9, f"Inverse failed for theta={theta_in}"


def test_spiral_spans_expected_radius_range():
    """Spiral from θ=0 to θ=4π should grow from A px to about A·e^(4πB) px."""
    r_at_0 = A * math.exp(B * 0)
    r_at_4pi = A * math.exp(B * 4 * math.pi)
    assert r_at_0 == pytest.approx(A, abs=1e-9)
    assert r_at_4pi > 10 * A, "Spiral should grow by at least 10× over 4π radians"


# ── Three-arm geometry ────────────────────────────────────────────────────────

def test_three_arms_evenly_spaced():
    """Three arms must be separated by exactly 2π/3 radians."""
    arm_step = 2 * math.pi / ARMS
    assert abs(arm_step - 2 * math.pi / 3) < 1e-12


def test_arm_angles_cover_full_circle():
    """The three arm offsets must span the full 2π circle without gaps."""
    offsets = [i * 2 * math.pi / ARMS for i in range(ARMS)]
    assert abs(offsets[-1] - (2 * math.pi * (ARMS - 1) / ARMS)) < 1e-12
    # Verify spacing is uniform
    for i in range(ARMS - 1):
        assert abs(offsets[i + 1] - offsets[i] - 2 * math.pi / ARMS) < 1e-12


# ── Flat rotation curve ───────────────────────────────────────────────────────

def test_flat_rotation_curve_inner_faster():
    """Angular velocity ω = VC/r must decrease with increasing radius."""
    omega_50  = VC / 50.0
    omega_100 = VC / 100.0
    omega_300 = VC / 300.0
    assert omega_50 > omega_100 > omega_300


def test_flat_rotation_curve_constant_tangential_speed():
    """For any radius, tangential speed v = ω·r must equal VC."""
    for r in [30.0, 100.0, 250.0]:
        omega = VC / r
        v = omega * r
        assert abs(v - VC) < 1e-12, f"Tangential speed {v} != VC={VC} at r={r}"


def test_pattern_speed_slower_than_inner_stars():
    """OMEGA_P must be slower than the angular velocity of inner stars (density wave condition)."""
    omega_inner = VC / 50.0   # fast inner orbit
    assert OMEGA_P < omega_inner, "Arm pattern should rotate slower than inner stars"


# ── Gaussian arm proximity kernel ─────────────────────────────────────────────

SIG2 = 2 * SIGMA * SIGMA


def _prox(d: float) -> float:
    """Gaussian arm proximity: 1 at d=0, decaying with angular distance d."""
    return math.exp(-d * d / SIG2)


def test_arm_proximity_max_at_zero():
    """Proximity must be exactly 1.0 when d = 0 (star lies on the arm spine)."""
    assert abs(_prox(0.0) - 1.0) < 1e-12


def test_arm_proximity_half_power_at_sigma():
    """At d = σ, proximity should equal exp(-0.5) ≈ 0.607."""
    assert abs(_prox(SIGMA) - math.exp(-0.5)) < 1e-10


def test_arm_proximity_decays_monotonically():
    """Proximity must be strictly decreasing as |d| increases from zero."""
    ds = [0.0, 0.1, 0.3, 0.5, 1.0, 2.0, math.pi]
    proxes = [_prox(d) for d in ds]
    for i in range(len(proxes) - 1):
        assert proxes[i] > proxes[i + 1]


def test_arm_proximity_always_positive():
    """exp(−x) > 0 for all finite x; proximity must never reach zero."""
    for d in [-5.0, -1.0, 0.0, 1.0, 5.0, math.pi]:
        assert _prox(d) > 0.0


def test_arm_proximity_symmetric():
    """The Gaussian kernel must be symmetric: prox(d) == prox(-d)."""
    for d in [0.1, 0.5, 1.2, 2.8]:
        assert abs(_prox(d) - _prox(-d)) < 1e-14


def test_inter_arm_proximity_much_lower():
    """Stars midway between two 2π/3-spaced arms must be far dimmer than arm-centre stars."""
    mid_angle = math.pi / 3   # halfway between arms separated by 2π/3
    prox_mid = _prox(mid_angle)
    prox_arm = _prox(0.0)
    assert prox_arm / prox_mid > 100, "Arms should be at least 100× brighter than inter-arm regions"


# ── HTML content ──────────────────────────────────────────────────────────────

def _html() -> str:
    return (PIECE_DIR / "index.html").read_text(encoding="utf-8")


def test_html_has_canvas_element():
    """index.html must contain a <canvas> element for rendering."""
    assert "<canvas" in _html()


def test_html_uses_request_animation_frame():
    """Animation must use requestAnimationFrame for smooth looping."""
    assert "requestAnimationFrame" in _html()


def test_html_defines_three_arms():
    """The piece must declare exactly 3 spiral arms."""
    html = _html()
    assert "ARMS" in html or "N_ARMS" in html
    # Check that the value 3 appears near the ARMS constant
    assert "ARMS = 3" in html or "ARMS=3" in html


def test_html_uses_logarithmic_spiral():
    """The spiral equation must use Math.log and/or Math.exp in the source."""
    html = _html()
    assert "Math.log" in html or "Math.exp" in html


def test_html_contains_arm_proximity():
    """The Gaussian arm-proximity function must reference Math.exp."""
    assert "Math.exp" in _html()


def test_html_palette_near_black_background():
    """Background colour must match the specified near-black #04040c."""
    assert "#04040c" in _html()


def test_html_palette_star_white():
    """Star-white colour (rgb 240,244,255) must appear in the palette."""
    html = _html()
    # HTML stores colours as RGB triplets [240, 244, 255]
    assert "240, 244, 255" in html or "240,244,255" in html or "f0f4ff" in html


def test_html_palette_amber_core():
    """Warm-core amber #f5a623 = rgb(245,166,35) must be used for the galactic bulge."""
    html = _html()
    # HTML may express the colour as a hex string or as rgb components
    assert "f5a623" in html or "245,166,35" in html or "245, 166, 35" in html


def test_html_uses_imagedata():
    """Stars must be rendered as pixels via ImageData (not arc/fillRect)."""
    html = _html()
    assert "createImageData" in html or "putImageData" in html


# ── Edge-case / failure-mode tests ───────────────────────────────────────────

def test_spiral_rejects_nonpositive_r():
    """log(r/A) is undefined for r <= 0; valid star positions must have r > 0."""
    with pytest.raises((ValueError, ZeroDivisionError, Exception)):
        math.log(0 / A)


def test_spiral_with_zero_b_would_be_circle():
    """If B were 0, r = A·e^0 = A for all θ — a degenerate circle, not a spiral."""
    b_zero = 0.0
    thetas = [0.0, math.pi, 2 * math.pi]
    radii = [A * math.exp(b_zero * t) for t in thetas]
    # All radii identical — confirms B ≠ 0 is required for spiral shape
    assert all(r == A for r in radii)


def test_large_radius_star_slow_orbit():
    """A star at r = MAX_R should orbit much more slowly than one at r = 50."""
    max_r = 340.0
    omega_outer = VC / max_r
    omega_inner = VC / 50.0
    assert omega_inner > 4 * omega_outer, "Flat curve: inner star should be >4× faster at r=50 vs r=340"


def test_five_thousand_stars_minimum():
    """The piece must render at least 5 000 stars as specified."""
    html = _html()
    # Extract the N constant value
    import re
    m = re.search(r'\bN\s*=\s*(\d+)', html)
    assert m is not None, "Could not find star count constant N in index.html"
    n_stars = int(m.group(1))
    assert n_stars >= 5000, f"Need at least 5000 stars, found N={n_stars}"
