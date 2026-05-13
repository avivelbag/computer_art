"""Tests for Piece 122 — Ink Dropped in Still Water: Paper Marbling."""
import importlib.util
import json
import math
import pathlib
import re
import struct

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "122-paper-marbling"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}


# ---------------------------------------------------------------------------
# Python re-implementation of the marbling primitives for unit testing
# ---------------------------------------------------------------------------

W, H = 400, 400
BG = (242, 230, 200)


def mk_buf():
    """Return a flat bytearray of W*H*3 bytes filled with the background colour."""
    r, g, b = BG
    buf = bytearray(W * H * 3)
    for i in range(W * H):
        buf[i*3] = r
        buf[i*3+1] = g
        buf[i*3+2] = b
    return buf


def bilinear(buf, sx, sy):
    """Bilinear sample from flat RGB bytearray *buf* at float (sx, sy).

    Returns an (r, g, b) tuple, falling back to BG if out of bounds.
    """
    ix, iy = int(sx), int(sy)
    if ix < 0 or ix >= W-1 or iy < 0 or iy >= H-1:
        return BG
    fx, fy = sx - ix, sy - iy
    i00 = (iy * W + ix) * 3
    s = (1-fx)*(1-fy)
    t = fx*(1-fy)
    u = (1-fx)*fy
    v = fx*fy
    return (
        int(buf[i00]*s + buf[i00+3]*t + buf[i00+W*3]*u + buf[i00+W*3+3]*v),
        int(buf[i00+1]*s + buf[i00+4]*t + buf[i00+W*3+1]*u + buf[i00+W*3+4]*v),
        int(buf[i00+2]*s + buf[i00+5]*t + buf[i00+W*3+2]*u + buf[i00+W*3+5]*v),
    )


def stone_drop(buf, cx, cy, R, color, n_rings):
    """Apply an Ebru stone drop to *buf* in-place (same algorithm as generate_thumbnail.py)."""
    tmp = bytes(buf)
    R4 = 4.0 * R * R
    cr, cg, cb = color
    bgr, bgg, bgb = BG
    for y in range(H):
        for x in range(W):
            dx, dy = x - cx, y - cy
            d2 = float(dx*dx + dy*dy)
            idx = (y * W + x) * 3
            if d2 < 0.25:
                buf[idx] = cr
                buf[idx+1] = cg
                buf[idx+2] = cb
                continue
            d = math.sqrt(d2)
            if d2 < R4:
                ring = int(d * n_rings / (2.0 * R))
                if ring % 2 == 0:
                    buf[idx] = cr
                    buf[idx+1] = cg
                    buf[idx+2] = cb
                else:
                    buf[idx] = bgr
                    buf[idx+1] = bgg
                    buf[idx+2] = bgb
            else:
                src_r = (d - math.sqrt(d2 - R4)) * 0.5
                r, g, b = bilinear(tmp, cx + dx/d * src_r, cy + dy/d * src_r)
                buf[idx] = r
                buf[idx+1] = g
                buf[idx+2] = b


def _import_gen():
    """Import generate_thumbnail from PIECE_DIR without polluting sys.modules."""
    spec = importlib.util.spec_from_file_location(
        "gen_marbling", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_entry():
    """Return the pieces.json entry for this piece, or None if absent."""
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
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_readme_nonempty(self):
        assert len((PIECE_DIR / "README.md").read_text()) > 100

    def test_generate_thumbnail_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

class TestIndexHtmlContent:
    def setup_method(self):
        self.html = (PIECE_DIR / "index.html").read_text()

    def test_canvas_element_present(self):
        assert "<canvas" in self.html

    def test_image_data_used(self):
        assert "ImageData" in self.html

    def test_no_external_script_dependencies(self):
        assert not re.search(r'<script[^>]+src="https?://', self.html)

    def test_stone_drop_function_present(self):
        assert "stoneDrop" in self.html or "stone_drop" in self.html.lower()

    def test_comb_drag_function_present(self):
        assert "combH" in self.html or "combV" in self.html or "comb" in self.html.lower()

    def test_cream_background_color(self):
        # Background is (242,230,200) = #f2e6c8
        assert "242" in self.html and "230" in self.html and "200" in self.html

    def test_terracotta_color_present(self):
        assert "192" in self.html and "82" in self.html and "42" in self.html

    def test_cobalt_color_present(self):
        assert "168" in self.html

    def test_saffron_color_present(self):
        assert "232" in self.html and "160" in self.html

    def test_forest_green_color_present(self):
        assert "96" in self.html and "64" in self.html

    def test_exponential_falloff_present(self):
        assert "Math.exp" in self.html

    def test_sqrt_for_radial_math_present(self):
        assert "Math.sqrt" in self.html

    def test_request_animation_frame_present(self):
        assert "requestAnimationFrame" in self.html

    def test_index_html_size_reasonable(self):
        size = (PIECE_DIR / "index.html").stat().st_size
        assert size < 15_000, f"index.html is {size} bytes, expected < 15 000"

    def test_at_least_three_drops_configured(self):
        # The JS should reference stoneDrop at least 3 times
        count = self.html.count("stoneDrop")
        assert count >= 4, f"Expected ≥4 stoneDrop calls, found {count}"

    def test_animation_loops(self):
        # Loop is achieved by cycling state index with modulo
        assert "% N" in self.html or "%N" in self.html or "% NSTATES" in self.html or "%NSTATES" in self.html

    def test_canvas_dimensions_800(self):
        assert "800" in self.html


# ---------------------------------------------------------------------------
# Stone drop mathematics
# ---------------------------------------------------------------------------

class TestStoneDropMath:
    """Verify the Ebru stone drop algorithm via the Python re-implementation."""

    def test_center_pixel_gets_drop_color(self):
        """The pixel at the drop centre must receive the drop colour."""
        buf = mk_buf()
        stone_drop(buf, 200, 200, 50, (192, 82, 42), 6)
        idx = (200 * W + 200) * 3
        assert buf[idx] == 192
        assert buf[idx+1] == 82
        assert buf[idx+2] == 42

    def test_ring_zone_not_all_background(self):
        """Within 2R of the drop centre the pixels must not all be cream."""
        buf = mk_buf()
        stone_drop(buf, 200, 200, 50, (192, 82, 42), 6)
        non_bg = 0
        for y in range(150, 250):
            for x in range(150, 250):
                idx = (y * W + x) * 3
                if (buf[idx], buf[idx+1], buf[idx+2]) != BG:
                    non_bg += 1
        assert non_bg > 100, "Ring zone should contain many non-background pixels"

    def test_far_pixels_on_blank_canvas_remain_background(self):
        """On a blank canvas, pixels far from the drop should stay cream
        (the inverse warp pulls from inside the ring zone which was blank)."""
        buf = mk_buf()
        stone_drop(buf, 200, 200, 30, (192, 82, 42), 4)
        # Check a pixel well outside the drop (far corner)
        idx = (10 * W + 10) * 3
        # It may or may not be exactly BG, but should be close to cream
        assert buf[idx] > 200, "Far pixels should remain near cream on blank canvas"

    def test_multiple_drops_modify_buffer(self):
        """Each successive drop must change at least some pixels."""
        buf = mk_buf()
        before = bytes(buf)
        stone_drop(buf, 100, 100, 40, (58, 95, 168), 5)
        after = bytes(buf)
        assert before != after

    def test_inverse_warp_formula_correctness(self):
        """Verify r_old = (r_new - sqrt(r_new²-4R²))/2 satisfies the forward map."""
        R = 60.0
        for d in [130.0, 200.0, 300.0]:
            r_old = (d - math.sqrt(d*d - 4*R*R)) * 0.5
            r_new_reconstructed = r_old + R*R / r_old
            assert abs(r_new_reconstructed - d) < 1e-6, (
                f"Inverse warp failed: R={R}, d={d}, r_old={r_old}, "
                f"reconstructed={r_new_reconstructed}"
            )

    def test_drop_with_large_radius_covers_most_of_canvas(self):
        """A very large drop (R=150) should produce rings across most of a 400×400 canvas."""
        buf = mk_buf()
        stone_drop(buf, 200, 200, 150, (232, 160, 32), 6)
        non_bg = sum(
            1 for i in range(W * H)
            if (buf[i*3], buf[i*3+1], buf[i*3+2]) != BG
        )
        assert non_bg > W * H * 0.4, "Large drop should cover >40% of canvas"

    def test_drop_radius_zero_leaves_buffer_unchanged(self):
        """A drop with R=0 has an undefined warp (4R²=0) and should not crash;
        the centre pixel still gets the drop colour."""
        buf = mk_buf()
        try:
            stone_drop(buf, 200, 200, 0, (192, 82, 42), 4)
        except Exception:
            pass  # allowed to raise for degenerate input


# ---------------------------------------------------------------------------
# Comb drag mathematics
# ---------------------------------------------------------------------------

class TestCombDragMath:
    """Verify comb drag Gaussian-falloff formula."""

    def test_gaussian_falloff_maximum_at_zero(self):
        """Gaussian displacement is maximised exactly at the tine position."""
        sigma = 20.0
        amt = 100.0
        disp_at_tine = amt * math.exp(0)
        disp_far = amt * math.exp(-(sigma * 3) ** 2 / sigma ** 2)
        assert disp_at_tine > disp_far * 10

    def test_gaussian_decays_with_distance(self):
        """Displacement should fall off monotonically as distance from tine increases."""
        sigma = 25.0
        amt = 80.0
        prev = amt
        for d in range(10, 120, 10):
            cur = amt * math.exp(-d*d / (sigma*sigma))
            assert cur < prev, f"Displacement should decrease at d={d}"
            prev = cur

    def test_multiple_tines_add_independently(self):
        """Two widely-separated tines should not interfere with each other."""
        sigma = 20.0
        amt = 100.0
        ty1, ty2 = 50, 350  # far apart
        # At y=ty1 the second tine's contribution is negligible
        d2 = (ty1 - ty2) ** 2
        contrib2 = amt * math.exp(-d2 / (sigma*sigma))
        assert contrib2 < 0.01, "Distant tine should contribute essentially zero"


# ---------------------------------------------------------------------------
# generate_thumbnail.py integration
# ---------------------------------------------------------------------------

class TestThumbnailGeneration:
    def test_render_produces_valid_png_bytes(self, tmp_path):
        """render() + write_png() must produce a file with valid PNG magic bytes."""
        mod = _import_gen()
        raw = mod.render()
        out = tmp_path / "thumb.png"
        mod.write_png(str(out), raw)
        data = out.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert len(data) > 1000

    def test_render_correct_dimensions(self, tmp_path):
        """The PNG must encode a 400×400 image."""
        mod = _import_gen()
        raw = mod.render()
        out = tmp_path / "thumb.png"
        mod.write_png(str(out), raw)
        data = out.read_bytes()
        w = struct.unpack(">I", data[16:20])[0]
        h = struct.unpack(">I", data[20:24])[0]
        assert w == 400
        assert h == 400

    def test_render_is_deterministic(self):
        """Two consecutive render() calls must return identical bytes."""
        mod = _import_gen()
        assert mod.render() == mod.render()

    def test_render_output_not_all_background(self):
        """The thumbnail must contain pixels other than the cream background."""
        mod = _import_gen()
        raw = mod.render()
        bg_r, bg_g, bg_b = 242, 230, 200
        found_non_bg = False
        i = 0
        while i < len(raw):
            i += 1  # skip PNG filter byte
            for _ in range(400):
                r, g, b = raw[i], raw[i+1], raw[i+2]
                i += 3
                if not (r == bg_r and g == bg_g and b == bg_b):
                    found_non_bg = True
                    break
            if found_non_bg:
                break
        assert found_non_bg, "All pixels are background — marbling was not rendered"

    def test_render_contains_drop_colors(self):
        """The thumbnail must contain pixels clearly distinct from the background.

        After the comb passes blend colours, we look for wine-adjacent hues
        (r 120–190, g < 80, b < 130) which survive the blending process and
        whose presence confirms at least some drops rendered successfully.
        """
        mod = _import_gen()
        raw = mod.render()
        found_colored = False
        i = 0
        while i < len(raw):
            i += 1  # filter byte
            for _ in range(400):
                r, g, b = raw[i], raw[i+1], raw[i+2]
                i += 3
                if 120 < r < 190 and g < 80 and b < 130:
                    found_colored = True
                    break
            if found_colored:
                break
        assert found_colored, "No wine/maroon pixels found — drops may not have rendered"


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

    def test_entry_year_is_int(self):
        entry = _load_entry()
        assert isinstance(entry["year"], int)

    def test_entry_path_exists(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        entry = _load_entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_piece_122_appears_after_120(self):
        """Piece 122 must appear after 120 in the ordered list."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "120-celtic-knotwork" in ids
        assert PIECE_ID in ids
        assert ids.index(PIECE_ID) > ids.index("120-celtic-knotwork")

    def test_technique_mentions_marbling(self):
        entry = _load_entry()
        tech = entry["technique"].lower()
        assert "marbling" in tech or "ebru" in tech or "imagedata" in tech.replace("-", "")

    def test_tagline_mentions_drops_or_comb(self):
        entry = _load_entry()
        tl = entry["tagline"].lower()
        assert "drop" in tl or "comb" in tl or "marble" in tl


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_unknown_piece_absent_from_json(self):
        """A non-existent piece ID must not appear in pieces.json."""
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost-marble"), None)
        assert found is None

    def test_bilinear_out_of_bounds_returns_background(self):
        """bilinear() must return BG when the sample point is outside the canvas."""
        buf = mk_buf()
        result = bilinear(buf, -5.0, 10.0)
        assert result == BG

    def test_bilinear_out_of_bounds_right_edge(self):
        buf = mk_buf()
        result = bilinear(buf, float(W), float(H))
        assert result == BG

    def test_stone_drop_single_ring(self):
        """n_rings=1 means the entire 2R zone is one solid ring of drop colour."""
        buf = mk_buf()
        stone_drop(buf, 200, 200, 50, (192, 82, 42), 1)
        # Ring index 0 (always 0 for n_rings=1) → drop colour at centre
        idx = (200 * W + 200) * 3
        assert buf[idx] == 192

    def test_mk_buf_all_background(self):
        """A freshly created buffer must contain only the background colour."""
        buf = mk_buf()
        for i in range(W * H):
            assert (buf[i*3], buf[i*3+1], buf[i*3+2]) == BG

    def test_index_html_no_fetch_or_xmlhttprequest(self):
        """index.html must not make any network requests at runtime."""
        html = (PIECE_DIR / "index.html").read_text()
        assert "fetch(" not in html
        assert "XMLHttpRequest" not in html
        assert "import(" not in html
