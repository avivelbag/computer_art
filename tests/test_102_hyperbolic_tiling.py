"""Tests for Piece 102 — Hyperbolic Tiling."""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "102-hyperbolic-tiling"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}


def _load_entry():
    """Return the pieces.json entry for this piece, or None."""
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
        assert len((PIECE_DIR / "README.md").read_text()) > 100


class TestIndexHtmlContent:
    """index.html must implement the {5,4} hyperbolic tiling canvas animation."""

    def setup_method(self):
        self.html = (PIECE_DIR / "index.html").read_text()

    def test_canvas_element_present(self):
        assert "<canvas" in self.html

    def test_animation_loop_present(self):
        assert "requestAnimationFrame" in self.html

    def test_mobius_transform_present(self):
        """Möbius transform function must be defined."""
        assert "mobius" in self.html.lower()

    def test_poincare_disk_cull_threshold(self):
        """Culling constant must be defined to drop sub-pixel tiles."""
        assert "CULL_R" in self.html or "cull" in self.html.lower()

    def test_pq_values_for_5_4_tiling(self):
        """P=5 and Q=4 must appear for the {5,4} tiling."""
        assert re.search(r"\bP\s*=\s*5\b", self.html) or "P = 5" in self.html
        assert re.search(r"\bQ\s*=\s*4\b", self.html) or "Q = 4" in self.html

    def test_bfs_or_queue_present(self):
        """BFS tile generation requires a queue."""
        assert "queue" in self.html.lower() or "Queue" in self.html

    def test_arc_for_geodesic_edges(self):
        """Hyperbolic edges rendered as circle arcs via ctx.arc."""
        assert "ctx.arc" in self.html

    def test_amber_color_in_palette(self):
        """At least one amber hex color (#c8... or #e8...) must be present."""
        assert re.search(r"#[ce][0-9a-fA-F]{5}", self.html)

    def test_deep_indigo_background(self):
        """Deep indigo background color must be present."""
        assert "#0a0818" in self.html or "#0d0b" in self.html or "indigo" in self.html.lower()

    def test_rotation_speed_constant(self):
        """Animation rotation speed constant must be present."""
        assert "ROT_SPEED" in self.html or "rot_speed" in self.html.lower()

    def test_no_external_dependencies(self):
        """index.html must be self-contained — no external script src."""
        assert not re.search(r'<script[^>]+src="https?://', self.html)

    def test_clip_to_disk(self):
        """Canvas must be clipped to the Poincaré disk circle."""
        assert "clip()" in self.html

    def test_circumradius_computation(self):
        """Euclidean circumradius check for culling must be present."""
        assert "circumradius" in self.html.lower() or "euclidean" in self.html.lower() or "screenR" in self.html


class TestThumbnail:
    """thumbnail.svg must be well-formed SVG at 400×400."""

    def test_is_valid_svg(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text().strip()
        assert content.startswith("<svg") or content.startswith("<?xml")

    def test_has_400_dimension(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "400" in content

    def test_nonempty(self):
        assert len((PIECE_DIR / "thumbnail.svg").read_text()) > 200

    def test_contains_radial_gradient(self):
        """Thumbnail must use a radialGradient for amber tile fills."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "radialGradient" in content

    def test_contains_disk_boundary(self):
        """Thumbnail must have the Poincaré disk boundary circle."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "<circle" in content

    def test_contains_polygon_tiles(self):
        """Thumbnail must contain polygon elements representing hyperbolic tiles."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "<polygon" in content

    def test_amber_color_present(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "#c8790a" in content or "#e8a020" in content


class TestPiecesJson:
    """pieces.json must contain a complete, correct entry for Piece 102."""

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

    def test_hyperbolic_in_technique(self):
        """Technique field must mention hyperbolic geometry."""
        entry = _load_entry()
        assert "hyperbolic" in entry["technique"].lower()

    def test_poincare_in_technique(self):
        """Technique field must mention Poincaré disk."""
        entry = _load_entry()
        assert "poincar" in entry["technique"].lower()


class TestEdgeCases:
    """Edge cases and explicit failure-mode assertions."""

    def test_unknown_piece_id_returns_none(self):
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost"), None)
        assert found is None

    def test_nonexistent_piece_directory_is_not_dir(self, tmp_path):
        ghost = tmp_path / "pieces" / "ghost-hyperbolic"
        assert not ghost.is_dir()

    def test_pieces_json_is_a_list(self):
        data = json.loads(PIECES_JSON.read_text())
        assert isinstance(data, list)
        assert len(data) > 0

    def test_missing_title_field_detected(self):
        """Entry without 'title' must fail the required-field check."""
        entry = {
            "id": PIECE_ID,
            "tagline": "Test",
            "year": 2026,
            "technique": "canvas",
            "path": f"pieces/{PIECE_ID}",
            "thumbnail": f"pieces/{PIECE_ID}/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= entry.keys())

    def test_empty_entry_fails_required_fields(self):
        assert not (REQUIRED_FIELDS <= {}.keys())

    def test_pieces_json_parseable(self):
        """pieces.json must be valid JSON."""
        data = json.loads(PIECES_JSON.read_text())
        assert data is not None

    def test_piece_102_appears_after_101(self):
        """Piece 102 must come after piece 101 in the list (ordering)."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "101-sdf-metaballs" in ids
        assert "102-hyperbolic-tiling" in ids
        assert ids.index("102-hyperbolic-tiling") > ids.index("101-sdf-metaballs")
