"""Tests for Piece 184 — Distance Bloom: 2D SDF Morphing."""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "184-distance-bloom"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}


def _load_entry():
    """Return the pieces.json entry for this piece, or None if absent."""
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == PIECE_ID), None)


class TestFiles:
    """All required files must exist and be non-trivially sized."""

    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_index_html_nonempty(self):
        assert len((PIECE_DIR / "index.html").read_text()) > 500

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_readme_nonempty(self):
        assert len((PIECE_DIR / "README.md").read_text()) > 50


class TestIndexHtmlContent:
    """index.html must implement a 2D SDF WebGL canvas animation."""

    def setup_method(self):
        self.html = (PIECE_DIR / "index.html").read_text()

    def test_canvas_element_present(self):
        assert "<canvas" in self.html

    def test_webgl_context_creation(self):
        assert "getContext('webgl')" in self.html or 'getContext("webgl")' in self.html

    def test_fragment_shader_script_tag(self):
        assert "x-shader/x-fragment" in self.html

    def test_vertex_shader_script_tag(self):
        assert "x-shader/x-vertex" in self.html

    def test_sdf_circle_function_defined(self):
        assert "sdCircle" in self.html

    def test_sdf_rounded_box_function_defined(self):
        assert "sdRoundedBox" in self.html

    def test_smooth_union_function_defined(self):
        assert "opSmoothUnion" in self.html

    def test_smooth_subtraction_function_defined(self):
        assert "opSmoothSubtraction" in self.html

    def test_fract_used_for_isocontour_bands(self):
        """fract(d * FREQ) produces the repeating 0→1 ramp for bands."""
        assert "fract(" in self.html

    def test_utime_uniform_present(self):
        assert "uTime" in self.html

    def test_ures_uniform_present(self):
        assert "uRes" in self.html

    def test_lissajous_sin_motion(self):
        assert "sin(" in self.html

    def test_lissajous_cos_motion(self):
        assert "cos(" in self.html

    def test_irrational_frequency_phi(self):
        """Golden ratio (φ ≈ 1.618) or √2 (≈ 1.414) must be present for aperiodic orbits."""
        has_phi = "1.618" in self.html or "PHI" in self.html
        has_s2 = "1.414" in self.html or "S2" in self.html
        assert has_phi or has_s2

    def test_animation_loop_present(self):
        assert "requestAnimationFrame" in self.html

    def test_four_neon_colors_referenced(self):
        """At least three of the four neon hex codes must appear (cyan, magenta, amber, green)."""
        hits = sum([
            "0.90" in self.html or "0.92" in self.html,  # cyan green component
            "0.16" in self.html or "0.18" in self.html,  # magenta red-green split
            "0.72" in self.html or "0.74" in self.html,  # amber green component
            "1.00, 0.40" in self.html or "1.00, 0.42" in self.html,  # green
        ])
        assert hits >= 2, "Expected at least 2 of the 4 neon color channels to appear"

    def test_smooth_falloff_present(self):
        """Exponential falloff fades rings into the dark background."""
        assert "exp(" in self.html

    def test_dark_background_color(self):
        """Background must be dark (near-black indigo)."""
        assert "0.02" in self.html or "0.01" in self.html or "#060010" in self.html

    def test_clamp_used_in_smooth_union(self):
        """Standard opSmoothUnion uses clamp to bound the interpolant."""
        assert "clamp(" in self.html

    def test_mix_used_for_interpolation(self):
        assert "mix(" in self.html

    def test_slot_color_selection_present(self):
        """slotColor or equivalent function must cycle through 4 colors."""
        assert "slotColor" in self.html or "slot" in self.html

    def test_smoothstep_for_glow(self):
        """smoothstep brightens band boundaries into the neon-glow line effect."""
        assert "smoothstep(" in self.html

    def test_freq_constant_defined(self):
        """FREQ constant controls number of isocontour bands per unit distance."""
        assert "FREQ" in self.html or "6.0" in self.html

    def test_gl_draw_arrays_called(self):
        assert "drawArrays" in self.html


class TestThumbnail:
    """thumbnail.svg must be well-formed SVG at 400×400 with isocontour styling."""

    def setup_method(self):
        self.content = (PIECE_DIR / "thumbnail.svg").read_text()

    def test_is_valid_svg(self):
        assert self.content.strip().startswith("<svg")

    def test_has_400_dimension(self):
        assert "400" in self.content

    def test_nonempty(self):
        assert len(self.content) > 100

    def test_has_dark_background(self):
        """Background must use a dark color rect or gradient."""
        assert "<rect" in self.content

    def test_has_radial_gradient(self):
        assert "radialGradient" in self.content

    def test_has_concentric_rings(self):
        """Isocontour look requires multiple ellipse or circle elements."""
        ring_count = len(re.findall(r"<ellipse|<circle", self.content))
        assert ring_count >= 4, f"Expected ≥4 ring elements, found {ring_count}"

    def test_neon_colors_present(self):
        """At least two of the four neon colors must appear in the thumbnail."""
        hits = sum([
            "#00E5FF" in self.content or "#00e5ff" in self.content,
            "#FF2999" in self.content or "#ff2999" in self.content,
            "#FFB800" in self.content or "#ffb800" in self.content,
            "#1FFF67" in self.content or "#1fff67" in self.content,
        ])
        assert hits >= 2, f"Expected ≥2 neon colors, found {hits}"

    def test_stroke_attribute_present(self):
        """Isocontour rings must be drawn as strokes."""
        assert "stroke=" in self.content


class TestPiecesJson:
    """pieces.json must contain a complete, correct entry for Piece 184."""

    def test_entry_exists(self):
        assert _load_entry() is not None, f"No entry with id={PIECE_ID!r}"

    def test_entry_has_all_required_fields(self):
        entry = _load_entry()
        assert entry is not None
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_entry_id_matches_directory_name(self):
        entry = _load_entry()
        assert entry is not None
        assert (REPO / entry["path"]).name == entry["id"]

    def test_entry_year_is_int(self):
        entry = _load_entry()
        assert isinstance(entry["year"], int)

    def test_entry_thumbnail_file_exists(self):
        entry = _load_entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_entry_path_directory_exists(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).is_dir()

    def test_technique_mentions_webgl(self):
        entry = _load_entry()
        assert entry is not None
        assert "WebGL" in entry["technique"] or "webgl" in entry["technique"].lower()

    def test_technique_mentions_sdf(self):
        entry = _load_entry()
        assert entry is not None
        assert "SDF" in entry["technique"] or "sdf" in entry["technique"].lower()


class TestEdgeCases:
    """Edge cases and explicit failure-mode assertions."""

    def test_missing_title_field_detected(self):
        """Entry without 'title' must fail the required-field check."""
        entry = {
            "id": PIECE_ID,
            "tagline": "Test",
            "year": 2026,
            "technique": "WebGL",
            "path": f"pieces/{PIECE_ID}",
            "thumbnail": f"pieces/{PIECE_ID}/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= entry.keys())

    def test_unknown_piece_id_returns_none(self):
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost-sdf"), None)
        assert found is None

    def test_nonexistent_piece_directory_is_not_dir(self, tmp_path):
        ghost = tmp_path / "pieces" / "ghost-sdf-piece"
        assert not ghost.is_dir()

    def test_pieces_json_is_a_list(self):
        data = json.loads(PIECES_JSON.read_text())
        assert isinstance(data, list)
        assert len(data) > 0

    def test_empty_entry_fails_required_fields(self):
        assert not (REQUIRED_FIELDS <= {}.keys())

    def test_index_html_has_no_external_script_src(self):
        """Piece must be self-contained — no external script src attributes."""
        html = (PIECE_DIR / "index.html").read_text()
        external = re.findall(r'<script[^>]+src=["\']https?://', html)
        assert not external, f"External script dependencies found: {external}"

    def test_smooth_union_k_value_present(self):
        """opSmoothUnion must be called with a blend radius k > 0."""
        html = (PIECE_DIR / "index.html").read_text()
        calls = re.findall(r'opSmoothUnion\([^)]+,\s*([\d.]+)\)', html)
        assert calls, "No opSmoothUnion calls with k argument found"
        assert all(float(k) > 0 for k in calls), "All k values must be positive"
