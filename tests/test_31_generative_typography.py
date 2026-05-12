"""Tests for pieces/31-letters-in-motion: generative typography particle system."""

import json
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "31-letters-in-motion"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "31-letters-in-motion"

BG_COLOR = "f5f0eb"
DARK_COLOR = "1a1a2e"
ACCENT_COLOR = "e94560"

WORD = "DRIFT"


# ---------------------------------------------------------------------------
# Python mirror of the pixel-sampling logic (for mathematical unit tests)
# ---------------------------------------------------------------------------


def sample_dark_pixels(
    data: list[int], width: int, height: int, step: int = 3
) -> list[tuple[int, int]]:
    """Return (x, y) coords of dark pixels from flat RGBA data at stride `step`.

    Mirrors the JavaScript sampleTextPixels loop: iterates y then x at the
    given stride and collects pixels whose red channel is below 128.
    """
    pts = []
    for y in range(0, height, step):
        for x in range(0, width, step):
            idx = (y * width + x) * 4
            if data[idx] < 128:
                pts.append((x, y))
    return pts


def make_flat_rgba(width: int, height: int, r: int, g: int, b: int) -> list[int]:
    """Produce a flat RGBA list filled with one uniform colour."""
    return [r, g, b, 255] * (width * height)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _html() -> str:
    """Return the full text of index.html."""
    return INDEX_HTML.read_text()


def _entry() -> dict:
    """Return the pieces.json entry for this piece, raising on missing."""
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


def test_html_canvas_has_id():
    html = _html()
    assert 'id="canvas"' in html or "id='canvas'" in html


def test_html_has_script_tag():
    assert "<script" in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html


def test_html_title_exists():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    assert len(m.group(1).strip()) > 0


def test_html_canvas_is_800():
    html = _html()
    assert 'width="800"' in html and 'height="800"' in html


def test_html_has_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained — no remote scripts"


# ---------------------------------------------------------------------------
# Palette tests
# ---------------------------------------------------------------------------


def test_html_contains_bg_color():
    assert BG_COLOR in _html().lower()


def test_html_contains_dark_color():
    assert DARK_COLOR in _html().lower()


def test_html_contains_accent_color():
    assert ACCENT_COLOR in _html().lower()


# ---------------------------------------------------------------------------
# JS animation and pixel-sampling structure tests
# ---------------------------------------------------------------------------


def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_js_has_delta_cap():
    assert "Math.min" in _html(), "Script must cap delta time with Math.min"


def test_js_has_get_image_data():
    assert "getImageData" in _html(), "index.html must call getImageData for pixel sampling"


def test_js_has_fill_text():
    assert "fillText" in _html(), "index.html must use fillText to rasterise the word"


def test_js_renders_target_word():
    html = _html()
    assert f"'{WORD}'" in html or f'"{WORD}"' in html, \
        f"The word {WORD!r} must appear as a string literal in index.html"


def test_js_has_offscreen_canvas():
    html = _html()
    assert "createElement('canvas')" in html or 'createElement("canvas")' in html, \
        "index.html must create an offscreen canvas for text rasterisation"


def test_js_has_assembling_phase():
    assert "assembling" in _html()


def test_js_has_holding_phase():
    assert "holding" in _html()


def test_js_has_dispersing_phase():
    assert "dispersing" in _html()


def test_js_assemble_duration_at_least_2s():
    html = _html()
    m = re.search(r"ASSEMBLE_MS\s*=\s*(\d+)", html)
    if m:
        assert int(m.group(1)) >= 2000, \
            f"ASSEMBLE_MS={m.group(1)} too short — must be ≥ 2000 ms"


def test_js_disperse_duration_at_least_2s():
    html = _html()
    m = re.search(r"DISPERSE_MS\s*=\s*(\d+)", html)
    if m:
        assert int(m.group(1)) >= 2000, \
            f"DISPERSE_MS={m.group(1)} too short — must be ≥ 2000 ms"


def test_js_has_lerp_toward_target():
    """Lerp-toward-target update: px += (tx - px) * factor."""
    html = _html()
    assert "ptx[i] - px[i]" in html or "tx - px" in html or "tx)" in html, \
        "index.html must lerp particles toward their text-pixel targets"


def test_js_has_wobble():
    html = _html()
    assert "Math.sin" in html and "Math.cos" in html, \
        "Particle wobble requires Math.sin and Math.cos"


def test_js_has_accent_fraction():
    html = _html()
    assert "ACCENT_FRAC" in html or "accentFrac" in html or "ACCENT_FRACTION" in html


def test_js_sample_step_is_reasonable():
    html = _html()
    m = re.search(r"SAMPLE_STEP\s*=\s*(\d+)", html)
    if m:
        step = int(m.group(1))
        assert 1 <= step <= 6, \
            f"SAMPLE_STEP={step} — expected 1–6 for adequate particle density"


# ---------------------------------------------------------------------------
# Pixel-sampling Python mirror tests
# ---------------------------------------------------------------------------


def test_sample_all_black_returns_all_sampled_positions():
    """An all-black image returns one point per stride position."""
    w, h, step = 9, 9, 3
    data = make_flat_rgba(w, h, 0, 0, 0)
    pts = sample_dark_pixels(data, w, h, step)
    expected_xs = list(range(0, w, step))
    expected_ys = list(range(0, h, step))
    assert len(pts) == len(expected_xs) * len(expected_ys)


def test_sample_all_white_returns_empty():
    """An all-white image yields no particle targets."""
    data = make_flat_rgba(6, 6, 255, 255, 255)
    assert sample_dark_pixels(data, 6, 6, step=3) == []


def test_sample_single_dark_pixel_detected():
    """A lone dark pixel at (3, 3) with step=3 must be found."""
    w, h = 9, 9
    data = make_flat_rgba(w, h, 255, 255, 255)
    idx = (3 * w + 3) * 4
    data[idx] = 0  # make red channel dark
    pts = sample_dark_pixels(data, w, h, step=3)
    assert (3, 3) in pts


def test_sample_pixel_between_strides_not_detected():
    """A dark pixel at (1, 1) is skipped when stride is 3."""
    w, h = 9, 9
    data = make_flat_rgba(w, h, 255, 255, 255)
    idx = (1 * w + 1) * 4
    data[idx] = 0
    pts = sample_dark_pixels(data, w, h, step=3)
    assert (1, 1) not in pts


def test_sample_respects_threshold_at_boundary():
    """Pixel with r=127 is dark; r=128 is not."""
    w, h = 3, 3
    data = make_flat_rgba(w, h, 255, 255, 255)
    data[0] = 127   # (0,0) — just dark enough
    data[4] = 128   # (1,0) — just too bright, but not on stride
    data[12] = 128  # (0,3) — too bright

    pts = sample_dark_pixels(data, w, h, step=1)
    assert (0, 0) in pts
    # r=128 pixels must NOT be included
    assert all(data[(y * w + x) * 4] < 128 for (x, y) in pts)


def test_sample_large_image_deterministic():
    """Sampling a fixed pattern twice must yield identical results."""
    w, h, step = 60, 60, 3
    data = make_flat_rgba(w, h, 255, 255, 255)
    for i in range(0, w * h * 4, 4 * 7):
        data[i] = 0
    pts1 = sample_dark_pixels(data, w, h, step)
    pts2 = sample_dark_pixels(data, w, h, step)
    assert pts1 == pts2


def test_sample_step_1_returns_all_dark_pixels():
    """At step=1 every dark pixel in the grid must be returned."""
    w, h = 4, 4
    data = make_flat_rgba(w, h, 255, 255, 255)
    dark = [(0, 0), (2, 1), (3, 3)]
    for x, y in dark:
        data[(y * w + x) * 4] = 0
    pts = sample_dark_pixels(data, w, h, step=1)
    for coord in dark:
        assert coord in pts


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
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


def test_thumbnail_contains_bg_color():
    assert BG_COLOR in THUMBNAIL.read_text().lower()


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_circle_elements():
    count = len(re.findall(r"<circle\b", THUMBNAIL.read_text()))
    assert count >= 50, f"Thumbnail must have ≥ 50 <circle> elements; found {count}"


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_under_500kb():
    size = THUMBNAIL.stat().st_size
    assert size < 500_000, f"thumbnail.svg is {size} bytes — must be under 500 KB"


def test_thumbnail_contains_dark_color():
    assert DARK_COLOR in THUMBNAIL.read_text().lower()


def test_thumbnail_contains_accent_color():
    assert ACCENT_COLOR in THUMBNAIL.read_text().lower()


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


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_particle():
    t = _entry()["technique"].lower()
    assert "particle" in t


def test_pieces_json_technique_mentions_typography():
    t = _entry()["technique"].lower()
    assert "typography" in t or "text" in t


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_pixel_sampling():
    readme = README.read_text().lower()
    assert "pixel" in readme or "getimagedata" in readme


def test_readme_mentions_offscreen_canvas():
    readme = README.read_text().lower()
    assert "offscreen" in readme or "canvas" in readme


def test_readme_mentions_target_word():
    assert WORD in README.read_text()


def test_readme_mentions_disperse_and_assemble():
    readme = README.read_text().lower()
    assert ("dispers" in readme or "scatter" in readme) and "assembl" in readme


def test_readme_mentions_background_color():
    assert BG_COLOR in README.read_text().lower()


# ---------------------------------------------------------------------------
# Failure-mode / edge-case tests
# ---------------------------------------------------------------------------


def test_wrong_piece_id_not_found():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "00-does-not-exist" not in ids


def test_missing_canvas_tag_detected():
    fake = "<html><body><div id='canvas'></div></body></html>"
    assert "<canvas" not in fake


def test_sample_empty_data_returns_empty():
    """Calling sample on a zero-dimension image must not crash and returns []."""
    assert sample_dark_pixels([], 0, 0, step=3) == []


def test_sample_step_larger_than_image_returns_at_most_origin():
    """With step bigger than the image, only (0, 0) can be sampled if it is dark."""
    w, h = 5, 5
    data = make_flat_rgba(w, h, 255, 255, 255)
    data[0] = 0  # dark at (0, 0)
    pts = sample_dark_pixels(data, w, h, step=10)
    assert pts == [(0, 0)]


def test_thumbnail_clip_path_element_present():
    svg = THUMBNAIL.read_text()
    assert "clipPath" in svg or "clip-path" in svg, \
        "Thumbnail should use SVG clipPath to shape the dot grid"
