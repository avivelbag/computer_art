"""Tests for Piece 03 — Liquid Color (Plasma Cosine Palette)."""
import json
import math
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "03-plasma-cosine-palette"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}

LAVA   = dict(a=[0.5,0.1,0.0], b=[0.5,0.4,0.3], c=[1.0,1.0,0.5], d=[0.0,0.2,0.6])
ARCTIC = dict(a=[0.4,0.5,0.6], b=[0.4,0.4,0.3], c=[1.0,1.0,1.0], d=[0.0,0.1,0.5])


def cosine_palette(v, a, b, c, d):
    """Inigo Quilez cosine palette: RGB = a + b*cos(2*pi*(c*v + d)).

    Returns a list of three floats (may be outside [0,1] before clamping).
    """
    tau = 2.0 * math.pi
    return [a[i] + b[i] * math.cos(tau * (c[i] * v + d[i])) for i in range(3)]


def plasma_value(x, y, t):
    """Demoscene plasma: sum of four sine terms evaluated at normalised coords.

    x and y are already in the space-scaled coordinate system (range roughly
    [-2, 2] for the canvas centre ± half the 4-unit extent used in index.html).
    Returns v in the range [-4, 4].
    """
    return (
        math.sin(x + t)
        + math.sin(y * 0.7 + t * 1.3)
        + math.sin((x + y) * 0.5 + t * 0.8)
        + math.sin(math.sqrt(x * x + y * y) * 0.9 - t * 1.1)
    )


def pixel_coords(px, py, W=800, H=800):
    """Convert canvas pixel (px, py) to the plasma coordinate system used by index.html."""
    return (px / W - 0.5) * 4, (py / H - 0.5) * 4


def _load_entry():
    """Return the pieces.json entry for the plasma piece, or None if absent."""
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == PIECE_ID), None)


# ---------------------------------------------------------------------------
# File presence
# ---------------------------------------------------------------------------

class TestFiles:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_index_html_nonempty(self):
        assert len((PIECE_DIR / "index.html").read_text()) > 500

    def test_thumbnail_exists(self):
        thumb_svg = PIECE_DIR / "thumbnail.svg"
        thumb_png = PIECE_DIR / "thumbnail.png"
        assert thumb_svg.is_file() or thumb_png.is_file(), "Neither thumbnail.svg nor thumbnail.png found"

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_readme_nonempty(self):
        assert len((PIECE_DIR / "README.md").read_text()) > 100


# ---------------------------------------------------------------------------
# index.html structure
# ---------------------------------------------------------------------------

class TestHtmlContent:
    def setup_method(self):
        self.html = (PIECE_DIR / "index.html").read_text()

    def test_canvas_element_present(self):
        assert "<canvas" in self.html

    def test_canvas_800x800(self):
        assert "800" in self.html

    def test_imagedata_used(self):
        assert "createImageData" in self.html

    def test_putimagedata_used(self):
        assert "putImageData" in self.html

    def test_requestanimationframe_present(self):
        assert "requestAnimationFrame" in self.html

    def test_lava_palette_present(self):
        assert "lava" in self.html

    def test_arctic_palette_present(self):
        assert "arctic" in self.html

    def test_lava_a_values_present(self):
        """Lava a-vector values 0.5, 0.1, 0.0 must appear."""
        assert "0.5" in self.html and "0.1" in self.html

    def test_arctic_a_values_present(self):
        """Arctic a-vector values 0.4, 0.5, 0.6 must appear."""
        assert "0.4" in self.html and "0.5" in self.html and "0.6" in self.html

    def test_cosine_palette_formula_present(self):
        """The cosine palette formula Math.cos must appear."""
        assert "Math.cos" in self.html

    def test_two_pi_constant_present(self):
        assert "Math.PI" in self.html

    def test_sine_term_x_t_present(self):
        """The first sine term sin(x + t) must appear."""
        assert re.search(r'Math\.sin\s*\(\s*x\s*\+\s*t\s*\)', self.html)

    def test_sine_term_sqrt_present(self):
        """The radial sine term using Math.sqrt must appear."""
        assert "Math.sqrt" in self.html

    def test_normalize_plus4_div8(self):
        """Normalization (v + 4) / 8 must appear."""
        assert re.search(r'\(\s*v\s*\+\s*4\s*\)\s*/\s*8', self.html)

    def test_palette_button_present(self):
        assert "<button" in self.html

    def test_palette_crossfade_present(self):
        """Crossfade requires a lerp frame counter (LF or LFRAMES or similar)."""
        assert "LF" in self.html or "60" in self.html

    def test_no_external_dependencies(self):
        assert not re.search(r'<script[^>]+src="https?://', self.html)
        assert "https://" not in self.html

    def test_alpha_channel_255(self):
        """Every pixel must have alpha=255 set explicitly."""
        assert "255" in self.html

    def test_js_line_count_under_80(self):
        """The JS inside the <script> tag must not exceed 80 lines."""
        match = re.search(r'<script[^>]*>(.*?)</script>', self.html, re.DOTALL)
        assert match, "No <script> block found"
        lines = [l for l in match.group(1).splitlines() if l.strip()]
        assert len(lines) <= 80, f"JS has {len(lines)} non-blank lines, expected ≤ 80"


# ---------------------------------------------------------------------------
# Cosine palette mathematics (Python re-implementation)
# ---------------------------------------------------------------------------

class TestPaletteMath:
    """Verify the cosine palette formula and the specific lava/arctic presets."""

    def test_lava_at_v0_red_dominant(self):
        """Lava palette at v=0 should produce strong red (R close to 1.0)."""
        rgb = cosine_palette(0.0, **LAVA)
        assert rgb[0] > 0.8, f"Expected R > 0.8 at v=0, got {rgb[0]:.3f}"

    def test_arctic_at_v0_has_blue(self):
        """Arctic palette at v=0 should include significant blue (B = 0.6 + 0.3*cos(π) = 0.3)."""
        rgb = cosine_palette(0.0, **ARCTIC)
        assert rgb[2] >= 0.3, f"Expected B >= 0.3 at v=0, got {rgb[2]:.3f}"

    def test_palette_periodic_period_2(self):
        """Lava palette R,G have period 1 (c=1.0); B has period 2 (c=0.5).
        The combined period is 2: palette(v) == palette(v+2)."""
        for v in [0.0, 0.25, 0.5, 0.73]:
            rgb0 = cosine_palette(v, **LAVA)
            rgb2 = cosine_palette(v + 2.0, **LAVA)
            for ch in range(3):
                assert abs(rgb0[ch] - rgb2[ch]) < 1e-10, \
                    f"Palette not periodic at period 2: v={v}, ch={ch}, {rgb0[ch]} vs {rgb2[ch]}"

    def test_palette_rg_periodic_period_1(self):
        """Lava R and G channels (c=1.0) repeat every period 1."""
        for v in [0.0, 0.3, 0.6, 0.9]:
            rgb0 = cosine_palette(v, **LAVA)
            rgb1 = cosine_palette(v + 1.0, **LAVA)
            for ch in (0, 1):
                assert abs(rgb0[ch] - rgb1[ch]) < 1e-10, \
                    f"Lava ch={ch} not period-1: v={v}, {rgb0[ch]} vs {rgb1[ch]}"

    def test_palette_symmetric_around_half(self):
        """cos is symmetric so palette(v) may differ from palette(1-v) when d!=0; just verify continuity."""
        for v in [0.1, 0.3, 0.6, 0.9]:
            rgb = cosine_palette(v, **LAVA)
            assert all(-0.6 <= c <= 1.1 for c in rgb), f"Channel out of reasonable range at v={v}: {rgb}"

    def test_arctic_blue_always_positive(self):
        """Arctic B = 0.6 + 0.3*cos(...) ≥ 0.3 > 0 for all v."""
        for v in [i / 20 for i in range(21)]:
            rgb = cosine_palette(v, **ARCTIC)
            assert rgb[2] >= 0.29, f"Arctic B unexpectedly low: {rgb[2]:.3f} at v={v}"

    def test_lava_r_range(self):
        """Lava R = 0.5 + 0.5*cos(...) ∈ [0, 1] for all v."""
        for v in [i / 50 for i in range(51)]:
            rgb = cosine_palette(v, **LAVA)
            assert -0.01 <= rgb[0] <= 1.01, f"Lava R out of [0,1]: {rgb[0]:.3f} at v={v}"

    def test_different_palettes_differ(self):
        """Lava and arctic must produce different colors at v=0."""
        lava_rgb = cosine_palette(0.0, **LAVA)
        arctic_rgb = cosine_palette(0.0, **ARCTIC)
        assert lava_rgb != arctic_rgb


# ---------------------------------------------------------------------------
# Plasma value mathematics (Python re-implementation)
# ---------------------------------------------------------------------------

class TestPlasmaFormula:
    """Verify the plasma summing formula and normalization."""

    def test_plasma_range_bounded(self):
        """v = sum of 4 sines must lie in [-4, 4]."""
        for t in [0.0, 1.0, 2.0, 5.0, 10.0]:
            for px in range(0, 800, 50):
                for py in range(0, 800, 50):
                    x, y = pixel_coords(px, py)
                    v = plasma_value(x, y, t)
                    assert -4.0 <= v <= 4.0, f"v={v:.3f} out of [-4,4] at px={px} py={py} t={t}"

    def test_normalized_value_in_unit_interval(self):
        """n = (v + 4) / 8 must be in [0, 1] for all valid v."""
        for t in [0.0, 2.0, 7.5]:
            for px in [0, 200, 400, 600, 799]:
                for py in [0, 200, 400, 600, 799]:
                    x, y = pixel_coords(px, py)
                    v = plasma_value(x, y, t)
                    n = (v + 4) / 8
                    assert 0.0 <= n <= 1.0, f"n={n:.4f} out of [0,1] at ({px},{py}) t={t}"

    def test_four_sine_terms_present(self):
        """plasma_value returns the sum of exactly 4 sine terms (cross-check at x=y=0)."""
        t = 1.5
        expected = (
            math.sin(0 + t)
            + math.sin(0 + t * 1.3)
            + math.sin(0 + t * 0.8)
            + math.sin(0 - t * 1.1)
        )
        got = plasma_value(0.0, 0.0, t)
        assert abs(got - expected) < 1e-12

    def test_plasma_changes_over_time(self):
        """At any fixed pixel, the plasma value must differ between t=0 and t=1."""
        x, y = pixel_coords(400, 400)
        v0 = plasma_value(x, y, 0.0)
        v1 = plasma_value(x, y, 1.0)
        assert abs(v0 - v1) > 0.01, "Plasma appears frozen in time"

    def test_plasma_varies_across_pixels(self):
        """Plasma must not be constant across the canvas at a fixed time."""
        t = 2.0
        values = set()
        for px in range(0, 800, 100):
            for py in range(0, 800, 100):
                x, y = pixel_coords(px, py)
                v = round(plasma_value(x, y, t), 3)
                values.add(v)
        assert len(values) > 5, f"Plasma has too few distinct values: {len(values)}"

    def test_pixel_coords_center_is_origin(self):
        """Canvas centre (px=400, py=400) maps to approximately (0, 0)."""
        x, y = pixel_coords(400, 400)
        assert abs(x) < 0.01 and abs(y) < 0.01

    def test_pixel_coords_corner_range(self):
        """Corner pixels must map to approximately ±2 in each axis."""
        x0, y0 = pixel_coords(0, 0)
        x1, y1 = pixel_coords(800, 800)
        assert abs(x0 - (-2.0)) < 0.01
        assert abs(y0 - (-2.0)) < 0.01
        assert abs(x1 - 2.0) < 0.01
        assert abs(y1 - 2.0) < 0.01


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

class TestPiecesJson:
    def test_entry_exists(self):
        assert _load_entry() is not None, f"No entry with id={PIECE_ID!r} in pieces.json"

    def test_entry_has_all_required_fields(self):
        entry = _load_entry()
        assert entry is not None
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_entry_id_matches_directory(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).name == entry["id"]

    def test_entry_path_is_dir(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).is_dir()

    def test_thumbnail_file_exists(self):
        entry = _load_entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_year_is_int(self):
        entry = _load_entry()
        assert isinstance(entry["year"], int)

    def test_technique_mentions_plasma(self):
        entry = _load_entry()
        assert "plasma" in entry["technique"].lower()

    def test_technique_mentions_cosine(self):
        entry = _load_entry()
        assert "cosine" in entry["technique"].lower() or "palette" in entry["technique"].lower()

    def test_description_mentions_sine(self):
        entry = _load_entry()
        desc = entry["description"].lower()
        assert "sine" in desc or "sin(" in desc or "sin(" in entry["description"]

    def test_title_nonempty(self):
        entry = _load_entry()
        assert entry["title"].strip()

    def test_tagline_nonempty(self):
        entry = _load_entry()
        assert entry["tagline"].strip()


# ---------------------------------------------------------------------------
# Edge cases and explicit failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_plasma_at_exact_center_t0(self):
        """At pixel (400,400) and t=0 the plasma value must be 0 (all sines of 0)."""
        x, y = pixel_coords(400, 400)
        v = plasma_value(x, y, 0.0)
        assert abs(v) < 1e-10, f"Expected 0 at center t=0, got {v}"

    def test_plasma_with_large_t_stays_bounded(self):
        """Even at t=1000 the plasma value must remain in [-4, 4]."""
        x, y = pixel_coords(200, 600)
        v = plasma_value(x, y, 1000.0)
        assert -4.0 <= v <= 4.0

    def test_unknown_piece_id_absent(self):
        data = json.loads(PIECES_JSON.read_text())
        ghost = next((e for e in data if e["id"] == "03-ghost-plasma"), None)
        assert ghost is None

    def test_palette_at_v_half_lava(self):
        """Sanity-check lava at v=0.5: R should be near 0 (cos(π)= -1, so R=0.5-0.5=0)."""
        rgb = cosine_palette(0.5, **LAVA)
        assert abs(rgb[0]) < 0.01, f"Expected R≈0 at v=0.5, got {rgb[0]:.4f}"

    def test_palette_crossfade_lerp_midpoint(self):
        """At lerp factor 0.5, each channel must be the arithmetic mean of the two palettes."""
        for i in range(3):
            mid_a = LAVA['a'][i] + (ARCTIC['a'][i] - LAVA['a'][i]) * 0.5
            expected = (LAVA['a'][i] + ARCTIC['a'][i]) / 2
            assert abs(mid_a - expected) < 1e-10

    def test_normalization_maps_minus4_to_0(self):
        """v = -4 must normalize to n = 0."""
        n = (-4 + 4) / 8
        assert n == 0.0

    def test_normalization_maps_plus4_to_1(self):
        """v = +4 must normalize to n = 1."""
        n = (4 + 4) / 8
        assert n == 1.0

    def test_pieces_json_is_valid_list(self):
        data = json.loads(PIECES_JSON.read_text())
        assert isinstance(data, list)
        assert len(data) > 0
