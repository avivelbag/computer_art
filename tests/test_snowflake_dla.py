"""Tests for piece 291-crystalline — hexagonal DLA snowflake.

Validates the piece directory layout, pieces.json metadata, hex-grid math
used in the thumbnail generator, and the D6 symmetry logic.
"""
import json
import math
import pathlib
import sys

import importlib.util

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "291-crystalline"
PIECES_JSON = REPO / "pieces.json"

# ---------------------------------------------------------------------------
# Helpers imported from generate_thumbnail.py
# Load via importlib to avoid polluting sys.path for other test modules.
# ---------------------------------------------------------------------------

def _load_thumbnail_module():
    """Load generate_thumbnail.py from the piece directory without modifying sys.path."""
    spec = importlib.util.spec_from_file_location(
        "crystalline_generate_thumbnail",
        PIECE_DIR / "generate_thumbnail.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_thumb = _load_thumbnail_module()
hex_radius = _thumb.hex_radius
hex_to_pixel = _thumb.hex_to_pixel
hex_polygon_points = _thumb.hex_polygon_points
symmetry_set = _thumb.symmetry_set
build_snowflake = _thumb.build_snowflake


# ---------------------------------------------------------------------------
# Happy-path: piece directory structure
# ---------------------------------------------------------------------------

class TestPieceLayout:
    """Verify all required files are present in the piece directory."""

    def test_directory_exists(self):
        """The piece directory must exist."""
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        """index.html must be present."""
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_svg_exists(self):
        """thumbnail.svg must be present and non-empty."""
        thumb = PIECE_DIR / "thumbnail.svg"
        assert thumb.is_file()
        assert thumb.stat().st_size > 0

    def test_readme_exists(self):
        """README.md must be present."""
        assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# Happy-path: pieces.json registration
# ---------------------------------------------------------------------------

class TestPiecesJsonEntry:
    """Verify that 291-crystalline is correctly registered in pieces.json."""

    def _entry(self) -> dict:
        data = json.loads(PIECES_JSON.read_text())
        matches = [e for e in data if e.get("id") == "291-crystalline"]
        assert len(matches) == 1, "Expected exactly one entry with id=291-crystalline"
        return matches[0]

    def test_entry_present(self):
        """Entry with id '291-crystalline' must exist in pieces.json."""
        self._entry()

    def test_required_fields(self):
        """All required metadata fields must be present."""
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
        entry = self._entry()
        assert required <= entry.keys(), f"Missing fields: {required - entry.keys()}"

    def test_id_matches_path(self):
        """The id field must equal the last path component."""
        entry = self._entry()
        assert entry["id"] == pathlib.Path(entry["path"]).name

    def test_thumbnail_file_matches_entry(self):
        """The thumbnail path in pieces.json must point to an existing file."""
        entry = self._entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_year_is_int(self):
        """Year field must be an integer."""
        entry = self._entry()
        assert isinstance(entry["year"], int)

    def test_technique_mentions_hexagonal(self):
        """Technique field must reference the hexagonal grid."""
        entry = self._entry()
        assert "hexagonal" in entry["technique"].lower() or "hex" in entry["technique"].lower()

    def test_description_non_empty(self):
        """Description must be a non-empty string."""
        entry = self._entry()
        assert isinstance(entry["description"], str)
        assert len(entry["description"]) > 20


# ---------------------------------------------------------------------------
# Hex math: hex_radius
# ---------------------------------------------------------------------------

class TestHexRadius:
    """Verify the Chebyshev distance function in cube hex coordinates."""

    def test_origin_is_zero(self):
        assert hex_radius(0, 0) == 0

    def test_unit_neighbors(self):
        """All six immediate neighbors of the origin are at distance 1."""
        neighbors = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
        for q, r in neighbors:
            assert hex_radius(q, r) == 1, f"Expected radius 1 for {(q, r)}"

    def test_known_distance(self):
        """A cell at (3, -3) is at hex radius 3."""
        assert hex_radius(3, -3) == 3

    def test_large_cell(self):
        """hex_radius(10, 10) = max(10, 10, 20) = 20."""
        assert hex_radius(10, 10) == 20

    def test_symmetry_equivalents_share_radius(self):
        """All D6 images of a cell share the same hex radius."""
        q, r = 5, -2
        base_r = hex_radius(q, r)
        for cq, cr in symmetry_set(q, r):
            assert hex_radius(cq, cr) == base_r, (
                f"Symmetry image {(cq, cr)} has radius {hex_radius(cq, cr)}, expected {base_r}"
            )


# ---------------------------------------------------------------------------
# Hex math: hex_to_pixel
# ---------------------------------------------------------------------------

class TestHexToPixel:
    """Verify the axial-to-pixel conversion (pointy-top orientation)."""

    CX, CY = 200, 200
    SIZE = 5.0

    def test_origin_maps_to_canvas_center(self):
        """The hex origin (0, 0) must map exactly to the canvas centre."""
        px, py = hex_to_pixel(0, 0)
        assert abs(px - self.CX) < 1e-9
        assert abs(py - self.CY) < 1e-9

    def test_unit_q_step(self):
        """Moving one step in q shifts px by SIZE*sqrt(3) and leaves py unchanged."""
        px0, py0 = hex_to_pixel(0, 0)
        px1, py1 = hex_to_pixel(1, 0)
        assert abs(px1 - px0 - self.SIZE * math.sqrt(3)) < 1e-6
        assert abs(py1 - py0) < 1e-9

    def test_unit_r_step(self):
        """Moving one step in r shifts py by SIZE*1.5."""
        _, py0 = hex_to_pixel(0, 0)
        _, py1 = hex_to_pixel(0, 1)
        assert abs(py1 - py0 - self.SIZE * 1.5) < 1e-6


# ---------------------------------------------------------------------------
# D6 symmetry set
# ---------------------------------------------------------------------------

class TestSymmetrySet:
    """Verify the 12-element D6 orbit generation."""

    def test_origin_orbit_is_single_cell(self):
        """The origin (0, 0) maps to itself under all 12 D6 elements."""
        orbit = symmetry_set(0, 0)
        unique = set(orbit)
        assert unique == {(0, 0)}

    def test_general_position_has_12_distinct_cells(self):
        """A cell not on any symmetry axis must have exactly 12 distinct images."""
        orbit = symmetry_set(3, 1)
        assert len(set(orbit)) == 12, f"Expected 12 distinct cells, got {len(set(orbit))}"

    def test_orbit_is_closed_under_60deg_rotation(self):
        """Applying a 60° rotation to every orbit member should give the same set."""
        q, r = 4, -1

        def rotate60(q: int, r: int) -> tuple[int, int]:
            """Apply one 60° counter-clockwise rotation in axial coordinates."""
            return (-r, q + r)

        orbit = set(symmetry_set(q, r))
        rotated = {rotate60(cq, cr) for cq, cr in orbit}
        assert orbit == rotated, "Orbit is not closed under 60° rotation"

    def test_orbit_closed_under_reflection(self):
        """Applying the canonical reflection S: (q,r)→(q,-q-r) to every orbit
        member should return the same set."""
        q, r = 5, -2

        def reflect(q: int, r: int) -> tuple[int, int]:
            """Apply the canonical D6 reflection in axial coordinates."""
            return (q, -q - r)

        orbit = set(symmetry_set(q, r))
        reflected = {reflect(cq, cr) for cq, cr in orbit}
        assert orbit == reflected, "Orbit is not closed under reflection"

    def test_all_orbit_cells_have_same_hex_radius(self):
        """Every cell in the orbit must be equidistant from the origin."""
        q, r = 7, -3
        base_r = hex_radius(q, r)
        for cq, cr in symmetry_set(q, r):
            assert hex_radius(cq, cr) == base_r


# ---------------------------------------------------------------------------
# Snowflake builder
# ---------------------------------------------------------------------------

class TestBuildSnowflake:
    """Verify the deterministic snowflake cell set produced for the thumbnail."""

    def test_origin_is_included(self):
        """The seed cell (0, 0) must be present."""
        cells = build_snowflake()
        assert (0, 0) in cells

    def test_non_empty(self):
        """The snowflake must contain more than one cell."""
        cells = build_snowflake()
        assert len(cells) > 1

    def test_six_fold_rotational_symmetry(self):
        """For every cell (q, r) in the snowflake, all 6 rotations must also be present.

        This validates that symmetry_set and build_snowflake together produce
        a rotationally symmetric flake.
        """
        cells = build_snowflake()

        def rotate60(q: int, r: int) -> tuple[int, int]:
            return (-r, q + r)

        for q, r in list(cells):
            cq, cr = q, r
            for _ in range(6):
                cq, cr = rotate60(cq, cr)
                assert (cq, cr) in cells, (
                    f"60° rotation of {(q, r)} → {(cq, cr)} not in snowflake"
                )

    def test_reflective_symmetry(self):
        """For every cell, its reflection S must also be present."""
        cells = build_snowflake()
        for q, r in list(cells):
            reflected = (q, -q - r)
            assert reflected in cells, (
                f"Reflection of {(q, r)} → {reflected} missing from snowflake"
            )

    def test_no_cell_exceeds_max_radius(self):
        """No cell should have a hex radius beyond MAX_R + a few branch cells."""
        MAX_R = _thumb.MAX_R
        cells = build_snowflake()
        max_found = max(hex_radius(q, r) for q, r in cells)
        assert max_found <= MAX_R + MAX_R // 2, (
            f"Unexpected large cell at radius {max_found}"
        )


# ---------------------------------------------------------------------------
# SVG output from generate_thumbnail
# ---------------------------------------------------------------------------

class TestThumbnailSvg:
    """Verify the generated thumbnail.svg content."""

    def _content(self) -> str:
        return (PIECE_DIR / "thumbnail.svg").read_text()

    def test_is_valid_svg_root(self):
        """File must start with an SVG XML declaration or <svg> tag."""
        content = self._content()
        assert "<svg" in content

    def test_contains_background_rect(self):
        """Background rectangle with the correct colour must be present."""
        assert 'fill="#080c18"' in self._content()

    def test_contains_polygon_elements(self):
        """There must be at least one <polygon> representing hex cells."""
        assert "<polygon" in self._content()

    def test_uses_correct_crystal_colour(self):
        """Crystal colour must be rgb(222,238,255) — the #deeeff palette."""
        assert "rgb(222,238,255)" in self._content()


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

class TestIndexHtml:
    """Smoke-test the index.html source for key algorithm elements."""

    def _source(self) -> str:
        return (PIECE_DIR / "index.html").read_text()

    def test_no_external_scripts(self):
        """No <script src=...> tags allowed — all JS must be inline."""
        import re
        assert not re.search(r'<script\s+src=', self._source(), re.IGNORECASE)

    def test_has_symmetry_set(self):
        """The symmetrySet function must be defined in index.html."""
        assert "symmetrySet" in self._source()

    def test_has_hex_to_pixel(self):
        """The hexToPixel function must be defined."""
        assert "hexToPixel" in self._source()

    def test_has_background_colour(self):
        """Background colour #080c18 must appear in the source."""
        assert "#080c18" in self._source()

    def test_has_crystal_colour(self):
        """Crystal colour #deeeff / 222,238,255 must appear in the source."""
        source = self._source()
        assert "222,238,255" in source or "deeeff" in source.lower()

    def test_uses_request_animation_frame(self):
        """Animation must use requestAnimationFrame."""
        assert "requestAnimationFrame" in self._source()

    def test_hex_grid_js_under_200_lines(self):
        """The total JS in index.html must be self-contained in < 200 lines."""
        import re
        source = self._source()
        script_blocks = re.findall(
            r'<script[^>]*>(.*?)</script>', source, re.DOTALL | re.IGNORECASE
        )
        js_lines = sum(len(block.splitlines()) for block in script_blocks)
        assert js_lines < 200, f"JS is {js_lines} lines; must be < 200"


# ---------------------------------------------------------------------------
# Edge cases: malformed / empty inputs
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge-case behavior of the hex math utilities."""

    def test_hex_radius_large_values(self):
        """hex_radius should work for arbitrarily large coordinates."""
        assert hex_radius(1000, -500) == max(1000, 500, 500)

    def test_hex_to_pixel_large_coords(self):
        """hex_to_pixel must not raise for large or negative coordinates."""
        px, py = hex_to_pixel(-100, 200)
        assert isinstance(px, float)
        assert isinstance(py, float)

    def test_hex_polygon_points_returns_six_coords(self):
        """hex_polygon_points must return exactly 6 coordinate pairs."""
        pts = hex_polygon_points(0, 0, 5)
        pairs = pts.strip().split()
        assert len(pairs) == 6

    def test_symmetry_set_center_collapses(self):
        """The origin (0, 0) produces a single unique orbit member."""
        assert set(symmetry_set(0, 0)) == {(0, 0)}

    def test_symmetry_set_on_axis_fewer_than_12(self):
        """A cell on a symmetry axis has fewer than 12 distinct orbit members."""
        # (1, 0) lies on the q-axis which is a symmetry axis of the hex grid
        orbit = symmetry_set(1, 0)
        assert len(set(orbit)) < 12

    def test_build_snowflake_is_deterministic(self):
        """Calling build_snowflake twice must return identical results."""
        cells1 = build_snowflake()
        cells2 = build_snowflake()
        assert cells1 == cells2
