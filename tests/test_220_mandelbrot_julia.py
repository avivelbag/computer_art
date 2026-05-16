"""Tests for Piece 220 — Mandelbrot + Julia Interactive Explorer."""

import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "220-mandelbrot-julia"
INDEX = PIECE_DIR / "index.html"
THUMB = PIECE_DIR / "thumbnail.svg"
README = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# Directory and file existence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX.is_file()


def test_thumbnail_exists():
    assert THUMB.is_file()


def test_readme_exists():
    assert README.is_file()


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def entry():
    data = json.loads(PIECES_JSON.read_text())
    matches = [e for e in data if e.get("id") == "220-mandelbrot-julia"]
    assert matches, "No entry with id '220-mandelbrot-julia' found in pieces.json"
    return matches[0]


def test_entry_id(entry):
    assert entry["id"] == "220-mandelbrot-julia"


def test_entry_required_fields(entry):
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    assert required <= entry.keys()


def test_entry_path_matches_directory(entry):
    assert entry["path"] == "pieces/220-mandelbrot-julia"
    assert (REPO / entry["path"]).is_dir()


def test_entry_thumbnail_file_exists(entry):
    assert (REPO / entry["thumbnail"]).is_file()


def test_entry_technique_contains_required_keywords(entry):
    tech = entry["technique"].lower()
    for kw in ("webgl", "mandelbrot", "julia", "glsl", "escape-time"):
        assert kw in tech, f"Expected '{kw}' in technique field"


def test_entry_year(entry):
    assert entry["year"] == 2026


# ---------------------------------------------------------------------------
# index.html content
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def html():
    return INDEX.read_text()


def test_html_has_two_canvas_elements(html):
    mandel = "mandel-gl" in html
    julia = "julia-gl" in html
    assert mandel and julia, "Expected canvas ids 'mandel-gl' and 'julia-gl'"


def test_html_includes_panel_css(html):
    assert "lib/panel.css" in html


def test_html_includes_panel_js(html):
    assert "lib/panel.js" in html


def test_html_calls_gallery_panel_init(html):
    assert "GalleryPanel.init(" in html


def test_html_has_gallery_panel_sections(html):
    """Drawer must contain the four required educational sections."""
    assert "Mandelbrot set" in html or "mandelbrot" in html.lower()
    assert "Julia" in html
    assert "smooth" in html.lower() or "escape" in html.lower()
    assert "boundary" in html.lower() or "infinite" in html.lower()


def test_html_has_webgl_context_call(html):
    assert "getContext('webgl')" in html or 'getContext("webgl")' in html


def test_html_has_webgl_fallback(html):
    assert "WebGL" in html and ("unavailable" in html or "not available" in html or "no-webgl" in html)


def test_html_has_fragment_shader_with_smooth_coloring(html):
    """GLSL source must include the smooth iteration formula."""
    assert "log2" in html and "log" in html
    assert "u_maxIter" in html or "maxIter" in html


def test_html_has_julia_uniform(html):
    """Shader must accept c as a uniform for Julia mode."""
    assert "u_julia" in html
    assert "u_c" in html


def test_html_has_orbit_canvas(html):
    assert "orbit-canvas" in html or "orbit_canvas" in html


def test_html_has_pan_zoom_controls(html):
    """Scroll-wheel zoom and drag-to-pan must be wired up."""
    assert "mousemove" in html
    assert "wheel" in html
    assert "mousedown" in html


def test_html_has_max_iter_slider(html):
    assert 'id="iter-slider"' in html or "iter-slider" in html
    assert "min=" in html and "max=" in html


def test_html_has_reset_button(html):
    assert "reset" in html.lower()


def test_html_doctype(html):
    assert html.strip().startswith("<!DOCTYPE html>")


# ---------------------------------------------------------------------------
# thumbnail.svg content
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def svg():
    return THUMB.read_text()


def test_thumbnail_is_svg(svg):
    assert "<svg" in svg


def test_thumbnail_has_viewbox(svg):
    assert "viewBox" in svg


def test_thumbnail_has_content(svg):
    assert len(svg) > 200


# ---------------------------------------------------------------------------
# README.md content
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def readme():
    return README.read_text()


def test_readme_has_title(readme):
    assert "Mandelbrot" in readme and "Julia" in readme


def test_readme_explains_mandelbrot_set(readme):
    assert "z → z²" in readme or "z^2" in readme or "z²" in readme or "iteration" in readme.lower()


def test_readme_explains_smooth_coloring(readme):
    assert "smooth" in readme.lower() or "log" in readme.lower()


def test_readme_has_controls_section(readme):
    assert "Controls" in readme or "controls" in readme


# ---------------------------------------------------------------------------
# Edge / failure cases
# ---------------------------------------------------------------------------

def test_pieces_json_is_valid_json():
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list)
    assert len(data) > 0


def test_entry_id_matches_dir_name(entry):
    dir_name = pathlib.Path(entry["path"]).name
    assert entry["id"] == dir_name


def test_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "Duplicate ids found in pieces.json"


def test_thumbnail_svg_not_empty():
    content = THUMB.read_bytes()
    assert len(content) > 100


def test_index_html_not_empty():
    content = INDEX.read_bytes()
    assert len(content) > 1000
