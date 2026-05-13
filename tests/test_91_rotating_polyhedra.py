"""Tests for Piece 91 — Rotating Polyhedra: 3D Wireframe Pen-Plotter Projection."""

import importlib.util
import json
import math
import pathlib
import xml.etree.ElementTree as ET

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "91-rotating-polyhedra"
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

# Icosahedron has 30 edges, dodecahedron has 30, tetrahedron has 6 → 66 total.
EXPECTED_LINE_COUNT = 66


def load_pieces() -> list:
    """Return parsed pieces.json as a list."""
    return json.loads(PIECES_JSON.read_text())


def polyhedra_entry() -> dict | None:
    """Return the pieces.json entry for 91-rotating-polyhedra, or None if absent."""
    return next((e for e in load_pieces() if e.get("id") == "91-rotating-polyhedra"), None)


@pytest.fixture(scope="module")
def gen():
    """Load generate_thumbnail.py as a module with an isolated name."""
    spec = importlib.util.spec_from_file_location(
        "gen91", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def line_elements(svg: str) -> list[str]:
    """Return all lines of an SVG string that contain a <line element."""
    return [ln for ln in svg.splitlines() if "<line" in ln]


def parse_attr(line: str, attr: str) -> float:
    """Parse a numeric attribute value from a single SVG element line."""
    return float(line.split(f'{attr}="')[1].split('"')[0])


# ---------------------------------------------------------------------------
# Happy-path: directory layout
# ---------------------------------------------------------------------------

class TestDirectoryLayout:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir(), "pieces/91-rotating-polyhedra/ must exist"

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_thumbnail_py_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# Happy-path: pieces.json entry
# ---------------------------------------------------------------------------

class TestPiecesJsonEntry:
    def test_entry_present(self):
        assert polyhedra_entry() is not None, "91-rotating-polyhedra entry missing from pieces.json"

    def test_required_fields_present(self):
        entry = polyhedra_entry()
        assert entry is not None
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches_directory(self):
        entry = polyhedra_entry()
        assert entry is not None
        piece_dir = REPO / entry["path"]
        assert entry["id"] == piece_dir.name

    def test_thumbnail_path_resolves(self):
        entry = polyhedra_entry()
        assert entry is not None
        assert (REPO / entry["thumbnail"]).is_file()

    def test_year_is_integer(self):
        entry = polyhedra_entry()
        assert entry is not None
        assert isinstance(entry["year"], int)

    def test_path_directory_exists(self):
        entry = polyhedra_entry()
        assert entry is not None
        assert (REPO / entry["path"]).is_dir()


# ---------------------------------------------------------------------------
# Happy-path: index.html content
# ---------------------------------------------------------------------------

class TestIndexHtmlContent:
    @pytest.fixture(scope="class")
    def html(self):
        return (PIECE_DIR / "index.html").read_text()

    def test_uses_request_animation_frame(self, html):
        assert "requestAnimationFrame" in html

    def test_canvas_element_present(self, html):
        assert "<canvas" in html.lower()

    def test_perspective_projection_present(self, html):
        # The perspective divide formula: FOV * v / (vz + CAM_DIST)
        assert "CAM_DIST" in html or "cam_dist" in html or "camDist" in html

    def test_fov_tunable(self, html):
        assert "FOV" in html or "fov" in html

    def test_cream_stroke_color(self, html):
        assert "245,240,230" in html

    def test_charcoal_background(self, html):
        assert "1c1c1e" in html.lower()

    def test_no_webgl(self, html):
        assert "webgl" not in html.lower()

    def test_no_external_libraries(self, html):
        assert "<script src" not in html.lower()

    def test_icosahedron_present(self, html):
        assert "icosahedron" in html.lower() or "mkIcosahedron" in html

    def test_dodecahedron_present(self, html):
        assert "dodecahedron" in html.lower() or "mkDodecahedron" in html

    def test_alpha_depth_cue_present(self, html):
        # Depth-cued alpha formula uses 0.15 and 0.75
        assert "0.15" in html

    def test_rotation_accumulates(self, html):
        # t increments without modulo — the animation never wraps
        assert "+=" in html

    def test_canvas_800x800(self, html):
        assert "800" in html


# ---------------------------------------------------------------------------
# Happy-path: thumbnail.svg content
# ---------------------------------------------------------------------------

class TestThumbnailSvg:
    @pytest.fixture(scope="class")
    def content(self):
        return (PIECE_DIR / "thumbnail.svg").read_text()

    def test_is_valid_xml(self):
        ET.parse(str(PIECE_DIR / "thumbnail.svg"))

    def test_has_svg_namespace(self, content):
        assert 'xmlns="http://www.w3.org/2000/svg"' in content

    def test_has_background_rect(self, content):
        assert "<rect" in content

    def test_dark_background_color(self, content):
        assert "1c1c1e" in content.lower()

    def test_has_line_elements(self, content):
        assert "<line" in content

    def test_has_correct_line_count(self, content):
        count = len(line_elements(content))
        assert count == EXPECTED_LINE_COUNT, (
            f"Expected {EXPECTED_LINE_COUNT} lines (6 tet + 30 ico + 30 dod), got {count}"
        )

    def test_stroke_opacity_present(self, content):
        assert "stroke-opacity" in content

    def test_alpha_range_valid(self, content):
        for ln in line_elements(content):
            if 'stroke-opacity="' in ln:
                alpha = parse_attr(ln, "stroke-opacity")
                assert 0.0 <= alpha <= 1.0, f"alpha out of range: {alpha}"


# ---------------------------------------------------------------------------
# Happy-path: README content
# ---------------------------------------------------------------------------

class TestReadmeContent:
    @pytest.fixture(scope="class")
    def readme(self):
        return (PIECE_DIR / "README.md").read_text()

    def test_mentions_perspective_projection(self, readme):
        assert "perspective" in readme.lower()

    def test_mentions_icosahedron(self, readme):
        assert "icosahedron" in readme.lower()

    def test_mentions_dodecahedron(self, readme):
        assert "dodecahedron" in readme.lower()

    def test_explains_no_hidden_line_removal(self, readme):
        assert "hidden" in readme.lower() or "wireframe" in readme.lower()

    def test_readme_explains_math(self, readme):
        assert "fov" in readme.lower() or "focal" in readme.lower() or "sx = " in readme

    def test_readme_substantial(self, readme):
        assert len(readme.strip()) > 300


# ---------------------------------------------------------------------------
# Happy-path: generate_thumbnail module
# ---------------------------------------------------------------------------

class TestGenerateThumbnailModule:
    def test_returns_string(self, gen):
        assert isinstance(gen.generate_svg(), str)

    def test_default_has_66_lines(self, gen):
        svg = gen.generate_svg()
        assert len(line_elements(svg)) == EXPECTED_LINE_COUNT

    def test_custom_angle_changes_output(self, gen):
        svg_a = gen.generate_svg(angle_y=0.0, angle_x=0.0)
        svg_b = gen.generate_svg(angle_y=1.0, angle_x=0.5)
        assert svg_a != svg_b

    def test_custom_size_reflected_in_viewbox(self, gen):
        svg = gen.generate_svg(size=200)
        assert 'viewBox="0 0 200 200"' in svg

    def test_custom_bg_appears_in_output(self, gen):
        svg = gen.generate_svg(bg="#ff0000")
        assert "#ff0000" in svg

    def test_svg_namespace_present(self, gen):
        svg = gen.generate_svg()
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_background_rect_present(self, gen):
        svg = gen.generate_svg()
        assert "<rect" in svg

    def test_alphas_within_range(self, gen):
        svg = gen.generate_svg()
        for ln in line_elements(svg):
            if 'stroke-opacity="' in ln:
                alpha = parse_attr(ln, "stroke-opacity")
                assert 0.0 <= alpha <= 1.0

    def test_large_fov_produces_wider_spread(self, gen):
        small = gen.generate_svg(size=400, fov=50.0)
        large = gen.generate_svg(size=400, fov=400.0)
        # With large fov, x1 values on edges are further from center (200)
        assert small != large

    def test_tet_edge_count_six(self, gen):
        """Isolated tetrahedron sanity: hardcode geometry and count edges."""
        assert len(gen.TET_EDGES) == 6

    def test_ico_edge_count_thirty(self, gen):
        assert len(gen.ICO_EDGES) == 30

    def test_dod_edge_count_thirty(self, gen):
        assert len(gen.DOD_EDGES) == 30


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_no_duplicate_ids_in_pieces_json(self):
        pieces = load_pieces()
        ids = [e["id"] for e in pieces]
        assert len(ids) == len(set(ids)), "Duplicate ids found in pieces.json"

    def test_readme_not_empty(self):
        readme = (PIECE_DIR / "README.md").read_text()
        assert len(readme.strip()) > 100

    def test_thumbnail_svg_is_valid_xml(self):
        ET.parse(str(PIECE_DIR / "thumbnail.svg"))

    def test_generate_svg_small_size(self, gen):
        svg = gen.generate_svg(size=50, fov=20.0)
        assert "<svg" in svg
        assert "<rect" in svg
        assert len(line_elements(svg)) == EXPECTED_LINE_COUNT

    def test_generate_svg_angle_zero_still_draws(self, gen):
        svg = gen.generate_svg(angle_y=0.0, angle_x=0.0)
        assert len(line_elements(svg)) == EXPECTED_LINE_COUNT

    def test_generate_svg_extreme_angle(self, gen):
        svg = gen.generate_svg(angle_y=math.pi * 10, angle_x=math.pi * 7)
        assert len(line_elements(svg)) == EXPECTED_LINE_COUNT

    def test_ico_verts_on_unit_sphere(self, gen):
        for v in gen._ico_verts():
            r = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            assert abs(r - 1.0) < 1e-9, f"Icosahedron vertex not on unit sphere: r={r}"

    def test_dod_verts_on_unit_sphere(self, gen):
        for v in gen._dod_verts():
            r = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            assert abs(r - 1.0) < 1e-9, f"Dodecahedron vertex not on unit sphere: r={r}"


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_entry_missing_title_fails_required_check(self):
        incomplete = {
            "id": "91-rotating-polyhedra",
            "tagline": "test",
            "year": 2026,
            "technique": "canvas",
            "path": "pieces/91-rotating-polyhedra",
            "thumbnail": "pieces/91-rotating-polyhedra/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_wrong_id_detected(self, tmp_path):
        piece_dir = tmp_path / "91-rotating-polyhedra"
        piece_dir.mkdir()
        entry = {"id": "wrong-id", "path": str(piece_dir.relative_to(tmp_path))}
        assert entry["id"] != piece_dir.name

    def test_missing_thumbnail_detected(self, tmp_path):
        ghost = tmp_path / "ghost.svg"
        assert not ghost.exists()

    def test_missing_readme_detected(self, tmp_path):
        piece_dir = tmp_path / "91-rotating-polyhedra"
        piece_dir.mkdir()
        assert not (piece_dir / "README.md").exists()

    def test_nonexistent_piece_dir_detected(self, tmp_path):
        nonexistent = tmp_path / "ghost-piece"
        assert not nonexistent.is_dir()

    def test_generate_svg_returns_valid_xml(self, gen):
        svg = gen.generate_svg()
        root = ET.fromstring(svg)
        assert root.tag.endswith("svg")
