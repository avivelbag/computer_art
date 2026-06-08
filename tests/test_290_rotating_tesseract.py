"""Tests for Piece 290 — Through the Fourth Wall: rotating 4D hypercube."""

import importlib.util
import json
import math
import pathlib
import xml.etree.ElementTree as ET

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "290-rotating-tesseract"
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}

EXPECTED_VERTEX_COUNT = 16
EXPECTED_EDGE_COUNT = 32


def load_pieces() -> list:
    return json.loads(PIECES_JSON.read_text())


def tesseract_entry() -> dict | None:
    return next((e for e in load_pieces() if e.get("id") == "290-rotating-tesseract"), None)


@pytest.fixture(scope="module")
def gen():
    spec = importlib.util.spec_from_file_location(
        "gen290", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def line_elements(svg: str) -> list[str]:
    return [ln for ln in svg.splitlines() if "<line" in ln]


# ---------------------------------------------------------------------------
# Happy-path: directory layout
# ---------------------------------------------------------------------------

class TestDirectoryLayout:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

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
        assert tesseract_entry() is not None

    def test_required_fields_present(self):
        entry = tesseract_entry()
        assert entry is not None
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches_directory(self):
        entry = tesseract_entry()
        assert entry is not None
        piece_dir = REPO / entry["path"]
        assert entry["id"] == piece_dir.name

    def test_thumbnail_path_resolves(self):
        entry = tesseract_entry()
        assert entry is not None
        assert (REPO / entry["thumbnail"]).is_file()

    def test_year_is_integer(self):
        entry = tesseract_entry()
        assert entry is not None
        assert isinstance(entry["year"], int)

    def test_path_directory_exists(self):
        entry = tesseract_entry()
        assert entry is not None
        assert (REPO / entry["path"]).is_dir()


# ---------------------------------------------------------------------------
# Happy-path: index.html content
# ---------------------------------------------------------------------------

class TestIndexHtmlContent:
    @pytest.fixture(scope="class")
    def html(self):
        return (PIECE_DIR / "index.html").read_text()

    def test_canvas_600x600(self, html):
        assert 'width="600"' in html
        assert 'height="600"' in html

    def test_uses_request_animation_frame(self, html):
        assert "requestAnimationFrame" in html

    def test_black_background(self, html):
        assert "#000" in html or "#000000" in html

    def test_no_external_libraries(self, html):
        assert "<script src" not in html.lower()
        assert "https://" not in html
        assert "http://" not in html

    def test_xw_rotation_present(self, html):
        assert "XW" in html or "rotXW" in html or "SPEED_XW" in html

    def test_yz_rotation_present(self, html):
        assert "YZ" in html or "rotYZ" in html or "SPEED_YZ" in html

    def test_d4_projection_present(self, html):
        assert "D4" in html

    def test_d3_projection_present(self, html):
        assert "D3" in html

    def test_cyan_color_present(self, html):
        assert "00e5ff" in html.lower() or "0xe5" in html

    def test_indigo_color_present(self, html):
        assert "1a0050" in html.lower() or "0x1a" in html

    def test_16_vertices(self, html):
        assert "16" in html

    def test_32_edges(self, html):
        assert "32" in html or "d === 1" in html

    def test_js_under_150_lines(self, html):
        script_start = html.index("<script>")
        script_end = html.index("</script>")
        js_block = html[script_start:script_end]
        assert js_block.count("\n") < 150, "JS block exceeds 150 lines"


# ---------------------------------------------------------------------------
# Happy-path: thumbnail SVG
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

    def test_black_background(self, content):
        assert "#000000" in content or 'fill="#000"' in content

    def test_has_line_elements(self, content):
        assert "<line" in content

    def test_has_32_lines(self, content):
        count = len(line_elements(content))
        assert count == EXPECTED_EDGE_COUNT, f"Expected 32 edges, got {count}"

    def test_stroke_opacity_present(self, content):
        assert "stroke-opacity" in content

    def test_opacity_range_valid(self, content):
        for ln in line_elements(content):
            if 'stroke-opacity="' in ln:
                opacity = float(ln.split('stroke-opacity="')[1].split('"')[0])
                assert 0.0 <= opacity <= 1.0


# ---------------------------------------------------------------------------
# Happy-path: README
# ---------------------------------------------------------------------------

class TestReadmeContent:
    @pytest.fixture(scope="class")
    def readme(self):
        return (PIECE_DIR / "README.md").read_text()

    def test_mentions_perspective(self, readme):
        assert "perspective" in readme.lower()

    def test_mentions_rotation(self, readme):
        assert "rotation" in readme.lower() or "rotate" in readme.lower()

    def test_mentions_quasiperiodic(self, readme):
        assert "quasiperiodic" in readme.lower() or "irrational" in readme.lower()

    def test_mentions_32_edges(self, readme):
        assert "32" in readme

    def test_mentions_16_vertices(self, readme):
        assert "16" in readme

    def test_readme_substantial(self, readme):
        assert len(readme.strip()) > 400


# ---------------------------------------------------------------------------
# Happy-path: generate_thumbnail module
# ---------------------------------------------------------------------------

class TestGenerateThumbnailModule:
    def test_vertex_count(self, gen):
        assert len(gen.VERTICES) == EXPECTED_VERTEX_COUNT

    def test_edge_count(self, gen):
        assert len(gen.EDGES) == EXPECTED_EDGE_COUNT

    def test_edges_connect_by_one_coordinate(self, gen):
        for i, j in gen.EDGES:
            diff = sum(gen.VERTICES[i][k] != gen.VERTICES[j][k] for k in range(4))
            assert diff == 1

    def test_returns_string(self, gen):
        assert isinstance(gen.generate_svg(), str)

    def test_default_has_32_lines(self, gen):
        svg = gen.generate_svg()
        assert len(line_elements(svg)) == EXPECTED_EDGE_COUNT

    def test_svg_namespace_present(self, gen):
        svg = gen.generate_svg()
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_background_rect_present(self, gen):
        svg = gen.generate_svg()
        assert "<rect" in svg

    def test_different_frames_produce_different_output(self, gen):
        svg_a = gen.generate_svg(frame=0)
        svg_b = gen.generate_svg(frame=100)
        assert svg_a != svg_b

    def test_custom_size_in_viewbox(self, gen):
        svg = gen.generate_svg(size=200)
        assert 'viewBox="0 0 200 200"' in svg

    def test_custom_bg_present(self, gen):
        svg = gen.generate_svg(bg="#ff0000")
        assert "#ff0000" in svg

    def test_is_valid_xml(self, gen):
        svg = gen.generate_svg()
        ET.fromstring(svg)

    def test_opacity_range(self, gen):
        svg = gen.generate_svg()
        for ln in line_elements(svg):
            if 'stroke-opacity="' in ln:
                opacity = float(ln.split('stroke-opacity="')[1].split('"')[0])
                assert 0.0 <= opacity <= 1.0

    def test_frame_zero_still_draws(self, gen):
        svg = gen.generate_svg(frame=0)
        assert len(line_elements(svg)) == EXPECTED_EDGE_COUNT


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_no_duplicate_ids_in_pieces_json(self):
        pieces = load_pieces()
        ids = [e["id"] for e in pieces]
        assert len(ids) == len(set(ids)), "Duplicate ids found in pieces.json"

    def test_all_vertices_are_unit_hypercube(self, gen):
        for v in gen.VERTICES:
            for coord in v:
                assert abs(abs(coord) - 1.0) < 1e-9, f"Vertex coord not ±1: {coord}"

    def test_no_self_loops_in_edges(self, gen):
        for i, j in gen.EDGES:
            assert i != j

    def test_each_vertex_has_four_edges(self, gen):
        """Each hypercube vertex connects to exactly 4 others (one per axis)."""
        from collections import Counter
        counts = Counter()
        for i, j in gen.EDGES:
            counts[i] += 1
            counts[j] += 1
        for v_idx in range(EXPECTED_VERTEX_COUNT):
            assert counts[v_idx] == 4, f"Vertex {v_idx} has {counts[v_idx]} edges, expected 4"

    def test_large_frame_produces_valid_svg(self, gen):
        svg = gen.generate_svg(frame=10000)
        assert len(line_elements(svg)) == EXPECTED_EDGE_COUNT
        ET.fromstring(svg)

    def test_generate_svg_small_size(self, gen):
        svg = gen.generate_svg(size=50)
        assert "<svg" in svg
        assert len(line_elements(svg)) == EXPECTED_EDGE_COUNT

    def test_xw_rotation_changes_output(self, gen):
        svg_a = gen.generate_svg(frame=42, xw_speed=0.0, yz_speed=0.0)
        svg_b = gen.generate_svg(frame=42, xw_speed=0.5, yz_speed=0.0)
        assert svg_a != svg_b

    def test_yz_rotation_changes_output(self, gen):
        svg_a = gen.generate_svg(frame=42, xw_speed=0.0, yz_speed=0.0)
        svg_b = gen.generate_svg(frame=42, xw_speed=0.0, yz_speed=0.5)
        assert svg_a != svg_b


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_entry_missing_title_fails_required_check(self):
        incomplete = {
            "id": "290-rotating-tesseract",
            "year": 2026,
            "technique": "canvas",
            "path": "pieces/290-rotating-tesseract",
            "thumbnail": "pieces/290-rotating-tesseract/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_wrong_edge_diff_count_not_an_edge(self, gen):
        """Vertices differing in 2 coordinates must not be in EDGES."""
        for i in range(EXPECTED_VERTEX_COUNT):
            for j in range(i + 1, EXPECTED_VERTEX_COUNT):
                diff = sum(gen.VERTICES[i][k] != gen.VERTICES[j][k] for k in range(4))
                if diff != 1:
                    assert (i, j) not in gen.EDGES

    def test_missing_thumbnail_detected(self, tmp_path):
        ghost = tmp_path / "ghost.svg"
        assert not ghost.exists()

    def test_missing_readme_detected(self, tmp_path):
        piece_dir = tmp_path / "290-rotating-tesseract"
        piece_dir.mkdir()
        assert not (piece_dir / "README.md").exists()

    def test_color_lerp_at_zero_is_indigo(self, gen):
        r, g, b, opacity = gen._edge_color(0.0)
        assert r == 0x1a
        assert g == 0
        assert b == 0x50
        assert abs(opacity - 0.2) < 1e-6

    def test_color_lerp_at_one_is_cyan(self, gen):
        r, g, b, opacity = gen._edge_color(1.0)
        assert r == 0
        assert g == 0xe5
        assert b == 0xff
        assert abs(opacity - 1.0) < 1e-6

    def test_color_lerp_clamps_below_zero(self, gen):
        r, g, b, opacity = gen._edge_color(-5.0)
        assert opacity >= 0.2

    def test_color_lerp_clamps_above_one(self, gen):
        r, g, b, opacity = gen._edge_color(5.0)
        assert opacity <= 1.0

    def test_proj4to3_identity_at_w_zero(self, gen):
        """When w=0, f4 = D4/(D4-0) = 1, so 3D coords equal 4D xyz."""
        v = (0.5, -0.3, 0.7, 0.0)
        out = gen._proj4to3(v)
        assert abs(out[0] - 0.5) < 1e-9
        assert abs(out[1] - (-0.3)) < 1e-9
        assert abs(out[2] - 0.7) < 1e-9

    def test_rot_xw_preserves_yz(self, gen):
        """XW rotation must not change y or z components."""
        v = (0.3, 0.7, -0.5, 0.4)
        out = gen._rot_xw(v, 1.234)
        assert abs(out[1] - v[1]) < 1e-12
        assert abs(out[2] - v[2]) < 1e-12

    def test_rot_yz_preserves_xw(self, gen):
        """YZ rotation must not change x or w components."""
        v = (0.3, 0.7, -0.5, 0.4)
        out = gen._rot_yz(v, 0.987)
        assert abs(out[0] - v[0]) < 1e-12
        assert abs(out[3] - v[3]) < 1e-12

    def test_rot_xw_is_isometry(self, gen):
        """Rotation must preserve the 4D vector magnitude."""
        v = (0.3, 0.7, -0.5, 0.4)
        mag_before = math.sqrt(sum(c**2 for c in v))
        out = gen._rot_xw(v, 2.718)
        mag_after = math.sqrt(sum(c**2 for c in out))
        assert abs(mag_before - mag_after) < 1e-12
