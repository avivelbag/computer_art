"""Tests for Piece 111 — Bifurcation: Where Order Fractures Into Chaos."""
import json
import pathlib
import re
import struct

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "111-bifurcation"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

R_MIN = 2.5
R_MAX = 4.0
R_SPAN = 1.5
CHAOS_ONSET = 3.57
WARMUP = 300
PLOT = 300


def _load_entry():
    """Return the pieces.json entry for piece 111, or None if absent."""
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == PIECE_ID), None)


def logistic_iterate(r, x, steps):
    """Advance the logistic map x → r·x·(1−x) for *steps* iterations."""
    for _ in range(steps):
        x = r * x * (1 - x)
    return x


def logistic_attractor(r, warmup=WARMUP, plot=PLOT, x0=0.5):
    """Return the list of plotted x values after *warmup* steps of burn-in."""
    x = logistic_iterate(r, x0, warmup)
    values = []
    for _ in range(plot):
        x = r * x * (1 - x)
        values.append(x)
    return values


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

    def test_thumbnail_png_exists(self):
        assert (PIECE_DIR / "thumbnail.png").is_file()

    def test_thumbnail_png_magic_bytes(self):
        """thumbnail.png must start with valid PNG magic bytes."""
        data = (PIECE_DIR / "thumbnail.png").read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_readme_nonempty(self):
        assert len((PIECE_DIR / "README.md").read_text()) > 100

    def test_generate_thumbnail_script_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# PNG dimensions (read from IHDR without Pillow)
# ---------------------------------------------------------------------------

class TestPngDimensions:
    def test_thumbnail_is_400x400(self):
        """Check width/height from the PNG IHDR chunk (bytes 16–23)."""
        data = (PIECE_DIR / "thumbnail.png").read_bytes()
        w = struct.unpack('>I', data[16:20])[0]
        h = struct.unpack('>I', data[20:24])[0]
        assert w == 400 and h == 400, f"Expected 400×400, got {w}×{h}"


# ---------------------------------------------------------------------------
# index.html content
# ---------------------------------------------------------------------------

class TestIndexHtmlContent:
    def setup_method(self):
        self.html = (PIECE_DIR / "index.html").read_text()

    def test_canvas_element_present(self):
        assert "<canvas" in self.html

    def test_createimagedata_present(self):
        assert "createImageData" in self.html

    def test_putimagedata_present(self):
        assert "putImageData" in self.html

    def test_animation_loop_present(self):
        assert "requestAnimationFrame" in self.html

    def test_r_min_25_present(self):
        assert "2.5" in self.html

    def test_r_span_covers_range(self):
        assert "1.5" in self.html

    def test_warmup_300_present(self):
        assert "300" in self.html

    def test_chaos_onset_357_present(self):
        assert "3.57" in self.html

    def test_logistic_map_formula_present(self):
        """The update rule x = r * x * (1 - x) must appear literally."""
        assert re.search(r'r\s*\*\s*x\s*\*\s*\(1\s*-\s*x\)', self.html)

    def test_color_lerp_present(self):
        """Blue→gold color mapping must use a lerp or linear interpolation."""
        assert "lerp" in self.html

    def test_hold_4000ms_present(self):
        """The 4-second hold must be expressed as 4000 ms."""
        assert "4000" in self.html or "HOLD_MS" in self.html

    def test_reset_present(self):
        """A reset function or reset path must be present."""
        assert "reset" in self.html.lower()

    def test_chaos_line_drawn_with_lineto(self):
        """The chaos-onset line requires ctx.lineTo."""
        assert "lineTo" in self.html

    def test_dashed_line_via_setlinedash(self):
        """The dashed vertical line must use setLineDash."""
        assert "setLineDash" in self.html

    def test_no_external_dependencies(self):
        assert not re.search(r'<script[^>]+src="https?://', self.html)

    def test_background_near_black(self):
        """Background fill must use the near-black #050508 palette."""
        assert "050508" in self.html or "5, 5, 8" in self.html or "5,5,8" in self.html

    def test_canvas_width_800(self):
        assert "800" in self.html

    def test_canvas_height_500(self):
        assert "500" in self.html


# ---------------------------------------------------------------------------
# Logistic map mathematics (Python re-implementation)
# ---------------------------------------------------------------------------

class TestLogisticMapLogic:
    """Verify the mathematical behaviour of the logistic map at key parameter values."""

    def test_fixed_point_below_3(self):
        """For r < 3 the attractor is the unique fixed point x* = 1 − 1/r."""
        r = 2.8
        x = logistic_iterate(r, 0.5, 500)
        expected = 1 - 1 / r
        assert abs(x - expected) < 1e-6, f"Expected {expected:.6f}, got {x:.6f}"

    def test_period_2_at_r32(self):
        """At r=3.2 the attractor has period 2: ≤3 distinct values after warmup."""
        values = logistic_attractor(3.2)
        unique = {round(v, 4) for v in values}
        assert len(unique) <= 3, f"Expected period-2 orbit, got {len(unique)} distinct values"

    def test_all_plotted_values_in_unit_interval(self):
        """Iterated x values must remain in [0, 1] for all tested r values."""
        for r in [2.5, 3.0, 3.5, 3.57, 3.9, 3.99]:
            values = logistic_attractor(r)
            assert all(0.0 <= v <= 1.0 for v in values), f"Out-of-range x at r={r}"

    def test_chaos_at_r39(self):
        """At r=3.9 (chaotic region) 300 plotted steps yield many distinct values.

        Note: r=4.0 is avoided here because x₀=0.5 is a degenerate pre-image of 0
        at exactly r=4.0 (x₀ → 1.0 → 0.0 → fixed), producing a trivial orbit.
        The JavaScript canvas uses r = 2.5 + (px/W)*1.5, which never hits r=4.0
        exactly for integer px < W, so this degenerate case never appears in practice.
        """
        values = logistic_attractor(3.9)
        unique = {round(v, 3) for v in values}
        assert len(unique) > 50, f"Expected dense chaotic orbit, got {len(unique)} values"

    def test_stable_region_single_attractor(self):
        """At r=2.6 the long-run orbit collapses to a single fixed point."""
        values = logistic_attractor(2.6)
        unique = {round(v, 3) for v in values}
        assert len(unique) <= 2, f"Expected single fixed point, got {len(unique)} values"

    def test_pixel_row_in_bounds_for_all_r(self):
        """Pixel row py = int((1−x)·H) must be within [0, H) for any valid x."""
        H = 500
        for r in [2.5, 3.0, 3.57, 3.9]:
            for x in logistic_attractor(r):
                py = int((1 - x) * H)
                assert 0 <= py < H, f"py={py} out of bounds at r={r}, x={x}"

    def test_warmup_removes_transient(self):
        """After 300 warmup steps at r=2.8, x must be near the fixed point 1−1/r≈0.643."""
        r = 2.8
        x_after = logistic_iterate(r, 0.5, WARMUP)
        expected = 1 - 1 / r  # ≈ 0.6429
        assert abs(x_after - expected) < 1e-6, f"Warmup did not converge to fixed point {expected:.4f}"


# ---------------------------------------------------------------------------
# Color palette math
# ---------------------------------------------------------------------------

class TestColorPalette:
    """Verify the blue→gold lerp mapping used to color bifurcation points."""

    @staticmethod
    def _color(r):
        """Return (R, G, B) integers for parameter r using the spec's lerp formula."""
        def lerp(a, b, t):
            return a + (b - a) * t
        t = (r - R_MIN) / R_SPAN
        return int(lerp(30, 255, t)), int(lerp(80, 200, t * t)), int(lerp(200, 30, t))

    def test_stable_region_is_blue_dominant(self):
        """At r=2.6 (stable region) the blue channel must exceed the red channel."""
        rv, gv, bv = self._color(2.6)
        assert bv > rv, f"Expected blue dominance at r=2.6, got R={rv} G={gv} B={bv}"

    def test_chaotic_region_is_warm(self):
        """At r=3.9 (chaotic region) the red channel must exceed the blue channel."""
        rv, gv, bv = self._color(3.9)
        assert rv > bv, f"Expected warm tone at r=3.9, got R={rv} G={gv} B={bv}"

    def test_color_at_r_min_max_blue(self):
        """At r=2.5 (t=0) the blue channel must be 200 (its maximum)."""
        _, _, bv = self._color(R_MIN)
        assert bv == 200

    def test_color_at_r_max_full_red(self):
        """At r=4.0 (t=1) the red channel must be 255 (its maximum)."""
        rv, _, _ = self._color(R_MAX)
        assert rv == 255

    def test_chaos_line_pixel_in_right_half(self):
        """The chaos onset line at r=3.57 must fall in the right half of the canvas."""
        W = 800
        cx = round(W * (CHAOS_ONSET - R_MIN) / R_SPAN)
        assert W // 2 < cx < W, f"Expected cx in ({W//2}, {W}), got {cx}"


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
        assert entry is not None
        assert (REPO / entry["path"]).name == entry["id"]

    def test_thumbnail_references_png(self):
        entry = _load_entry()
        assert entry is not None
        assert entry["thumbnail"].endswith(".png")

    def test_entry_year_is_int(self):
        entry = _load_entry()
        assert isinstance(entry["year"], int)

    def test_entry_path_exists(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        entry = _load_entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_bifurcation_in_technique(self):
        """Technique field must mention bifurcation or logistic map."""
        entry = _load_entry()
        assert (
            "bifurcation" in entry["technique"].lower()
            or "logistic" in entry["technique"].lower()
        )

    def test_piece_111_appears_after_106(self):
        """Piece 111 must appear after piece 106 in the ordered list."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "106-langtons-turmites" in ids
        assert PIECE_ID in ids
        assert ids.index(PIECE_ID) > ids.index("106-langtons-turmites")


# ---------------------------------------------------------------------------
# Edge cases and explicit failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_logistic_at_x0_equals_0_stays_zero(self):
        """x=0 is a trivial fixed point — logistic map keeps it at 0 forever."""
        for r in [2.5, 3.0, 4.0]:
            assert logistic_iterate(r, 0.0, 100) == 0.0

    def test_logistic_at_x1_gives_0_on_next_step(self):
        """x=1 maps to 0 on the first step for any r."""
        assert logistic_iterate(3.5, 1.0, 1) == 0.0

    def test_r_span_equals_r_max_minus_r_min(self):
        assert R_SPAN == pytest.approx(R_MAX - R_MIN)

    def test_unknown_piece_id_returns_none(self):
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost-bifurcation"), None)
        assert found is None

    def test_zero_warmup_preserves_initial_x(self):
        """With zero warmup steps the iterate starts exactly from x0."""
        assert logistic_iterate(3.0, 0.5, 0) == 0.5

    def test_large_warmup_does_not_raise(self):
        """Iterating 10 000 steps must not raise any exception."""
        logistic_iterate(3.8, 0.5, 10_000)

    def test_all_r_columns_produce_valid_pixels_small_canvas(self):
        """For W=10, H=10 all pixel rows computed from the logistic map are in [0, H)."""
        W_small, H_small = 10, 10
        for px in range(W_small):
            r = R_MIN + (px / W_small) * R_SPAN
            for x in logistic_attractor(r, warmup=50, plot=50):
                py = int((1 - x) * H_small)
                assert 0 <= py < H_small
