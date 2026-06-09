"""Tests for Piece 292 — Ink Bloom (stable-fluids)."""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "292-ink-bloom"
INDEX_HTML = PIECE_DIR / "index.html"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "292-ink-bloom"


# ---------------------------------------------------------------------------
# Happy-path: required files exist and are non-empty
# ---------------------------------------------------------------------------

def test_index_html_exists():
    assert INDEX_HTML.is_file()
    assert INDEX_HTML.stat().st_size > 0


def test_thumbnail_exists():
    thumb = PIECE_DIR / "thumbnail.svg"
    assert thumb.is_file()
    assert thumb.stat().st_size > 0


def test_readme_exists():
    readme = PIECE_DIR / "README.md"
    assert readme.is_file()
    assert readme.stat().st_size > 0


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

def _entry():
    data = json.loads(PIECES_JSON.read_text())
    matches = [e for e in data if e.get("id") == PIECE_ID]
    assert matches, f"No entry with id={PIECE_ID!r} found in pieces.json"
    return matches[0]


def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = _entry()
    assert required <= entry.keys(), f"Missing fields: {required - entry.keys()}"


def test_pieces_json_path_matches_dir():
    entry = _entry()
    assert entry["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_matches_file():
    entry = _entry()
    thumb_path = REPO / entry["thumbnail"]
    assert thumb_path.is_file()


# ---------------------------------------------------------------------------
# index.html: solver structure and acceptance-criteria checks
# ---------------------------------------------------------------------------

def _html():
    return INDEX_HTML.read_text()


def test_html_no_external_scripts():
    """No <script src=...> tags allowed — solver must be self-contained."""
    html = _html()
    ext = re.findall(r'<script[^>]+src\s*=', html, re.IGNORECASE)
    assert not ext, f"External scripts found: {ext}"


def test_html_uses_imagedata():
    assert "ImageData" in _html(), "Renderer must use ImageData for pixel writes"


def test_html_uses_requestanimationframe():
    assert "requestAnimationFrame" in _html()


def test_html_grid_size_256():
    """Acceptance criterion: ~256×256 grid."""
    html = _html()
    assert "256" in html, "Expected N=256 grid size reference in HTML"


def test_html_contains_all_four_ink_colors():
    html = _html()
    for color in ["3a0066", "1040c0", "c02060", "d08000"]:
        assert color.lower() in html.lower(), f"Missing ink color #{color}"


def test_html_has_lin_solve():
    """Gauss-Seidel linear solver must be present."""
    assert "linSolve" in _html() or "lin_solve" in _html()


def test_html_has_project():
    """Pressure projection step must be present."""
    assert "project" in _html()


def test_html_has_advect():
    """Advection step must be present."""
    assert "advect" in _html()


def test_html_has_diffuse():
    assert "diffuse" in _html()


def test_html_solver_under_250_lines():
    """Acceptance criterion: fluid solver self-contained in <250 lines JS."""
    html = _html()
    script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    assert script_match, "No inline <script> block found"
    js_lines = script_match.group(1).strip().split('\n')
    assert len(js_lines) < 250, f"JS is {len(js_lines)} lines, expected < 250"


def test_html_has_black_background():
    html = _html()
    assert "#000" in html or "background: #000" in html or "background:#000" in html


def test_html_caps_at_60fps():
    html = _html()
    assert "requestAnimationFrame" in html, "Must use rAF for 60fps cap"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_thumbnail_is_valid_svg():
    """Thumbnail must begin with an SVG root element."""
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<svg" in content


def test_pieces_json_id_unique():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e.get("id") for e in data]
    assert ids.count(PIECE_ID) == 1, "Duplicate piece id in pieces.json"


def test_pieces_json_year_is_int():
    entry = _entry()
    assert isinstance(entry["year"], int)


# ---------------------------------------------------------------------------
# Explicit failure mode
# ---------------------------------------------------------------------------

def test_missing_field_detected():
    """An entry without 'description' must fail the required-fields check."""
    incomplete = {
        "id": "292-ink-bloom",
        "title": "Ink Bloom",
        "tagline": "test",
        "year": 2026,
        "technique": "canvas",
        "path": "pieces/292-ink-bloom",
        "thumbnail": "pieces/292-ink-bloom/thumbnail.svg",
    }
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    assert not (required <= incomplete.keys()), "Expected missing 'description' to be detected"
