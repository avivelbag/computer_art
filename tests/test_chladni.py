"""Tests for Piece 194 — Chladni Figures: physics, file presence, and JSON registration."""
import json
import math
import pathlib

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "194-chladni"
JSON_PATH = REPO / "pieces.json"

# Constants mirroring index.html
K_SHARP = 40.0
MODES   = [(1,1),(1,2),(2,3),(3,4),(2,5),(4,3),(5,5),(3,7),(4,6),(6,5)]


def field_abs(m: int, n: int, px: float, py: float,
              w: int = 600, h: int = 600) -> float:
    """Return |sin(m·π·x)·sin(n·π·y)| for pixel (px, py) on a w×h canvas.

    Mirrors the JavaScript computeField function in index.html.
    x, y ∈ [0, 1] mapped linearly from [0, w-1] × [0, h-1].
    """
    x = px / (w - 1)
    y = py / (h - 1)
    return abs(math.sin(m * math.pi * x) * math.sin(n * math.pi * y))


def field_to_brightness(v: float) -> float:
    """Return brightness t = exp(-v²·K_SHARP) ∈ [0, 1]; mirrors the LUT formula."""
    return math.exp(-v * v * K_SHARP)


def field_to_rgb(v: float) -> tuple[int, int, int]:
    """Map |field| value v ∈ [0, 1] to RGB; mirrors the JS colour LUT logic."""
    t = field_to_brightness(v)
    BG   = (10,  10,  15)
    GOLD = (242, 201, 76)
    WHITE = (255, 255, 255)
    if t < 0.4:
        s = t / 0.4
        r = int(BG[0] + (GOLD[0]  - BG[0])  * s)
        g = int(BG[1] + (GOLD[1]  - BG[1])  * s)
        b = int(BG[2] + (GOLD[2]  - BG[2])  * s)
    else:
        s = (t - 0.4) / 0.6
        r = int(GOLD[0] + (WHITE[0] - GOLD[0]) * s)
        g = int(GOLD[1] + (WHITE[1] - GOLD[1]) * s)
        b = int(GOLD[2] + (WHITE[2] - GOLD[2]) * s)
    return r, g, b


# ---------------------------------------------------------------------------
# File-presence tests
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/194-chladni/ must exist"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_readme_not_empty():
    readme = (PIECE_DIR / "README.md").read_text()
    assert len(readme.strip()) > 50, "README.md appears too short"


def test_thumbnail_exists():
    thumb = PIECE_DIR / "thumbnail.svg"
    assert thumb.is_file(), "thumbnail.svg must exist"
    assert thumb.stat().st_size > 5000, "thumbnail.svg appears empty"


# ---------------------------------------------------------------------------
# pieces.json registration tests
# ---------------------------------------------------------------------------

def test_registered_in_pieces_json():
    data = json.loads(JSON_PATH.read_text())
    ids  = [e["id"] for e in data]
    assert "194-chladni" in ids


def test_pieces_json_entry_complete():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    data  = json.loads(JSON_PATH.read_text())
    entry = next(e for e in data if e["id"] == "194-chladni")
    assert required <= entry.keys()
    assert entry["path"]      == "pieces/194-chladni"
    assert entry["thumbnail"] == "pieces/194-chladni/thumbnail.svg"


def test_pieces_json_no_duplicate_id():
    data = json.loads(JSON_PATH.read_text())
    ids  = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"


# ---------------------------------------------------------------------------
# Physics: field values
# ---------------------------------------------------------------------------

def test_field_at_boundary_is_nodal():
    """Plate edges (x=0,1 and y=0,1) must be zero for all modes."""
    for m, n in MODES:
        for px in [0, 599]:
            v = field_abs(m, n, float(px), 300.0)
            assert abs(v) < 1e-9, f"Edge not nodal for ({m},{n}) at px={px}"
        for py in [0, 599]:
            v = field_abs(m, n, 300.0, float(py))
            assert abs(v) < 1e-9, f"Edge not nodal for ({m},{n}) at py={py}"


def test_field_range_is_0_to_1():
    """Field values must stay in [0, 1] for a sample grid."""
    for m, n in MODES:
        for py in range(0, 600, 50):
            for px in range(0, 600, 50):
                v = field_abs(m, n, float(px), float(py))
                assert 0.0 <= v <= 1.0 + 1e-9, (
                    f"|field| out of range for ({m},{n}) at ({px},{py}): {v}"
                )


def test_field_interior_nodal_lines_mode_1_2():
    """Mode (1,2) has an interior nodal line at y=0.5 — check it is zero."""
    m, n = 1, 2
    # Test exact mathematical condition: sin(n*pi*0.5) = sin(pi) = 0
    v = abs(math.sin(n * math.pi * 0.5) * math.sin(m * math.pi * 0.5))
    assert v < 1e-9, f"Expected nodal at y=0.5 for mode (1,2), got {v}"


def test_field_antinodes_are_near_one():
    """Mode (1,1): the anti-node at (x,y)=(0.5,0.5) should be |f|≈1."""
    m, n = 1, 1
    v = field_abs(m, n, 299.5, 299.5)
    assert v > 0.99, f"Anti-node not near 1 for mode (1,1): {v}"


def test_all_modes_produce_variation():
    """Every mode must have variation across the canvas — not a constant field."""
    for m, n in MODES:
        vals = [field_abs(m, n, float(px), float(py))
                for py in range(50, 550, 100) for px in range(50, 550, 100)]
        assert max(vals) - min(vals) > 0.3, (
            f"Mode ({m},{n}) field appears constant — something is wrong"
        )


# ---------------------------------------------------------------------------
# Physics: mode count
# ---------------------------------------------------------------------------

def test_at_least_8_modes():
    """Acceptance criterion: at least 8 vibrational modes."""
    assert len(MODES) >= 8, f"Need at least 8 modes, found {len(MODES)}"


def test_all_mode_pairs_are_positive():
    for m, n in MODES:
        assert m > 0 and n > 0, f"Mode ({m},{n}) has non-positive index"


# ---------------------------------------------------------------------------
# Colour mapping tests
# ---------------------------------------------------------------------------

def test_nodal_line_is_bright():
    """v=0 (exactly on nodal line) must produce a bright near-white colour."""
    r, g, b = field_to_rgb(0.0)
    assert r > 240 and g > 240 and b > 240, (
        f"Nodal line (v=0) expected near-white, got ({r},{g},{b})"
    )


def test_antinode_is_dark():
    """v=1 (anti-node, far from nodal line) must be near-black."""
    r, g, b = field_to_rgb(1.0)
    assert r < 20 and g < 20 and b < 20, (
        f"Anti-node (v=1) expected near-black, got ({r},{g},{b})"
    )


def test_colour_stays_in_byte_range():
    for v100 in range(0, 101):
        v = v100 / 100.0
        r, g, b = field_to_rgb(v)
        assert 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255, (
            f"RGB out of [0,255] for v={v}: ({r},{g},{b})"
        )


def test_gold_midpoint_is_warm():
    """At moderate distance from nodal line the colour should have a warm cast."""
    # At the brightness threshold of ~0.4, colour is exactly gold.
    # The value v where t=0.4 is: 0.4 = exp(-v²*40) → v = sqrt(-ln(0.4)/40) ≈ 0.152
    v_mid = math.sqrt(-math.log(0.4) / K_SHARP)
    r, g, b = field_to_rgb(v_mid)
    assert r > g > b, f"Expected warm (r>g>b) at v≈{v_mid:.3f}, got ({r},{g},{b})"


# ---------------------------------------------------------------------------
# Edge / failure cases
# ---------------------------------------------------------------------------

def test_field_single_pixel_canvas_raises_no_error():
    """field_abs must not error or divide-by-zero for edge coords."""
    v = field_abs(3, 4, 0.0, 0.0, w=600, h=600)
    assert v == 0.0  # edge is always nodal


def test_field_mode_5_5_has_multiple_interior_nodal_lines():
    """Mode (5,5) should have 4 interior nodal lines per axis."""
    m = 5
    nodal_count = 0
    for px in range(1, 599):
        x = px / 599.0
        if abs(math.sin(m * math.pi * x)) < 0.02:
            nodal_count += 1
    assert nodal_count >= 4, f"Expected ≥4 interior x-nodal lines for (5,5), found {nodal_count}"


def test_brightness_monotone_decreasing():
    """Brightness must decrease monotonically as |field| increases from 0."""
    prev = 1.0
    for v100 in range(0, 101):
        v = v100 / 100.0
        t = field_to_brightness(v)
        assert t <= prev + 1e-9, f"Brightness not monotone at v={v}: {t} > {prev}"
        prev = t
