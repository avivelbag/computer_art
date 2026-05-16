"""Tests for piece 191-quasicrystal: math correctness, file presence, and JSON registration."""
import json
import math
import pathlib

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "191-quasicrystal"
JSON_PATH = REPO / "pieces.json"

N = 5
K = 2 * math.pi / 120  # must match index.html


def field(px: float, py: float, t: float = 0.0, rot: float = 0.0) -> float:
    """Quasicrystal field value at canvas pixel (px, py); canvas is 600×600.

    Mirrors the JavaScript implementation in index.html so the Python
    tests exercise the same mathematical contract.
    """
    x = px - 300.0
    y = py - 300.0
    total = 0.0
    for i in range(N):
        theta = (i * 2 * math.pi / N) + rot
        total += math.cos(K * (x * math.cos(theta) + y * math.sin(theta)))
    return total / N


def value_to_rgb(v: float) -> tuple[int, int, int]:
    """Python mirror of the JS valueToRGB function."""
    t = (v + 1) * 0.5
    if t < 0.5:
        s = t * 2
        r = int(6  + s * 54)
        g = int(4  + s * 16)
        b = int(15 + s * 85)
    else:
        s = (t - 0.5) * 2
        r = int(60  + s * 195)
        g = int(20  + s * 220)
        b = int(100 - s * 20)
    return r, g, b


# ---------------------------------------------------------------------------
# File-presence tests
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/191-quasicrystal/ must exist"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_thumbnail_exists():
    thumb = PIECE_DIR / "thumbnail.svg"
    assert thumb.is_file(), "thumbnail.svg must exist"
    assert thumb.stat().st_size > 1000, "thumbnail.svg appears empty"


# ---------------------------------------------------------------------------
# pieces.json registration tests
# ---------------------------------------------------------------------------

def test_registered_in_pieces_json():
    data = json.loads(JSON_PATH.read_text())
    ids  = [e["id"] for e in data]
    assert "191-quasicrystal" in ids


def test_pieces_json_entry_complete():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    data  = json.loads(JSON_PATH.read_text())
    entry = next(e for e in data if e["id"] == "191-quasicrystal")
    assert required <= entry.keys()
    assert entry["path"] == "pieces/191-quasicrystal"
    assert entry["thumbnail"] == "pieces/191-quasicrystal/thumbnail.svg"


# ---------------------------------------------------------------------------
# Mathematical correctness — happy path
# ---------------------------------------------------------------------------

def test_field_at_center_is_one():
    """At the canvas centre (300,300) with rot=0, all waves have arg=0 → field=1."""
    v = field(300, 300, rot=0.0)
    assert abs(v - 1.0) < 1e-9


def test_field_range_sample_grid():
    """Field values must lie in [-1, 1] for a coarse sample grid."""
    for py in range(0, 600, 30):
        for px in range(0, 600, 30):
            v = field(px, py)
            assert -1.0 <= v <= 1.0, f"Out-of-range value {v} at ({px},{py})"


def test_field_five_fold_symmetry_at_origin():
    """Rotating coords by 72° about centre must give the same field value (at rot=0)."""
    angle = 2 * math.pi / 5   # 72 degrees
    px, py = 450.0, 300.0     # arbitrary off-centre point
    x0, y0 = px - 300, py - 300
    x1 = x0 * math.cos(angle) - y0 * math.sin(angle)
    y1 = x0 * math.sin(angle) + y0 * math.cos(angle)
    v0 = field(px, py, rot=0.0)
    v1 = field(300 + x1, 300 + y1, rot=0.0)
    assert abs(v0 - v1) < 1e-9, f"5-fold symmetry broken: {v0} vs {v1}"


def test_field_varies_across_canvas():
    """The field must not be constant — interference must create variation."""
    values = {field(px, py) for py in range(0, 600, 60) for px in range(0, 600, 60)}
    assert max(values) - min(values) > 0.5, "Field is nearly constant — something is wrong"


# ---------------------------------------------------------------------------
# Mathematical correctness — colour mapping
# ---------------------------------------------------------------------------

def test_value_to_rgb_at_minus_one_is_dark():
    r, g, b = value_to_rgb(-1.0)
    assert r < 20 and g < 20 and b < 30, f"Expected dark colour, got ({r},{g},{b})"


def test_value_to_rgb_at_plus_one_is_bright():
    r, g, b = value_to_rgb(1.0)
    assert r > 200 and g > 200, f"Expected bright warm colour, got ({r},{g},{b})"


def test_value_to_rgb_stays_in_byte_range():
    for v100 in range(-100, 101):
        v = v100 / 100.0
        r, g, b = value_to_rgb(v)
        assert 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255, (
            f"RGB out of [0,255] for v={v}: ({r},{g},{b})"
        )


# ---------------------------------------------------------------------------
# Edge / failure cases
# ---------------------------------------------------------------------------

def test_field_with_large_rotation_still_in_range():
    """Pattern must remain bounded even after many full rotations."""
    for rot in [0, math.pi, 10 * math.pi, 1000.0]:
        v = field(300, 300, rot=rot)
        assert -1.0 - 1e-9 <= v <= 1.0 + 1e-9, f"Out-of-range at rot={rot}: {v}"


def test_field_at_corners():
    """Corner pixels must be reachable and in range."""
    for px, py in [(0, 0), (599, 0), (0, 599), (599, 599)]:
        v = field(px, py)
        assert -1.0 <= v <= 1.0


def test_pieces_json_no_duplicate_id():
    data = json.loads(JSON_PATH.read_text())
    ids  = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"
