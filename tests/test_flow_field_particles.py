"""Tests for Piece 115 — The Field Remembers: Flow Field Particle Trails."""
import json
import math
import pathlib
import random
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "115-the-field-remembers"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

# ---------------------------------------------------------------------------
# Python re-implementation of generate_thumbnail helpers for unit testing
# ---------------------------------------------------------------------------

_F2 = 0.5 * (math.sqrt(3) - 1)
_G2 = (3 - math.sqrt(3)) / 6
_GRAD2 = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]


def build_perm(seed):
    """Return a 512-entry permutation table seeded deterministically."""
    rng = random.Random(seed)
    p = list(range(256))
    rng.shuffle(p)
    return [p[i & 255] for i in range(512)]


def noise2d(xin, yin, perm):
    """2D simplex noise returning a value in approximately [-1, 1]."""
    s = (xin + yin) * _F2
    i = math.floor(xin + s)
    j = math.floor(yin + s)
    t = (i + j) * _G2
    x0 = xin - (i - t)
    y0 = yin - (j - t)
    i1, j1 = (1, 0) if x0 > y0 else (0, 1)
    x1 = x0 - i1 + _G2
    y1 = y0 - j1 + _G2
    x2 = x0 - 1 + 2 * _G2
    y2 = y0 - 1 + 2 * _G2
    ii = i & 255
    jj = j & 255
    g0 = perm[ii + perm[jj]] % 8
    g1 = perm[ii + i1 + perm[jj + j1]] % 8
    g2 = perm[ii + 1 + perm[jj + 1]] % 8
    n = 0.0
    t0 = 0.5 - x0 * x0 - y0 * y0
    if t0 >= 0:
        t0 *= t0
        n += t0 * t0 * (_GRAD2[g0][0] * x0 + _GRAD2[g0][1] * y0)
    t1 = 0.5 - x1 * x1 - y1 * y1
    if t1 >= 0:
        t1 *= t1
        n += t1 * t1 * (_GRAD2[g1][0] * x1 + _GRAD2[g1][1] * y1)
    t2 = 0.5 - x2 * x2 - y2 * y2
    if t2 >= 0:
        t2 *= t2
        n += t2 * t2 * (_GRAD2[g2][0] * x2 + _GRAD2[g2][1] * y2)
    return 70 * n


def _load_entry():
    """Return the pieces.json entry for piece 115, or None if absent."""
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

    def test_thumbnail_png_exists(self):
        assert (PIECE_DIR / "thumbnail.png").is_file()

    def test_thumbnail_png_is_valid_png(self):
        data = (PIECE_DIR / "thumbnail.png").read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n', "File does not begin with PNG magic bytes"

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_readme_nonempty(self):
        assert len((PIECE_DIR / "README.md").read_text()) > 100

    def test_generate_thumbnail_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# index.html content
# ---------------------------------------------------------------------------

class TestIndexHtmlContent:
    def setup_method(self):
        self.html = (PIECE_DIR / "index.html").read_text()

    def test_canvas_element_present(self):
        assert "<canvas" in self.html

    def test_request_animation_frame_present(self):
        assert "requestAnimationFrame" in self.html

    def test_no_external_script_dependencies(self):
        assert not re.search(r'<script[^>]+src="https?://', self.html)

    def test_particle_count_in_3000_to_6000_range(self):
        """N constant must fall between 3000 and 6000 per the acceptance criteria."""
        matches = [int(m) for m in re.findall(r'\bN\s*=\s*(\d+)', self.html)]
        assert matches, "No N = <number> assignment found in HTML"
        assert any(3000 <= v <= 6000 for v in matches), f"Particle count {matches} outside [3000, 6000]"

    def test_cream_background_color(self):
        assert "f2ede4" in self.html.lower()

    def test_navy_ink_color(self):
        assert "1a2744" in self.html.lower()

    def test_rust_ink_color(self):
        assert "c0392b" in self.html.lower()

    def test_sage_ink_color(self):
        assert "4a7c59" in self.html.lower()

    def test_clear_interval_around_600(self):
        """Canvas must be cleared periodically; interval should be ~600 frames."""
        assert re.search(r'\b[56]\d{2}\b', self.html), "Expected clear interval near 600 frames"

    def test_noise_function_defined(self):
        assert "function noise" in self.html

    def test_cos_sin_used_for_particle_step(self):
        assert "Math.cos" in self.html and "Math.sin" in self.html

    def test_wrap_at_canvas_edges(self):
        """Particles must wrap toroidally using modulo arithmetic."""
        assert re.search(r'\+\s*W\s*\)\s*%\s*W', self.html)
        assert re.search(r'\+\s*H\s*\)\s*%\s*H', self.html)

    def test_canvas_dimensions(self):
        assert "800" in self.html and "500" in self.html

    def test_simplex_noise_constants_present(self):
        """F2 and G2 are the skewing factors unique to 2D simplex noise."""
        assert "sqrt(3)" in self.html

    def test_permutation_table_present(self):
        assert "perm" in self.html or "_pm" in self.html or "_perm" in self.html


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

    def test_technique_is_exact(self):
        entry = _load_entry()
        assert entry["technique"] == "canvas / flow field / Perlin noise / particle trails"

    def test_entry_year_is_int(self):
        entry = _load_entry()
        assert isinstance(entry["year"], int)

    def test_entry_path_exists(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        entry = _load_entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_piece_115_appears_after_113(self):
        """Piece 115 must appear after 113 in the ordered list."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "113-boids-flocking" in ids
        assert PIECE_ID in ids
        assert ids.index(PIECE_ID) > ids.index("113-boids-flocking")


# ---------------------------------------------------------------------------
# Noise math (Python re-implementation)
# ---------------------------------------------------------------------------

class TestNoiseMath:
    def setup_method(self):
        self.perm = build_perm(42)

    def test_output_within_plausible_range(self):
        """Simplex noise must stay within [-1, 1] for a range of inputs."""
        samples = [
            noise2d(x * 0.01, y * 0.01, self.perm)
            for x in range(0, 100, 5)
            for y in range(0, 100, 5)
        ]
        for v in samples:
            assert -1.1 <= v <= 1.1, f"Noise value {v} outside expected [-1, 1]"

    def test_different_positions_give_different_values(self):
        v1 = noise2d(1.0, 1.0, self.perm)
        v2 = noise2d(10.0, 10.0, self.perm)
        assert v1 != v2, "Noise must vary across space"

    def test_time_shift_changes_value(self):
        """Shifting the y-coordinate simulates temporal evolution of the field."""
        v1 = noise2d(5.0, 5.0, self.perm)
        v2 = noise2d(5.0, 5.05, self.perm)
        assert v1 != v2

    def test_zero_input_returns_float(self):
        v = noise2d(0.0, 0.0, self.perm)
        assert isinstance(v, float)

    def test_deterministic_with_same_perm(self):
        """Same perm table must produce identical outputs."""
        perm2 = build_perm(42)
        assert noise2d(3.14, 2.71, self.perm) == noise2d(3.14, 2.71, perm2)

    def test_different_seeds_give_different_fields(self):
        perm_a = build_perm(1)
        perm_b = build_perm(2)
        v_a = noise2d(5.0, 5.0, perm_a)
        v_b = noise2d(5.0, 5.0, perm_b)
        assert v_a != v_b, "Different seeds must produce different noise fields"


# ---------------------------------------------------------------------------
# Thumbnail generation
# ---------------------------------------------------------------------------

class TestThumbnailGeneration:
    def _import_gen(self):
        """Import generate_thumbnail from PIECE_DIR, bypassing sys.modules cache."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "generate_thumbnail_115", PIECE_DIR / "generate_thumbnail.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_generate_thumbnail_produces_valid_png(self, tmp_path):
        """Running generate_thumbnail.py's render() must produce valid PNG bytes."""
        mod = self._import_gen()
        raw = mod.render()
        out = tmp_path / "thumbnail.png"
        mod.write_png(str(out), raw)
        data = out.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        assert len(data) > 1000

    def test_generate_thumbnail_deterministic(self):
        """Calling render() twice must produce identical bytes."""
        mod = self._import_gen()
        a = mod.render()
        b = mod.render()
        assert a == b

    def test_generate_thumbnail_correct_dimensions(self, tmp_path):
        """The PNG must encode a 400×250 image."""
        import struct
        mod = self._import_gen()
        raw = mod.render()
        out = tmp_path / "thumb.png"
        mod.write_png(str(out), raw)
        data = out.read_bytes()
        # IHDR chunk: bytes 16-24 encode width and height as big-endian uint32
        w = struct.unpack('>I', data[16:20])[0]
        h = struct.unpack('>I', data[20:24])[0]
        assert w == 400
        assert h == 250


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_unknown_piece_absent_from_json(self):
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost-field"), None)
        assert found is None

    def test_noise_large_coordinates_does_not_crash(self):
        """Simplex noise must handle large positive inputs without error."""
        perm = build_perm(0)
        v = noise2d(1e6, 1e6, perm)
        assert isinstance(v, float)

    def test_noise_negative_coordinates(self):
        """Simplex noise must work correctly for negative input coordinates."""
        perm = build_perm(7)
        v = noise2d(-5.0, -3.0, perm)
        assert -1.1 <= v <= 1.1

    def test_build_perm_length(self):
        """Permutation table must be exactly 512 entries."""
        perm = build_perm(99)
        assert len(perm) == 512

    def test_build_perm_values_in_range(self):
        """All permutation values must be in [0, 255]."""
        perm = build_perm(13)
        assert all(0 <= v <= 255 for v in perm)

    def test_index_html_size_reasonable(self):
        """index.html must be under 10 KB (self-contained, no bloat)."""
        size = (PIECE_DIR / "index.html").stat().st_size
        assert size < 10_000, f"index.html is {size} bytes, expected < 10 000"
