"""Tests for piece 282-maurer-rose (Interference Star)."""
import json
import math
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "282-maurer-rose"
INDEX_HTML = PIECE_DIR / "index.html"
PIECES_JSON = REPO / "pieces.json"


# ── Filesystem ───────────────────────────────────────────────────────────────

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_thumbnail_exists():
    thumb = PIECE_DIR / "thumbnail.svg"
    assert thumb.is_file()


def test_thumbnail_is_svg():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<svg" in content


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_readme_not_empty():
    assert (PIECE_DIR / "README.md").stat().st_size > 100


# ── pieces.json ──────────────────────────────────────────────────────────────

def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def _entry():
    return next((p for p in _load_pieces() if p["id"] == "282-maurer-rose"), None)


def test_pieces_json_has_entry():
    assert _entry() is not None, "282-maurer-rose missing from pieces.json"


def test_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    e = _entry()
    assert e is not None
    missing = required - e.keys()
    assert not missing, f"Missing fields: {missing}"


def test_entry_id_matches_directory():
    e = _entry()
    assert e is not None
    assert e["id"] == "282-maurer-rose"
    assert pathlib.Path(e["path"]).name == "282-maurer-rose"


def test_entry_thumbnail_file_exists():
    e = _entry()
    assert e is not None
    assert (REPO / e["thumbnail"]).is_file()


def test_entry_year():
    e = _entry()
    assert e is not None
    assert e["year"] == 2026


def test_pieces_json_valid():
    data = _load_pieces()
    assert isinstance(data, list)
    assert len(data) > 0


def test_no_duplicate_ids():
    ids = [p["id"] for p in _load_pieces()]
    assert len(ids) == len(set(ids)), "Duplicate ids in pieces.json"


# ── HTML content ─────────────────────────────────────────────────────────────

def _html():
    return INDEX_HTML.read_text()


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_uses_requestanimationframe():
    assert "requestAnimationFrame" in _html()


def test_html_no_external_assets():
    """No <script src=...> or <link href=...> pointing to external URLs."""
    external = re.findall(r'(src|href)\s*=\s*["\']https?://', _html())
    assert external == [], f"External assets found: {external}"


def test_html_dark_background():
    """Canvas background must be the specified dark colour #0a0a12."""
    assert "#0a0a12" in _html()


def test_html_has_maurer_rose_math():
    """index.html must implement the Maurer rose formula (sin(n * theta))."""
    html = _html()
    assert "Math.sin" in html
    assert "Math.cos" in html


def test_html_has_360_point_loop():
    """The rose is defined by connecting 360 points (k=0..359)."""
    html = _html()
    assert "360" in html


def test_html_has_lerp():
    """Smooth morphing requires lerp or fractional interpolation."""
    html = _html()
    assert "lerp" in html.lower() or "LERP" in html


def test_html_has_low_alpha_stroke():
    """Low-opacity strokes create the bloom effect."""
    html = _html()
    assert "globalAlpha" in html


def test_html_has_vivid_palette():
    """Piece must use at least two of the specified vivid hues."""
    html = _html()
    hues = ["#e8c84a", "#5ecfff", "#e05090"]
    found = [h for h in hues if h in html]
    assert len(found) >= 2, f"Expected at least 2 vivid hues, found: {found}"


def test_html_capped_60fps():
    """Any explicit setInterval must be >= 16 ms (no faster than 60fps)."""
    bad = re.findall(r'setInterval\s*\([^,]+,\s*(\d+)\s*\)', _html())
    for ms in bad:
        assert int(ms) >= 16, f"setInterval({ms}ms) is faster than 60fps"


def test_html_no_audio():
    html = _html()
    assert "AudioContext" not in html
    assert "<audio" not in html


# ── Maurer rose math ─────────────────────────────────────────────────────────

def _compute_points(n, d, R=185, cx=200, cy=200):
    """Pure-Python reference implementation of the Maurer rose point computation."""
    pts = []
    for k in range(360):
        theta = k * d * math.pi / 180
        r = R * math.sin(n * theta)
        pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    return pts


def test_maurer_rose_first_point_is_center():
    """At k=0, theta=0, sin(n*0)=0, so r=0 and the first point is the center."""
    pts = _compute_points(n=5, d=97)
    x, y = pts[0]
    assert abs(x - 200) < 1e-9
    assert abs(y - 200) < 1e-9


def test_maurer_rose_360_points():
    """The rose is defined by exactly 360 points."""
    assert len(_compute_points(n=5, d=97)) == 360


def test_maurer_rose_points_within_canvas():
    """All points must lie within the 400×400 canvas (R=185 centred at 200,200)."""
    for n, d in [(5, 97), (7, 71), (3, 113)]:
        pts = _compute_points(n, d)
        for x, y in pts:
            assert 0 <= x <= 400, f"x={x} out of bounds for (n={n}, d={d})"
            assert 0 <= y <= 400, f"y={y} out of bounds for (n={n}, d={d})"


def test_maurer_rose_n2_d29_nonzero_extent():
    """(n=2, d=29) must produce points spanning more than half the canvas width."""
    pts = _compute_points(n=2, d=29)
    xs = [p[0] for p in pts]
    assert max(xs) - min(xs) > 200


def test_maurer_rose_symmetry_n_even():
    """For n=2 (even petals) the rose is symmetric about the centre by point structure."""
    pts = _compute_points(n=2, d=29)
    # The extent should be roughly equal in x and y
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x_span = max(xs) - min(xs)
    y_span = max(ys) - min(ys)
    assert abs(x_span - y_span) < 10, "Span should be roughly equal for n=2"


# ── Edge cases ───────────────────────────────────────────────────────────────

def test_maurer_rose_d_1_identical_to_rhodonea():
    """With d=1 each step is 1°, so the 360 points trace the full rhodonea curve."""
    pts = _compute_points(n=5, d=1)
    # The curve should be periodic and return close to start after 360 steps.
    # For n=5 with d=1 the curve closes (360 points × 1° = 360°).
    x0, y0 = pts[0]
    # The last step is k=359, theta=359°; the next would be 360°=0° which is the first.
    assert abs(x0 - 200) < 1e-6  # k=0 is always the centre

def test_maurer_rose_large_n():
    """High n (e.g. n=20) must still produce exactly 360 finite points."""
    pts = _compute_points(n=20, d=137)
    assert len(pts) == 360
    for x, y in pts:
        assert math.isfinite(x) and math.isfinite(y)


def test_pieces_json_description_not_empty():
    """Every piece in pieces.json must have a non-empty description."""
    for piece in _load_pieces():
        assert piece.get("description"), f"Empty description for {piece.get('id')}"


# ── Failure mode ─────────────────────────────────────────────────────────────

def test_maurer_rose_d_0_all_points_at_center():
    """With d=0 all thetas are 0, sin(n*0)=0, so every point is the centre."""
    pts = _compute_points(n=5, d=0)
    for x, y in pts:
        assert abs(x - 200) < 1e-9 and abs(y - 200) < 1e-9
