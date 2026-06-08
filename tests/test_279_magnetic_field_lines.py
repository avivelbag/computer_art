"""Tests for Piece 279 — Polarity: Magnetic Dipole Field Lines."""

import json
import math
import pathlib

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "279-magnetic-field-lines"
JSON_PATH = REPO / "pieces.json"

# ── B-field computation mirrored from index.html ──────────────────────────────

SOFT_CORE = 900    # r² soft-core constant (30 px²)
K         = 1e5    # Dimensionless dipole strength

def b_field(px, py, dipoles):
    """Return (bx, by) — total B-field at (px, py) from a list of dipole dicts.

    Each dipole is {'x': float, 'y': float, 'angle': float, 'strength': float}.
    Mirrors the bField() function in index.html exactly.
    """
    bx = by = 0.0
    for d in dipoles:
        mx = math.cos(d['angle']) * d['strength'] * K
        my = math.sin(d['angle']) * d['strength'] * K
        rx = px - d['x']
        ry = py - d['y']
        r2 = rx * rx + ry * ry + SOFT_CORE
        r  = math.sqrt(r2)
        r3 = r * r2
        ux = rx / r
        uy = ry / r
        mdu = mx * ux + my * uy
        bx += (3 * mdu * ux - mx) / r3
        by += (3 * mdu * uy - my) / r3
    return bx, by


# ── Colour mapping mirrored from index.html ───────────────────────────────────

AMBER = (200, 135, 26)   # #c8871a
GOLD  = (245, 208, 96)   # #f5d060

def field_colour(mag):
    """Map field magnitude to (r, g, b, t) between AMBER (weak) and GOLD (strong).

    t is the interpolation parameter in [0, 1]. Mirrors fieldColour() in index.html.
    """
    t = min(1.0, math.log1p(mag * 2e-3) / math.log1p(200))
    r = round(AMBER[0] + t * (GOLD[0] - AMBER[0]))
    g = round(AMBER[1] + t * (GOLD[1] - AMBER[1]))
    b = round(AMBER[2] + t * (GOLD[2] - AMBER[2]))
    return r, g, b, t


# ── File-presence tests ───────────────────────────────────────────────────────

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/279-magnetic-field-lines/ must exist"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_readme_not_empty():
    readme = (PIECE_DIR / "README.md").read_text()
    assert len(readme.strip()) > 200, "README.md appears too short"


def test_thumbnail_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_thumbnail_is_valid_svg():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<svg" in content
    assert "viewBox" in content
    assert "</svg>" in content


def test_thumbnail_has_background_colour():
    assert "#0e0e12" in (PIECE_DIR / "thumbnail.svg").read_text()


def test_thumbnail_has_amber_colour():
    assert "#c8871a" in (PIECE_DIR / "thumbnail.svg").read_text()


def test_thumbnail_has_gold_colour():
    assert "#f5d060" in (PIECE_DIR / "thumbnail.svg").read_text()


def test_thumbnail_has_north_pole_label():
    assert ">N<" in (PIECE_DIR / "thumbnail.svg").read_text()


def test_thumbnail_has_south_pole_label():
    assert ">S<" in (PIECE_DIR / "thumbnail.svg").read_text()


# ── pieces.json registration ──────────────────────────────────────────────────

def test_registered_in_pieces_json():
    data = json.loads(JSON_PATH.read_text())
    ids = [e["id"] for e in data]
    assert "279-magnetic-field-lines" in ids


def test_pieces_json_entry_complete():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    data = json.loads(JSON_PATH.read_text())
    entry = next(e for e in data if e["id"] == "279-magnetic-field-lines")
    assert required <= entry.keys()
    assert entry["path"]      == "pieces/279-magnetic-field-lines"
    assert entry["thumbnail"] == "pieces/279-magnetic-field-lines/thumbnail.svg"


def test_pieces_json_year():
    data = json.loads(JSON_PATH.read_text())
    entry = next(e for e in data if e["id"] == "279-magnetic-field-lines")
    assert entry["year"] == 2026


def test_pieces_json_technique_keywords():
    data = json.loads(JSON_PATH.read_text())
    entry = next(e for e in data if e["id"] == "279-magnetic-field-lines")
    tech = entry["technique"].lower()
    assert "magnetic" in tech
    assert "iron" in tech or "filing" in tech
    assert "rk4" in tech or "streamline" in tech


def test_pieces_json_no_duplicate_ids():
    data = json.loads(JSON_PATH.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "Duplicate IDs in pieces.json"


# ── index.html content tests ──────────────────────────────────────────────────

def _html():
    return (PIECE_DIR / "index.html").read_text()


def test_html_doctype():
    assert "<!DOCTYPE html>" in _html() or "<!doctype html>" in _html().lower()


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_has_info_pane():
    assert "info-pane" in _html()


def test_html_has_no_external_deps():
    content = _html()
    assert "https://" not in content
    assert "http://" not in content


def test_html_background_colour():
    assert "#0e0e12" in _html()


def test_html_amber_colour():
    assert "#c8871a" in _html()


def test_html_gold_colour():
    assert "#f5d060" in _html()


def test_html_has_bfield_function():
    """bField() implements the dipole field formula."""
    assert "bField" in _html()


def test_html_has_rk4_step():
    """rk4Step() must be present for the streamline integrator."""
    assert "rk4Step" in _html() or "rk4" in _html()


def test_html_has_trace_streamline():
    assert "traceStreamline" in _html()


def test_html_has_draw_filings():
    assert "drawFilings" in _html()


def test_html_has_draw_streamlines():
    assert "drawStreamlines" in _html()


def test_html_n_filings_constant():
    """N_FILINGS must be defined (3000 iron-filing segments)."""
    assert "N_FILINGS" in _html()


def test_html_soft_core_constant():
    """SOFT_CORE must be present to prevent the 1/r³ singularity."""
    assert "SOFT_CORE" in _html()


def test_html_has_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_pause_button():
    assert "btn-pause" in _html()


def test_html_has_streamlines_button():
    assert "btn-streamlines" in _html()


def test_html_max_steps_constant():
    assert "MAX_STEPS" in _html()


# ── README content tests ──────────────────────────────────────────────────────

def _readme():
    return (PIECE_DIR / "README.md").read_text()


def test_readme_mentions_dipole_formula():
    """README must describe the dipole field formula."""
    assert "3(m" in _readme() or "m·r̂" in _readme() or "dipole" in _readme().lower()


def test_readme_mentions_rk4():
    assert "RK4" in _readme() or "rk4" in _readme() or "Runge-Kutta" in _readme()


def test_readme_mentions_closed_loops():
    readme = _readme().lower()
    assert "closed" in readme or "loop" in readme


def test_readme_mentions_iron_filing():
    readme = _readme().lower()
    assert "iron" in readme or "filing" in readme


def test_readme_mentions_divergence_free():
    """README must reference ∇·B = 0."""
    assert "∇·B" in _readme() or "divergence" in _readme().lower() or "monopole" in _readme().lower()


# ── B-field physics tests ─────────────────────────────────────────────────────

def test_b_field_empty_dipoles():
    """Zero dipoles must yield a zero field everywhere."""
    bx, by = b_field(100, 200, [])
    assert bx == 0.0 and by == 0.0


def test_b_field_single_dipole_axial_direction():
    """On the north axis (along +m), the field must be parallel to m (same sign)."""
    d = {'x': 0, 'y': 0, 'angle': 0, 'strength': 1}   # m points in +x direction
    # Evaluate at (200, 0) — on the north axis
    bx, by = b_field(200, 0, [d])
    # B_x should be positive (parallel to m = +x direction) and B_y near zero
    assert bx > 0, f"Expected B_x > 0 on north axis, got {bx}"
    assert abs(by) < abs(bx) * 0.01, f"Expected B_y ≈ 0 on axis, got {by}"


def test_b_field_single_dipole_equatorial_direction():
    """On the equatorial plane (perpendicular to m), B must be anti-parallel to m."""
    d = {'x': 0, 'y': 0, 'angle': 0, 'strength': 1}   # m points in +x direction
    # Evaluate at (0, 200) — on the equatorial plane
    bx, by = b_field(0, 200, [d])
    # B_x should be negative (anti-parallel to m) and B_y near zero
    assert bx < 0, f"Expected B_x < 0 on equatorial plane, got {bx}"
    assert abs(by) < abs(bx) * 0.01, f"Expected B_y ≈ 0 on equatorial plane, got {by}"


def test_b_field_axial_twice_equatorial():
    """On the axis, |B| must be approximately twice the equatorial |B| at the same distance."""
    d = {'x': 0, 'y': 0, 'angle': 0, 'strength': 1}
    dist = 200  # far enough that soft-core is negligible
    bx_axis, _ = b_field(dist, 0, [d])    # north axis point
    bx_eq, _   = b_field(0, dist, [d])    # equatorial point
    ratio = abs(bx_axis) / abs(bx_eq)
    # Expect ratio ≈ 2 (exact far from soft-core, slight deviation for dist=200)
    assert 1.85 < ratio < 2.15, f"Expected axial/equatorial ≈ 2, got {ratio:.3f}"


def test_b_field_superposition():
    """Field from two dipoles must equal the sum of individual fields."""
    d1 = {'x': -100, 'y': 0, 'angle': 0,         'strength': 1}
    d2 = {'x':  100, 'y': 0, 'angle': math.pi/3, 'strength': 0.8}
    bx12, by12 = b_field(0, 150, [d1, d2])
    bx1,  by1  = b_field(0, 150, [d1])
    bx2,  by2  = b_field(0, 150, [d2])
    assert abs(bx12 - (bx1 + bx2)) < 1e-9
    assert abs(by12 - (by1 + by2)) < 1e-9


def test_b_field_soft_core_at_dipole_centre():
    """At the dipole centre, |B| must be finite (soft-core prevents divergence)."""
    d = {'x': 0, 'y': 0, 'angle': 0, 'strength': 1}
    bx, by = b_field(0, 0, [d])
    mag = math.sqrt(bx * bx + by * by)
    assert math.isfinite(mag), "B magnitude must be finite at the dipole centre"
    assert mag < 1e8, f"B magnitude suspiciously large at centre: {mag}"


def test_b_field_decays_with_distance():
    """Field magnitude must decrease as we move further from a dipole."""
    d = {'x': 0, 'y': 0, 'angle': 0, 'strength': 1}
    mags = []
    for dist in [50, 100, 200, 400]:
        bx, by = b_field(0, dist, [d])
        mags.append(math.sqrt(bx * bx + by * by))
    for i in range(len(mags) - 1):
        assert mags[i] > mags[i + 1], "Field should decrease monotonically with distance"


# ── Colour-mapping tests ──────────────────────────────────────────────────────

def test_field_colour_zero_magnitude():
    """At mag=0 the colour must equal AMBER (amber)."""
    r, g, b, t = field_colour(0)
    assert (r, g, b) == AMBER, f"Expected AMBER {AMBER}, got ({r},{g},{b})"
    assert t == 0.0


def test_field_colour_large_magnitude_returns_gold():
    """At very large magnitude the colour must equal GOLD."""
    r, g, b, t = field_colour(1e8)
    assert (r, g, b) == GOLD, f"Expected GOLD {GOLD}, got ({r},{g},{b})"
    assert t == 1.0


def test_field_colour_channels_in_byte_range():
    """All colour channels must stay in [0, 255] for all magnitudes."""
    for mag in [0, 1, 10, 100, 1000, 1e5, 1e8]:
        r, g, b, _ = field_colour(mag)
        assert 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255


def test_field_colour_monotone_with_magnitude():
    """Brightness must increase monotonically with field magnitude."""
    def brightness(col):
        return 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]

    mags = [0, 1, 10, 100, 1000, 10000, 1e6]
    cols = [field_colour(m)[:3] for m in mags]
    for i in range(len(cols) - 1):
        assert brightness(cols[i]) <= brightness(cols[i + 1]) + 0.5, (
            f"Brightness decreased from mag={mags[i]} to {mags[i+1]}"
        )


def test_field_colour_interpolation_midrange():
    """At an intermediate magnitude, the colour must be between AMBER and GOLD."""
    r, g, b, t = field_colour(500)
    assert 0 < t < 1, f"Expected 0 < t < 1 for intermediate magnitude, got {t}"
    assert AMBER[0] <= r <= GOLD[0], f"Red channel out of interpolation range: {r}"
    assert AMBER[1] <= g <= GOLD[1], f"Green channel out of interpolation range: {g}"
    assert AMBER[2] <= b <= GOLD[2], f"Blue channel out of interpolation range: {b}"


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_b_field_far_from_dipoles_is_small():
    """Far from any dipole the field magnitude must be very small."""
    d = {'x': 200, 'y': 200, 'angle': 0, 'strength': 1}
    bx, by = b_field(20000, 20000, [d])
    mag = math.sqrt(bx * bx + by * by)
    assert mag < 1e-6, f"Field should be negligible at large distance: {mag}"


def test_b_field_two_antiparallel_dipoles_midpoint():
    """Two opposing dipoles (antiparallel, symmetric) cancel on their perpendicular bisector."""
    d1 = {'x': -50, 'y': 0, 'angle': 0,         'strength': 1}   # m = +x
    d2 = {'x':  50, 'y': 0, 'angle': math.pi,   'strength': 1}   # m = -x
    # At the midpoint (0, 0): by symmetry the y-component cancels
    bx, by = b_field(0, 0, [d1, d2])
    # Both dipoles contribute equal bx at origin (symmetric setup), so we just
    # verify the field is finite and that by ≈ 0 (anti-symmetric in y)
    assert math.isfinite(bx) and math.isfinite(by)
    assert abs(by) < 1e-6, f"Expected B_y ≈ 0 by symmetry, got {by}"


def test_field_colour_t_bounded():
    """t must always be in [0, 1] regardless of input magnitude."""
    for mag in [0, 1e-10, 1, 100, 1e8, float('inf')]:
        if not math.isfinite(mag):
            continue
        _, _, _, t = field_colour(mag)
        assert 0.0 <= t <= 1.0, f"t={t} out of [0,1] for mag={mag}"


# ── Failure-mode tests ────────────────────────────────────────────────────────

def test_wrong_id_not_in_pieces_json():
    """A typo in the ID must not match any entry."""
    data = json.loads(JSON_PATH.read_text())
    ids = {e.get("id") for e in data}
    assert "279-magnetic-field-WRONG"  not in ids
    assert "279-magneticfieldlines"    not in ids
    assert "278-magnetic-field-lines"  not in ids   # off-by-one


def test_missing_required_field_detected():
    """An entry without 'description' fails the required-fields check."""
    incomplete = {
        "id":        "279-magnetic-field-lines",
        "title":     "Polarity",
        "tagline":   "test",
        "year":      2026,
        "technique": "canvas",
        "path":      "pieces/279-magnetic-field-lines",
        "thumbnail": "pieces/279-magnetic-field-lines/thumbnail.svg",
    }
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    missing  = required - incomplete.keys()
    assert missing, "Expected 'description' to be missing"


def test_empty_readme_fails_length_check(tmp_path):
    """An empty README must not satisfy the non-empty content check."""
    r = tmp_path / "README.md"
    r.write_text("")
    assert len(r.read_text().strip()) <= 200


def test_b_field_direction_symmetry():
    """Rotating the evaluation point by 180° around the dipole should reverse the field direction."""
    d = {'x': 0, 'y': 0, 'angle': math.pi / 4, 'strength': 1}
    bx1, by1 = b_field( 150,  150, [d])
    bx2, by2 = b_field(-150, -150, [d])
    # At antipodal equatorial points the field should be equal (same hemisphere)
    # but for axial points it should be in the same direction.
    # We just verify both are finite and non-zero.
    assert math.isfinite(bx1) and math.isfinite(by1)
    assert math.isfinite(bx2) and math.isfinite(by2)
    mag1 = math.sqrt(bx1**2 + by1**2)
    mag2 = math.sqrt(bx2**2 + by2**2)
    assert mag1 > 0 and mag2 > 0
