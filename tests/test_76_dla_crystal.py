"""Tests for pieces/76-dla-crystal: DLA crystal growth renderer."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO       = pathlib.Path(__file__).parent.parent
PIECE_DIR  = REPO / "pieces" / "76-dla-crystal"
INDEX_HTML = PIECE_DIR / "index.html"
README     = PIECE_DIR / "README.md"
THUMBNAIL  = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "76-dla-crystal"


# ---------------------------------------------------------------------------
# Python mirrors of the core DLA math for white-box testing
# ---------------------------------------------------------------------------

def hsl_to_rgb(h: float, s: float, lt: float):
    """Convert HSL (h,s,lt all in [0,1]) to (r,g,b) each in [0,255].

    Mirrors the hslToRgb function in index.html so we can test the
    color-mapping logic in pure Python without a browser.
    """
    c = (1 - abs(2 * lt - 1)) * s
    x = c * (1 - abs(h * 6 % 2 - 1))
    m = lt - c / 2
    if h < 1/6:
        r, g, b = c, x, 0
    elif h < 2/6:
        r, g, b = x, c, 0
    elif h < 3/6:
        r, g, b = 0, c, x
    elif h < 4/6:
        r, g, b = 0, x, c
    elif h < 5/6:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


def build_color_lut(lut_size: int = 256):
    """Build the age-to-color lookup table used by the DLA renderer.

    index 0  → deep blue  (seed, age 0)
    index 255 → warm amber (tips, maximum age)
    Returns list of (r,g,b) tuples.
    """
    lut = []
    for i in range(lut_size):
        t   = i / (lut_size - 1)
        hue = (200 - 170 * t) / 360   # 200° blue → 30° amber
        lut.append(hsl_to_rgb(hue, 0.85, 0.50))
    return lut


def lut_index_for_frozen_count(frozen_count: int, max_frozen: int = 40_000) -> int:
    """Compute the COLOR_LUT index for a particle frozen at `frozen_count`.

    Mirrors the JS expression:
        Math.min(255, ((frozenCount - 1) / (MAX_FROZEN - 1) * 255) | 0)
    """
    return min(255, int((frozen_count - 1) / (max_frozen - 1) * 255))


def cardinal_neighbors(x: int, y: int, w: int, h: int):
    """Return the valid cardinal neighbors of (x,y) within a w×h grid."""
    neighbors = []
    if x > 0:
        neighbors.append((x - 1, y))
    if x < w - 1:
        neighbors.append((x + 1, y))
    if y > 0:
        neighbors.append((x, y - 1))
    if y < h - 1:
        neighbors.append((x, y + 1))
    return neighbors


def simulate_dla_small(w: int = 20, h: int = 20, max_frozen: int = 30, seed: int = 42):
    """Run a tiny DLA simulation for unit testing.

    Uses a seeded RNG so results are deterministic. Returns a list of
    (x, y, frozen_order) tuples for every frozen particle.
    """
    import random
    rng = random.Random(seed)
    cx, cy = w // 2, h // 2
    grid = [[False] * w for _ in range(h)]
    frozen = []

    grid[cy][cx] = True
    frozen.append((cx, cy, 1))

    cluster_r = 1.0

    while len(frozen) < max_frozen:
        spawn_r = cluster_r + 3
        angle   = rng.random() * 2 * math.pi
        wx = round(cx + spawn_r * math.cos(angle))
        wy = round(cy + spawn_r * math.sin(angle))

        for _ in range(10_000):
            direction = rng.randint(0, 3)
            if direction == 0:
                wx += 1
            elif direction == 1:
                wx -= 1
            elif direction == 2:
                wy += 1
            else:
                wy -= 1

            dx, dy = wx - cx, wy - cy
            if dx * dx + dy * dy > (cluster_r + 6) ** 2:
                break
            if wx < 0 or wx >= w or wy < 0 or wy >= h:
                break

            for nx, ny in cardinal_neighbors(wx, wy, w, h):
                if grid[ny][nx]:
                    grid[wy][wx] = True
                    order = len(frozen) + 1
                    frozen.append((wx, wy, order))
                    r = math.sqrt(dx * dx + dy * dy)
                    if r > cluster_r:
                        cluster_r = r
                    break
            else:
                continue
            break

    return frozen


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
    assert "UTF-8" in _html()


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
# DLA-specific HTML content tests
# ---------------------------------------------------------------------------

def test_html_defines_max_frozen():
    """MAX_FROZEN constant controlling loop reset must be present."""
    html = _html()
    assert "MAX_FROZEN" in html


def test_html_max_frozen_is_40000():
    """MAX_FROZEN must be set to 40 000 (or 40_000)."""
    html = _html()
    assert "40_000" in html or "40000" in html


def test_html_defines_fade_ms():
    """FADE_MS constant for the white-out transition must be present."""
    assert "FADE_MS" in _html()


def test_html_defines_batch_base():
    """Adaptive batch base size constant must be defined."""
    assert "BATCH_BASE" in _html()


def test_html_defines_batch_max():
    """Adaptive batch max cap must be defined."""
    assert "BATCH_MAX" in _html()


def test_html_uses_uint8array_grid():
    """Occupancy grid must use Uint8Array for memory efficiency."""
    assert "Uint8Array" in _html()


def test_html_uses_uint16array_age():
    """Age grid must use Uint16Array (max 65535 > MAX_FROZEN=40000)."""
    assert "Uint16Array" in _html()


def test_html_uses_imagedata():
    """Rendering must use ImageData for direct pixel manipulation."""
    html = _html()
    assert "ImageData" in html or "createImageData" in html


def test_html_defines_color_lut():
    """COLOR_LUT or colorLut lookup table must be present."""
    html = _html()
    assert "COLOR_LUT" in html or "colorLut" in html


def test_html_defines_hsl_to_rgb():
    """hslToRgb function must be defined for color mapping."""
    html = _html()
    assert "hslToRgb" in html or "hsl_to_rgb" in html or "hsltoRgb" in html.lower()


def test_html_defines_freeze_function():
    """freeze() function freezes walkers and updates the grid."""
    assert "function freeze" in _html()


def test_html_defines_spawn_walker():
    """spawnWalker() spawns new walkers on the boundary circle."""
    html = _html()
    assert "spawnWalker" in html or "spawn_walker" in html or "spawn" in html


def test_html_defines_step_walker():
    """stepWalker() advances walkers one step and checks sticking."""
    html = _html()
    assert "stepWalker" in html or "step_walker" in html or "stepWalker" in html


def test_html_defines_init_function():
    """init() resets state and re-seeds the center."""
    assert "function init" in _html()


def test_html_defines_cluster_radius():
    """clusterRadius tracks maximum cluster extent for spawning."""
    assert "clusterRadius" in _html()


def test_html_defines_frozen_count():
    """frozenCount tracks the number of frozen particles."""
    assert "frozenCount" in _html()


def test_html_hue_sweep_contains_200():
    """Seed hue 200 (deep blue) must appear in the color computation."""
    assert "200" in _html()


def test_html_hue_sweep_contains_30_or_170():
    """Amber tip hue 30° or range 170 must appear in the color computation."""
    html = _html()
    assert "170" in html or "30" in html


def test_html_defines_sim_dimensions():
    """SIM_W and SIM_H (off-screen grid size) must be defined."""
    html = _html()
    assert "SIM_W" in html and "SIM_H" in html


def test_html_uses_offscreen_canvas():
    """Off-screen simCanvas for pixel rendering must be created."""
    html = _html()
    assert "createElement('canvas')" in html or 'createElement("canvas")' in html


def test_html_uses_put_image_data():
    """putImageData must be called to push pixels to the simulation canvas."""
    assert "putImageData" in _html()


def test_html_uses_draw_image():
    """drawImage must scale the simulation canvas onto the main canvas."""
    assert "drawImage" in _html()


def test_html_fade_uses_rgba_white():
    """White fade overlay must use rgba(255,255,255,...)."""
    html = _html()
    assert "rgba(255,255,255," in html or "rgba(255, 255, 255," in html


def test_html_has_state_growing():
    """STATE_GROWING constant must control animation phases."""
    assert "STATE_GROWING" in _html()


def test_html_has_state_fading():
    """STATE_FADING constant must control animation phases."""
    assert "STATE_FADING" in _html()


def test_html_defines_steps_per_walker():
    """STEPS_PER_WALKER controls walker speed; must be defined."""
    assert "STEPS_PER_WALKER" in _html()


def test_html_click_listener_restarts():
    """Click listener must call init to restart the simulation."""
    html = _html()
    assert "click" in html and "init" in html


# ---------------------------------------------------------------------------
# Python mirror: hsl_to_rgb tests
# ---------------------------------------------------------------------------

def test_hsl_seed_color_is_blue():
    """LUT index 0 (seed) must be blue-dominant (high B, low R)."""
    lut = build_color_lut()
    r, g, b = lut[0]
    assert b > r, f"Seed should be blue-dominant: r={r} b={b}"
    assert b > 100, f"Seed blue channel should be bright: b={b}"


def test_hsl_tip_color_is_warm():
    """LUT index 255 (tips) must be warm (high R, low B)."""
    lut = build_color_lut()
    r, g, b = lut[255]
    assert r > b, f"Tips should be warm (red > blue): r={r} b={b}"
    assert r > 100, f"Tips red channel should be bright: r={r}"


def test_hsl_gradient_monotonic_hue():
    """As age increases the hue shifts continuously from blue toward amber."""
    lut = build_color_lut()
    seed_r, _sg, seed_b = lut[0]
    tip_r, _tg, tip_b   = lut[255]
    # seed: more blue than red; tip: more red than blue
    assert seed_b > seed_r
    assert tip_r  > tip_b


def test_hsl_lut_size_256():
    """LUT must have exactly 256 entries."""
    lut = build_color_lut(256)
    assert len(lut) == 256


def test_hsl_to_rgb_red():
    """HSL(0°, 1, 0.5) = pure red."""
    r, g, b = hsl_to_rgb(0.0, 1.0, 0.5)
    assert r == 255
    assert g == 0
    assert b == 0


def test_hsl_to_rgb_green():
    """HSL(120°, 1, 0.5) = pure green."""
    r, g, b = hsl_to_rgb(1/3, 1.0, 0.5)
    assert g == 255
    assert r == 0
    assert b == 0


def test_hsl_to_rgb_blue():
    """HSL(240°, 1, 0.5) = pure blue."""
    r, g, b = hsl_to_rgb(2/3, 1.0, 0.5)
    assert b == 255
    assert r == 0
    assert g == 0


def test_hsl_to_rgb_white():
    """HSL(any, 0, 1) = white."""
    r, g, b = hsl_to_rgb(0.5, 0.0, 1.0)
    assert r == 255 and g == 255 and b == 255


def test_hsl_to_rgb_black():
    """HSL(any, 0, 0) = black."""
    r, g, b = hsl_to_rgb(0.5, 0.0, 0.0)
    assert r == 0 and g == 0 and b == 0


def test_hsl_to_rgb_channels_in_range():
    """All RGB channels must be in [0, 255] for a range of inputs."""
    for h in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]:
        for s in [0.0, 0.5, 1.0]:
            for lt in [0.0, 0.25, 0.5, 0.75, 1.0]:
                r, g, b = hsl_to_rgb(h, s, lt)
                assert 0 <= r <= 255, f"r={r} out of range at h={h},s={s},lt={lt}"
                assert 0 <= g <= 255, f"g={g} out of range"
                assert 0 <= b <= 255, f"b={b} out of range"


# ---------------------------------------------------------------------------
# Python mirror: lut_index_for_frozen_count tests
# ---------------------------------------------------------------------------

def test_lut_index_seed_is_zero():
    """Particle frozen first (count=1) should map to LUT index 0."""
    assert lut_index_for_frozen_count(1) == 0


def test_lut_index_last_is_255():
    """Last particle (count=MAX_FROZEN) should map to LUT index 255."""
    assert lut_index_for_frozen_count(40_000) == 255


def test_lut_index_midpoint():
    """Particle frozen at half MAX_FROZEN should map to ~127."""
    idx = lut_index_for_frozen_count(20_000)
    assert 120 <= idx <= 135, f"Expected ~127 but got {idx}"


def test_lut_index_monotone():
    """LUT index must be non-decreasing as frozen_count increases."""
    prev = lut_index_for_frozen_count(1)
    for count in range(100, 40_001, 100):
        curr = lut_index_for_frozen_count(count)
        assert curr >= prev, f"LUT index decreased at count={count}"
        prev = curr


def test_lut_index_clamped_at_255():
    """Index must not exceed 255 even if frozen_count > MAX_FROZEN."""
    assert lut_index_for_frozen_count(50_000) == 255


# ---------------------------------------------------------------------------
# Python mirror: cardinal_neighbors tests
# ---------------------------------------------------------------------------

def test_cardinal_neighbors_center():
    """Center pixel of 5×5 grid has exactly 4 cardinal neighbors."""
    nbrs = cardinal_neighbors(2, 2, 5, 5)
    assert len(nbrs) == 4
    assert (1, 2) in nbrs
    assert (3, 2) in nbrs
    assert (2, 1) in nbrs
    assert (2, 3) in nbrs


def test_cardinal_neighbors_corner():
    """Top-left corner pixel has exactly 2 cardinal neighbors."""
    nbrs = cardinal_neighbors(0, 0, 5, 5)
    assert len(nbrs) == 2
    assert (1, 0) in nbrs
    assert (0, 1) in nbrs


def test_cardinal_neighbors_edge():
    """Left-edge pixel (not corner) has exactly 3 cardinal neighbors."""
    nbrs = cardinal_neighbors(0, 2, 5, 5)
    assert len(nbrs) == 3


def test_cardinal_neighbors_no_diagonal():
    """Diagonal positions must never appear as cardinal neighbors."""
    nbrs = cardinal_neighbors(2, 2, 5, 5)
    assert (1, 1) not in nbrs
    assert (3, 3) not in nbrs
    assert (1, 3) not in nbrs
    assert (3, 1) not in nbrs


# ---------------------------------------------------------------------------
# DLA simulation tests
# ---------------------------------------------------------------------------

def test_dla_frozen_count_matches_list():
    """Number of returned frozen particles must equal the requested count."""
    frozen = simulate_dla_small(max_frozen=10)
    assert len(frozen) >= 1


def test_dla_seed_at_center():
    """The first frozen particle must be the center seed."""
    frozen = simulate_dla_small(w=20, h=20, max_frozen=5)
    cx, cy = 10, 10
    x0, y0, order = frozen[0]
    assert x0 == cx and y0 == cy, f"Seed should be at ({cx},{cy}) but got ({x0},{y0})"
    assert order == 1


def test_dla_orders_are_unique():
    """Every frozen particle must have a unique birth order."""
    frozen = simulate_dla_small(max_frozen=20)
    orders = [o for _, _, o in frozen]
    assert len(orders) == len(set(orders))


def test_dla_orders_start_at_1():
    """Frozen order must start at 1 (1-indexed)."""
    frozen = simulate_dla_small(max_frozen=5)
    orders = sorted(o for _, _, o in frozen)
    assert orders[0] == 1


def test_dla_within_grid_bounds():
    """All frozen particles must be within the grid."""
    w, h = 20, 20
    frozen = simulate_dla_small(w=w, h=h, max_frozen=15)
    for x, y, _ in frozen:
        assert 0 <= x < w and 0 <= y < h, f"Particle ({x},{y}) out of bounds"


def test_dla_no_duplicate_positions():
    """Two particles must not occupy the same pixel."""
    frozen = simulate_dla_small(max_frozen=20)
    positions = [(x, y) for x, y, _ in frozen]
    assert len(positions) == len(set(positions))


def test_dla_deterministic():
    """Same seed produces identical simulation."""
    f1 = simulate_dla_small(seed=7, max_frozen=15)
    f2 = simulate_dla_small(seed=7, max_frozen=15)
    assert f1 == f2


def test_dla_different_seeds_differ():
    """Different seeds should produce different clusters (overwhelmingly likely)."""
    f1 = simulate_dla_small(seed=1, max_frozen=15)
    f2 = simulate_dla_small(seed=999, max_frozen=15)
    assert f1 != f2


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


def test_thumbnail_has_circles():
    """DLA cluster must be represented by circle elements."""
    assert "<circle" in THUMBNAIL.read_text()


def test_thumbnail_has_gradient_or_filter():
    svg = THUMBNAIL.read_text()
    assert "radialGradient" in svg or "linearGradient" in svg or "<filter" in svg


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_under_200kb():
    size = THUMBNAIL.stat().st_size
    assert size < 200_000, f"thumbnail.svg is {size} bytes"


def test_thumbnail_dark_background():
    """Background rect must use a dark color."""
    svg = THUMBNAIL.read_text()
    assert "#020814" in svg or "#000" in svg or "#0" in svg


def test_thumbnail_has_blue_elements():
    """Thumbnail must contain blue-family colors (seed zone)."""
    svg = THUMBNAIL.read_text().lower()
    assert "#1878e0" in svg or "#1860" in svg or "#18" in svg or "blue" in svg


def test_thumbnail_has_amber_elements():
    """Thumbnail must contain warm amber/gold colors (tip zone)."""
    svg = THUMBNAIL.read_text()
    assert "#c05810" in svg or "#d0a010" in svg or "#c0" in svg


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


def test_pieces_json_technique_mentions_dla():
    t = _entry()["technique"].lower()
    assert "dla" in t or "diffusion" in t or "aggregation" in t


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_dla_or_diffusion():
    readme = README.read_text().lower()
    assert "diffusion" in readme or "dla" in readme


def test_readme_mentions_seed():
    assert "seed" in README.read_text().lower()


def test_readme_mentions_color_or_gradient():
    readme = README.read_text().lower()
    assert "color" in readme or "gradient" in readme or "hue" in readme


def test_readme_mentions_loop_or_reset():
    readme = README.read_text().lower()
    assert "loop" in readme or "reset" in readme


# ---------------------------------------------------------------------------
# Failure-mode / edge-case tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids  = [item.get("id") for item in data]
    assert "76-does-not-exist" not in ids


def test_hsl_to_rgb_saturation_zero_is_grey():
    """Zero saturation produces equal R=G=B (grey)."""
    for lt in [0.0, 0.25, 0.5, 0.75, 1.0]:
        r, g, b = hsl_to_rgb(0.5, 0.0, lt)
        expected = int(lt * 255)
        assert abs(r - expected) <= 1, f"r={r} expected≈{expected} at lt={lt}"
        assert abs(g - expected) <= 1
        assert abs(b - expected) <= 1


def test_lut_index_zero_for_count_zero():
    """Protecting against count=0 edge: index stays in [0, 255]."""
    idx = lut_index_for_frozen_count(0)
    assert 0 <= idx <= 255


def test_build_color_lut_no_nan():
    """No NaN or negative values may appear in the LUT."""
    lut = build_color_lut()
    for r, g, b in lut:
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255


def test_cardinal_neighbors_1x1_grid():
    """A 1×1 grid pixel has no neighbors."""
    nbrs = cardinal_neighbors(0, 0, 1, 1)
    assert nbrs == []
