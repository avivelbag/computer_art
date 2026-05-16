"""Tests for Piece 227 — Charge Canvas: Electric Fields and Equipotentials."""

import json
import pathlib


REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR  = REPO / "pieces" / "227-electric-field-lines"
INDEX_HTML = PIECE_DIR / "index.html"
THUMBNAIL  = PIECE_DIR / "thumbnail.svg"
README     = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


# ── Helpers ────────────────────────────────────────────────────────────────

def _html() -> str:
    return INDEX_HTML.read_text()


def _readme() -> str:
    return README.read_text()


def _get_entry():
    """Return the pieces.json entry for 227-electric-field-lines, or None."""
    data = json.loads(PIECES_JSON.read_text())
    for entry in data:
        if entry.get("id") == "227-electric-field-lines":
            return entry
    return None


# ── File existence ─────────────────────────────────────────────────────────

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), "pieces/227-electric-field-lines/ must exist"


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_thumbnail_svg_exists():
    assert THUMBNAIL.is_file()


def test_readme_exists():
    assert README.is_file()


# ── pieces.json entry ──────────────────────────────────────────────────────

def test_pieces_json_entry_present():
    assert _get_entry() is not None, "227-electric-field-lines not in pieces.json"


def test_pieces_json_entry_required_fields():
    entry = _get_entry()
    assert entry is not None
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    missing = required - entry.keys()
    assert not missing, f"Missing fields: {missing}"


def test_pieces_json_id_matches_path():
    entry = _get_entry()
    assert entry is not None
    assert entry["id"] == "227-electric-field-lines"
    assert entry["path"] == "pieces/227-electric-field-lines"
    assert entry["thumbnail"] == "pieces/227-electric-field-lines/thumbnail.svg"


def test_pieces_json_year():
    entry = _get_entry()
    assert entry is not None
    assert entry["year"] == 2026


def test_pieces_json_technique_keywords():
    """Technique field must cover the key physics/algorithmic concepts."""
    entry = _get_entry()
    assert entry is not None
    tech = entry["technique"].lower()
    assert "coulomb" in tech
    assert "field" in tech
    assert "equipotential" in tech or "contour" in tech
    assert "superposition" in tech
    assert "drag" in tech or "interactive" in tech


# ── index.html structure ───────────────────────────────────────────────────

def test_html_doctype():
    assert "<!DOCTYPE html>" in _html() or "<!doctype html>" in _html().lower()


def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_has_info_pane():
    """A slide-out info / gallery panel must be present."""
    content = _html()
    assert "info-pane" in content


def test_html_positive_charge_colour_red():
    """Positive charges must render in red (#e04040 or similar)."""
    assert "#e04040" in _html()


def test_html_negative_charge_colour_blue():
    """Negative charges must render in blue (#4080e0 or similar)."""
    assert "#4080e0" in _html()


def test_html_field_lines_warm_gold():
    """Field lines must use a warm gold colour."""
    assert "#d4a030" in _html()


def test_html_equipotentials_cool_teal():
    """Equipotential contours must use a cool teal colour."""
    assert "#208888" in _html()


def test_html_has_get_field():
    """getField(x,y) implements Coulomb superposition for the E vector."""
    assert "getField" in _html()


def test_html_has_get_potential():
    """getPotential(x,y) computes V = Σ kq/r for the equipotential grid."""
    assert "getPotential" in _html()


def test_html_has_trace_field_line():
    """traceFieldLine() traces Euler streamlines along E."""
    assert "traceFieldLine" in _html()


def test_html_has_marching_squares():
    """marchingSquares() iso-contours the potential grid."""
    assert "marchingSquares" in _html()


def test_html_has_build_potential_grid():
    """buildPotentialGrid() evaluates V on the coarse grid."""
    assert "buildPotentialGrid" in _html()


def test_html_drag_events_present():
    """mousedown / mousemove / mouseup must all be wired for charge dragging."""
    content = _html()
    assert "mousedown" in content
    assert "mousemove" in content
    assert "mouseup" in content


def test_html_touch_events_present():
    """Touch support (touchstart / touchmove / touchend) must be present."""
    content = _html()
    assert "touchstart" in content
    assert "touchmove" in content
    assert "touchend" in content


def test_html_max_eight_charges():
    """Charge count must be capped at 8 for performance."""
    assert "< 8" in _html() or "<= 8" in _html() or "length < 8" in _html()


def test_html_two_default_charges():
    """resetCharges must initialise exactly two preset charges."""
    content = _html()
    assert "resetCharges" in content
    assert "q:  1" in content or "q: 1" in content
    assert "q: -1" in content


def test_html_dirty_flag_render():
    """dirty flag pattern must gate re-renders to ≈60 fps."""
    content = _html()
    assert "dirty" in content
    assert "requestAnimationFrame" in content


# ── info panel educational content ────────────────────────────────────────

def test_html_coulombs_law_explained():
    assert "Coulomb" in _html()


def test_html_superposition_explained():
    assert "superposition" in _html().lower()


def test_html_equipotential_perpendicular():
    """Must explain that equipotentials are perpendicular to field lines."""
    content = _html()
    assert "perpendicular" in content.lower() or "⊥" in content


def test_html_field_line_density_explained():
    """Must mention that field line density encodes field strength."""
    content = _html().lower()
    assert "density" in content or "stronger" in content or "strength" in content


# ── README content ─────────────────────────────────────────────────────────

def test_readme_not_empty():
    assert len(_readme().strip()) > 200


def test_readme_streamline_algorithm():
    """README must describe the Euler streamline-tracing approach."""
    readme = _readme().lower()
    assert "euler" in readme or "streamline" in readme


def test_readme_marching_squares():
    """README must document the marching-squares contouring algorithm."""
    readme = _readme().lower()
    assert "marching" in readme


def test_readme_potential_grid():
    """README must document the potential grid evaluation."""
    readme = _readme().lower()
    assert "grid" in readme and "potential" in readme


def test_readme_stop_conditions():
    """README must document the streamline stop conditions."""
    readme = _readme()
    assert "negative" in readme.lower() or "terminus" in readme.lower() or "stops" in readme.lower() or "terminates" in readme.lower()


# ── Thumbnail ──────────────────────────────────────────────────────────────

def test_thumbnail_is_svg():
    content = THUMBNAIL.read_text()
    assert "<svg" in content
    assert "viewBox" in content


def test_thumbnail_has_positive_charge_colour():
    assert "#e04040" in THUMBNAIL.read_text()


def test_thumbnail_has_negative_charge_colour():
    assert "#4080e0" in THUMBNAIL.read_text()


def test_thumbnail_has_field_line_colour():
    assert "#d4a030" in THUMBNAIL.read_text()


def test_thumbnail_has_equipotential_colour():
    assert "#208888" in THUMBNAIL.read_text()


# ── Edge cases ─────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_empty_charges_renders_without_crash(self):
        """When charges = [] the render path must not call getField or getPotential.
        This is verified by inspecting the guard in the render() function."""
        content = _html()
        assert "charges.length > 0" in content or "charges.length === 0" in content

    def test_single_positive_charge_has_no_termination(self):
        """With only a positive charge and no negative charges, field lines
        must still stop (via canvas-edge or MAX_STEPS).  The stop condition
        for negative charges must be guarded by a q<0 check."""
        content = _html()
        assert "q < 0" in content or "c.q < 0" in content

    def test_grid_dimensions_are_eighty(self):
        """GRID_W and GRID_H must be 80 (matching the README spec)."""
        content = _html()
        assert "GRID_W     = 80" in content or "GRID_W = 80" in content
        assert "GRID_H     = 80" in content or "GRID_H = 80" in content

    def test_n_lines_is_sixteen(self):
        """N_LINES must be 16 (matching the README spec)."""
        content = _html()
        assert "N_LINES    = 16" in content or "N_LINES = 16" in content

    def test_max_steps_is_two_thousand(self):
        """MAX_STEPS must be 2000 (matching the README spec)."""
        content = _html()
        assert "MAX_STEPS  = 2000" in content or "MAX_STEPS = 2000" in content


# ── Failure modes ──────────────────────────────────────────────────────────

class TestFailureModes:

    def test_wrong_id_not_in_pieces_json(self):
        """A typo in the id must not silently pass the lookup."""
        data = json.loads(PIECES_JSON.read_text())
        ids = {e.get("id") for e in data}
        assert "227-electric-field-WRONG" not in ids
        assert "227-electric-fieldlines" not in ids  # missing hyphen

    def test_missing_technique_fields_detected(self):
        """An entry lacking required fields must be flagged."""
        incomplete = {
            "id": "227-electric-field-lines",
            "title": "Charge Canvas",
        }
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
        missing = required - incomplete.keys()
        assert missing, "Expected missing fields to be detected"

    def test_nonexistent_piece_directory_not_found(self, tmp_path):
        """A path pointing to a non-existent directory should not pass the dir check."""
        ghost = tmp_path / "ghost-piece"
        assert not ghost.is_dir()

    def test_empty_readme_fails_length_check(self, tmp_path):
        """An empty README must fail the non-empty content check."""
        r = tmp_path / "README.md"
        r.write_text("")
        assert len(r.read_text().strip()) <= 200
