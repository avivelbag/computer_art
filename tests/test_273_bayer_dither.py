"""Tests for Piece 273 — The Grain of Light (Bayer ordered dithering)."""

import json
import math
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "273-bayer-dither"
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}

# Standard 8×8 Bayer matrix values 0–63 (mirrors the JS BAYER8 constant).
BAYER8 = [
     0, 32,  8, 40,  2, 34, 10, 42,
    48, 16, 56, 24, 50, 18, 58, 26,
    12, 44,  4, 36, 14, 46,  6, 38,
    60, 28, 52, 20, 62, 30, 54, 22,
     3, 35, 11, 43,  1, 33,  9, 41,
    51, 19, 59, 27, 49, 17, 57, 25,
    15, 47,  7, 39, 13, 45,  5, 37,
    63, 31, 55, 23, 61, 29, 53, 21,
]

P3 = math.pi * 3
P4 = math.pi * 4
P5 = math.pi * 5 / 800


def plasma(x, y, t, W=800, H=800):
    """Python mirror of the four-term plasma field in index.html's render().

    Returns a value in [0, 1].  Each of the four sine terms lies in [-1, 1];
    adding 4 to the sum (range [-4, 4]) then multiplying by 0.125 maps to [0, 1].
    """
    nx, ny = x / W, y / H
    dx, dy = nx - 0.5, ny - 0.5
    rd = math.sqrt(dx * dx + dy * dy) * 12 * math.pi
    return (
        math.sin(nx * P3 + t * 0.7)
        + math.sin(ny * P4 + t * 0.5)
        + math.sin((x + y) / W * math.pi * 5 + t * 0.3)
        + math.sin(rd + t * 0.9)
        + 4
    ) * 0.125


def bayer_threshold(x, y):
    """Return the Bayer threshold for pixel (x, y) in [0, 1)."""
    return BAYER8[(y & 7) * 8 + (x & 7)] / 64


# ---------------------------------------------------------------------------
# File-structure tests
# ---------------------------------------------------------------------------


class TestFileStructure:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_thumbnail_exists(self):
        assert (PIECE_DIR / "thumbnail.png").is_file() or (PIECE_DIR / "thumbnail.svg").is_file()

    def test_index_html_not_empty(self):
        html = (PIECE_DIR / "index.html").read_text()
        assert len(html) > 500

    def test_readme_not_empty(self):
        readme = (PIECE_DIR / "README.md").read_text()
        assert len(readme) > 100


# ---------------------------------------------------------------------------
# pieces.json registration tests
# ---------------------------------------------------------------------------


class TestPiecesJson:
    def _load(self):
        return json.loads(PIECES_JSON.read_text())

    def _find_entry(self):
        return next((e for e in self._load() if e["id"] == "273-bayer-dither"), None)

    def test_entry_exists(self):
        assert self._find_entry() is not None

    def test_entry_has_all_required_fields(self):
        entry = self._find_entry()
        assert entry is not None
        assert REQUIRED_FIELDS <= entry.keys(), f"Missing: {REQUIRED_FIELDS - entry.keys()}"

    def test_entry_id_matches_dir_name(self):
        entry = self._find_entry()
        assert entry is not None
        assert entry["id"] == pathlib.Path(entry["path"]).name

    def test_entry_path_points_to_directory(self):
        entry = self._find_entry()
        assert entry is not None
        assert (REPO / entry["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        entry = self._find_entry()
        assert entry is not None
        assert (REPO / entry["thumbnail"]).is_file()

    def test_entry_year_is_int(self):
        entry = self._find_entry()
        assert entry is not None
        assert isinstance(entry["year"], int)

    def test_entry_technique_mentions_bayer(self):
        entry = self._find_entry()
        assert entry is not None
        assert "bayer" in entry["technique"].lower() or "dither" in entry["technique"].lower()

    def test_existing_entry_count_not_reduced(self):
        data = self._load()
        assert len(data) >= 110, f"Expected ≥110 entries, got {len(data)}"


# ---------------------------------------------------------------------------
# Bayer matrix correctness
# ---------------------------------------------------------------------------


class TestBayerMatrix:
    def test_matrix_has_64_entries(self):
        assert len(BAYER8) == 64

    def test_matrix_values_all_unique(self):
        """All 64 entries must be distinct — the standard Bayer property."""
        assert len(set(BAYER8)) == 64

    def test_matrix_values_cover_zero_to_63(self):
        """Values must be exactly {0, 1, …, 63}."""
        assert set(BAYER8) == set(range(64))

    def test_thresholds_in_unit_interval(self):
        """All thresholds B/64 must lie in [0, 1)."""
        for v in BAYER8:
            t = v / 64
            assert 0.0 <= t < 1.0, f"Bayer threshold {t} out of [0, 1)"

    def test_top_left_corner_is_zero(self):
        """By convention the (0,0) Bayer entry is 0 — the minimum threshold."""
        assert BAYER8[0] == 0

    def test_bayer_threshold_wraps_with_modulo(self):
        """bayer_threshold(x, y) == bayer_threshold(x+8, y) and (x, y+8)."""
        for x in range(8):
            for y in range(8):
                assert bayer_threshold(x, y) == bayer_threshold(x + 8, y)
                assert bayer_threshold(x, y) == bayer_threshold(x, y + 8)


# ---------------------------------------------------------------------------
# Plasma function correctness
# ---------------------------------------------------------------------------


class TestPlasmaFunction:
    def test_output_in_unit_interval_at_t0(self):
        """Plasma must return values in [0, 1] at t=0 for all sampled pixels."""
        for x in range(0, 800, 40):
            for y in range(0, 800, 40):
                v = plasma(x, y, 0.0)
                assert 0.0 <= v <= 1.0, f"plasma({x},{y},0) = {v:.6f} out of [0, 1]"

    def test_output_in_unit_interval_at_t5(self):
        """Plasma must return values in [0, 1] at t=5 for all sampled pixels."""
        for x in range(0, 800, 40):
            for y in range(0, 800, 40):
                v = plasma(x, y, 5.0)
                assert 0.0 <= v <= 1.0, f"plasma({x},{y},5) = {v:.6f} out of [0, 1]"

    def test_output_is_finite_at_all_corners(self):
        for x, y in [(0, 0), (799, 0), (0, 799), (799, 799)]:
            assert math.isfinite(plasma(x, y, 0.0)), f"plasma({x},{y},0) not finite"

    def test_field_has_spatial_variation(self):
        """Values must vary across the image — a degenerate constant field would be a bug."""
        vals = {round(plasma(x, y, 0.0), 3) for x in range(0, 800, 80) for y in range(0, 800, 80)}
        assert len(vals) > 5, f"Only {len(vals)} distinct values — plasma field is degenerate"

    def test_field_varies_with_time(self):
        """The same pixel must differ between t=0 and t=10 (field must animate)."""
        v0 = plasma(400, 400, 0.0)
        v1 = plasma(400, 400, 10.0)
        assert abs(v0 - v1) > 0.01, "Centre pixel unchanged between t=0 and t=10 — field does not animate"


# ---------------------------------------------------------------------------
# Dithering logic
# ---------------------------------------------------------------------------


class TestDitheringLogic:
    def test_all_dark_when_v_is_zero(self):
        """When plasma = 0, all Bayer thresholds are > 0 so every pixel is off."""
        for x in range(8):
            for y in range(8):
                assert not (0.0 > bayer_threshold(x, y)), (
                    f"Pixel ({x},{y}) should be off when v=0 but threshold is {bayer_threshold(x,y)}"
                )

    def test_all_lit_when_v_exceeds_max_threshold(self):
        """When plasma = 1.0, it exceeds 63/64 ≈ 0.984, so every pixel is on."""
        max_threshold = max(BAYER8) / 64  # 63/64
        for x in range(8):
            for y in range(8):
                assert 1.0 > bayer_threshold(x, y), (
                    f"Bayer threshold {bayer_threshold(x,y):.4f} ≥ 1.0 — v=1 would not fully fill"
                )
        assert 1.0 > max_threshold

    def test_half_density_at_v_equals_half(self):
        """At v=0.5, Bayer dithering should turn on exactly 32 of the 64 cells."""
        v = 0.5
        on_count = sum(1 for x in range(8) for y in range(8) if v > bayer_threshold(x, y))
        assert on_count == 32, f"Expected 32 'on' cells at v=0.5, got {on_count}"

    def test_quarter_density_at_v_quarter(self):
        """At v≈0.25, approximately 25% (16 of 64) cells should be on."""
        v = 16 / 64  # exactly the 17th threshold value
        on_count = sum(1 for x in range(8) for y in range(8) if v > bayer_threshold(x, y))
        assert on_count == 16, f"Expected 16 'on' cells at v=16/64, got {on_count}"

    def test_three_quarter_density(self):
        """At v≈0.75, approximately 75% (48 of 64) cells should be on."""
        v = 48 / 64
        on_count = sum(1 for x in range(8) for y in range(8) if v > bayer_threshold(x, y))
        assert on_count == 48, f"Expected 48 'on' cells at v=48/64, got {on_count}"


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------


class TestHtmlContent:
    def html(self):
        return (PIECE_DIR / "index.html").read_text()

    def test_uses_canvas(self):
        assert "<canvas" in self.html()

    def test_uses_image_data(self):
        assert "createImageData" in self.html()

    def test_uses_put_image_data(self):
        assert "putImageData" in self.html()

    def test_animates_with_raf(self):
        assert "requestAnimationFrame" in self.html()

    def test_declares_bayer_matrix(self):
        html = self.html()
        assert "BAYER8" in html or "BAYER" in html or "bayer" in html.lower()

    def test_has_background_color(self):
        assert "0d0d0d" in self.html()

    def test_has_sand_gold_color(self):
        html = self.html()
        assert "e8c97a" in html or "e8c9" in html

    def test_no_external_dependencies(self):
        html = self.html()
        assert "https://" not in html
        assert "http://" not in html

    def test_has_canvas_800_by_800(self):
        html = self.html()
        assert 'width="800"' in html and 'height="800"' in html


# ---------------------------------------------------------------------------
# Thumbnail tests
# ---------------------------------------------------------------------------


class TestThumbnail:
    def thumb_path(self):
        entry = next(e for e in json.loads(PIECES_JSON.read_text()) if e["id"] == "273-bayer-dither")
        return REPO / entry["thumbnail"]

    def test_thumbnail_file_exists(self):
        assert self.thumb_path().is_file()

    def test_thumbnail_under_100kb(self):
        size = self.thumb_path().stat().st_size
        assert size < 100 * 1024, f"Thumbnail is {size // 1024} KB, must be < 100 KB"

    def test_thumbnail_not_empty(self):
        assert self.thumb_path().stat().st_size > 100

    def test_png_thumbnail_has_valid_header(self):
        """PNG files must begin with the 8-byte PNG signature."""
        data = self.thumb_path().read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n", "thumbnail.png does not start with the PNG signature"


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_plasma_at_extreme_coords_does_not_crash(self):
        """Calling plasma at boundary pixels must not raise."""
        for x, y, t in [(0, 0, 0), (799, 799, 0), (0, 799, 100), (799, 0, 999)]:
            v = plasma(x, y, t)
            assert math.isfinite(v)

    def test_bayer_lookup_does_not_overflow_for_large_coords(self):
        """bayer_threshold must be stable for coordinates far beyond the 8×8 tile."""
        for x in [0, 8, 64, 800, 10000]:
            for y in [0, 8, 64, 800, 10000]:
                t = bayer_threshold(x, y)
                assert 0.0 <= t < 1.0

    def test_missing_required_field_detected(self):
        """An entry without 'title' must fail the required-field check."""
        incomplete = {"id": "273-bayer-dither", "tagline": "test"}
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_id_mismatch_would_be_caught(self):
        """id must equal the last segment of the path."""
        entry = {"id": "wrong-id", "path": "pieces/273-bayer-dither"}
        assert entry["id"] != pathlib.Path(entry["path"]).name

    def test_plasma_with_very_large_t_stays_bounded(self):
        """Very large t values must not produce out-of-range plasma values."""
        for t in [1e4, 1e6]:
            v = plasma(400, 400, t)
            assert 0.0 <= v <= 1.0, f"plasma(400,400,{t}) = {v:.6f} out of [0,1]"

    def test_dithering_is_deterministic(self):
        """Same (x, y, t) inputs must always produce the same output."""
        v1 = plasma(123, 456, 7.89)
        v2 = plasma(123, 456, 7.89)
        assert v1 == v2
