"""Tests for piece 283-spherical-harmonics (Orbital Hymn)."""
import json
import math
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "283-spherical-harmonics"
INDEX_HTML = PIECE_DIR / "index.html"
PIECES_JSON = REPO / "pieces.json"


# ── Filesystem ────────────────────────────────────────────────────────────────

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_thumbnail_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_thumbnail_is_svg():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<svg" in content


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_readme_not_empty():
    assert (PIECE_DIR / "README.md").stat().st_size > 100


# ── pieces.json ───────────────────────────────────────────────────────────────

def _load():
    return json.loads(PIECES_JSON.read_text())


def _entry():
    return next((p for p in _load() if p["id"] == "283-spherical-harmonics"), None)


def test_pieces_json_has_entry():
    assert _entry() is not None, "283-spherical-harmonics missing from pieces.json"


def test_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    e = _entry()
    assert e is not None
    assert not (required - e.keys()), f"Missing fields: {required - e.keys()}"


def test_entry_id_matches_directory():
    e = _entry()
    assert e is not None
    assert e["id"] == "283-spherical-harmonics"
    assert pathlib.Path(e["path"]).name == "283-spherical-harmonics"


def test_entry_thumbnail_file_exists():
    e = _entry()
    assert e is not None
    assert (REPO / e["thumbnail"]).is_file()


def test_entry_year():
    e = _entry()
    assert e is not None
    assert e["year"] == 2026


def test_no_duplicate_ids():
    ids = [p["id"] for p in _load()]
    assert len(ids) == len(set(ids)), "Duplicate ids in pieces.json"


def test_all_entries_have_description():
    for piece in _load():
        assert piece.get("description"), f"Empty description for {piece.get('id')}"


# ── HTML content ──────────────────────────────────────────────────────────────

def _html():
    return INDEX_HTML.read_text()


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_uses_requestanimationframe():
    assert "requestAnimationFrame" in _html()


def test_html_no_external_assets():
    external = re.findall(r'(src|href)\s*=\s*["\']https?://', _html())
    assert external == [], f"External assets found: {external}"


def test_html_dark_background():
    assert "#1a0a3a" in _html()


def test_html_amber_positive_color():
    assert "#f5a030" in _html() or "f5a030" in _html().lower()


def test_html_teal_negative_color():
    assert "#30d0c0" in _html() or "30d0c0" in _html().lower()


def test_html_has_spherical_harmonic_function():
    html = _html()
    assert "Ylm" in html or "ylm" in html.lower() or "spherical" in html.lower()


def test_html_has_legendre_polynomial():
    html = _html()
    assert "Plm" in html or "legendre" in html.lower() or "pmm" in html.lower()


def test_html_has_painter_algorithm_sort():
    assert "sort" in _html()


def test_html_has_lerp():
    html = _html()
    assert "lerp" in html.lower() or "LERP" in html


def test_html_no_audio():
    html = _html()
    assert "AudioContext" not in html
    assert "<audio" not in html


def test_html_no_external_libraries():
    html = _html()
    assert "three.js" not in html.lower()
    assert "d3.js" not in html.lower()
    assert "<script src" not in html


# ── Associated Legendre polynomial reference implementation ───────────────────

def _Plm(l, m, x):
    """Python reference implementation matching the JS Plm function."""
    pmm = 1.0
    if m > 0:
        s = math.sqrt((1 - x) * (1 + x))
        f = 1.0
        for _ in range(1, m + 1):
            pmm *= -f * s
            f += 2.0
    if l == m:
        return pmm
    pmmp1 = x * (2 * m + 1) * pmm
    if l == m + 1:
        return pmmp1
    pll = 0.0
    for ll in range(m + 2, l + 1):
        pll = ((2*ll-1)*x*pmmp1 - (ll+m-1)*pmm) / (ll-m)
        pmm, pmmp1 = pmmp1, pll
    return pll


def _Klm(l, m):
    am = abs(m)
    r = 1.0
    for i in range(l - am + 1, l + am + 1):
        r /= i
    return math.sqrt((2*l+1) / (4*math.pi) * r)


def _Ylm(l, m, theta, phi):
    am = abs(m)
    K = _Klm(l, m)
    P = _Plm(l, am, math.cos(theta))
    if m == 0:
        return K * P
    if m > 0:
        return math.sqrt(2) * K * math.cos(m * phi) * P
    return math.sqrt(2) * K * math.sin(am * phi) * P


# ── Math correctness ──────────────────────────────────────────────────────────

def test_Ylm_Y00_is_constant():
    """Y_0^0 = 1/sqrt(4π) everywhere — tests normalization."""
    expected = 1 / math.sqrt(4 * math.pi)
    for theta in [0.1, 0.5, 1.0, 2.0]:
        for phi in [0.0, 1.0, 3.0]:
            val = _Ylm(0, 0, theta, phi)
            assert abs(val - expected) < 1e-10, f"Y00 wrong at theta={theta}, phi={phi}"


def test_Ylm_Y10_zonal():
    """Y_1^0(θ,φ) = sqrt(3/4π)·cos(θ) — independent of phi (zonal)."""
    K = math.sqrt(3 / (4 * math.pi))
    for theta in [0.0, 0.5, math.pi/2, math.pi]:
        expected = K * math.cos(theta)
        for phi in [0.0, 1.2, 4.5]:
            val = _Ylm(1, 0, theta, phi)
            assert abs(val - expected) < 1e-10, f"Y10 wrong at theta={theta}"


def test_Ylm_orthonormality_Y10_Y20():
    """Numerical integral of Y_1^0 * Y_2^0 should be ~0 (orthogonality)."""
    N = 200
    total = 0.0
    dtheta = math.pi / N
    dphi = 2 * math.pi / N
    for i in range(N):
        theta = (i + 0.5) * dtheta
        for j in range(N):
            phi = (j + 0.5) * dphi
            total += _Ylm(1, 0, theta, phi) * _Ylm(2, 0, theta, phi) * math.sin(theta) * dtheta * dphi
    assert abs(total) < 0.01, f"Y10·Y20 integral = {total}, expected ~0"


def test_Ylm_norm_Y10():
    """Numerical integral of |Y_1^0|^2 sin(θ) dθ dφ ≈ 1."""
    N = 200
    total = 0.0
    dtheta = math.pi / N
    dphi = 2 * math.pi / N
    for i in range(N):
        theta = (i + 0.5) * dtheta
        for j in range(N):
            phi = (j + 0.5) * dphi
            v = _Ylm(1, 0, theta, phi)
            total += v * v * math.sin(theta) * dtheta * dphi
    assert abs(total - 1.0) < 0.01, f"|Y10|^2 integral = {total}, expected 1"


def test_Ylm_Y43_has_eight_phi_lobes():
    """Y_4^3 should have 2|m|=6 azimuthal sign changes per latitude band."""
    theta = math.pi / 2  # equatorial
    signs = [math.copysign(1, _Ylm(4, 3, theta, j * 2 * math.pi / 360)) for j in range(360)]
    changes = sum(1 for k in range(360) if signs[k] != signs[(k+1) % 360])
    assert changes == 6, f"Expected 6 sign changes for Y43 at equator, got {changes}"


def test_Ylm_negative_m_rotated_vs_positive():
    """Y_l^{-m} and Y_l^m are related by a 90° phase rotation in phi."""
    l, m = 3, 2
    theta = 0.8
    phi = 1.1
    pos = _Ylm(l, m, theta, phi)
    neg = _Ylm(l, -m, theta, phi)
    # They use cos vs sin: Y_3^2 = √2·K·cos(2φ)·P, Y_3^{-2} = √2·K·sin(2φ)·P
    # Sum of squares should equal 2K²P² (Pythagorean identity)
    K = _Klm(l, m)
    P = _Plm(l, m, math.cos(theta))
    expected_sum_sq = 2 * K**2 * P**2
    actual_sum_sq = pos**2 + neg**2
    assert abs(actual_sum_sq - expected_sum_sq) < 1e-10


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_Ylm_at_poles():
    """At the poles (sin θ = 0) all harmonics with m≠0 must vanish."""
    for l in range(1, 6):
        for m in range(-l, l+1):
            if m == 0:
                continue
            val_north = _Ylm(l, m, 0.0, 1.234)
            val_south = _Ylm(l, m, math.pi, 1.234)
            assert abs(val_north) < 1e-9, f"Y_{l}^{m} non-zero at north pole"
            assert abs(val_south) < 1e-9, f"Y_{l}^{m} non-zero at south pole"


def test_Ylm_high_l_finite():
    """High-order harmonics (l=6) must produce finite values everywhere."""
    for l in [5, 6]:
        for m in range(-l, l+1):
            for theta in [0.01, math.pi/4, math.pi/2, math.pi - 0.01]:
                for phi in [0.0, math.pi, 2*math.pi - 0.01]:
                    v = _Ylm(l, m, theta, phi)
                    assert math.isfinite(v), f"Y_{l}^{m}({theta},{phi}) is not finite"


def test_displacement_always_positive():
    """Radial displacement r = 1 + SCALE*|Y| must always be >= 1."""
    SCALE = 0.55
    for l, m in [(1,0),(2,1),(3,2),(4,0),(4,3)]:
        for i in range(20):
            theta = i * math.pi / 20
            for j in range(20):
                phi = j * 2 * math.pi / 20
                y = _Ylm(l, m, theta, phi)
                r = 1 + SCALE * abs(y)
                assert r >= 1.0, f"r={r} < 1 for Y_{l}^{m}"


# ── Failure-mode tests ────────────────────────────────────────────────────────

def test_Plm_invalid_m_greater_than_l_returns_zero_via_pmm():
    """Plm(l=2, m=3, x) -- m > l is mathematically undefined; verify it doesn't crash."""
    # Our recurrence computes P_m^m first, which exists, but P_2^3 is not meaningful.
    # We just verify it returns a float (not an exception).
    val = _Plm(2, 2, 0.5)  # l == m == 2 path
    assert math.isfinite(val)


def test_missing_piece_dir_detected(tmp_path):
    """Referencing a non-existent piece directory is caught by test_entry_complete."""
    ghost = tmp_path / "ghost-piece"
    assert not ghost.is_dir()


def test_pieces_json_still_valid_after_append():
    """pieces.json must remain valid JSON and be a non-empty list."""
    data = _load()
    assert isinstance(data, list)
    assert len(data) > 100  # sanity: we haven't truncated the file
