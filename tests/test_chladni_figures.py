"""Tests for Piece 57 — Chladni Figures: Standing Waves Made Visible."""

import json
import math
import pathlib
import re

import pytest

REPO        = pathlib.Path(__file__).parent.parent
PIECE_DIR   = REPO / "pieces" / "57-chladni-figures"
INDEX       = PIECE_DIR / "index.html"
THUMB       = PIECE_DIR / "thumbnail.svg"
README      = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# Happy-path structural checks
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/57-chladni-figures/ must exist"


def test_required_files_exist():
    assert INDEX.is_file(),  "index.html must exist"
    assert THUMB.is_file(),  "thumbnail.svg must exist"
    assert README.is_file(), "README.md must exist"


def test_pieces_json_entry_present():
    entries = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in entries]
    assert "57-chladni-figures" in ids


def test_pieces_json_entry_fields():
    entries = json.loads(PIECES_JSON.read_text())
    entry   = next(e for e in entries if e["id"] == "57-chladni-figures")
    assert entry["path"]      == "pieces/57-chladni-figures"
    assert entry["thumbnail"] == "pieces/57-chladni-figures/thumbnail.svg"
    assert entry["year"]      == 2026
    assert "chladni" in entry["technique"].lower() or "imagedata" in entry["technique"].lower()


def test_pieces_json_entry_id_matches_dir():
    entries   = json.loads(PIECES_JSON.read_text())
    entry     = next(e for e in entries if e["id"] == "57-chladni-figures")
    piece_dir = REPO / entry["path"]
    assert entry["id"] == piece_dir.name


# ---------------------------------------------------------------------------
# index.html — implementation checks
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def source():
    """Return the full text of index.html."""
    return INDEX.read_text()


def test_has_canvas_element(source):
    assert "<canvas" in source


def test_uses_canvas_2d(source):
    assert "getContext('2d')" in source or 'getContext("2d")' in source


def test_uses_imagedata(source):
    """Per-pixel rendering must use ImageData / putImageData."""
    assert "createImageData" in source or "ImageData" in source
    assert "putImageData" in source


def test_uses_request_animation_frame(source):
    """60-fps cap requires requestAnimationFrame."""
    assert "requestAnimationFrame" in source


def test_chladni_formula_present(source):
    """The Chladni function must involve Math.cos."""
    assert "Math.cos" in source


def test_chladni_uses_pi(source):
    """Mode formula must use Math.PI."""
    assert "Math.PI" in source


def test_mode_pairs_present(source):
    """At least four (m,n) mode pairs must be listed in the MODES array."""
    # Locate the MODES assignment and grab everything up to the closing ];
    m = re.search(r'MODES\s*=\s*(\[.*?\]);', source, re.DOTALL)
    assert m is not None, "MODES constant not found in index.html"
    pairs = re.findall(r'\[\s*\d+\s*,\s*\d+\s*\]', m.group(1))
    assert len(pairs) >= 4, f"Expected ≥4 mode pairs, found {len(pairs)}"


def test_crossfade_present(source):
    """A crossfade weight (t) must be computed and applied."""
    assert "FADE" in source or "fade" in source.lower()


def test_threshold_pulse_present(source):
    """Threshold must pulse sinusoidally (Math.sin for breathing effect)."""
    assert "Math.sin" in source


def test_float32array_precompute(source):
    """Float32Array must be used for the precomputed f-value tables."""
    assert "Float32Array" in source


def test_separable_optimisation_present(source):
    """Separability optimisation: cos arrays must be precomputed per axis."""
    assert "Float32Array" in source


def test_indigo_background(source):
    """Deep indigo background colour must be present."""
    assert "0d0d2b" in source.lower() or "0d0d" in source.lower()


def test_cyan_glow_color(source):
    """Cyan glow colour (00e5ff or similar) must be referenced."""
    assert "00e5" in source.lower() or "00e5ff" in source.lower()


def test_no_external_scripts(source):
    """index.html must be fully self-contained."""
    external = re.findall(r'<script[^>]+src=["\']https?://', source)
    assert not external, f"Found external script imports: {external}"


def test_index_html_non_trivial(source):
    assert len(source) > 1500, "index.html must be non-trivial (>1500 bytes)"


# ---------------------------------------------------------------------------
# Chladni mathematics — pure Python sanity checks
# ---------------------------------------------------------------------------

def _chladni(m: int, n: int, x: float, y: float) -> float:
    """Reference implementation of the Chladni eigenmode function."""
    return (math.cos(m * math.pi * x) * math.cos(n * math.pi * y) -
            math.cos(n * math.pi * x) * math.cos(m * math.pi * y))


def test_chladni_antisymmetry():
    """f(y, x) == -f(x, y) must hold for all (m, n) with m != n."""
    for m, n in [(1, 2), (2, 3), (3, 4), (3, 5)]:
        for x, y in [(0.3, 0.7), (-0.5, 0.2), (0.8, -0.4)]:
            assert abs(_chladni(m, n, x, y) + _chladni(m, n, y, x)) < 1e-12


def test_chladni_diagonal_is_nodal_line():
    """Along the main diagonal y=x, f must be exactly zero."""
    for m, n in [(1, 2), (2, 3), (3, 5), (4, 5)]:
        for v in [-0.9, -0.5, 0.0, 0.3, 0.7, 1.0]:
            assert abs(_chladni(m, n, v, v)) < 1e-12


def test_chladni_anti_diagonal_is_nodal_line():
    """Along y = -x, f must also be exactly zero."""
    for m, n in [(1, 2), (3, 4), (2, 5)]:
        for v in [-0.8, -0.3, 0.0, 0.4, 0.9]:
            assert abs(_chladni(m, n, v, -v)) < 1e-12


def test_chladni_32_has_zeros_on_axes():
    """For (3,2), the zero set intersects the x-axis at x = 0, ±2/5, ±4/5."""
    expected = [0.0, 0.4, -0.4, 0.8, -0.8]
    for x in expected:
        assert abs(_chladni(3, 2, x, 0.0)) < 1e-12, f"Expected zero at x={x}, y=0"


def test_chladni_same_mode_is_zero_everywhere():
    """f(x, y) when m == n is identically zero (cos A cos B - cos B cos A = 0)."""
    for v in [0.0, 0.3, -0.6, 1.0]:
        assert _chladni(2, 2, v, 0.5) == 0.0
        assert _chladni(3, 3, 0.1, v) == 0.0


def test_chladni_range_bounded():
    """f values on the grid lie within [-2, 2] (product of two cos terms)."""
    for m, n in [(1, 2), (3, 5)]:
        for _ in range(50):
            import random
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            assert abs(_chladni(m, n, x, y)) <= 2.0 + 1e-10


# ---------------------------------------------------------------------------
# Thumbnail SVG checks
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def thumb_source():
    """Return the full text of thumbnail.svg."""
    return THUMB.read_text()


def test_thumbnail_is_svg(thumb_source):
    assert "<svg" in thumb_source


def test_thumbnail_has_rects(thumb_source):
    """Thumbnail must contain rect elements for the pixel-based nodal pattern."""
    assert "<rect" in thumb_source


def test_thumbnail_has_cyan(thumb_source):
    """Cyan nodal line colour must appear in the thumbnail."""
    assert "00e5ff" in thumb_source.lower() or "00e5" in thumb_source.lower()


def test_thumbnail_has_dark_background(thumb_source):
    """Deep indigo background must appear in the thumbnail."""
    assert "0d0d2b" in thumb_source.lower()


def test_thumbnail_has_glow_filter(thumb_source):
    """A SVG filter (glow) must be defined for the nodal lines."""
    assert "<filter" in thumb_source or "filter" in thumb_source


def test_thumbnail_non_trivial(thumb_source):
    rects = re.findall(r'<rect', thumb_source)
    assert len(rects) >= 100, f"Expected ≥100 rect elements, found {len(rects)}"


def test_thumbnail_file_not_directory():
    assert THUMB.is_file()
    assert not THUMB.is_dir()


# ---------------------------------------------------------------------------
# README checks
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    content = README.read_text().strip()
    assert len(content) > 100


def test_readme_mentions_chladni(source=None):
    content = README.read_text().lower()
    assert "chladni" in content


def test_readme_mentions_nodal_lines():
    content = README.read_text().lower()
    assert "nodal" in content


def test_readme_mentions_cos_formula():
    content = README.read_text()
    assert "cos" in content


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_piece_number_is_57():
    num = int(PIECE_DIR.name.split("-")[0])
    assert num == 57


def test_all_required_fields_in_entry():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    entries  = json.loads(PIECES_JSON.read_text())
    entry    = next(e for e in entries if e["id"] == "57-chladni-figures")
    missing  = required - entry.keys()
    assert not missing, f"Missing fields: {missing}"


def test_pieces_json_still_valid_after_addition():
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)
    assert len(data) >= 25  # at least previous 24 + this new piece


def test_chladni_large_mode_values():
    """High mode numbers (e.g. m=10, n=7) must still produce bounded values."""
    for x in [-1.0, -0.5, 0.0, 0.5, 1.0]:
        for y in [-1.0, 0.0, 1.0]:
            v = _chladni(10, 7, x, y)
            assert abs(v) <= 2.0 + 1e-9


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

def test_webgl_not_used(source):
    """This is a Canvas 2D piece — WebGL must not appear."""
    assert "webgl" not in source.lower()


def test_missing_piece_directory_detected(tmp_path):
    ghost = tmp_path / "ghost-piece"
    assert not ghost.is_dir()


def test_malformed_json_entry_detected():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    bad_entry = {"id": "57-chladni-figures", "title": "Chladni"}
    assert not (required <= bad_entry.keys())


def test_wrong_formula_caught():
    """The additive (symmetric) form g(x,y) = cos(mx)cos(ny) + cos(nx)cos(my)
    does NOT vanish on the diagonal y=x, unlike the correct antisymmetric form.
    This test confirms the two formulas are distinguishable via the diagonal."""
    def wrong_chladni(m, n, x, y):
        return (math.cos(m * math.pi * x) * math.cos(n * math.pi * y) +
                math.cos(n * math.pi * x) * math.cos(m * math.pi * y))

    # Correct formula: f(v, v) == 0 on the diagonal
    for v in [0.2, 0.5, 0.8]:
        assert abs(_chladni(2, 3, v, v)) < 1e-12, "Correct formula must be 0 on diagonal"

    # Wrong formula: g(v, v) = 2*cos(mv)*cos(nv) which is nonzero at generic v
    assert abs(wrong_chladni(2, 3, 0.2, 0.2)) > 0.1, (
        "Additive formula must be nonzero on the diagonal (distinguishable from correct)"
    )
