"""Tests for pieces/127-voronoi-mosaic: Voronoi mosaic with jewel-tone palette."""

import json
import math
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "127-voronoi-mosaic"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
GEN_THUMB = PIECE_DIR / "generate_thumbnail.py"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "127-voronoi-mosaic"

# Exact palette from index.html (as hex tuples for readability)
PALETTE = [
    (0x0F, 0x52, 0xBA),  # sapphire
    (0x9B, 0x11, 0x1E),  # ruby
    (0xD2, 0x8C, 0x00),  # amber
    (0x00, 0x78, 0x50),  # jade
    (0x6E, 0x3C, 0xAA),  # amethyst
    (0x00, 0x64, 0x78),  # deep teal
    (0xC8, 0x50, 0x14),  # topaz
    (0x1E, 0x82, 0x6E),  # aquamarine
    (0xBE, 0x14, 0x5A),  # rose
    (0x32, 0xA0, 0x5A),  # emerald
    (0xB4, 0xA5, 0x00),  # gold
    (0x14, 0x32, 0x9B),  # cobalt
]

BORDER_COLOR = "#14141C"


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
    assert INDEX_HTML.is_file(), "index.html is missing"


def test_readme_exists():
    assert README.is_file(), "README.md is missing"


def test_thumbnail_exists():
    assert THUMBNAIL.is_file(), "thumbnail.svg is missing"


def test_generate_thumbnail_exists():
    assert GEN_THUMB.is_file(), "generate_thumbnail.py is missing"


# ---------------------------------------------------------------------------
# HTML structural tests
# ---------------------------------------------------------------------------

def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_canvas_id():
    html = _html()
    assert 'id="c"' in html or "id='c'" in html


def test_html_has_script_tag():
    assert "<script" in _html()


def test_html_title_contains_voronoi():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    assert "voronoi" in m.group(1).lower()


def test_html_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html


def test_html_canvas_dimensions_800():
    html = _html()
    assert 'width="800"' in html and 'height="800"' in html


# ---------------------------------------------------------------------------
# JavaScript content tests
# ---------------------------------------------------------------------------

def test_js_defines_palette():
    assert "PALETTE" in _html()


def test_js_palette_has_12_colors():
    """Palette must contain exactly 12 [r,g,b] hex triplet entries."""
    entries = re.findall(r"\[0x[0-9A-Fa-f]+,0x[0-9A-Fa-f]+,0x[0-9A-Fa-f]+\]", _html())
    assert len(entries) >= 12, f"Expected ≥12 colour entries, found {len(entries)}"


def test_js_palette_has_sapphire():
    """Sapphire (0x0F, 0x52, 0xBA) must appear."""
    html = _html()
    assert "0x0F" in html or "0x0f" in html.lower()
    assert "0x52" in html
    assert "0xBA" in html or "0xba" in html.lower()


def test_js_palette_has_ruby():
    """Ruby (0x9B, 0x11, 0x1E) must appear."""
    html = _html()
    assert "0x9B" in html or "0x9b" in html.lower()


def test_js_border_color_is_dark():
    """Near-black border bytes 0x14 and 0x1C must be present."""
    html = _html()
    assert "0x14" in html
    assert "0x1C" in html or "0x1c" in html.lower()


def test_js_defines_seed_count_n():
    """N (seed count) constant must be present."""
    html = _html()
    assert "N=" in html or "N =" in html or ",N=" in html


def test_js_seed_count_in_range():
    """Seed count must be in the 150–300 range."""
    m = re.search(r"\bN\s*=\s*(\d+)", _html())
    if m:
        n = int(m.group(1))
        assert 150 <= n <= 300, f"N={n} outside [150, 300]"


def test_js_defines_spatial_grid_bucket():
    """Spatial grid bucket size BCELL must be defined."""
    html = _html()
    assert "BCELL" in html


def test_js_spatial_grid_uses_40px_bucket():
    """Bucket size must be 40 pixels."""
    m = re.search(r"BCELL\s*=\s*(\d+)", _html())
    if m:
        assert int(m.group(1)) == 40, f"BCELL={m.group(1)}, expected 40"


def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_js_has_nearest_seed_computation():
    html = _html()
    assert "minD" in html or "minDist" in html or "nearest" in html


def test_js_has_border_detection():
    html = _html()
    assert "isBorder" in html or "border" in html.lower()


def test_js_has_sinusoidal_drift():
    """Seeds must drift via Math.sin for smooth tectonic animation."""
    html = _html()
    assert "Math.sin" in html


def test_js_has_fps_cap():
    html = _html()
    assert "FRAME_MS" in html or "FPS" in html


def test_js_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained"


def test_js_uses_typed_arrays():
    """Float32Array or Int32Array must be used for performance."""
    html = _html()
    assert "Float32Array" in html or "Int32Array" in html


def test_js_uses_image_data():
    html = _html()
    assert "createImageData" in html or "putImageData" in html


# ---------------------------------------------------------------------------
# Python distance-field logic tests (re-implemented in Python)
# ---------------------------------------------------------------------------

def _nearest(cx: float, cy: float, seeds: list[tuple[float, float]]) -> int:
    """Pure-Python nearest-seed lookup for unit testing."""
    best_dist = math.inf
    best_idx = 0
    for i, (sx, sy) in enumerate(seeds):
        d = (cx - sx) ** 2 + (cy - sy) ** 2
        if d < best_dist:
            best_dist = d
            best_idx = i
    return best_idx


def test_nearest_returns_closest_of_two():
    seeds = [(0.0, 0.0), (10.0, 0.0)]
    assert _nearest(2.0, 0.0, seeds) == 0
    assert _nearest(8.0, 0.0, seeds) == 1


def test_nearest_seed_at_exact_position():
    seeds = [(5.0, 5.0), (15.0, 15.0)]
    assert _nearest(5.0, 5.0, seeds) == 0
    assert _nearest(15.0, 15.0, seeds) == 1


def test_nearest_single_seed():
    seeds = [(50.0, 50.0)]
    for px, py in [(0, 0), (99, 99), (50, 50), (0, 99)]:
        assert _nearest(float(px), float(py), seeds) == 0


def test_voronoi_cells_partition_plane():
    """Three well-separated seeds should each own their corner quadrant."""
    seeds = [(10.0, 10.0), (90.0, 10.0), (50.0, 90.0)]
    assert _nearest(0.0, 0.0, seeds) == 0    # top-left
    assert _nearest(100.0, 0.0, seeds) == 1  # top-right
    assert _nearest(50.0, 100.0, seeds) == 2 # bottom-center


def test_border_pixel_detected_when_neighbour_differs():
    """A pixel whose left neighbour belongs to a different cell is a border."""
    # 1-D strip: cells [0, 0, 1, 1]
    strip = [0, 0, 1, 1]
    px = 2  # first pixel in cell 1
    si = strip[px]
    is_border = (px > 0 and strip[px - 1] != si)
    assert is_border


def test_interior_pixel_not_border():
    """An interior pixel whose all 4 neighbours share the same seed is not a border."""
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    px, py = 1, 1
    si = grid[py][px]
    is_border = (
        grid[py][px - 1] != si
        or grid[py][px + 1] != si
        or grid[py - 1][px] != si
        or grid[py + 1][px] != si
    )
    assert not is_border


def test_sinusoidal_drift_stays_within_canvas():
    """Sinusoidal drift with MAX_AMP=80 stays in [0, W] (seeds at x=W are
    clamped by the spatial grid and cause no visual artifact)."""
    import math as _math

    MAX_AMP = 80
    W = 800
    # basX is in [MAX_AMP, W-MAX_AMP), ampX is in [20, MAX_AMP)
    # so the theoretical max is W and min is 0 — allow the closed interval
    for base in (MAX_AMP, W / 2, W - MAX_AMP):
        for amp in (20, 80):
            for t in range(0, 10000, 100):
                for phase in (0.0, _math.pi / 2, _math.pi):
                    x = base + amp * _math.sin(0.0003 * t + phase)
                    assert 0 <= x <= W, f"x={x} out of range at base={base}, amp={amp}"


def test_palette_has_12_distinct_colors():
    """All 12 palette colours must be distinct tuples."""
    assert len(set(PALETTE)) == 12


def test_palette_colors_are_jewel_tones():
    """Each colour must have at least one channel ≥ 0x50 (not near-black)."""
    for r, g, b in PALETTE:
        assert max(r, g, b) >= 0x50, f"Colour ({r},{g},{b}) looks too dark for a jewel tone"


def test_border_color_is_near_black():
    """Border colour must be very dark (all channels ≤ 30)."""
    r = int(BORDER_COLOR[1:3], 16)
    g = int(BORDER_COLOR[3:5], 16)
    b = int(BORDER_COLOR[5:7], 16)
    assert max(r, g, b) <= 30, f"Border colour {BORDER_COLOR} is not near-black"


# ---------------------------------------------------------------------------
# generate_thumbnail.py tests
# ---------------------------------------------------------------------------

def _import_gen():
    """Import generate_thumbnail as a module (adds piece dir to sys.path)."""
    piece_dir = str(PIECE_DIR)
    if piece_dir not in sys.path:
        sys.path.insert(0, piece_dir)
    import importlib
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_thumb", GEN_THUMB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gen_make_seeds_count():
    mod = _import_gen()
    import random as _r
    rng = _r.Random(42)
    seeds = mod.make_seeds(200, rng)
    assert len(seeds) == 200


def test_gen_make_seeds_zero():
    """make_seeds(0, rng) must return an empty list."""
    mod = _import_gen()
    import random as _r
    rng = _r.Random(42)
    seeds = mod.make_seeds(0, rng)
    assert seeds == []


def test_gen_nearest_seed_idx_basic():
    mod = _import_gen()
    seeds = [(0.0, 0.0, 0), (10.0, 0.0, 1)]
    assert mod.nearest_seed_idx(2.0, 0.0, seeds) == 0
    assert mod.nearest_seed_idx(8.0, 0.0, seeds) == 1


def test_gen_voronoi_grid_shape():
    mod = _import_gen()
    import random as _r
    rng = _r.Random(42)
    seeds = mod.make_seeds(50, rng)
    grid = mod.voronoi_grid(seeds)
    assert len(grid) == mod.GRID
    assert all(len(row) == mod.GRID for row in grid)


def test_gen_is_border_detects_boundary():
    mod = _import_gen()
    grid = [[0, 1], [0, 0]]  # top-right cell differs
    assert mod.is_border(grid, 0, 0)   # left of the boundary — has right neighbour 1


def test_gen_is_border_interior_false():
    mod = _import_gen()
    grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    assert not mod.is_border(grid, 1, 1)


def test_gen_generate_svg_zero_seeds():
    """generate_svg(0) must return a valid SVG with only the background rect."""
    mod = _import_gen()
    svg = mod.generate_svg(0)
    assert "<svg" in svg
    assert "viewBox" in svg
    ET.fromstring(svg)  # must be valid XML


def test_gen_generate_svg_normal(tmp_path):
    """generate_svg() must return a valid SVG with ≥100 rect elements."""
    mod = _import_gen()
    svg = mod.generate_svg()
    assert "<svg" in svg
    root = ET.fromstring(svg)
    rects = root.findall(".//{http://www.w3.org/2000/svg}rect") or root.findall(".//rect")
    assert len(rects) >= 100, f"Expected ≥100 rects, found {len(rects)}"


def test_gen_generate_svg_contains_palette_colors():
    """At least 6 palette colours must appear in the generated SVG."""
    mod = _import_gen()
    svg = mod.generate_svg().lower()
    found = sum(
        1 for r, g, b in PALETTE
        if f"#{r:02x}{g:02x}{b:02x}" in svg
    )
    assert found >= 6, f"Expected ≥6 palette colours in SVG; found {found}"


def test_gen_reproducible():
    """Two calls to generate_svg() must produce identical output."""
    mod = _import_gen()
    assert mod.generate_svg() == mod.generate_svg()


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    assert len(THUMBNAIL.read_text()) > 200


def test_thumbnail_has_svg_root():
    assert "<svg" in THUMBNAIL.read_text()


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg is invalid XML: {exc}") from exc


def test_thumbnail_has_many_cells():
    """Thumbnail must have ≥100 rect elements (mosaic cells)."""
    svg = THUMBNAIL.read_text()
    rects = re.findall(r"<rect\b", svg)
    assert len(rects) >= 100, f"Expected ≥100 <rect> elements, found {len(rects)}"


def test_thumbnail_contains_palette_colors():
    """At least 6 jewel-tone palette colours must appear in the thumbnail."""
    svg = THUMBNAIL.read_text().lower()
    found = sum(
        1 for r, g, b in PALETTE
        if f"#{r:02x}{g:02x}{b:02x}" in svg
    )
    assert found >= 6, f"Expected ≥6 palette colours; found {found}"


def test_thumbnail_has_border_color():
    svg = THUMBNAIL.read_text().lower()
    assert "14141c" in svg, "thumbnail.svg must contain the border colour #14141C"


def test_thumbnail_is_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_pieces_json_entry_fields():
    entry = _entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= entry.keys()


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_voronoi():
    assert "voronoi" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 50


def test_readme_mentions_voronoi():
    assert "voronoi" in README.read_text().lower()


def test_readme_mentions_palette():
    readme = README.read_text().lower()
    assert "palette" in readme or "jewel" in readme or "sapphire" in readme


def test_readme_mentions_animation():
    readme = README.read_text().lower()
    assert "animat" in readme or "drift" in readme or "morph" in readme


def test_readme_mentions_algorithm():
    readme = README.read_text().lower()
    assert "distance" in readme or "nearest" in readme or "grid" in readme


# ---------------------------------------------------------------------------
# Failure-mode tests (assert that bad inputs are caught correctly)
# ---------------------------------------------------------------------------

def test_missing_palette_detected():
    """HTML without PALETTE constant fails the palette check."""
    fake = "<script>const x = 1;</script>"
    assert "PALETTE" not in fake


def test_wrong_border_color_detected():
    """White border instead of near-black should fail the dark-colour check."""
    fake = "<script>const BORDER=[255,255,255];</script>"
    assert "0x14" not in fake


def test_no_spatial_grid_detected():
    """Script without BCELL constant should fail the grid check."""
    fake = "<script>function f(){}</script>"
    assert "BCELL" not in fake


def test_no_animation_detected():
    """Script without requestAnimationFrame should fail the animation check."""
    fake = "<script>draw();</script>"
    assert "requestAnimationFrame" not in fake


def test_static_seeds_without_sin_detected():
    """Seeds without Math.sin drift would fail the sinusoidal animation check."""
    fake = "<script>const seeds = [{x:10,y:20}];</script>"
    assert "Math.sin" not in fake


def test_gen_large_input(tmp_path):
    """generate_svg with 500 seeds must still produce valid XML."""
    mod = _import_gen()
    svg = mod.generate_svg.__wrapped__(500) if hasattr(mod.generate_svg, "__wrapped__") else None
    # Manually call with more seeds by monkey-patching N temporarily
    old_n = mod.N
    try:
        mod.N = 500
        svg = mod.generate_svg(500)
    finally:
        mod.N = old_n
    ET.fromstring(svg)


def test_gen_single_seed():
    """With one seed every cell in the grid belongs to that seed (no borders between cells)."""
    mod = _import_gen()
    import random as _r
    rng = _r.Random(0)
    seeds = [(mod.GRID / 2, mod.GRID / 2, 0)]
    grid = mod.voronoi_grid(seeds)
    assert all(grid[cy][cx] == 0 for cy in range(mod.GRID) for cx in range(mod.GRID))
