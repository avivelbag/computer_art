"""Tests for piece 244-spirolaterals."""

import json
import math
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "244-spirolaterals"
PIECES_JSON = REPO / "pieces.json"


# ---------------------------------------------------------------------------
# File-presence acceptance criteria
# ---------------------------------------------------------------------------

def test_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/244-spirolaterals/ must exist"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_thumbnail_svg_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

def _entry():
    data = json.loads(PIECES_JSON.read_text())
    for e in data:
        if e.get("id") == "244-spirolaterals":
            return e
    return None


def test_pieces_json_has_entry():
    assert _entry() is not None, "244-spirolaterals not found in pieces.json"


def test_entry_id_matches_dir():
    e = _entry()
    assert e["id"] == PIECE_DIR.name


def test_entry_technique():
    e = _entry()
    tech = e.get("technique", "")
    assert "spirolateral" in tech
    assert "requestAnimationFrame" in tech


def test_entry_thumbnail_path_resolves():
    e = _entry()
    thumb = REPO / e["thumbnail"]
    assert thumb.is_file(), f"Thumbnail missing: {e['thumbnail']}"


def test_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    e = _entry()
    assert required <= e.keys()


def test_entry_year():
    assert _entry()["year"] == 2026


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def _html():
    return (PIECE_DIR / "index.html").read_text()


def test_html_uses_canvas():
    assert "<canvas" in _html()


def test_html_uses_raf():
    assert "requestAnimationFrame" in _html()


def test_html_references_panel_css():
    assert "panel.css" in _html()


def test_html_references_panel_js():
    assert "panel.js" in _html()


def test_html_has_gallery_panel_init():
    assert "GalleryPanel.init" in _html()


def test_html_palette_colors():
    html = _html()
    for color in ("#7fffd4", "#ffb3c1", "#ffd700", "#c9a7ff"):
        assert color in html, f"Palette color {color} missing from index.html"


def test_html_background_color():
    assert "#0d1117" in _html()


def test_html_has_controls():
    html = _html()
    assert "btnSlow" in html or "Slow" in html
    assert "btnFast" in html or "Fast" in html
    assert "btnSkip" in html or "Skip" in html


def test_html_has_crossfade_logic():
    html = _html()
    assert "fadein" in html or "fadeAlpha" in html


def test_html_mentions_two_sets():
    html = _html()
    assert "SETS" in html


def test_html_4x4_grid():
    html = _html()
    assert "COLS = 4" in html or "COLS=4" in html


# ---------------------------------------------------------------------------
# Spirolateral algorithm correctness (Python port)
# ---------------------------------------------------------------------------

def gcd(a, b):
    a, b = abs(int(round(a))), abs(int(round(b)))
    while b:
        a, b = b, a % b
    return a or 1


def closure_repeats(n, angle):
    mod = (n * angle) % 360
    if mod == 0:
        return 4
    return min(360 // gcd(mod, 360), 12)


def compute_points(seq, angle_deg, repeats):
    pts = [(0.0, 0.0)]
    x, y, direction = 0.0, 0.0, 0.0
    rad = math.pi / 180
    for _ in range(repeats):
        for length in seq:
            x += length * math.cos(direction * rad)
            y += length * math.sin(direction * rad)
            pts.append((x, y))
            direction = (direction + angle_deg) % 360
    return pts


class TestClosureRepeats:
    def test_123_at_90(self):
        # [1,2,3] @ 90°: n=3, 3×90=270, mod=270, gcd(270,360)=90 → R=4
        assert closure_repeats(3, 90) == 4

    def test_12_at_144(self):
        # [1,2] @ 144°: n=2, 2×144=288, mod=288, gcd(288,360)=72 → R=5
        assert closure_repeats(2, 144) == 5

    def test_1234_at_120(self):
        # [1,2,3,4] @ 120°: n=4, 4×120=480, mod=120, gcd(120,360)=120 → R=3
        assert closure_repeats(4, 120) == 3

    def test_123456_at_60(self):
        # 6×60=360, mod=0 → default 4
        assert closure_repeats(6, 60) == 4

    def test_12345_at_72(self):
        # 5×72=360, mod=0 → default 4
        assert closure_repeats(5, 72) == 4

    def test_returns_positive(self):
        for n in range(1, 8):
            for angle in (60, 72, 90, 120, 144):
                assert closure_repeats(n, angle) >= 1


class TestComputePoints:
    def test_single_step_walks_right(self):
        pts = compute_points([1], 90, 1)
        assert len(pts) == 2
        assert abs(pts[1][0] - 1.0) < 1e-9
        assert abs(pts[1][1] - 0.0) < 1e-9

    def test_two_steps_90_turn(self):
        # Walk 1 right then 2 down
        pts = compute_points([1, 2], 90, 1)
        assert len(pts) == 3
        assert abs(pts[1][0] - 1.0) < 1e-9
        assert abs(pts[1][1] - 0.0) < 1e-9
        # After 90° turn, walk 2 in the +y direction (screen: down)
        assert abs(pts[2][0] - 1.0) < 1e-9
        assert abs(pts[2][1] - 2.0) < 1e-9

    def test_point_count_is_repeats_times_seq_len_plus_one(self):
        seq = [1, 2, 3]
        repeats = 4
        pts = compute_points(seq, 90, repeats)
        assert len(pts) == repeats * len(seq) + 1

    def test_123_at_90_returns_to_origin_after_4_passes(self):
        # [1,2,3] @ 90° is a classic closed spirolateral — closes after 4 passes.
        pts = compute_points([1, 2, 3], 90, 4)
        start, end = pts[0], pts[-1]
        assert abs(end[0] - start[0]) < 1e-6
        assert abs(end[1] - start[1]) < 1e-6

    def test_empty_seq_returns_only_origin(self):
        pts = compute_points([], 90, 3)
        assert pts == [(0.0, 0.0)]

    def test_large_seq_does_not_crash(self):
        seq = list(range(1, 20))
        pts = compute_points(seq, 90, 4)
        assert len(pts) == 4 * len(seq) + 1

    def test_zero_repeats_returns_only_origin(self):
        pts = compute_points([1, 2, 3], 90, 0)
        assert pts == [(0.0, 0.0)]


# ---------------------------------------------------------------------------
# thumbnail.svg sanity
# ---------------------------------------------------------------------------

def test_thumbnail_svg_is_valid_xml():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert content.strip().startswith("<svg")
    assert "</svg>" in content


def test_thumbnail_svg_has_paths():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<path" in content


def test_thumbnail_svg_has_background():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#0d1117" in content
