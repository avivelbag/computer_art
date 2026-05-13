"""Tests for pieces/78-wolfram-ca: Wolfram elementary CA — Rule 30 / 90 / 110."""

import json
import pathlib
import re
import xml.etree.ElementTree as ET

REPO       = pathlib.Path(__file__).parent.parent
PIECE_DIR  = REPO / "pieces" / "78-wolfram-ca"
INDEX_HTML = PIECE_DIR / "index.html"
README     = PIECE_DIR / "README.md"
THUMBNAIL  = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "78-wolfram-ca"


# ---------------------------------------------------------------------------
# Python mirror of the core CA algorithm for white-box testing
# ---------------------------------------------------------------------------

def apply_rule(row: list[int], rule: int) -> list[int]:
    """Apply a Wolfram elementary CA rule to produce the next generation.

    Uses periodic (wrap-around) boundary conditions: the leftmost cell's left
    neighbor is the rightmost cell, and vice versa.

    Args:
        row:  current generation as a list of 0s and 1s.
        rule: Wolfram rule number, 0–255.

    Returns:
        The next generation as a list of 0s and 1s of the same length.
    """
    n = len(row)
    result = []
    for i in range(n):
        pat = (row[(i - 1) % n] << 2) | (row[i] << 1) | row[(i + 1) % n]
        result.append((rule >> pat) & 1)
    return result


def evolve(width: int, rule: int, generations: int) -> list[list[int]]:
    """Evolve a single-center-cell seed for `generations` steps.

    Returns a list of rows (including the seed row at index 0).
    """
    row = [0] * width
    row[width // 2] = 1
    rows = [list(row)]
    for _ in range(generations):
        row = apply_rule(row, rule)
        rows.append(list(row))
    return rows


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
# CA-specific HTML content tests
# ---------------------------------------------------------------------------

def test_html_mentions_rule_30():
    """Rule 30 (chaotic) must be referenced in the script."""
    assert "30" in _html()


def test_html_mentions_rule_90():
    """Rule 90 (Sierpiński) must be referenced in the script."""
    assert "90" in _html()


def test_html_mentions_rule_110():
    """Rule 110 (Turing-complete) must be referenced in the script."""
    assert "110" in _html()


def test_html_uses_uint8array():
    """CA row state must use Uint8Array for memory efficiency."""
    assert "Uint8Array" in _html()


def test_html_uses_imagedata():
    """Rendering must use ImageData for direct pixel manipulation."""
    html = _html()
    assert "ImageData" in html or "createImageData" in html


def test_html_uses_put_image_data():
    """putImageData must push pixels to the off-screen canvas."""
    assert "putImageData" in _html()


def test_html_uses_draw_image():
    """drawImage must scale the sim canvas onto the main canvas."""
    assert "drawImage" in _html()


def test_html_uses_copy_within_for_scroll():
    """copyWithin must be used for the O(1) upward scroll of ImageData."""
    assert "copyWithin" in _html()


def test_html_has_seed_row_function():
    """A seedRow or equivalent must initialize the single-center-cell seed."""
    html = _html()
    assert "seedRow" in html or "SIM_W >> 1" in html or "SIM_W / 2" in html


def test_html_has_next_row_or_advance():
    """nextRow or advance must compute each new CA generation."""
    html = _html()
    assert "nextRow" in html or "advance" in html


def test_html_has_rule_duration_constant():
    """RULE_DURATION controls how long each rule is shown."""
    assert "RULE_DURATION" in _html()


def test_html_has_fade_duration_constant():
    """FADE_DURATION controls the cross-fade length."""
    assert "FADE_DURATION" in _html()


def test_html_defines_sim_dimensions():
    """SIM_W and SIM_H define the off-screen simulation grid."""
    html = _html()
    assert "SIM_W" in html and "SIM_H" in html


def test_html_uses_offscreen_canvas():
    """Off-screen canvas for pixel rendering must be created dynamically."""
    html = _html()
    assert "createElement('canvas')" in html or 'createElement("canvas")' in html


def test_html_has_init_function():
    """init() resets state and re-seeds the center cell."""
    assert "function init" in _html()


def test_html_palettes_contain_amber():
    """Amber color components for Rule 30 must appear in PALETTES."""
    html = _html()
    assert "255" in html and "176" in html


def test_html_palettes_contain_teal():
    """Teal color components for Rule 90 must appear in PALETTES."""
    html = _html()
    assert "200" in html and "170" in html


def test_html_palettes_contain_rose():
    """Rose color components for Rule 110 must appear in PALETTES."""
    html = _html()
    assert "220" in html and "70" in html


def test_html_has_global_alpha_crossfade():
    """globalAlpha must be used for the cross-fade between rules."""
    assert "globalAlpha" in _html()


def test_html_click_listener_restarts():
    """Click listener must call init to restart."""
    html = _html()
    assert "click" in html and "init" in html


# ---------------------------------------------------------------------------
# Python mirror: apply_rule algorithm tests
# ---------------------------------------------------------------------------

def test_rule30_first_row_from_seed():
    """Rule 30 from a single center cell: first generation matches known output."""
    rows = evolve(width=7, rule=30, generations=1)
    assert rows[0] == [0, 0, 0, 1, 0, 0, 0]
    assert rows[1] == [0, 0, 1, 1, 1, 0, 0]


def test_rule30_second_row_from_seed():
    """Rule 30, second generation from single center cell."""
    rows = evolve(width=7, rule=30, generations=2)
    # Row 2: [0,1,1,0,0,1,0] (verified by manual neighborhood computation)
    assert rows[2] == [0, 1, 1, 0, 0, 1, 0]


def test_rule90_first_row_from_seed():
    """Rule 90 (XOR neighbors) from single center: first generation."""
    rows = evolve(width=7, rule=90, generations=1)
    assert rows[0] == [0, 0, 0, 1, 0, 0, 0]
    assert rows[1] == [0, 0, 1, 0, 1, 0, 0]


def test_rule90_is_xor_of_neighbors():
    """Rule 90 output equals left XOR right for any input row."""
    import random
    rng = random.Random(42)
    for _ in range(20):
        row = [rng.randint(0, 1) for _ in range(13)]
        nxt = apply_rule(row, 90)
        n   = len(row)
        for i in range(n):
            expected = row[(i - 1) % n] ^ row[(i + 1) % n]
            assert nxt[i] == expected, f"Rule 90 XOR violated at i={i}"


def test_rule110_first_row_from_seed():
    """Rule 110 from single center cell: first generation."""
    rows = evolve(width=7, rule=110, generations=1)
    assert rows[0] == [0, 0, 0, 1, 0, 0, 0]
    assert rows[1] == [0, 0, 1, 1, 0, 0, 0]


def test_all_zeros_stays_zero_for_rule_30():
    """All-dead row maps to all-dead under Rule 30 (000→0 for rule 30)."""
    row = [0] * 10
    assert apply_rule(row, 30) == [0] * 10


def test_all_zeros_stays_zero_for_rule_90():
    """All-dead row maps to all-dead under Rule 90."""
    row = [0] * 10
    assert apply_rule(row, 90) == [0] * 10


def test_all_zeros_stays_zero_for_rule_110():
    """All-dead row maps to all-dead under Rule 110."""
    row = [0] * 10
    assert apply_rule(row, 110) == [0] * 10


def test_all_ones_maps_to_zero_for_all_three_rules():
    """111 → 0 for all three rules (bit 7 is 0 in 30, 90, and 110)."""
    row = [1] * 10
    for rule in (30, 90, 110):
        result = apply_rule(row, rule)
        assert result == [0] * 10, f"Rule {rule}: all-ones should map to all-zeros"


def test_apply_rule_preserves_length():
    """Output row has the same length as the input row."""
    for n in (1, 5, 13, 100):
        row = [0] * n
        assert len(apply_rule(row, 30)) == n


def test_apply_rule_output_is_binary():
    """All output cells must be 0 or 1."""
    import random
    rng = random.Random(7)
    for rule in (30, 90, 110):
        for _ in range(10):
            row = [rng.randint(0, 1) for _ in range(20)]
            nxt = apply_rule(row, rule)
            for cell in nxt:
                assert cell in (0, 1), f"Cell value {cell} is not 0 or 1"


def test_rule90_generates_sierpinski_pattern():
    """After 4 generations of Rule 90 with width=9, row 3 is alternating 1s."""
    rows = evolve(width=9, rule=90, generations=3)
    # Row 3 should be [0,1,0,1,0,1,0,1,0] — the classic Sierpiński row
    assert rows[3] == [0, 1, 0, 1, 0, 1, 0, 1, 0]


def test_apply_rule_empty_row():
    """An empty row should produce an empty row without error."""
    assert apply_rule([], 30) == []


def test_rule_zero_always_produces_zeros():
    """Rule 0 maps every pattern to 0, so any row becomes all-zeros."""
    import random
    rng = random.Random(99)
    row = [rng.randint(0, 1) for _ in range(15)]
    assert apply_rule(row, 0) == [0] * 15


def test_rule_255_always_produces_ones():
    """Rule 255 maps every pattern to 1, so any row becomes all-ones."""
    import random
    rng = random.Random(99)
    row = [rng.randint(0, 1) for _ in range(15)]
    assert apply_rule(row, 255) == [1] * 15


def test_evolve_returns_correct_number_of_rows():
    """evolve(width, rule, G) returns G+1 rows (seed + G generations)."""
    rows = evolve(width=20, rule=30, generations=10)
    assert len(rows) == 11


def test_seed_is_single_center_cell():
    """The seed row always has exactly one live cell at the center."""
    for width in (5, 10, 21, 100):
        rows = evolve(width=width, rule=30, generations=0)
        seed = rows[0]
        center = width // 2
        assert seed[center] == 1
        assert sum(seed) == 1, f"Seed for width={width} has more than one live cell"


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
        raise AssertionError(f"thumbnail.svg is invalid XML: {exc}") from exc


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_live_cells():
    """Live cells must be encoded in the thumbnail (path or rect elements)."""
    svg = THUMBNAIL.read_text()
    assert "<path" in svg or "<rect" in svg


def test_thumbnail_dark_background():
    """Background must use the near-black palette color."""
    svg = THUMBNAIL.read_text()
    assert "#0a080f" in svg or "#000" in svg


def test_thumbnail_has_amber_cells():
    """Rule 30 thumbnail must use the amber palette color."""
    svg = THUMBNAIL.read_text()
    assert "#ffb000" in svg.lower() or "ffb000" in svg.lower()


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_under_200kb():
    size = THUMBNAIL.stat().st_size
    assert size < 200_000, f"thumbnail.svg is {size} bytes (must be < 200 KB)"


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


def test_pieces_json_technique_mentions_cellular_automata():
    t = _entry()["technique"].lower()
    assert "cellular automata" in t or "ca" in t or "wolfram" in t


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_explains_rule_number():
    """README must explain what a Wolfram rule number is."""
    readme = README.read_text().lower()
    assert "rule" in readme and ("lookup" in readme or "table" in readme or "bit" in readme)


def test_readme_mentions_all_three_rules():
    readme = README.read_text()
    assert "30" in readme and "90" in readme and "110" in readme


def test_readme_mentions_single_cell_seed():
    readme = README.read_text().lower()
    assert "single" in readme and "cell" in readme


def test_readme_mentions_scroll_or_downward():
    readme = README.read_text().lower()
    assert "scroll" in readme or "downward" in readme or "bottom" in readme


def test_readme_mentions_color_or_palette():
    readme = README.read_text().lower()
    assert "color" in readme or "palette" in readme or "amber" in readme


# ---------------------------------------------------------------------------
# Failure-mode / edge-case tests
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_in_json():
    data = json.loads(PIECES_JSON.read_text())
    ids  = [item.get("id") for item in data]
    assert "78-does-not-exist" not in ids


def test_apply_rule_single_cell_width():
    """Width-1 row wraps onto itself: all three neighbors are the same cell."""
    # For a single cell [1]: left=row[0], center=row[0], right=row[0] → pattern 111 → rule bit 7
    # Rule 30: bit 7 = 0 → [0]
    assert apply_rule([1], 30) == [0]
    # Rule 255: bit 7 = 1 → [1]
    assert apply_rule([1], 255) == [1]


def test_evolve_large_width_does_not_raise():
    """evolve must complete without error for a wide grid."""
    rows = evolve(width=600, rule=30, generations=5)
    assert len(rows) == 6
    assert all(len(r) == 600 for r in rows)


def test_rule90_symmetric_seed_stays_symmetric():
    """Rule 90 from a symmetric seed produces symmetric rows."""
    rows = evolve(width=11, rule=90, generations=5)
    for i, row in enumerate(rows):
        rev = list(reversed(row))
        assert row == rev, f"Row {i} is not symmetric under Rule 90: {row}"


def test_apply_rule_does_not_mutate_input():
    """apply_rule must not modify the input row in place."""
    original = [0, 0, 1, 1, 1, 0, 0]
    original_copy = list(original)
    apply_rule(original, 30)
    assert original == original_copy, "apply_rule mutated its input"
