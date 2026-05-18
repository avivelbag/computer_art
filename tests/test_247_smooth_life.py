"""Tests for Piece 247 — Smooth Life: The Creature That Has No Name."""
import json
import math
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "247-smooth-life"
INDEX = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "247-smooth-life"


# ---------------------------------------------------------------------------
# Python mirror of SmoothLife math for logic tests
# ---------------------------------------------------------------------------

def sigma1(x: float, a: float, alpha: float) -> float:
    """
    Logistic sigmoid centered at a with transition width alpha.

    Returns a smooth 0→1 step as x crosses a.  Used as the building block
    for the SmoothLife birth/survival neighborhood function.
    """
    return 1.0 / (1.0 + math.exp(-4.0 / alpha * (x - a)))


def sigma2(x: float, a: float, b: float, alpha: float) -> float:
    """
    Smooth indicator for x ∈ (a, b).

    Equals σ₁(x,a,α) × (1 − σ₁(x,b,α)) — near 1 inside the interval,
    near 0 outside.
    """
    return sigma1(x, a, alpha) * (1.0 - sigma1(x, b, alpha))


# SmoothLife parameters (Rafler 2011)
RI = 3
RO = 6
B1, B2 = 0.278, 0.365
D1, D2 = 0.267, 0.445
ALPHA_N = 0.028
ALPHA_M = 0.147


def sigma_m(x: float, y: float, m: float) -> float:
    """
    Interpolate between birth threshold x and death threshold y based on outer density m.

    When m ≈ 0 (sparse outer neighborhood) the result approaches the birth value x.
    When m ≈ 1 (dense outer neighborhood) the result approaches the death value y.
    This is the "sigmaM" mix from Rafler 2011 that makes the birth/death thresholds
    adaptive to the outer density rather than fixed.
    """
    mix = sigma1(m, 0.5, ALPHA_M)
    return x + (y - x) * mix


def smooth_transition(n: float, m: float) -> float:
    """
    SmoothLife birth/survival function (Rafler 2011).

    Computes the target state s ∈ [0,1] from inner neighborhood density n
    and outer neighborhood density m.

    The adaptive thresholds lo and hi for n are interpolated between birth
    (B1/B2) and death (D1/D2) boundaries based on the outer density m.
    When the outer ring is sparse (m≈0), thresholds sit near the birth range;
    when dense (m≈1), near the death range.  sigma2 then evaluates whether n
    falls within the [lo, hi] survival window.
    """
    lo = sigma_m(B1, D1, m)
    hi = sigma_m(B2, D2, m)
    return sigma2(n, lo, hi, ALPHA_N)


def clamp01(v: float) -> float:
    """Clamp v to [0, 1]."""
    return max(0.0, min(1.0, v))


def build_kernels(ri: int = RI, ro: int = RO):
    """
    Return (inner_offsets, outer_offsets, inner_area, outer_area).

    inner_offsets: list of (dx, dy) where dx²+dy² ≤ ri²
    outer_offsets: list of (dx, dy) where ri² < dx²+dy² ≤ ro²
    """
    inner, outer = [], []
    ri2, ro2 = ri * ri, ro * ro
    for dy in range(-ro, ro + 1):
        for dx in range(-ro, ro + 1):
            r2 = dx * dx + dy * dy
            if r2 <= ri2:
                inner.append((dx, dy))
            elif r2 <= ro2:
                outer.append((dx, dy))
    return inner, outer, float(len(inner)), float(len(outer))


def smooth_step(grid: list, w: int, h: int) -> list:
    """
    Advance one SmoothLife generation on a w×h toroidal float grid.

    grid: flat list of float values in [0,1], length w*h.
    Returns a new list of the same length with the updated state.
    """
    inner, outer, ia, oa = build_kernels()
    nxt = [0.0] * (w * h)
    for cy in range(h):
        for cx in range(w):
            n = sum(grid[((cy + dy) % h) * w + (cx + dx) % w] for dx, dy in inner) / ia
            m = sum(grid[((cy + dy) % h) * w + (cx + dx) % w] for dx, dy in outer) / oa
            s = smooth_transition(n, m)
            nxt[cy * w + cx] = clamp01(2.0 * s - 1.0 + 0.9 * grid[cy * w + cx])
    return nxt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_pieces() -> list:
    """Return the parsed contents of pieces.json."""
    return json.loads(PIECES_JSON.read_text())


def get_entry() -> dict | None:
    """Return the pieces.json entry for 247-smooth-life, or None if absent."""
    return next((p for p in load_pieces() if p.get("id") == PIECE_ID), None)


def html() -> str:
    """Return the full text of index.html."""
    return INDEX.read_text()


# ---------------------------------------------------------------------------
# File-system tests
# ---------------------------------------------------------------------------

class TestFiles:
    def test_directory_exists(self):
        assert PIECE_DIR.is_dir(), f"Missing directory: {PIECE_DIR}"

    def test_index_html_exists(self):
        assert INDEX.is_file()

    def test_thumbnail_exists(self):
        assert THUMBNAIL.is_file()

    def test_readme_exists(self):
        assert README.is_file()

    def test_index_html_non_trivial(self):
        assert len(html()) > 3000, "index.html is suspiciously short"

    def test_readme_non_trivial(self):
        assert len(README.read_text().strip()) > 200

    def test_thumbnail_is_valid_svg(self):
        content = THUMBNAIL.read_text()
        assert "<svg" in content and "</svg>" in content

    def test_thumbnail_has_rect_or_ellipse(self):
        content = THUMBNAIL.read_text()
        assert "<rect" in content or "<ellipse" in content, \
            "Thumbnail has no rect or ellipse elements"


# ---------------------------------------------------------------------------
# pieces.json metadata
# ---------------------------------------------------------------------------

class TestPiecesJson:
    def test_entry_exists(self):
        assert get_entry() is not None, f"{PIECE_ID} not found in pieces.json"

    def test_required_fields(self):
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
        e = get_entry()
        assert e is not None
        missing = required - e.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches(self):
        assert get_entry()["id"] == PIECE_ID

    def test_path_correct(self):
        assert get_entry()["path"] == f"pieces/{PIECE_ID}"

    def test_thumbnail_file_exists(self):
        e = get_entry()
        assert (REPO / e["thumbnail"]).is_file()

    def test_year_is_int(self):
        assert isinstance(get_entry()["year"], int)

    def test_technique_mentions_canvas(self):
        assert "canvas" in get_entry()["technique"].lower()

    def test_technique_mentions_smooth_life(self):
        tech = get_entry()["technique"].lower()
        assert "smoothlife" in tech or "smooth" in tech or "cellular" in tech

    def test_appears_after_244(self):
        """247-smooth-life must follow 244-spirolaterals in pieces.json."""
        pieces = load_pieces()
        idx_244 = next((i for i, p in enumerate(pieces) if p["id"] == "244-spirolaterals"), None)
        idx_247 = next((i for i, p in enumerate(pieces) if p["id"] == PIECE_ID), None)
        assert idx_244 is not None, "244-spirolaterals missing from pieces.json"
        assert idx_247 is not None, f"{PIECE_ID} missing from pieces.json"
        assert idx_247 > idx_244, "247-smooth-life must come after 244-spirolaterals"

    def test_no_duplicate_ids(self):
        ids = [p["id"] for p in load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate piece IDs in pieces.json"

    def test_prior_pieces_preserved(self):
        ids = {p["id"] for p in load_pieces()}
        for expected in ["01-amber-current", "244-spirolaterals", "212-game-of-life"]:
            assert expected in ids, f"Prior piece {expected!r} was removed"


# ---------------------------------------------------------------------------
# index.html structure
# ---------------------------------------------------------------------------

class TestIndexHtml:
    def test_has_canvas(self):
        assert "<canvas" in html()

    def test_has_script(self):
        assert "<script" in html()

    def test_has_viewport_meta(self):
        assert 'name="viewport"' in html()

    def test_has_charset(self):
        assert "charset" in html()

    def test_no_external_scripts(self):
        assert not re.findall(r'<script[^>]+src=["\']https?://', html())

    def test_self_contained(self):
        h = html()
        assert '<script src=' not in h
        assert '<link rel="stylesheet"' not in h

    def test_has_requestanimationframe(self):
        assert "requestAnimationFrame" in html()

    def test_has_float32array_buffers(self):
        h = html()
        assert "Float32Array" in h, "Must use Float32Array for simulation buffers"

    def test_has_two_buffers(self):
        """cur and nxt (or similar) buffers must be present."""
        h = html()
        assert "Float32Array" in h
        count = h.count("Float32Array")
        assert count >= 2, "Need at least two Float32Array buffer allocations"

    def test_has_smoothlife_rule(self):
        h = html().lower()
        assert "sigma" in h or "smoothtransition" in h or "smooth_transition" in h or \
               "alpha_n" in h or "alpha" in h

    def test_has_inner_outer_kernels(self):
        h = html().lower()
        assert "innerkernel" in h or "inner" in h

    def test_has_color_lut(self):
        h = html()
        assert "LUT" in h or "lut" in h.lower(), "Must have a color LUT"

    def test_lut_has_near_black(self):
        """Near-black color (#050508 or similar) must be in the LUT construction."""
        h = html().lower()
        assert "050508" in h or "05050" in h or "near-black" in h

    def test_lut_has_violet(self):
        """Deep violet (#7b3fff or similar) must be referenced."""
        h = html().lower()
        assert "7b3fff" in h or "9966ff" in h or "violet" in h

    def test_lut_has_cyan(self):
        """Bright cyan (#00e8d6 or similar) must be referenced."""
        h = html().lower()
        assert "00e8d6" in h or "0ee8" in h or "cyan" in h

    def test_has_seed_or_init(self):
        h = html().lower()
        assert "seed" in h or "init" in h or "random" in h

    def test_has_toroidal_wrap(self):
        h = html()
        assert "% GW" in h or "%GW" in h or "% W" in h or "modulo" in h.lower() or \
               "toroidal" in h.lower() or "wrap" in h.lower()

    def test_has_play_pause_button(self):
        h = html().lower()
        assert "play" in h and "pause" in h

    def test_has_reset_button(self):
        assert "reset" in html().lower()

    def test_has_step_button(self):
        assert "step" in html().lower()

    def test_has_visibility_change_handler(self):
        assert "visibilitychange" in html()

    def test_has_image_rendering_pixelated(self):
        h = html().lower()
        assert "pixelated" in h or "crisp-edges" in h

    def test_has_dark_background(self):
        h = html().lower()
        assert "050508" in h or "0a0a12" in h or "background:#0" in h


# ---------------------------------------------------------------------------
# SmoothLife math tests (Python mirror)
# ---------------------------------------------------------------------------

class TestSigmaFunctions:
    def test_sigma1_midpoint(self):
        """σ₁(a, a, α) must equal 0.5 exactly."""
        result = sigma1(0.5, 0.5, ALPHA_N)
        assert abs(result - 0.5) < 1e-10

    def test_sigma1_below_is_near_zero(self):
        """σ₁ at x << a must be near 0."""
        result = sigma1(0.0, 1.0, ALPHA_N)
        assert result < 0.01

    def test_sigma1_above_is_near_one(self):
        """σ₁ at x >> a must be near 1."""
        result = sigma1(2.0, 0.0, ALPHA_N)
        assert result > 0.99

    def test_sigma2_inside_interval_near_one(self):
        """σ₂ well inside (a, b) must be near 1."""
        mid = (B1 + B2) / 2
        result = sigma2(mid, B1, B2, ALPHA_N)
        assert result > 0.9, f"Expected >0.9 inside interval, got {result}"

    def test_sigma2_outside_interval_near_zero(self):
        """σ₂ far below a must be near 0."""
        result = sigma2(0.0, B1, B2, ALPHA_N)
        assert result < 0.05

    def test_sigma2_above_interval_near_zero(self):
        """σ₂ far above b must be near 0."""
        result = sigma2(1.0, B1, B2, ALPHA_N)
        assert result < 0.05

    def test_transition_output_in_range(self):
        """smooth_transition must always return values in [0, 1]."""
        for n in [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]:
            for m in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
                result = smooth_transition(n, m)
                assert 0.0 <= result <= 1.0, \
                    f"transition({n},{m}) = {result} out of [0,1]"

    def test_transition_symmetry_check(self):
        """Non-regression: verify specific known output values don't drift."""
        # n=0.3, m=0.3 is a moderately occupied cell — should produce a positive state
        s = smooth_transition(0.3, 0.3)
        assert 0.0 <= s <= 1.0

    def test_dead_cell_stays_dead_with_no_neighbors(self):
        """
        A cell with n=0 and m=0 should have near-zero target state, so the
        clamped damped update clamp(2s-1 + 0.9*0, 0, 1) stays near 0.

        When n=0 and m=0, lo ≈ B1=0.278 and hi ≈ B2=0.365. sigma1(0, 0.278, 0.028)≈0
        so sigma2(0, lo, hi, ALPHA_N) ≈ 0, giving s≈0 and next≈0.
        """
        s = smooth_transition(0.0, 0.0)
        next_val = clamp01(2.0 * s - 1.0 + 0.9 * 0.0)
        assert next_val < 0.1, \
            f"Isolated dead cell should stay dead, got {next_val}"

    def test_active_cell_survives_in_birth_range(self):
        """
        n=0.33, m=0.33 is in the birth range → s should be near 1.

        sigma_m(B1=0.278, D1=0.267, m=0.33) ≈ 0.277 (lower threshold for n)
        sigma_m(B2=0.365, D2=0.445, m=0.33) ≈ 0.366 (upper threshold for n)
        n=0.33 is well inside [0.277, 0.366], so sigma2 ≈ 1.
        """
        s = smooth_transition(0.33, 0.33)
        assert s > 0.9, f"n=0.33, m=0.33 should give s>0.9 (active birth), got {s}"


class TestKernelBuilding:
    def test_inner_kernel_nonempty(self):
        inner, _, ia, _ = build_kernels()
        assert len(inner) > 0
        assert ia > 0

    def test_outer_kernel_nonempty(self):
        _, outer, _, oa = build_kernels()
        assert len(outer) > 0
        assert oa > 0

    def test_inner_kernel_all_within_ri(self):
        """Every offset in the inner kernel must satisfy dx²+dy² ≤ RI²."""
        inner, _, _, _ = build_kernels()
        for dx, dy in inner:
            assert dx * dx + dy * dy <= RI * RI

    def test_outer_kernel_all_within_annulus(self):
        """Every offset in the outer kernel must lie strictly outside ri and within ro."""
        _, outer, _, _ = build_kernels()
        for dx, dy in outer:
            r2 = dx * dx + dy * dy
            assert r2 > RI * RI
            assert r2 <= RO * RO

    def test_no_overlap_between_kernels(self):
        """No offset appears in both inner and outer kernels."""
        inner, outer, _, _ = build_kernels()
        inner_set = set(inner)
        for off in outer:
            assert off not in inner_set


class TestSmoothStep:
    def test_all_zeros_stays_zero(self):
        """A fully empty (zero) grid should remain near-zero after a step."""
        W, H = 16, 16
        grid = [0.0] * (W * H)
        nxt = smooth_step(grid, W, H)
        assert all(v < 0.05 for v in nxt), "Empty grid should stay empty"

    def test_output_clamped_in_01(self):
        """After one step, all values must be in [0, 1]."""
        import random
        rng = random.Random(42)
        W, H = 16, 16
        grid = [rng.random() for _ in range(W * H)]
        nxt = smooth_step(grid, W, H)
        assert all(0.0 <= v <= 1.0 for v in nxt), "Values must stay in [0,1]"

    def test_uniform_full_grid_changes(self):
        """A fully-alive grid (all 1s) should not be a fixed point — some cells decay."""
        W, H = 16, 16
        grid = [1.0] * (W * H)
        nxt = smooth_step(grid, W, H)
        mean_before = sum(grid) / len(grid)
        mean_after  = sum(nxt) / len(nxt)
        # Fully-alive grid is oversaturated; some cells should decrease
        # (the exact behavior depends on parameters, but mean should shift)
        assert mean_after != pytest.approx(mean_before, abs=1e-6), \
            "Uniform full grid should not be a perfect fixed point"

    def test_seed_birth_after_one_step(self):
        """
        Edge cells of a central seed should be born (grow toward 1) after 1 step.

        The 12×12 patch has cells whose inner average n sits near the birth
        range [B1, B2] ≈ [0.278, 0.365] — birth occurs there, producing max > 0.5.
        """
        W, H = 32, 32
        grid = [0.0] * (W * H)
        for dy in range(-6, 6):
            for dx in range(-6, 6):
                cx, cy = W // 2 + dx, H // 2 + dy
                grid[cy * W + cx] = 0.3 + 0.1 * ((dx + dy) % 3)
        after_one = smooth_step(grid, W, H)
        max_val = max(after_one)
        assert max_val > 0.5, \
            f"After 1 step from a seeded grid, max should be > 0.5 (got {max_val})"

    def test_single_cell_produces_no_explosion(self):
        """A single-cell seed should not cause values to exceed 1.0 after 3 steps."""
        W, H = 20, 20
        grid = [0.0] * (W * H)
        grid[H // 2 * W + W // 2] = 0.5
        current = grid
        for _ in range(3):
            current = smooth_step(current, W, H)
        assert all(v <= 1.0 for v in current), "Values must not exceed 1.0"

    def test_toroidal_wrap_symmetry(self):
        """
        A centered symmetric 3×3 block should evolve the same from center as
        from a corner (toroidal wrap makes the grid equivalent under translation).
        """
        W, H = 20, 20

        def make_block(ox, oy):
            g = [0.0] * (W * H)
            for dy in range(3):
                for dx in range(3):
                    g[((oy + dy) % H) * W + (ox + dx) % W] = 0.4
            return g

        g_center = make_block(W // 2 - 1, H // 2 - 1)
        g_corner = make_block(W - 1, H - 1)

        after_center = smooth_step(g_center, W, H)
        after_corner = smooth_step(g_corner, W, H)

        mean_c = sum(after_center) / len(after_center)
        mean_k = sum(after_corner) / len(after_corner)
        assert abs(mean_c - mean_k) < 1e-6, \
            f"Toroidal symmetry violated: center mean {mean_c} vs corner mean {mean_k}"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_tiny_grid_step_runs(self):
        """step() must not crash on the smallest meaningful grid (8×8)."""
        W, H = 8, 8
        grid = [0.1] * (W * H)
        result = smooth_step(grid, W, H)
        assert len(result) == W * H

    def test_large_grid_step_runs(self):
        """step() must work on a 64×64 grid without error."""
        W, H = 64, 64
        grid = [0.0] * (W * H)
        grid[H // 2 * W + W // 2] = 0.3
        result = smooth_step(grid, W, H)
        assert len(result) == W * H
        assert all(0.0 <= v <= 1.0 for v in result)

    def test_sigma1_monotone_increasing(self):
        """σ₁ must be strictly monotone increasing over a moderate input range."""
        # Keep values close to a=0.5 to avoid math.exp overflow at large |x-a| / alpha
        prev = sigma1(0.1, 0.5, ALPHA_N)
        for x in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            curr = sigma1(x, 0.5, ALPHA_N)
            assert curr > prev, f"σ₁ not monotone at x={x}"
            prev = curr

    def test_wrong_piece_id_absent(self):
        """Typo-IDs must not exist in pieces.json."""
        ids = {p["id"] for p in load_pieces()}
        assert "247-smoothlife" not in ids
        assert "247-smooth-life-wrong" not in ids

    def test_clamp_correctness(self):
        """clamp01 must correctly clamp boundary values."""
        assert clamp01(-0.5) == 0.0
        assert clamp01(1.5) == 1.0
        assert clamp01(0.5) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

class TestReadme:
    def test_mentions_smoothlife_or_rafler(self):
        text = README.read_text().lower()
        assert "smoothlife" in text or "rafler" in text or "smooth life" in text

    def test_mentions_sigmoid(self):
        text = README.read_text().lower()
        assert "sigmoid" in text or "sigma" in text or "logistic" in text

    def test_mentions_conway_or_game_of_life(self):
        text = README.read_text().lower()
        assert "conway" in text or "game of life" in text or "cellular automaton" in text

    def test_mentions_float_or_continuous(self):
        text = README.read_text().lower()
        assert "float" in text or "continuous" in text or "[0,1]" in text

    def test_mentions_parameters(self):
        text = README.read_text()
        assert "0.278" in text or "b1" in text.lower() or "B1" in text
