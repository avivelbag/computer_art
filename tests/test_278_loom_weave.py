"""Tests for Piece 278 — the loom remembers: generative textile weave."""
import json
import math
import pathlib

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "278-loom-weave"
JSON_PATH = REPO / "pieces.json"

# ── Weave logic mirrored from index.html ─────────────────────────────────────

PLAIN = {
    "cells": [1,0, 0,1],
    "size": 2, "rows": 2, "label": "Plain Weave",
}
TWILL = {
    "cells": [1,1,0,0, 0,1,1,0, 0,0,1,1, 1,0,0,1],
    "size": 4, "rows": 4, "label": "2/2 Twill",
}
SATIN = {
    "cells": [
        0,1,1,1,1,
        1,1,1,0,1,
        1,0,1,1,1,
        1,1,1,1,0,
        1,1,0,1,1,
    ],
    "size": 5, "rows": 5, "label": "4/1 Satin",
}
HERRINGBONE = {
    "cells": [
        1,1,0,0, 0,0,1,1,
        0,1,1,0, 0,1,1,0,
        0,0,1,1, 1,1,0,0,
        1,0,0,1, 1,0,0,1,
    ],
    "size": 8, "rows": 4, "label": "Herringbone",
}
DRAFTS = [PLAIN, TWILL, SATIN, HERRINGBONE]


def warp_over(draft, r, c):
    """Return True when warp thread c passes over weft thread r for this draft."""
    ri = r % draft["rows"]
    ci = c % draft["size"]
    return draft["cells"][ri * draft["size"] + ci] == 1


def lerp(a, b, t):
    return a + (b - a) * t


WARP_PAL = [(194, 113, 79), (201, 154, 58), (240, 224, 192)]
WEFT_PAL = [(59, 48, 120), (107, 123, 164), (168, 196, 212)]


def sample_palette(pal, t):
    """Linearly interpolate a multi-stop colour palette at position t ∈ [0, 1]."""
    t = max(0.0, min(1.0, t))
    n = len(pal) - 1
    i = min(n - 1, int(t * n))
    f = t * n - i
    return tuple(lerp(pal[i][k], pal[i + 1][k], f) for k in range(3))


# ── File-presence tests ───────────────────────────────────────────────────────

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/278-loom-weave/ must exist"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_readme_not_empty():
    readme = (PIECE_DIR / "README.md").read_text()
    assert len(readme.strip()) > 100, "README.md appears too short"


def test_thumbnail_exists():
    thumb = PIECE_DIR / "thumbnail.svg"
    assert thumb.is_file(), "thumbnail.svg must exist"


def test_thumbnail_not_empty():
    thumb = PIECE_DIR / "thumbnail.svg"
    assert thumb.stat().st_size > 10_000, "thumbnail.svg appears too small"


def test_thumbnail_is_valid_svg():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<svg" in content
    assert "viewBox" in content
    assert "</svg>" in content


def test_thumbnail_dimensions_400x400():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert 'width="400"' in content
    assert 'height="400"' in content


# ── pieces.json registration tests ───────────────────────────────────────────

def test_registered_in_pieces_json():
    data = json.loads(JSON_PATH.read_text())
    ids = [e["id"] for e in data]
    assert "278-loom-weave" in ids


def test_pieces_json_entry_complete():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    data = json.loads(JSON_PATH.read_text())
    entry = next(e for e in data if e["id"] == "278-loom-weave")
    assert required <= entry.keys()
    assert entry["path"] == "pieces/278-loom-weave"
    assert entry["thumbnail"] == "pieces/278-loom-weave/thumbnail.svg"


def test_pieces_json_technique_contains_required_terms():
    data = json.loads(JSON_PATH.read_text())
    entry = next(e for e in data if e["id"] == "278-loom-weave")
    assert entry["technique"] == "SVG / generative weave / threading draft / interlace clip masking / over-under rendering"


def test_pieces_json_no_duplicate_ids():
    data = json.loads(JSON_PATH.read_text())
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "Duplicate IDs in pieces.json"


# ── index.html content tests ──────────────────────────────────────────────────

def test_index_has_all_four_draft_labels():
    content = (PIECE_DIR / "index.html").read_text()
    for label in ["Plain Weave", "2/2 Twill", "4/1 Satin", "Herringbone"]:
        assert label in content, f"Missing draft label: {label}"


def test_index_has_warpover_function():
    content = (PIECE_DIR / "index.html").read_text()
    assert "warpOver" in content


def test_index_has_drift_period():
    content = (PIECE_DIR / "index.html").read_text()
    assert "DRIFT_PERIOD" in content


def test_index_has_no_external_dependencies():
    content = (PIECE_DIR / "index.html").read_text()
    assert "https://" not in content
    assert "http://" not in content


def test_index_cells_array_present():
    content = (PIECE_DIR / "index.html").read_text()
    assert "cells:" in content


# ── Draft logic: plain weave ──────────────────────────────────────────────────

def test_plain_weave_alternates():
    """Plain weave must alternate warp-over / weft-over like a checkerboard."""
    for r in range(8):
        for c in range(8):
            expected = (r + c) % 2 == 0
            assert warp_over(PLAIN, r, c) == expected, (
                f"Plain weave wrong at ({r},{c}): expected {expected}"
            )


def test_plain_weave_period_2():
    """Plain weave must repeat with period 2 in both axes."""
    for r in range(16):
        for c in range(16):
            assert warp_over(PLAIN, r, c) == warp_over(PLAIN, r + 2, c)
            assert warp_over(PLAIN, r, c) == warp_over(PLAIN, r, c + 2)


def test_plain_weave_50pct_warp():
    """Plain weave must have exactly 50% warp-over cells in one repeat."""
    over = sum(warp_over(PLAIN, r, c) for r in range(2) for c in range(2))
    assert over == 2


# ── Draft logic: 2/2 twill ───────────────────────────────────────────────────

def test_twill_has_diagonal_rib():
    """2/2 twill must shift the warp-over pattern by 1 column per row."""
    for r in range(8):
        for c in range(8):
            assert warp_over(TWILL, r, c) == warp_over(TWILL, r + 1, c + 1), (
                f"Twill diagonal broken at ({r},{c})"
            )


def test_twill_50pct_warp():
    """2/2 twill must have exactly 50% warp-over cells in one repeat."""
    over = sum(warp_over(TWILL, r, c) for r in range(4) for c in range(4))
    assert over == 8


def test_twill_row_has_one_run_per_period():
    """Each row of the 2/2 twill must have exactly one run of 2 adjacent warp-overs per 4-column period."""
    for r in range(4):
        # Check within one 4-column period (the repeat unit, wrapping at period end)
        row_vals = [int(warp_over(TWILL, r, c)) for c in range(4)]
        over_count = sum(row_vals)
        assert over_count == 2, (
            f"Twill row {r} must have exactly 2 warp-over cells in a 4-col period, got {over_count}"
        )
        # The 2 warp-over cells must be adjacent (contiguous run)
        found_pair = any(row_vals[i] == 1 and row_vals[(i+1) % 4] == 1 for i in range(4))
        assert found_pair, f"Twill row {r} should have at least one adjacent warp-over pair"


# ── Draft logic: 4/1 satin ───────────────────────────────────────────────────

def test_satin_one_down_per_row():
    """4/1 satin must have exactly one weft-over cell per row of the repeat."""
    for r in range(5):
        weft_count = sum(int(not warp_over(SATIN, r, c)) for c in range(5))
        assert weft_count == 1, (
            f"Satin row {r} should have 1 weft-over, got {weft_count}"
        )


def test_satin_one_down_per_column():
    """4/1 satin must have exactly one weft-over cell per column of the repeat."""
    for c in range(5):
        weft_count = sum(int(not warp_over(SATIN, r, c)) for r in range(5))
        assert weft_count == 1, (
            f"Satin col {c} should have 1 weft-over, got {weft_count}"
        )


def test_satin_no_adjacent_weft_cells():
    """No two weft-over cells should be adjacent in the satin repeat (no twill diagonal)."""
    for r in range(5):
        for c in range(5):
            if not warp_over(SATIN, r, c):
                assert warp_over(SATIN, r + 1, c + 1), (
                    f"Adjacent weft-over (diagonal) at satin ({r},{c}) — looks like twill"
                )
                assert warp_over(SATIN, r + 1, c - 1 + 5), (
                    f"Adjacent weft-over (anti-diagonal) at satin ({r},{c})"
                )


def test_satin_80pct_warp():
    """4/1 satin must be 80% warp-over (4 over, 1 under per pick)."""
    over = sum(warp_over(SATIN, r, c) for r in range(5) for c in range(5))
    assert over == 20  # 25 cells, 20 warp-over


# ── Draft logic: herringbone ─────────────────────────────────────────────────

def test_herringbone_left_half_is_twill():
    """Columns 0-3 of herringbone must match 2/2 twill."""
    for r in range(4):
        for c in range(4):
            assert warp_over(HERRINGBONE, r, c) == warp_over(TWILL, r, c), (
                f"Herringbone left half differs from twill at ({r},{c})"
            )


def test_herringbone_diagonal_reverses():
    """The twill diagonal shifts +1/col in the left half and -1/col in the right half.

    In the left half the warp-run start column increases by 1 each row (forward twill).
    In the right half it decreases by 1 each row (reversed twill).
    Verified by checking that the left-half pattern matches the forward twill, while
    the right-half pattern matches the forward twill mirrored horizontally.
    """
    for r in range(4):
        for c in range(4):
            # Left half must match forward 2/2 twill
            assert warp_over(HERRINGBONE, r, c) == warp_over(TWILL, r, c), (
                f"Herringbone left half differs from twill at ({r},{c})"
            )
        for c in range(4, 8):
            # Right half must match forward twill mirrored: col c mirrors to (7-c)
            mirrored_c = 7 - c
            assert warp_over(HERRINGBONE, r, c) == warp_over(TWILL, r, mirrored_c), (
                f"Herringbone right half not mirrored twill at ({r},{c})"
            )


def test_herringbone_50pct_warp():
    """Herringbone must have exactly 50% warp-over cells (same as twill)."""
    over = sum(warp_over(HERRINGBONE, r, c) for r in range(4) for c in range(8))
    assert over == 16  # 32 cells, 16 warp-over


# ── Colour palette tests ──────────────────────────────────────────────────────

def test_palette_endpoints():
    """sample_palette at t=0 and t=1 must return the first and last palette stops."""
    r0, g0, b0 = sample_palette(WARP_PAL, 0.0)
    assert abs(r0 - 194) < 1 and abs(g0 - 113) < 1 and abs(b0 - 79) < 1

    r1, g1, b1 = sample_palette(WARP_PAL, 1.0)
    assert abs(r1 - 240) < 1 and abs(g1 - 224) < 1 and abs(b1 - 192) < 1


def test_palette_midpoint_between_stops():
    """At t=0.5 the palette must be at the middle stop (ochre)."""
    r, g, b = sample_palette(WARP_PAL, 0.5)
    assert abs(r - 201) < 2 and abs(g - 154) < 2 and abs(b - 58) < 2


def test_palette_rgb_stays_in_byte_range():
    for t100 in range(101):
        t = t100 / 100.0
        for pal in [WARP_PAL, WEFT_PAL]:
            r, g, b = sample_palette(pal, t)
            assert 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255


def test_warp_palette_is_warm():
    """Warp palette (warm) must be redder than weft palette (cool) at t=0."""
    wr, wg, wb = sample_palette(WARP_PAL, 0.0)
    fr, fg, fb = sample_palette(WEFT_PAL, 0.0)
    assert wr > fr, "Warp palette should have more red than weft palette at t=0"


def test_weft_palette_is_cool():
    """Weft palette (cool) must have more blue than red at t=0."""
    r, g, b = sample_palette(WEFT_PAL, 0.0)
    assert b > r, "Weft palette should have more blue than red at t=0 (indigo)"


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_warp_over_large_coordinates():
    """warp_over must tile correctly at large row/column values."""
    for r in range(100):
        for c in range(100):
            for draft in DRAFTS:
                result = warp_over(draft, r, c)
                tiled = warp_over(draft, r % draft["rows"], c % draft["size"])
                assert result == tiled, (
                    f"Tiling mismatch for {draft['label']} at ({r},{c})"
                )


def test_draft_cells_are_binary():
    """All draft cells must be 0 or 1."""
    for draft in DRAFTS:
        for v in draft["cells"]:
            assert v in (0, 1), f"Non-binary cell {v} in {draft['label']}"


def test_draft_cells_length_matches_size_times_rows():
    """Each draft's cells array length must equal size * rows."""
    for draft in DRAFTS:
        expected = draft["size"] * draft["rows"]
        assert len(draft["cells"]) == expected, (
            f"{draft['label']}: expected {expected} cells, got {len(draft['cells'])}"
        )


def test_palette_monotone_warm_to_light():
    """Warp palette brightness must increase from terracotta to cream."""
    def brightness(c):
        return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

    samples = [sample_palette(WARP_PAL, t / 10) for t in range(11)]
    for i in range(len(samples) - 1):
        assert brightness(samples[i]) <= brightness(samples[i + 1]) + 1.0, (
            f"Warp palette brightness not monotone at t={i/10:.1f}"
        )


# ── Failure modes ─────────────────────────────────────────────────────────────

def test_plain_weave_not_all_warp():
    """Plain weave must not have all cells as warp-over."""
    over = sum(warp_over(PLAIN, r, c) for r in range(4) for c in range(4))
    assert over < 16


def test_plain_weave_not_all_weft():
    """Plain weave must not have all cells as weft-over."""
    over = sum(warp_over(PLAIN, r, c) for r in range(4) for c in range(4))
    assert over > 0


def test_twill_and_plain_differ():
    """Twill and plain must produce different patterns over the same region."""
    same = all(
        warp_over(PLAIN, r, c) == warp_over(TWILL, r, c)
        for r in range(4) for c in range(4)
    )
    assert not same, "Twill and plain should not be identical"


def test_satin_and_twill_differ():
    """Satin and twill must produce different patterns."""
    same = all(
        warp_over(SATIN, r, c) == warp_over(TWILL, r, c)
        for r in range(5) for c in range(5)
    )
    assert not same, "Satin and twill should not be identical"
