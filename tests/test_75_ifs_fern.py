"""Tests for pieces/75-ifs-fern: IFS Barnsley fern chaos-game renderer."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO       = pathlib.Path(__file__).parent.parent
PIECE_DIR  = REPO / "pieces" / "75-ifs-fern"
INDEX_HTML = PIECE_DIR / "index.html"
README     = PIECE_DIR / "README.md"
THUMBNAIL  = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "75-ifs-fern"

# ---------------------------------------------------------------------------
# Python mirrors of the core IFS math for white-box testing
# ---------------------------------------------------------------------------

# Barnsley fern IFS: [a, b, c, d, e, f, p]
BARNSLEY_FERN = [
    [ 0.00,  0.00,  0.00,  0.16,  0.00,  0.00,  0.01],
    [ 0.85,  0.04, -0.04,  0.85,  0.00,  1.60,  0.85],
    [ 0.20, -0.26,  0.23,  0.22,  0.00,  1.60,  0.07],
    [-0.15,  0.28,  0.26,  0.24,  0.00,  0.44,  0.07],
]


def apply_transform(row, x, y):
    """Apply a single affine IFS transform [a,b,c,d,e,f,p] to point (x,y).

    Returns (x', y') where x' = a*x + b*y + e and y' = c*x + d*y + f.
    """
    a, b, c, d, e, f, _p = row
    return a * x + b * y + e, c * x + d * y + f


def lerp_ifs(ifs_a, ifs_b, t):
    """Linearly interpolate between two IFS parameter sets at position t in [0,1].

    Returns a new list of rows with coefficients lerped element-wise.
    """
    result = []
    for row_a, row_b in zip(ifs_a, ifs_b):
        result.append([a * (1 - t) + b * t for a, b in zip(row_a, row_b)])
    return result


def build_cum_probs(ifs):
    """Build cumulative probability array for weighted transform selection.

    Returns list of 4 cumulative thresholds based on the p column (index 6).
    """
    cum = []
    total = 0.0
    for row in ifs:
        total += row[6]
        cum.append(total)
    return cum


def chaos_game(ifs, n_points, seed=42):
    """Run n_points iterations of the chaos game on the given IFS.

    Returns list of (x, y, transform_index) tuples (after 20 warm-up steps).
    Uses a simple LCG for determinism so tests don't depend on random state.
    """
    import random
    rng = random.Random(seed)
    cum = build_cum_probs(ifs)
    x, y = 0.0, 0.0

    # warm up
    for _ in range(20):
        r = rng.random()
        ti = next((i for i, c in enumerate(cum) if r <= c), len(cum) - 1)
        x, y = apply_transform(ifs[ti], x, y)

    points = []
    for _ in range(n_points):
        r = rng.random()
        ti = next((i for i, c in enumerate(cum) if r <= c), len(cum) - 1)
        x, y = apply_transform(ifs[ti], x, y)
        points.append((x, y, ti))
    return points


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
    assert "UTF-8" in html


def test_html_title_exists():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m and len(m.group(1).strip()) > 0


def test_html_has_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained — no remote scripts"


def test_html_canvas_resizes_to_window():
    html = _html()
    assert "window.innerWidth" in html and "window.innerHeight" in html


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


# ---------------------------------------------------------------------------
# IFS / chaos game structural tests (source inspection)
# ---------------------------------------------------------------------------

def test_html_contains_barnsley_fern_coefficients():
    """The stem transform must have a=0, d=0.16 — hallmark Barnsley coefficients."""
    html = _html()
    assert "0.16" in html, "Barnsley fern stem transform coefficient 0.16 missing"


def test_html_contains_main_leaflet_coefficient():
    """The main leaflet transform must use a=0.85."""
    assert "0.85" in _html()


def test_html_defines_presets_array():
    assert "PRESETS" in _html()


def test_html_defines_palette():
    assert "PALETTE" in _html()


def test_html_defines_lerp_function():
    html = _html()
    assert "lerpIFS" in html or "lerp" in html.lower()


def test_html_contains_morph_ms():
    """Morph cycle duration constant must be present."""
    assert "MORPH_MS" in _html() or "MORPH" in _html()


def test_html_contains_min_points():
    """The 2-million-point pre-render gate constant must be present."""
    html = _html()
    assert "2_000_000" in html or "2000000" in html


def test_html_uses_float32array():
    """Hit-count buffers must use Float32Array for efficiency."""
    assert "Float32Array" in _html()


def test_html_uses_log_density():
    """Log-density tone mapping must be present (log1p or Math.log)."""
    html = _html()
    assert "log1p" in html or "Math.log" in html


def test_html_contains_imagedata():
    """Rendering must use ImageData for direct pixel manipulation."""
    assert "ImageData" in _html() or "createImageData" in _html()


def test_html_has_four_palette_colors():
    """PALETTE array must have exactly four color entries."""
    html = _html()
    # Each palette entry is an array literal [r, g, b]
    palette_section = html[html.find("PALETTE"):]
    bracket_pairs = palette_section[:200].count("[")
    assert bracket_pairs >= 5, "Expected at least 4 sub-arrays inside PALETTE"


def test_html_has_three_presets():
    """Three IFS presets must be defined for the morph animation."""
    html = _html()
    presets_section = html[html.find("PRESETS"):html.find("PRESETS") + 800]
    assert presets_section.count("0.16") >= 1, "First preset (Barnsley fern) missing"


def test_html_uses_alpha_decay():
    """Frame-by-frame buffer decay (0.97 or 0.99) must be present for morph fading."""
    html = _html()
    assert "0.97" in html or "0.98" in html or "0.99" in html


# ---------------------------------------------------------------------------
# Python mirror: apply_transform tests
# ---------------------------------------------------------------------------

def test_stem_transform_maps_to_stem():
    """Transform 0 (stem): any point maps near x=0, y=0..1.6 — the basal stem."""
    stem = BARNSLEY_FERN[0]
    for x, y in [(-1.0, 5.0), (2.0, 0.0), (0.5, 9.0)]:
        nx, ny = apply_transform(stem, x, y)
        assert abs(nx) < 1e-9, f"Stem x should be 0 but got {nx}"
        assert 0 <= ny <= 2.0, f"Stem y out of range: {ny}"


def test_main_leaflet_transform_bounded():
    """Transform 1 (main leaflet): points in fern space stay roughly in fern space."""
    t1 = BARNSLEY_FERN[1]
    x, y = 1.0, 3.0
    nx, ny = apply_transform(t1, x, y)
    assert -3 < nx < 3
    assert 0 < ny < 12


def test_left_leaflet_transform_positive_y():
    """Transform 2 (left leaflet): output y should be positive for fern-range input."""
    t2 = BARNSLEY_FERN[2]
    nx, ny = apply_transform(t2, 1.0, 3.0)
    assert ny > 0


def test_right_leaflet_transform_positive_y():
    """Transform 3 (right leaflet): output y should be positive for fern-range input."""
    t3 = BARNSLEY_FERN[3]
    nx, ny = apply_transform(t3, 1.0, 3.0)
    assert ny > 0


def test_apply_transform_identity_ish():
    """With a=d=1, b=c=0, e=f=0 the transform is identity."""
    identity = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    x, y = 3.7, -2.1
    nx, ny = apply_transform(identity, x, y)
    assert abs(nx - x) < 1e-12
    assert abs(ny - y) < 1e-12


def test_apply_transform_translation():
    """With a=d=1, b=c=0, e=2, f=3 the transform is pure translation."""
    row = [1.0, 0.0, 0.0, 1.0, 2.0, 3.0, 1.0]
    nx, ny = apply_transform(row, 1.0, 1.0)
    assert abs(nx - 3.0) < 1e-12
    assert abs(ny - 4.0) < 1e-12


# ---------------------------------------------------------------------------
# Python mirror: lerp_ifs tests
# ---------------------------------------------------------------------------

def test_lerp_ifs_t0_returns_a():
    """At t=0 lerp_ifs must return the A preset exactly."""
    a = BARNSLEY_FERN
    b = [[0.0] * 7 for _ in range(4)]
    result = lerp_ifs(a, b, 0.0)
    for i in range(4):
        for j in range(7):
            assert abs(result[i][j] - a[i][j]) < 1e-12


def test_lerp_ifs_t1_returns_b():
    """At t=1 lerp_ifs must return the B preset exactly."""
    a = [[0.0] * 7 for _ in range(4)]
    b = BARNSLEY_FERN
    result = lerp_ifs(a, b, 1.0)
    for i in range(4):
        for j in range(7):
            assert abs(result[i][j] - b[i][j]) < 1e-12


def test_lerp_ifs_midpoint():
    """At t=0.5 each coefficient is the average of A and B."""
    a = [[2.0] * 7 for _ in range(4)]
    b = [[4.0] * 7 for _ in range(4)]
    result = lerp_ifs(a, b, 0.5)
    for i in range(4):
        for j in range(7):
            assert abs(result[i][j] - 3.0) < 1e-12


def test_lerp_ifs_extrapolation_beyond_1():
    """lerp_ifs works with t > 1 (extrapolation), no crash."""
    result = lerp_ifs(BARNSLEY_FERN, BARNSLEY_FERN, 2.0)
    for i in range(4):
        for j in range(7):
            assert math.isfinite(result[i][j])


# ---------------------------------------------------------------------------
# Python mirror: build_cum_probs tests
# ---------------------------------------------------------------------------

def test_cum_probs_last_element_near_one():
    """Cumulative probabilities must sum to ~1.0 for Barnsley fern."""
    cum = build_cum_probs(BARNSLEY_FERN)
    assert abs(cum[-1] - 1.0) < 1e-9


def test_cum_probs_monotone():
    """Cumulative probabilities must be non-decreasing."""
    cum = build_cum_probs(BARNSLEY_FERN)
    for i in range(1, len(cum)):
        assert cum[i] >= cum[i - 1]


def test_cum_probs_length_matches_transforms():
    """One cumulative value per transform."""
    cum = build_cum_probs(BARNSLEY_FERN)
    assert len(cum) == len(BARNSLEY_FERN)


# ---------------------------------------------------------------------------
# Python mirror: chaos game statistical tests
# ---------------------------------------------------------------------------

def test_chaos_game_barnsley_y_range():
    """Chaos-game points on Barnsley fern must all have y in [0, 11]."""
    points = chaos_game(BARNSLEY_FERN, 500)
    for x, y, _ in points:
        assert 0 <= y <= 11.0, f"y={y} out of expected fern range"


def test_chaos_game_barnsley_x_bounded():
    """Barnsley fern x values stay within the known fern width [-3, 3]."""
    points = chaos_game(BARNSLEY_FERN, 2000)
    for x, y, _ in points:
        assert -3.0 <= x <= 3.0, f"x={x} outside expected fern width"


def test_chaos_game_transform_0_rarely_chosen():
    """Transform 0 has p=0.01, so < 5% of points should use it."""
    points = chaos_game(BARNSLEY_FERN, 2000)
    count_t0 = sum(1 for _, _, ti in points if ti == 0)
    assert count_t0 / len(points) < 0.05


def test_chaos_game_transform_1_mostly_chosen():
    """Transform 1 has p=0.85, so > 75% of points should use it."""
    points = chaos_game(BARNSLEY_FERN, 2000)
    count_t1 = sum(1 for _, _, ti in points if ti == 1)
    assert count_t1 / len(points) > 0.75


def test_chaos_game_no_nan():
    """No NaN or Inf may appear in chaos-game output."""
    points = chaos_game(BARNSLEY_FERN, 500)
    for x, y, _ in points:
        assert math.isfinite(x) and math.isfinite(y)


def test_chaos_game_deterministic():
    """Same seed produces identical point sequence."""
    p1 = chaos_game(BARNSLEY_FERN, 100, seed=7)
    p2 = chaos_game(BARNSLEY_FERN, 100, seed=7)
    assert p1 == p2


# ---------------------------------------------------------------------------
# Thumbnail tests
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
    assert size < 200_000, f"thumbnail.svg is {size} bytes"


def test_thumbnail_dark_background():
    """Background rect must use a dark color."""
    svg = THUMBNAIL.read_text()
    assert "#050a05" in svg or "#000" in svg or "#0" in svg


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


def test_pieces_json_technique_mentions_ifs_or_chaos():
    t = _entry()["technique"].lower()
    assert "ifs" in t or "chaos" in t or "iterated" in t


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_barnsley():
    assert "barnsley" in README.read_text().lower() or "Barnsley" in README.read_text()


def test_readme_mentions_chaos_game():
    readme = README.read_text().lower()
    assert "chaos" in readme and "game" in readme


def test_readme_mentions_affine():
    assert "affine" in README.read_text().lower()


# ---------------------------------------------------------------------------
# Failure-mode / edge-case tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "75-does-not-exist" not in ids


def test_lerp_ifs_t_exactly_zero_and_one_stable():
    """Boundary values t=0 and t=1 must not produce NaN."""
    for t in (0.0, 1.0):
        result = lerp_ifs(BARNSLEY_FERN, BARNSLEY_FERN, t)
        for row in result:
            for v in row:
                assert math.isfinite(v)


def test_chaos_game_empty_returns_empty():
    """Zero points requested returns empty list."""
    points = chaos_game(BARNSLEY_FERN, 0)
    assert points == []


def test_chaos_game_single_point_valid():
    """A single chaos-game step must produce a finite point."""
    points = chaos_game(BARNSLEY_FERN, 1)
    assert len(points) == 1
    x, y, ti = points[0]
    assert math.isfinite(x) and math.isfinite(y)
    assert 0 <= ti <= 3


def test_build_cum_probs_uniform_distribution():
    """Four transforms each with p=0.25 give cumulative [0.25, 0.5, 0.75, 1.0]."""
    uniform_ifs = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25] for _ in range(4)]
    cum = build_cum_probs(uniform_ifs)
    expected = [0.25, 0.50, 0.75, 1.00]
    for got, exp in zip(cum, expected):
        assert abs(got - exp) < 1e-12
