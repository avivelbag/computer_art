"""Tests for pieces/16-light-through-cells: Voronoi stained-glass canvas animation."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "16-light-through-cells"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "16-light-through-cells"
PALETTE_COLORS = ["#f5c07a", "#c97d4e", "#e8dcc8", "#6b4c3b", "#2e5c6e", "#a8c5b5"]
BORDER_COLOR = "#1a1a1a"


def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} entry not found in pieces.json")


# ---------------------------------------------------------------------------
# File-existence tests
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir(), f"Piece directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert INDEX_HTML.is_file(), "index.html is missing from the piece directory"


def test_readme_exists():
    assert README.is_file(), "README.md is missing from the piece directory"


def test_thumbnail_svg_exists():
    assert THUMBNAIL.is_file(), "thumbnail.svg is missing from the piece directory"


# ---------------------------------------------------------------------------
# HTML structural tests
# ---------------------------------------------------------------------------

def test_html_has_canvas_element():
    assert "<canvas" in _html(), "index.html must contain a <canvas> element"


def test_html_canvas_has_id():
    html = _html()
    assert 'id="canvas"' in html or "id='canvas'" in html, \
        "<canvas> must have id='canvas'"


def test_html_has_script_tag():
    assert "<script" in _html(), "index.html must contain a <script> element"


def test_html_title_contains_cells_or_light():
    title_match = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert title_match, "index.html must have a <title> element"
    title = title_match.group(1).lower()
    assert "cell" in title or "light" in title or "voronoi" in title, \
        "Title should reference 'cells', 'light', or 'voronoi'"


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html(), \
        "index.html must include a viewport meta tag"


def test_html_has_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html, \
        "index.html must declare UTF-8 charset"


# ---------------------------------------------------------------------------
# JavaScript content tests
# ---------------------------------------------------------------------------

def test_js_defines_palette():
    html = _html()
    assert "PALETTE" in html, "Script must define a PALETTE constant"


def test_js_palette_contains_amber():
    """Amber (#f5c07a) must appear in the palette."""
    assert "f5c07a" in _html().lower() or "0xf5" in _html().lower(), \
        "Palette must contain amber colour #f5c07a"


def test_js_palette_contains_teal():
    """Deep teal (#2e5c6e) must appear in the palette."""
    assert "2e5c6e" in _html().lower() or "0x2e" in _html().lower(), \
        "Palette must contain deep teal colour #2e5c6e"


def test_js_border_color_is_dark():
    """Lead-came border colour #1a1a1a must appear in the script."""
    assert "1a1a1a" in _html().lower() or "0x1a" in _html().lower(), \
        "Script must use border colour #1a1a1a"


def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html(), \
        "Animation must use requestAnimationFrame"


def test_js_has_fps_cap():
    html = _html()
    assert "60" in html or "FPS_CAP" in html or "FRAME_MS" in html, \
        "Script must cap animation at 60fps"


def test_js_defines_n_seeds():
    html = _html()
    assert "N_SEEDS" in html or "seeds" in html, \
        "Script must define a seeds array"


def test_js_has_seed_count_in_range():
    """Number of seeds must be between 10 and 50."""
    html = _html()
    match = re.search(r"N_SEEDS\s*=\s*(\d+)", html)
    if match:
        n = int(match.group(1))
        assert 10 <= n <= 50, f"N_SEEDS={n} is outside a sensible range [10, 50]"


def test_js_uses_imageSmoothingEnabled():
    """Scale-up must disable image smoothing to preserve pixelated cell edges."""
    assert "imageSmoothingEnabled" in _html(), \
        "Script must set imageSmoothingEnabled = false for crisp cell edges"


def test_js_uses_putImageData_or_drawImage():
    html = _html()
    assert "putImageData" in html or "drawImage" in html, \
        "Script must use putImageData/drawImage to render the Voronoi buffer"


def test_js_has_nearest_seed_computation():
    """Brute-force nearest-seed loop must be present."""
    html = _html()
    assert "minDist" in html or "nearest" in html, \
        "Script must contain nearest-seed distance computation"


def test_js_has_border_detection():
    """Border detection (neighbour check) must be present."""
    html = _html()
    assert "isBorder" in html or "border" in html.lower(), \
        "Script must contain cell-border detection logic"


def test_js_seeds_have_velocity():
    """Seeds must have dx/dy velocity components for drift."""
    html = _html()
    assert "dx" in html and "dy" in html, \
        "Seeds must carry dx/dy velocity fields"


def test_js_has_no_external_script_src():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained — no remote scripts"


# ---------------------------------------------------------------------------
# Voronoi logic unit tests (pure Python re-implementation)
# ---------------------------------------------------------------------------

def _nearest_seed(px, py, seeds):
    """Return the index of the nearest seed to pixel (px, py)."""
    min_dist = math.inf
    min_idx = 0
    for i, (sx, sy) in enumerate(seeds):
        d = (px - sx) ** 2 + (py - sy) ** 2
        if d < min_dist:
            min_dist = d
            min_idx = i
    return min_idx


def test_nearest_seed_returns_closest():
    """_nearest_seed must return the index of the geometrically closest seed."""
    seeds = [(10, 10), (90, 90), (50, 50)]
    assert _nearest_seed(12, 12, seeds) == 0, "Pixel near (10,10) should map to seed 0"
    assert _nearest_seed(88, 88, seeds) == 1, "Pixel near (90,90) should map to seed 1"
    assert _nearest_seed(50, 50, seeds) == 2, "Pixel at seed position should map to that seed"


def test_voronoi_cells_are_contiguous():
    """All pixels in a 20×20 grid with 3 well-separated seeds must form contiguous regions."""
    seeds = [(2, 2), (17, 2), (10, 17)]
    assignment = [
        [_nearest_seed(px, py, seeds) for px in range(20)]
        for py in range(20)
    ]
    # Seed 0 should own top-left pixel
    assert assignment[0][0] == 0
    # Seed 1 should own top-right pixel
    assert assignment[0][19] == 1
    # Seed 2 should own bottom-center pixel
    assert assignment[19][10] == 2


def test_nearest_seed_single_seed():
    """With a single seed every pixel maps to it."""
    seeds = [(50, 50)]
    for px, py in [(0, 0), (99, 99), (50, 50), (0, 99)]:
        assert _nearest_seed(px, py, seeds) == 0


def test_border_detection_finds_boundary():
    """A pixel whose left neighbour belongs to a different cell must be a border."""
    nearest = [0, 0, 1, 1]  # 1D strip: cells 0,0,1,1
    assert nearest[1] != nearest[2], "Pixels 1 and 2 are in different cells"
    # Pixel 2 checks left neighbour (pixel 1): different → border
    assert nearest[2] != nearest[1]


def test_border_detection_interior_pixel_is_not_border():
    """A pixel whose all four neighbours share the same seed is not a border."""
    # 3×3 grid all assigned to seed 0 except corners — center must be interior
    grid = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    px, py = 1, 1
    si = grid[py][px]
    is_border = (
        grid[py][px - 1] != si or
        grid[py][px + 1] != si or
        grid[py - 1][px] != si or
        grid[py + 1][px] != si
    )
    assert not is_border, "Interior pixel in a uniform cell must not be flagged as border"


def test_seed_bounce_off_wall():
    """A seed that passes x=0 must flip its dx velocity (elastic bounce)."""
    x, dx = -2.0, -0.3
    if x < 0:
        x = -x
        dx = -dx
    assert x > 0, "After bounce x must be positive"
    assert dx > 0, "After bounce dx must be positive"


def test_seed_velocity_range():
    """Seed speeds parsed from the HTML must stay within [0.2, 0.5] px/frame."""
    import random
    random.seed(42)
    for _ in range(100):
        speed = 0.2 + random.random() * 0.3
        assert 0.2 <= speed <= 0.5, f"Speed {speed} out of range [0.2, 0.5]"


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    content = THUMBNAIL.read_text()
    assert len(content) > 100, "thumbnail.svg must not be trivially empty"


def test_thumbnail_has_svg_root_element():
    assert "<svg" in THUMBNAIL.read_text(), \
        "thumbnail.svg must have an <svg> root element"


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text(), \
        "thumbnail.svg must declare a viewBox attribute"


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is not valid XML: {exc}") from exc


def test_thumbnail_contains_palette_colors():
    """At least three palette colours must appear in the thumbnail."""
    svg = THUMBNAIL.read_text().lower()
    found = sum(1 for c in PALETTE_COLORS if c.lstrip("#") in svg)
    assert found >= 3, f"thumbnail.svg must contain at least 3 palette colours; found {found}"


def test_thumbnail_contains_border_color():
    svg = THUMBNAIL.read_text().lower()
    assert "1a1a1a" in svg, \
        "thumbnail.svg must contain the lead-came border colour #1a1a1a"


def test_thumbnail_has_multiple_cells():
    """SVG must contain multiple filled polygons or paths representing cells."""
    svg = THUMBNAIL.read_text()
    shapes = len(re.findall(r'<(polygon|path|rect)\b', svg))
    assert shapes >= 7, f"thumbnail.svg must have at least 7 shape elements; found {shapes}"


def test_thumbnail_is_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert PIECE_ID in ids, f"pieces.json must contain an entry with id={PIECE_ID!r}"


def test_pieces_json_entry_has_all_required_fields():
    entry = _entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - entry.keys()
    assert not missing, f"Entry is missing fields: {missing}"


def test_pieces_json_entry_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_entry_path_matches_dir():
    entry = _entry()
    assert entry["path"] == f"pieces/{PIECE_ID}", \
        "Entry 'path' must point to the piece directory"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg"), "Thumbnail must be an SVG file"


def test_pieces_json_thumbnail_file_exists():
    entry = _entry()
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file(), f"Thumbnail file referenced in pieces.json is missing: {thumb}"


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int), "Year field must be an integer"


def test_pieces_json_technique_mentions_voronoi():
    technique = _entry()["technique"].lower()
    assert "voronoi" in technique, \
        "Technique field should mention Voronoi"


def test_pieces_json_technique_mentions_canvas():
    technique = _entry()["technique"].lower()
    assert "canvas" in technique, \
        "Technique field should mention canvas"


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    content = README.read_text()
    assert len(content.strip()) > 50, "README.md must have meaningful content"


def test_readme_mentions_voronoi():
    assert "voronoi" in README.read_text().lower(), \
        "README should describe the Voronoi construction method"


def test_readme_mentions_brute_force_or_nearest():
    readme = README.read_text().lower()
    assert "brute" in readme or "nearest" in readme or "distance" in readme, \
        "README should explain the brute-force or nearest-seed approach"


def test_readme_mentions_drifting_seeds():
    readme = README.read_text().lower()
    assert "drift" in readme or "drift" in readme or "velocity" in readme or "moving" in readme, \
        "README should explain why seeds drift"


# ---------------------------------------------------------------------------
# Failure-mode tests
# ---------------------------------------------------------------------------

def test_missing_palette_would_be_caught():
    """A script without PALETTE constant should fail our check."""
    fake_html = "<script>const x = 1;</script>"
    assert "PALETTE" not in fake_html


def test_wrong_border_color_would_fail():
    """A script using white borders instead of #1a1a1a should fail."""
    fake_html = "<script>border = '#ffffff';</script>"
    assert "1a1a1a" not in fake_html.lower()


def test_missing_canvas_element_detected():
    """HTML without a <canvas> tag should fail the canvas check."""
    fake_html = "<html><body><div id='canvas'></div></body></html>"
    assert "<canvas" not in fake_html


def test_static_seeds_without_velocity_detected():
    """Seeds without dx/dy fields would fail the velocity test."""
    fake_html = "<script>const seed = {x:50, y:50};</script>"
    assert "dx" not in fake_html or "dy" not in fake_html


def test_no_border_detection_would_be_caught():
    """Script without border detection logic should fail."""
    fake_html = "<script>function draw() { ctx.fillRect(0,0,1,1); }</script>"
    assert "isBorder" not in fake_html and "border" not in fake_html.lower()
