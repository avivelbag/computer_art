"""Tests for Piece 101 — SDF Metaballs."""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "101-sdf-metaballs"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}


def _load_entry():
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == PIECE_ID), None)


class TestFiles:
    """All required files must exist and be non-trivially sized."""

    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_index_html_nonempty(self):
        assert len((PIECE_DIR / "index.html").read_text()) > 200

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()


class TestIndexHtmlContent:
    """index.html must implement the SDF metaball canvas animation."""

    def setup_method(self):
        self.html = (PIECE_DIR / "index.html").read_text()

    def test_canvas_element_present(self):
        assert "<canvas" in self.html

    def test_animation_loop_present(self):
        assert "requestAnimationFrame" in self.html

    def test_imagdata_creation_present(self):
        assert "createImageData" in self.html

    def test_sdf_sqrt_present(self):
        assert "Math.sqrt" in self.html

    def test_lissajous_sin_present(self):
        assert "Math.sin" in self.html

    def test_canvas_pixel_grid_at_most_300(self):
        """Canvas width/height attributes must be ≤ 300 for performance."""
        sizes = [int(m) for m in re.findall(r'<canvas[^>]+width="(\d+)"', self.html)]
        assert sizes, "No <canvas width=…> found"
        assert all(s <= 300 for s in sizes), f"Canvas too large: {sizes}"

    def test_threshold_constant_defined(self):
        assert "THR" in self.html or "THRESHOLD" in self.html or "threshold" in self.html.lower()

    def test_at_least_six_balls_defined(self):
        """The BALLS array must contain ≥ 6 entries."""
        matches = re.findall(r"\{[^}]*\bphx\b[^}]*\}", self.html)
        assert len(matches) >= 6, f"Expected ≥6 ball objects, found {len(matches)}"

    def test_irrational_frequency_constants_present(self):
        """PHI or √2/√3 constants must be present for irrational frequencies."""
        has_phi = "PHI" in self.html or "1.618" in self.html
        has_s2 = "S2" in self.html or "1.4142" in self.html
        assert has_phi or has_s2

    def test_finite_difference_gradient_present(self):
        """Specular relies on finite-difference gradient — EPS offset must appear."""
        assert "EPS" in self.html or "+ EPS" in self.html or "+ eps" in self.html.lower()


class TestThumbnail:
    """thumbnail.svg must be well-formed SVG at 400×400."""

    def test_is_valid_svg(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text().strip()
        assert content.startswith("<svg") or content.startswith("<?xml")

    def test_has_400_dimension(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "400" in content

    def test_nonempty(self):
        assert len((PIECE_DIR / "thumbnail.svg").read_text()) > 100

    def test_contains_radial_gradient(self):
        """Thumbnail must use a radialGradient for the violet→cyan blobscape look."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "radialGradient" in content


class TestPiecesJson:
    """pieces.json must contain a complete, correct entry for Piece 101."""

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


class TestEdgeCases:
    """Edge cases and explicit failure-mode assertions."""

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

    def test_unknown_piece_id_returns_none(self):
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost"), None)
        assert found is None

    def test_nonexistent_piece_directory_is_not_dir(self, tmp_path):
        ghost = tmp_path / "pieces" / "ghost-piece"
        assert not ghost.is_dir()

    def test_pieces_json_is_a_list(self):
        data = json.loads(PIECES_JSON.read_text())
        assert isinstance(data, list)
        assert len(data) > 0

    def test_empty_entry_fails_required_fields(self):
        assert not (REQUIRED_FIELDS <= {}.keys())
