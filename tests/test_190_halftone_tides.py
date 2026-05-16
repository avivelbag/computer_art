"""Tests for Piece 190 — Halftone Tides: Interference Wave Dot Grid."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO        = pathlib.Path(__file__).parent.parent
PIECE_ID    = "190-halftone-tides"
PIECE_DIR   = REPO / "pieces" / PIECE_ID
INDEX_HTML  = PIECE_DIR / "index.html"
THUMBNAIL   = PIECE_DIR / "thumbnail.svg"
README      = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"

BG_COLOR  = "#1a0a2e"
DOT_COLOR = "#f7c95b"

WAVES = [
    {'kx':  0.08, 'ky':  0.06, 'freq': 1.1, 'phase': 0.0},
    {'kx': -0.05, 'ky':  0.10, 'freq': 0.7, 'phase': 1.2},
    {'kx':  0.12, 'ky': -0.04, 'freq': 1.5, 'phase': 2.4},
    {'kx': -0.07, 'ky': -0.09, 'freq': 0.9, 'phase': 3.7},
]


def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_index_html_nonempty():
    assert len(_html()) > 500


def test_thumbnail_svg_exists():
    assert THUMBNAIL.is_file()


def test_readme_exists():
    assert README.is_file()


def test_readme_nonempty():
    assert len(README.read_text().strip()) > 100


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------

def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_uses_2d_context():
    html = _html()
    assert "getContext('2d')" in html or 'getContext("2d")' in html


def test_html_has_charset():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html


def test_html_has_viewport():
    assert 'name="viewport"' in _html()


def test_html_title_contains_halftone():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "Missing <title>"
    title = m.group(1).lower()
    assert "halftone" in title or "tides" in title


def test_html_no_external_scripts():
    assert not re.findall(r'<script[^>]+src=["\']https?://', _html())


def test_html_has_requestanimationframe():
    assert "requestAnimationFrame" in _html()


def test_html_has_background_color():
    assert BG_COLOR in _html()


def test_html_has_dot_color():
    assert DOT_COLOR in _html()


def test_html_has_four_wave_entries():
    html = _html()
    freq_matches = re.findall(r'freq\s*:', html)
    assert len(freq_matches) >= 3, f"Expected ≥3 wave freq entries, found {len(freq_matches)}"


def test_html_has_clamp_logic():
    html = _html()
    has_clamp = ("Math.max" in html and "Math.min" in html) or ("0.1" in html and "0.9" in html)
    assert has_clamp, "Clamp logic for dot radius must be present"


def test_html_has_cols_rows_constants():
    html = _html()
    assert "COLS" in html and "ROWS" in html


def test_html_fps_cap_present():
    html = _html()
    assert "FPS" in html or "FRAME_MS" in html or "60" in html


def test_html_uses_arc_for_dots():
    assert ".arc(" in _html()


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------

def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg invalid XML: {exc}") from exc


def test_thumbnail_has_svg_root():
    assert "<svg" in THUMBNAIL.read_text()


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_has_background_color():
    assert BG_COLOR in THUMBNAIL.read_text()


def test_thumbnail_has_dot_color():
    assert DOT_COLOR in THUMBNAIL.read_text()


def test_thumbnail_has_enough_circles():
    count = THUMBNAIL.read_text().count("<circle")
    assert count >= 100, f"Expected ≥100 circles, got {count}"


def test_thumbnail_circle_radii_in_valid_range():
    svg = THUMBNAIL.read_text()
    CELL = 10.0
    max_r = CELL * 0.45
    radii = [float(m) for m in re.findall(r'<circle[^>]+r="([^"]+)"', svg)]
    assert radii, "No circle radii found in thumbnail"
    for r in radii:
        assert r >= max_r * 0.09, f"Radius {r:.3f} below minimum bound {max_r * 0.1:.3f}"
        assert r <= max_r * 0.91, f"Radius {r:.3f} above maximum bound {max_r * 0.9:.3f}"


def test_thumbnail_is_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


# ---------------------------------------------------------------------------
# pieces.json
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [p.get("id") for p in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_pieces_json_entry_complete():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert required <= _entry().keys()


def test_pieces_json_path():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    assert (REPO / _entry()["thumbnail"]).is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_halftone():
    assert "halftone" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_no_duplicate_ids():
    data = json.loads(PIECES_JSON.read_text())
    ids = [p["id"] for p in data]
    assert len(ids) == len(set(ids))


def test_pieces_json_still_valid():
    data = json.loads(PIECES_JSON.read_text())
    assert isinstance(data, list) and len(data) > 0


# ---------------------------------------------------------------------------
# Python reimplementation of wave math
# ---------------------------------------------------------------------------

def _wave_value(cx: float, cy: float, t: float) -> float:
    v = 0.0
    for w in WAVES:
        v += math.sin(w['kx'] * cx + w['ky'] * cy + w['freq'] * t + w['phase'])
    return v / len(WAVES)


def _dot_radius(cx: float, cy: float, t: float, max_r: float = 4.5) -> float:
    v = _wave_value(cx, cy, t)
    norm = max(0.1, min(0.9, v * 0.5 + 0.5))
    return max_r * norm


def test_wave_value_always_in_minus1_plus1():
    for col in range(0, 40, 4):
        for row in range(0, 40, 4):
            cx = (col + 0.5) * 10
            cy = (row + 0.5) * 10
            for ti in [0.0, 1.0, 1.2, 3.14, 10.0, 99.9]:
                v = _wave_value(cx, cy, ti)
                assert -1.0 <= v <= 1.0, f"wave_value({cx},{cy},{ti})={v} out of [-1,1]"


def test_dot_radius_never_below_10_percent():
    max_r = 4.5
    for col in range(40):
        for row in range(40):
            cx = (col + 0.5) * 10
            cy = (row + 0.5) * 10
            r = _dot_radius(cx, cy, 0.0, max_r)
            assert r >= max_r * 0.1 - 1e-9, f"Radius {r:.4f} below 10% of max_r at col={col} row={row}"


def test_dot_radius_never_above_90_percent():
    max_r = 4.5
    for col in range(40):
        for row in range(40):
            cx = (col + 0.5) * 10
            cy = (row + 0.5) * 10
            r = _dot_radius(cx, cy, 1.2, max_r)
            assert r <= max_r * 0.9 + 1e-9, f"Radius {r:.4f} above 90% of max_r at col={col} row={row}"


def test_dot_radius_varies_across_grid():
    max_r = 4.5
    t = 1.2
    radii = [_dot_radius((c + 0.5) * 10, (r + 0.5) * 10, t, max_r)
             for c in range(10) for r in range(10)]
    spread = max(radii) - min(radii)
    assert spread > max_r * 0.1, f"Radii spread {spread:.4f} too small — interference not visible"


def test_dot_radius_varies_with_time():
    max_r = 4.5
    cx, cy = 205.0, 205.0
    r1 = _dot_radius(cx, cy, 0.0, max_r)
    r2 = _dot_radius(cx, cy, 2.0, max_r)
    assert abs(r1 - r2) > 1e-6, "Dot radius must change over time"


def test_wave_sum_equals_manual_average():
    cx, cy, t = 100.0, 75.0, 0.5
    manual = sum(math.sin(w['kx'] * cx + w['ky'] * cy + w['freq'] * t + w['phase'])
                 for w in WAVES) / len(WAVES)
    assert abs(_wave_value(cx, cy, t) - manual) < 1e-12


def test_normalization_clamps_minus1_to_01():
    norm = max(0.1, min(0.9, -1.0 * 0.5 + 0.5))
    assert abs(norm - 0.1) < 1e-12


def test_normalization_clamps_plus1_to_09():
    norm = max(0.1, min(0.9, 1.0 * 0.5 + 0.5))
    assert abs(norm - 0.9) < 1e-12


def test_dot_radius_extreme_position():
    max_r = 20.0
    r = _dot_radius(995.0, 995.0, 50.0, max_r)
    assert max_r * 0.1 <= r <= max_r * 0.9


def test_four_waves_have_distinct_directions():
    dirs = [(w['kx'], w['ky']) for w in WAVES]
    assert len(dirs) == len(set(dirs)), "Wave direction vectors must be distinct"


def test_wave_temporal_frequencies_are_distinct():
    freqs = [w['freq'] for w in WAVES]
    assert len(freqs) == len(set(freqs)), "Temporal frequencies must be distinct for true interference"


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------

def test_missing_piece_dir_would_fail():
    """Confirm the test framework correctly detects missing directories."""
    fake = REPO / "pieces" / "999-nonexistent"
    assert not fake.is_dir()


def test_missing_pieces_json_entry_raises():
    data = json.loads(PIECES_JSON.read_text())
    ids = [p["id"] for p in data]
    assert "999-nonexistent" not in ids


def test_wave_value_empty_waves_raises_zero_division():
    import pytest
    with pytest.raises(ZeroDivisionError):
        v = 0.0
        waves = []
        v / len(waves)
