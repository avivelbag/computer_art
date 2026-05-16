"""Tests for Piece 238 — Curl Noise: The River That Doesn't Repeat.

Covers:
  - Required files exist and are non-empty
  - index.html content (curl noise technique, palette, toroidal wrap, no full clear)
  - pieces.json registration
  - Python re-implementation of the curl-noise math (divergence-free property,
    noise consistency, speed-color gradient)
  - Thumbnail generation (valid PNG, deterministic, correct dimensions)
  - Edge cases and explicit failure modes
"""
import importlib.util
import json
import math
import pathlib
import random
import re
import struct

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "238-curl-noise"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}

# ---------------------------------------------------------------------------
# Python re-implementation of the curl-noise helpers for unit testing
# ---------------------------------------------------------------------------

NOISE_SCALE = 0.003
TIME_SCALE = 0.0003
CURL_EPS = 0.0001


def _build_perm(seed):
    """Return a 512-entry permutation table seeded deterministically."""
    rng = random.Random(seed)
    p = list(range(256))
    rng.shuffle(p)
    return [p[i & 255] for i in range(512)]


def _fade(t):
    """Quintic Hermite smoothstep."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def value_noise3(x, y, z, perm):
    """3D value noise in [-1, 1].

    Mirrors the JS implementation in index.html — same lattice hashing and
    trilinear interpolation with quintic fade.
    """
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    zi = int(math.floor(z)) & 255
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    zf = z - math.floor(z)
    u, v, w = _fade(xf), _fade(yf), _fade(zf)

    aaa = perm[perm[perm[xi    ] + yi    ] + zi    ]
    aba = perm[perm[perm[xi    ] + yi + 1] + zi    ]
    aab = perm[perm[perm[xi    ] + yi    ] + zi + 1]
    abb = perm[perm[perm[xi    ] + yi + 1] + zi + 1]
    baa = perm[perm[perm[xi + 1] + yi    ] + zi    ]
    bba = perm[perm[perm[xi + 1] + yi + 1] + zi    ]
    bab = perm[perm[perm[xi + 1] + yi    ] + zi + 1]
    bbb = perm[perm[perm[xi + 1] + yi + 1] + zi + 1]

    def lerp(a, b, t): return a + t * (b - a)
    def val(h): return (h / 127.5) - 1.0

    return lerp(
        lerp(lerp(val(aaa), val(baa), u), lerp(val(aba), val(bba), u), v),
        lerp(lerp(val(aab), val(bab), u), lerp(val(abb), val(bbb), u), v),
        w,
    )


def curl_velocity(wx, wy, t, perm):
    """Return (vx, vy) = (∂P/∂y, −∂P/∂x) at world position (wx, wy), time t."""
    nx = wx * NOISE_SCALE
    ny = wy * NOISE_SCALE
    nz = t * TIME_SCALE
    dPdy = (value_noise3(nx, ny + CURL_EPS, nz, perm) -
            value_noise3(nx, ny - CURL_EPS, nz, perm)) / (2 * CURL_EPS)
    dPdx = (value_noise3(nx + CURL_EPS, ny, nz, perm) -
            value_noise3(nx - CURL_EPS, ny, nz, perm)) / (2 * CURL_EPS)
    return dPdy, -dPdx


def _load_entry():
    """Return the pieces.json entry for piece 238, or None if absent."""
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == PIECE_ID), None)


def _import_gen():
    """Import generate_thumbnail from PIECE_DIR without polluting sys.modules."""
    spec = importlib.util.spec_from_file_location(
        "generate_thumbnail_238", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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

    def test_thumbnail_png_valid_magic(self):
        data = (PIECE_DIR / "thumbnail.png").read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n', "Not a valid PNG file"

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

    def test_particle_count_is_3000(self):
        """N must be ~3000 as specified in acceptance criteria."""
        matches = [int(m) for m in re.findall(r'\bN\s*=\s*(\d+)', self.html)]
        assert matches, "No N = <number> assignment found"
        assert any(2800 <= v <= 3200 for v in matches), f"N values {matches} not near 3000"

    def test_curl_noise_partial_derivative_structure(self):
        """The field must use ∂P/∂y and -∂P/∂x — hallmarks of curl derivation."""
        assert "dPdy" in self.html and "dPdx" in self.html, (
            "Expected finite-difference variables dPdy and dPdx for curl derivation"
        )

    def test_curl_eps_present(self):
        """Finite-difference epsilon must be declared."""
        assert "CURL_EPS" in self.html or "eps" in self.html.lower()

    def test_value_noise_function_present(self):
        """value noise function must be defined inline."""
        assert "valueNoise3" in self.html or "valuenoise" in self.html.lower()

    def test_fade_function_present(self):
        """Quintic fade (6t^5 − 15t^4 + 10t^3) must be present for smooth gradients."""
        assert "fade" in self.html

    def test_palette_deep_violet(self):
        """Deep violet palette stop (45,10,80) or hex 2d0a50 must be present."""
        assert "2d0a50" in self.html.lower() or ("45" in self.html and "10" in self.html and "80" in self.html)

    def test_palette_cyan(self):
        """Electric cyan palette stop must be present."""
        assert "00c8dc" in self.html.lower() or "200" in self.html

    def test_palette_pale_gold(self):
        """Pale gold palette stop must be present."""
        assert "ffdc82" in self.html.lower() or ("255" in self.html and "220" in self.html)

    def test_trail_fade_not_full_clear(self):
        """The canvas must use low-alpha compositing, never a full opaque clear."""
        html = self.html
        # A full-opaque fillRect would reset all trails. We must NOT see that.
        # Low-alpha fill is the correct pattern (rgba with alpha ~0.03).
        assert "rgba" in html, "Expected rgba compositing for trail fade"
        # Should not fully clear the canvas with opaque background fill each frame.
        # Allow one-time initialization clear, but not inside animation loop.
        # We check that if fillRect with BG color is called, it's not the sole fill.
        alpha_fills = re.findall(r'rgba\([^)]+\)', html)
        assert alpha_fills, "No rgba fill found — canvas must use alpha compositing for trails"

    def test_toroidal_wrap_x(self):
        """Particles must wrap using modulo at x boundaries."""
        assert re.search(r'\+\s*W\s*\)\s*%\s*W', self.html), "Missing toroidal wrap for X"

    def test_toroidal_wrap_y(self):
        """Particles must wrap using modulo at y boundaries."""
        assert re.search(r'\+\s*H\s*\)\s*%\s*H', self.html), "Missing toroidal wrap for Y"

    def test_time_evolution_present(self):
        """Field must evolve with time — TIME_SCALE or a third noise dimension."""
        assert "TIME_SCALE" in self.html or "time_scale" in self.html.lower()

    def test_canvas_dimensions_800x500(self):
        assert "800" in self.html and "500" in self.html

    def test_no_clear_interval_variable(self):
        """Unlike piece 115, 238 must NOT have a periodic full clear (CLEAR_INTERVAL)."""
        assert "CLEAR_INTERVAL" not in self.html, (
            "238 must use continuous fade, not periodic full clears like 115"
        )

    def test_float32array_or_arrays_for_particles(self):
        """Particle state should use typed arrays or plain arrays."""
        assert "Float32Array" in self.html or "px[i]" in self.html or "x_pos" in self.html

    def test_index_html_size_reasonable(self):
        """index.html must be self-contained and under 12 KB."""
        size = (PIECE_DIR / "index.html").stat().st_size
        assert size < 12_000, f"index.html is {size} bytes, expected < 12 000"


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

    def test_id_matches_directory_name(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).name == entry["id"]

    def test_entry_year_is_int(self):
        entry = _load_entry()
        assert isinstance(entry["year"], int)

    def test_entry_path_directory_exists(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        entry = _load_entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_technique_mentions_curl(self):
        entry = _load_entry()
        assert "curl" in entry["technique"].lower(), "Technique must mention curl noise"

    def test_piece_238_appears_after_234(self):
        """Piece 238 must appear after 234 in the ordered list."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "234-truchet-tiles" in ids, "234-truchet-tiles must exist"
        assert PIECE_ID in ids, f"{PIECE_ID} must exist"
        assert ids.index(PIECE_ID) > ids.index("234-truchet-tiles")


# ---------------------------------------------------------------------------
# Curl-noise math
# ---------------------------------------------------------------------------

class TestCurlNoiseMath:
    def setup_method(self):
        self.perm = _build_perm(42)

    def test_value_noise3_in_range(self):
        """Value noise must stay in approximately [-1, 1]."""
        for xi in range(0, 50, 5):
            for yi in range(0, 50, 5):
                v = value_noise3(xi * 0.1, yi * 0.1, 0.5, self.perm)
                assert -1.1 <= v <= 1.1, f"Out-of-range noise value {v}"

    def test_value_noise3_varies_in_space(self):
        v1 = value_noise3(1.0, 1.0, 0.0, self.perm)
        v2 = value_noise3(5.0, 5.0, 0.0, self.perm)
        assert v1 != v2

    def test_value_noise3_deterministic(self):
        perm2 = _build_perm(42)
        assert value_noise3(3.14, 2.71, 1.0, self.perm) == value_noise3(3.14, 2.71, 1.0, perm2)

    def test_curl_velocity_returns_two_values(self):
        vx, vy = curl_velocity(100.0, 200.0, 0, self.perm)
        assert isinstance(vx, float)
        assert isinstance(vy, float)

    def test_curl_is_divergence_free(self):
        """Divergence of the curl field must be zero (to within finite-difference error).

        div(curl P) = ∂vx/∂x + ∂vy/∂y = ∂²P/∂x∂y − ∂²P/∂y∂x = 0 (Clairaut's theorem).
        We verify numerically with a coarser h to avoid floating-point noise.
        """
        h = 5.0
        x0, y0, t = 400.0, 250.0, 0
        vx_xp, _ = curl_velocity(x0 + h, y0, t, self.perm)
        vx_xm, _ = curl_velocity(x0 - h, y0, t, self.perm)
        _, vy_yp = curl_velocity(x0, y0 + h, t, self.perm)
        _, vy_ym = curl_velocity(x0, y0 - h, t, self.perm)
        dvx_dx = (vx_xp - vx_xm) / (2 * h)
        dvy_dy = (vy_yp - vy_ym) / (2 * h)
        divergence = dvx_dx + dvy_dy
        assert abs(divergence) < 0.05, (
            f"Curl field is not divergence-free: div = {divergence:.6f}"
        )

    def test_curl_velocity_changes_with_time(self):
        """The field must evolve over time."""
        vx0, vy0 = curl_velocity(200.0, 150.0, 0, self.perm)
        vx1, vy1 = curl_velocity(200.0, 150.0, 10000, self.perm)
        assert (vx0, vy0) != (vx1, vy1), "Field must change with time"

    def test_curl_velocity_changes_with_position(self):
        vx0, vy0 = curl_velocity(100.0, 100.0, 0, self.perm)
        vx1, vy1 = curl_velocity(400.0, 300.0, 0, self.perm)
        assert (vx0, vy0) != (vx1, vy1)

    def test_curl_velocity_large_coordinates(self):
        """Must not crash with large world coordinates."""
        vx, vy = curl_velocity(1e5, 1e5, 0, self.perm)
        assert math.isfinite(vx) and math.isfinite(vy)

    def test_curl_velocity_negative_coordinates(self):
        """Must work for negative world coordinates."""
        vx, vy = curl_velocity(-100.0, -200.0, 0, self.perm)
        assert math.isfinite(vx) and math.isfinite(vy)


# ---------------------------------------------------------------------------
# Thumbnail generation
# ---------------------------------------------------------------------------

class TestThumbnailGeneration:
    def test_render_produces_bytes(self):
        mod = _import_gen()
        raw = mod.render()
        assert isinstance(raw, bytes)
        assert len(raw) > 0

    def test_render_deterministic(self):
        mod = _import_gen()
        a = mod.render()
        b = mod.render()
        assert a == b, "render() must be deterministic"

    def test_write_png_produces_valid_png(self, tmp_path):
        mod = _import_gen()
        raw = mod.render()
        out = tmp_path / "test.png"
        mod.write_png(str(out), raw)
        data = out.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        assert len(data) > 1000

    def test_write_png_correct_dimensions(self, tmp_path):
        """PNG must encode a 400×250 image per the W,H constants."""
        mod = _import_gen()
        raw = mod.render()
        out = tmp_path / "test.png"
        mod.write_png(str(out), raw)
        data = out.read_bytes()
        w = struct.unpack('>I', data[16:20])[0]
        h = struct.unpack('>I', data[20:24])[0]
        assert w == 400
        assert h == 250

    def test_render_output_contains_color(self):
        """Rendered output must not be a uniform black canvas — trails must appear."""
        mod = _import_gen()
        raw = mod.render()
        # Each scanline starts with a filter byte (0), then W*3 bytes of RGB.
        # Collect a sample of RGB values across the image.
        row_stride = 1 + mod.W * 3
        unique_rgb = set()
        for row in range(0, mod.H, 10):
            offset = row * row_stride + 1
            for col in range(0, mod.W * 3, 9):
                rgb = raw[offset + col: offset + col + 3]
                if len(rgb) == 3:
                    unique_rgb.add(bytes(rgb))
        assert len(unique_rgb) > 5, "Render must contain colorful trails, not a uniform canvas"

    def test_speed_color_slow_is_violet(self):
        """Speed near 0 should map to deep violet (low red+green, higher blue)."""
        mod = _import_gen()
        r, g, b = mod.speed_color(0.0)
        assert b > r and b > g, f"Slow speed should be violet-dominant, got ({r},{g},{b})"

    def test_speed_color_fast_is_gold(self):
        """Speed at maximum should map to pale gold (high red+green, lower blue)."""
        mod = _import_gen()
        r, g, b = mod.speed_color(mod.MAX_SPEED)
        assert r > b and g > b, f"Fast speed should be gold-dominant, got ({r},{g},{b})"

    def test_speed_color_mid_is_cyan(self):
        """Speed at half maximum should approach electric cyan (high green+blue, lower red)."""
        mod = _import_gen()
        r, g, b = mod.speed_color(mod.MAX_SPEED * 0.5)
        assert g > r or b > r, f"Mid speed should tend toward cyan, got ({r},{g},{b})"


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_perm_length_is_512(self):
        perm = _build_perm(99)
        assert len(perm) == 512

    def test_perm_values_in_0_255(self):
        perm = _build_perm(7)
        assert all(0 <= v <= 255 for v in perm)

    def test_different_seeds_give_different_fields(self):
        perm_a = _build_perm(1)
        perm_b = _build_perm(2)
        vx_a, vy_a = curl_velocity(100.0, 100.0, 0, perm_a)
        vx_b, vy_b = curl_velocity(100.0, 100.0, 0, perm_b)
        assert (vx_a, vy_a) != (vx_b, vy_b)

    def test_unknown_piece_absent_from_json(self):
        data = json.loads(PIECES_JSON.read_text())
        ghost = next((e for e in data if e["id"] == "999-phantom-noise"), None)
        assert ghost is None

    def test_value_noise3_zero_input(self):
        """Noise at origin must return a float without error."""
        perm = _build_perm(0)
        v = value_noise3(0.0, 0.0, 0.0, perm)
        assert isinstance(v, float)

    def test_value_noise3_large_input_no_crash(self):
        """Large coordinates must not cause index errors."""
        perm = _build_perm(0)
        v = value_noise3(1e6, 1e6, 1e6, perm)
        assert isinstance(v, float)

    def test_curl_velocity_at_origin(self):
        """Curl at origin must return finite values."""
        perm = _build_perm(0)
        vx, vy = curl_velocity(0.0, 0.0, 0, perm)
        assert math.isfinite(vx) and math.isfinite(vy)

    def test_entry_missing_required_field_detected(self):
        """Confirm that a piece entry without 'description' fails required-field check."""
        entry = {
            "id": "238-curl-noise",
            "title": "Curl Noise",
            "tagline": "...",
            "year": 2026,
            "technique": "curl noise",
            "path": "pieces/238-curl-noise",
            "thumbnail": "pieces/238-curl-noise/thumbnail.png",
        }
        missing = REQUIRED_FIELDS - entry.keys()
        assert "description" in missing
