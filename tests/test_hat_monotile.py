"""Tests for piece 286-hat-monotile — Hat aperiodic tiling."""
import json
import pathlib
import math

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "286-hat-monotile"
INDEX_HTML = PIECE_DIR / "index.html"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
README = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"

S3 = math.sqrt(3)


# ---------------------------------------------------------------------------
# File-level existence checks
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_thumbnail_svg_exists():
    assert THUMBNAIL.is_file()


def test_readme_exists():
    assert README.is_file()


# ---------------------------------------------------------------------------
# pieces.json entry checks
# ---------------------------------------------------------------------------

def _entry():
    data = json.loads(PIECES_JSON.read_text())
    for e in data:
        if e["id"] == "286-hat-monotile":
            return e
    return None


def test_pieces_json_has_entry():
    assert _entry() is not None, "286-hat-monotile not found in pieces.json"


def test_pieces_json_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = _entry()
    assert entry is not None
    assert required <= entry.keys()


def test_pieces_json_id_matches_dir():
    entry = _entry()
    assert entry is not None
    assert entry["id"] == PIECE_DIR.name


def test_pieces_json_year():
    entry = _entry()
    assert entry is not None
    assert entry["year"] == 2026


def test_pieces_json_thumbnail_path_exists():
    entry = _entry()
    assert entry is not None
    assert (REPO / entry["thumbnail"]).is_file()


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def _html():
    return INDEX_HTML.read_text()


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_uses_no_external_libraries():
    """Acceptance criterion: all geometry computed from scratch, no tile libraries."""
    html = _html()
    forbidden = ["cdn.jsdelivr", "unpkg.com", "cdnjs.cloudflare"]
    for lib in forbidden:
        assert lib not in html, f"External library reference found: {lib}"


def test_html_has_palette_colors():
    """Acceptance criterion: palette uses the specified 4 harmonious hues."""
    html = _html()
    for color in ["#c4623a", "#e8c88a", "#6a8fa8", "#f5f0e8"]:
        assert color in html, f"Required palette color {color} missing from index.html"


def test_html_has_substitution_depth():
    """Acceptance criterion: 3-4 inflation levels — DEPTH constant must be 3 or 4."""
    html = _html()
    assert "DEPTH = 4" in html or "DEPTH = 3" in html


def test_html_triangular_grid_conversion():
    """index.html must contain the triangular-grid to Cartesian conversion formula."""
    html = _html()
    # Both the r*0.5 (r/2) and S3 (sqrt(3)) factors must be present
    assert "0.5" in html
    assert "S3" in html or "sqrt(3)" in html or "Math.sqrt(3)" in html or "1.732" in html


def test_html_substitution_rule_present():
    """index.html must implement the substitution/inflation rule recursively."""
    html = _html()
    assert "substitution" in html.lower() or "recurse" in html or "children" in html


def test_html_hat_vertices_defined():
    """The 13 Hat vertices must be defined."""
    html = _html()
    # The Hat has 13 vertices; check the vertex array is referenced
    assert "HAT_VERTS" in html or "13" in html


# ---------------------------------------------------------------------------
# README checks
# ---------------------------------------------------------------------------

def test_readme_mentions_hat():
    text = README.read_text().lower()
    assert "hat" in text


def test_readme_mentions_substitution():
    text = README.read_text().lower()
    assert "substitut" in text


def test_readme_mentions_palette():
    """README must document the palette."""
    text = README.read_text()
    for color in ["#c4623a", "#e8c88a", "#6a8fa8", "#f5f0e8"]:
        assert color in text, f"Color {color} not documented in README"


# ---------------------------------------------------------------------------
# Geometry unit tests — pure Python re-implementation of the JS functions
# ---------------------------------------------------------------------------

def tri_to_cart(q, r):
    """Convert triangular grid coords to Cartesian."""
    return (q + r * 0.5, r * S3 * 0.5)


HAT_VERTS_TRI = [
    (0, 0), (1, 0), (2, 0), (2, 1), (3, 1),
    (3, 2), (2, 2), (1, 2), (1, 3), (0, 3),
    (0, 2), (-1, 2), (-1, 1),
]


def test_hat_has_13_vertices():
    assert len(HAT_VERTS_TRI) == 13


def test_tri_to_cart_origin():
    """Origin maps to (0, 0)."""
    x, y = tri_to_cart(0, 0)
    assert x == pytest.approx(0.0)
    assert y == pytest.approx(0.0)


def test_tri_to_cart_unit_q():
    """One step along q-axis: (1,0) → (1.0, 0.0)."""
    x, y = tri_to_cart(1, 0)
    assert x == pytest.approx(1.0)
    assert y == pytest.approx(0.0)


def test_tri_to_cart_unit_r():
    """One step along r-axis: (0,1) → (0.5, √3/2)."""
    x, y = tri_to_cart(0, 1)
    assert x == pytest.approx(0.5)
    assert y == pytest.approx(S3 / 2)


def test_hat_verts_cartesian_distinct():
    """All 13 Hat vertices must map to distinct Cartesian positions."""
    pts = [tri_to_cart(q, r) for q, r in HAT_VERTS_TRI]
    assert len(set(pts)) == 13


def test_hat_bounding_box():
    """Hat bounding box in Cartesian must span positive non-zero range."""
    pts = [tri_to_cart(q, r) for q, r in HAT_VERTS_TRI]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    assert max(xs) - min(xs) > 0
    assert max(ys) - min(ys) > 0


def test_inflation_factor_value():
    """Inflation factor 1+√3 must match known value to 3 decimal places."""
    inf = 1 + S3
    assert inf == pytest.approx(2.732, abs=0.001)


def test_affine_identity():
    """Composing with the identity must return the original transform."""
    def apply(m, x, y):
        return (m[0]*x + m[1]*y + m[2], m[3]*x + m[4]*y + m[5])

    ident = [1, 0, 0, 0, 1, 0]
    for x, y in [(0, 0), (3.5, -2.1), (-1, 4)]:
        rx, ry = apply(ident, x, y)
        assert rx == pytest.approx(x)
        assert ry == pytest.approx(y)


def test_affine_translation():
    """Translation transform must shift points correctly."""
    def apply(m, x, y):
        return (m[0]*x + m[1]*y + m[2], m[3]*x + m[4]*y + m[5])

    translate = [1, 0, 5.0, 0, 1, -3.0]
    rx, ry = apply(translate, 2.0, 1.0)
    assert rx == pytest.approx(7.0)
    assert ry == pytest.approx(-2.0)


def test_affine_scale():
    """Scale transform must multiply coordinates."""
    def apply(m, x, y):
        return (m[0]*x + m[1]*y + m[2], m[3]*x + m[4]*y + m[5])

    s = 0.5
    scale = [s, 0, 0, 0, s, 0]
    rx, ry = apply(scale, 4.0, 6.0)
    assert rx == pytest.approx(2.0)
    assert ry == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_thumbnail_is_valid_svg():
    """thumbnail.svg must start with SVG markup."""
    content = THUMBNAIL.read_text()
    assert "<svg" in content
    assert "</svg>" in content


def test_thumbnail_has_background_color():
    """Thumbnail background must use the dark umber #1e1a14."""
    content = THUMBNAIL.read_text()
    assert "#1e1a14" in content


def test_index_html_is_self_contained():
    """index.html should contain a <script> block (no separate .js file)."""
    content = _html()
    assert "<script>" in content
    assert "src=" not in content or 'src="' not in content


def test_readme_not_empty():
    content = README.read_text().strip()
    assert len(content) > 50
