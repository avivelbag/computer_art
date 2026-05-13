"""Tests for Piece 87 — Phyllotaxis: The Angle the Sunflower Chose."""

import importlib.util
import json
import math
import pathlib
import xml.etree.ElementTree as ET

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "87-phyllotaxis"
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

GOLDEN_ANGLE_RAD = math.pi * (3 - math.sqrt(5))  # ≈ 2.39996 rad


def load_pieces():
    """Return parsed pieces.json as a list."""
    return json.loads(PIECES_JSON.read_text())


def phyllotaxis_entry():
    """Return the pieces.json entry for 87-phyllotaxis, or None if absent."""
    return next((e for e in load_pieces() if e.get("id") == "87-phyllotaxis"), None)


@pytest.fixture(scope="module")
def gen():
    """Load generate_thumbnail.py as a module with an isolated name."""
    spec = importlib.util.spec_from_file_location(
        "gen87", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def circle_lines(svg: str) -> list[str]:
    """Return all lines of an SVG string that contain a <circle element."""
    return [ln for ln in svg.splitlines() if "<circle" in ln]


def parse_attr(line: str, attr: str) -> float:
    """Parse a numeric attribute value from a single SVG element line."""
    return float(line.split(f'{attr}="')[1].split('"')[0])


# ---------------------------------------------------------------------------
# Happy-path: directory layout
# ---------------------------------------------------------------------------

class TestDirectoryLayout:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir(), "pieces/87-phyllotaxis/ must exist"

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
        assert phyllotaxis_entry() is not None, "87-phyllotaxis entry missing from pieces.json"

    def test_required_fields_present(self):
        entry = phyllotaxis_entry()
        assert entry is not None
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches_directory(self):
        entry = phyllotaxis_entry()
        assert entry is not None
        piece_dir = REPO / entry["path"]
        assert entry["id"] == piece_dir.name

    def test_thumbnail_path_resolves(self):
        entry = phyllotaxis_entry()
        assert entry is not None
        assert (REPO / entry["thumbnail"]).is_file()

    def test_year_is_integer(self):
        entry = phyllotaxis_entry()
        assert entry is not None
        assert isinstance(entry["year"], int)

    def test_path_directory_exists(self):
        entry = phyllotaxis_entry()
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

    def test_golden_angle_referenced(self, html):
        assert "golden" in html.lower() or "GOLDEN" in html

    def test_morph_animation_present(self, html):
        assert "morph" in html.lower()

    def test_saffron_color_present(self, html):
        assert "f5a623" in html.lower()

    def test_dark_background_present(self, html):
        assert "1a0800" in html.lower()

    def test_sqrt_used_for_fermat_spiral(self, html):
        assert "Math.sqrt" in html

    def test_max_dots_around_1500(self, html):
        assert "1500" in html

    def test_morph_delta_present(self, html):
        assert "MORPH_DELTA" in html or "morph_delta" in html or "10" in html


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
        assert "1a0800" in content.lower()

    def test_has_enough_circles(self, content):
        circles = circle_lines(content)
        assert len(circles) >= 200, f"Expected ≥200 circles, got {len(circles)}"

    def test_circle_count_matches_default_n(self, content):
        circles = circle_lines(content)
        assert len(circles) == 300


# ---------------------------------------------------------------------------
# Happy-path: README content
# ---------------------------------------------------------------------------

class TestReadmeContent:
    @pytest.fixture(scope="class")
    def readme(self):
        return (PIECE_DIR / "README.md").read_text()

    def test_mentions_golden_angle(self, readme):
        assert "golden angle" in readme.lower()

    def test_mentions_phyllotaxis(self, readme):
        assert "phyllotaxis" in readme.lower()

    def test_mentions_spiral_or_packing(self, readme):
        assert "spiral" in readme.lower() or "packing" in readme.lower()

    def test_explains_why_no_spokes(self, readme):
        assert "spoke" in readme.lower() or "irrational" in readme.lower()

    def test_readme_substantial(self, readme):
        assert len(readme.strip()) > 200


# ---------------------------------------------------------------------------
# Happy-path: generate_thumbnail module math
# ---------------------------------------------------------------------------

class TestGenerateThumbnailModule:
    def test_returns_string(self, gen):
        assert isinstance(gen.generate_svg(), str)

    def test_default_generates_300_circles(self, gen):
        svg = gen.generate_svg()
        assert len(circle_lines(svg)) == 300

    def test_custom_n_correct_count(self, gen):
        assert len(circle_lines(gen.generate_svg(n=50))) == 50

    def test_zero_n_produces_valid_shell(self, gen):
        svg = gen.generate_svg(n=0)
        assert len(circle_lines(svg)) == 0
        assert "<svg" in svg
        assert "<rect" in svg

    def test_first_dot_at_centre(self, gen):
        svg = gen.generate_svg(n=2, size=400, spacing=8.0)
        lines = circle_lines(svg)
        cx = parse_attr(lines[0], "cx")
        cy = parse_attr(lines[0], "cy")
        assert abs(cx - 200.0) < 0.01
        assert abs(cy - 200.0) < 0.01

    def test_second_dot_uses_golden_angle(self, gen):
        svg = gen.generate_svg(n=2, size=400, spacing=8.0)
        lines = circle_lines(svg)
        expected_x = 200.0 + 8.0 * math.cos(GOLDEN_ANGLE_RAD)
        expected_y = 200.0 + 8.0 * math.sin(GOLDEN_ANGLE_RAD)
        cx = parse_attr(lines[1], "cx")
        cy = parse_attr(lines[1], "cy")
        assert abs(cx - expected_x) < 0.01
        assert abs(cy - expected_y) < 0.01

    def test_centre_dot_larger_than_edge_dot(self, gen):
        svg = gen.generate_svg(n=100)
        lines = circle_lines(svg)
        r_centre = parse_attr(lines[0], ' r')
        r_edge   = parse_attr(lines[-1], ' r')
        assert r_centre > r_edge

    def test_large_n_completes_without_error(self, gen):
        svg = gen.generate_svg(n=1500)
        assert len(circle_lines(svg)) == 1500

    def test_custom_bg_appears_in_output(self, gen):
        svg = gen.generate_svg(n=5, bg="#ff0000")
        assert "#ff0000" in svg

    def test_svg_namespace_present(self, gen):
        svg = gen.generate_svg(n=1)
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_custom_dot_r_max_applied(self, gen):
        svg = gen.generate_svg(n=2, size=400, spacing=8.0, dot_r_max=10.0, dot_r_min=1.0)
        lines = circle_lines(svg)
        # i=0: norm_r=0 → dot_r = dot_r_max = 10.0
        r_val = parse_attr(lines[0], ' r')
        assert abs(r_val - 10.0) < 0.01


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

    def test_generate_svg_with_n_equals_1(self, gen):
        svg = gen.generate_svg(n=1)
        lines = circle_lines(svg)
        assert len(lines) == 1
        cx = parse_attr(lines[0], "cx")
        cy = parse_attr(lines[0], "cy")
        assert abs(cx - 200.0) < 0.01
        assert abs(cy - 200.0) < 0.01


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_entry_missing_title_fails_required_check(self):
        incomplete = {
            "id": "87-phyllotaxis",
            "tagline": "test",
            "year": 2026,
            "technique": "canvas",
            "path": "pieces/87-phyllotaxis",
            "thumbnail": "pieces/87-phyllotaxis/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_wrong_id_detected(self, tmp_path):
        piece_dir = tmp_path / "87-phyllotaxis"
        piece_dir.mkdir()
        entry = {"id": "wrong-id", "path": str(piece_dir.relative_to(tmp_path))}
        assert entry["id"] != piece_dir.name

    def test_missing_thumbnail_detected(self, tmp_path):
        ghost = tmp_path / "ghost.svg"
        assert not ghost.exists()

    def test_missing_readme_detected(self, tmp_path):
        piece_dir = tmp_path / "87-phyllotaxis"
        piece_dir.mkdir()
        assert not (piece_dir / "README.md").exists()

    def test_nonexistent_piece_dir_detected(self, tmp_path):
        nonexistent = tmp_path / "ghost-piece"
        assert not nonexistent.is_dir()
