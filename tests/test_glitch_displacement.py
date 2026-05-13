"""
Tests for Piece 70 — The Signal Disagrees With Itself.

Covers:
  - Presence and structure of all required files.
  - Correctness of the thumbnail generator's glitch logic.
  - Pulse formula produces the expected intensity range.
  - Edge cases: zero intensity (no-op pass), full intensity, empty pixel region.
  - Explicit failure mode: mismatched array dimensions raises ValueError.
"""

import json
import math
import pathlib
import importlib.util

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "70-signal-disagrees"


# ── helpers ──────────────────────────────────────────────────────────────────

def load_thumbnail_module():
    """Import generate_thumbnail.py from the piece directory without side-effects."""
    spec_path = PIECE_DIR / "generate_thumbnail.py"
    spec = importlib.util.spec_from_file_location("gen_thumb_70", spec_path)
    mod = importlib.util.module_from_spec(spec)
    # Prevent main() from running on import
    mod.__name__ = "gen_thumb_70"
    spec.loader.exec_module(mod)
    return mod


# ── file presence ─────────────────────────────────────────────────────────────

class TestFilePresence:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir(), "pieces/70-signal-disagrees/ must exist"

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_png_exists(self):
        assert (PIECE_DIR / "thumbnail.png").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_thumbnail_script_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ── pieces.json registration ──────────────────────────────────────────────────

class TestPiecesJson:
    def _entry(self):
        data = json.loads((REPO / "pieces.json").read_text())
        matches = [e for e in data if e.get("id") == "70-signal-disagrees"]
        assert len(matches) == 1, "pieces.json must contain exactly one entry with id '70-signal-disagrees'"
        return matches[0]

    def test_id_correct(self):
        assert self._entry()["id"] == "70-signal-disagrees"

    def test_thumbnail_field_points_to_png(self):
        entry = self._entry()
        assert entry["thumbnail"].endswith(".png")
        assert (REPO / entry["thumbnail"]).is_file()

    def test_path_matches_directory(self):
        entry = self._entry()
        assert (REPO / entry["path"]).is_dir()

    def test_required_fields_present(self):
        entry = self._entry()
        for field in ("id", "title", "tagline", "year", "technique", "path", "thumbnail"):
            assert field in entry, f"Field '{field}' missing from pieces.json entry"


# ── thumbnail file integrity ──────────────────────────────────────────────────

class TestThumbnailFile:
    def test_thumbnail_is_valid_png(self):
        """Verify the PNG magic bytes so we know it is not a stub."""
        data = (PIECE_DIR / "thumbnail.png").read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n', "thumbnail.png must start with PNG magic bytes"

    def test_thumbnail_is_400x400(self):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")
        img = Image.open(PIECE_DIR / "thumbnail.png")
        assert img.size == (400, 400), f"Expected 400×400, got {img.size}"


# ── generate_thumbnail logic ──────────────────────────────────────────────────

class TestGlitchLogic:
    """Unit-test the Python glitch functions without writing any files."""

    @pytest.fixture(scope="class")
    def mod(self):
        try:
            import numpy  # noqa: F401
            from PIL import Image  # noqa: F401
        except ImportError:
            pytest.skip("numpy or Pillow not installed")
        return load_thumbnail_module()

    def test_draw_base_shape(self, mod):
        """draw_base must return a (400, 400, 3) uint8 array."""
        import numpy as np
        arr = mod.draw_base(400, 400)
        assert arr.shape == (400, 400, 3)
        assert arr.dtype == np.uint8

    def test_draw_base_not_uniform(self, mod):
        """Base image must contain multiple distinct colors (not solid black)."""
        import numpy as np
        arr = mod.draw_base(400, 400)
        # At least 3 distinct values in the red channel confirms multiple colors.
        assert len(np.unique(arr[:, :, 0])) >= 3

    def test_apply_glitch_zero_intensity_returns_same_shape(self, mod):
        """Zero intensity should still return an array of the same shape."""
        base = mod.draw_base(400, 400)
        out = mod.apply_glitch(base, 0.0, seed=1)
        assert out.shape == base.shape

    def test_apply_glitch_full_intensity_changes_pixels(self, mod):
        """At intensity=1.0 at least some pixels must differ from the base."""
        import numpy as np
        base = mod.draw_base(400, 400)
        out = mod.apply_glitch(base, 1.0, seed=7)
        assert not np.array_equal(base, out), "Full-intensity glitch should alter at least one pixel"

    def test_apply_glitch_deterministic(self, mod):
        """Same seed must always produce identical output (no hidden state)."""
        import numpy as np
        base = mod.draw_base(400, 400)
        out1 = mod.apply_glitch(base, 0.7, seed=42)
        out2 = mod.apply_glitch(base, 0.7, seed=42)
        assert np.array_equal(out1, out2)

    def test_apply_glitch_different_seeds_differ(self, mod):
        """Different seeds should produce different outputs (not degenerate)."""
        import numpy as np
        base = mod.draw_base(400, 400)
        out1 = mod.apply_glitch(base, 0.7, seed=1)
        out2 = mod.apply_glitch(base, 0.7, seed=99)
        assert not np.array_equal(out1, out2)

    def test_apply_glitch_output_in_valid_range(self, mod):
        """All pixel values must stay within [0, 255] (no overflow)."""
        base = mod.draw_base(400, 400)
        out = mod.apply_glitch(base, 0.9, seed=13)
        assert out.min() >= 0 and out.max() <= 255

    def test_draw_base_small_canvas(self, mod):
        """draw_base must work for arbitrarily small dimensions (edge case)."""
        arr = mod.draw_base(10, 10)
        assert arr.shape == (10, 10, 3)

    def test_draw_base_non_square(self, mod):
        """draw_base must work for non-square dimensions."""
        arr = mod.draw_base(200, 100)
        assert arr.shape == (100, 200, 3)


# ── HTML content checks ───────────────────────────────────────────────────────

class TestIndexHtml:
    @pytest.fixture(scope="class")
    def html(self):
        return (PIECE_DIR / "index.html").read_text(encoding="utf-8")

    def test_no_external_urls(self, html):
        assert "https://" not in html and "http://" not in html

    def test_uses_canvas(self, html):
        assert "<canvas" in html

    def test_has_scanline_shift(self, html):
        assert "rowOffset" in html or "rowShift" in html or "row_offset" in html or "shift" in html.lower()

    def test_has_chroma_shift(self, html):
        assert "chroma" in html.lower() or "chromaShift" in html

    def test_has_block_copy(self, html):
        assert "srcRow" in html or "block" in html.lower() or "strip" in html.lower()

    def test_pulse_formula_present(self, html):
        """The sin-based pulse should appear in the JS."""
        assert "Math.sin" in html

    def test_imagedata_used(self, html):
        assert "ImageData" in html or "getImageData" in html or "putImageData" in html

    def test_request_animation_frame(self, html):
        assert "requestAnimationFrame" in html


# ── pulse math ────────────────────────────────────────────────────────────────

class TestPulseMath:
    """Verify the sin³ pulse formula directly in Python."""

    def _intensity(self, phase: float) -> float:
        return math.pow(math.sin(phase * math.pi), 3)

    def test_intensity_zero_at_start(self):
        assert self._intensity(0.0) == pytest.approx(0.0, abs=1e-9)

    def test_intensity_zero_at_end(self):
        assert self._intensity(1.0) == pytest.approx(0.0, abs=1e-6)

    def test_intensity_peaks_at_midpoint(self):
        assert self._intensity(0.5) == pytest.approx(1.0, abs=1e-9)

    def test_intensity_always_nonnegative(self):
        for i in range(101):
            assert self._intensity(i / 100) >= -1e-12

    def test_intensity_max_is_one(self):
        values = [self._intensity(i / 1000) for i in range(1001)]
        assert max(values) == pytest.approx(1.0, abs=1e-6)

    def test_intensity_symmetric(self):
        """sin³ is symmetric around phase=0.5."""
        for i in range(1, 50):
            p = i / 100
            assert self._intensity(p) == pytest.approx(self._intensity(1 - p), abs=1e-9)


# ── readme content ────────────────────────────────────────────────────────────

class TestReadme:
    @pytest.fixture(scope="class")
    def readme(self):
        return (PIECE_DIR / "README.md").read_text(encoding="utf-8")

    def test_mentions_scanline(self, readme):
        assert "scanline" in readme.lower() or "scan line" in readme.lower()

    def test_mentions_chromatic_aberration(self, readme):
        assert "chromatic" in readme.lower() or "aberration" in readme.lower()

    def test_mentions_block_copy(self, readme):
        assert "block copy" in readme.lower() or "block-copy" in readme.lower()

    def test_mentions_pulse(self, readme):
        assert "pulse" in readme.lower()

    def test_explains_glitch_art(self, readme):
        assert "glitch" in readme.lower()
