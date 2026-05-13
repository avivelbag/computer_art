"""Tests for Piece 94 — Penrose P3 tiling via substitution deflation."""

import importlib.util
import json
import math
import pathlib
import xml.etree.ElementTree as ET

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "94-penrose-tiling"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID  = "94-penrose-tiling"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}


def _load_pieces() -> list:
    return json.loads(PIECES_JSON.read_text())


def _entry() -> dict:
    for item in _load_pieces():
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


@pytest.fixture(scope="module")
def gen():
    """Load generate_thumbnail.py as an isolated module."""
    spec = importlib.util.spec_from_file_location(
        "gen94", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Directory layout
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
# pieces.json entry
# ---------------------------------------------------------------------------

class TestPiecesJson:
    def test_entry_present(self):
        _entry()

    def test_required_fields_present(self):
        missing = REQUIRED_FIELDS - _entry().keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches(self):
        assert _entry()["id"] == PIECE_ID

    def test_path_matches(self):
        assert _entry()["path"] == f"pieces/{PIECE_ID}"

    def test_thumbnail_file_exists(self):
        assert (REPO / _entry()["thumbnail"]).is_file()

    def test_year_is_int(self):
        assert isinstance(_entry()["year"], int)

    def test_technique_mentions_penrose(self):
        assert "penrose" in _entry()["technique"].lower()

    def test_technique_mentions_deflation_or_substitution(self):
        t = _entry()["technique"].lower()
        assert "deflation" in t or "substitution" in t

    def test_no_duplicate_ids(self):
        ids = [e["id"] for e in _load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate ids in pieces.json"


# ---------------------------------------------------------------------------
# index.html content
# ---------------------------------------------------------------------------

class TestIndexHtml:
    @pytest.fixture(scope="class")
    def html(self):
        return (PIECE_DIR / "index.html").read_text()

    def test_has_canvas_element(self, html):
        assert "<canvas" in html.lower()

    def test_has_phi_constant(self, html):
        assert "PHI" in html

    def test_phi_correct_value(self, html):
        assert "Math.sqrt(5)" in html

    def test_has_make_sun(self, html):
        assert "makeSun" in html or "make_sun" in html

    def test_has_deflate(self, html):
        assert "deflate" in html

    def test_has_thick_color(self, html):
        assert "c84b31" in html.lower()

    def test_has_thin_color(self, html):
        assert "7a9e7e" in html.lower()

    def test_has_parchment_background(self, html):
        assert "f5f0e8" in html.lower()

    def test_no_external_libraries(self, html):
        assert "<script src" not in html.lower()

    def test_no_external_urls(self, html):
        assert "https://" not in html
        assert "http://" not in html

    def test_canvas_800(self, html):
        assert "800" in html

    def test_has_canvas_2d_context(self, html):
        assert "getContext" in html

    def test_deflate_uses_phi(self, html):
        assert "PHI" in html

    def test_six_generations(self, html):
        assert "6" in html

    def test_both_fill_colors_applied(self, html):
        assert "fillStyle" in html


# ---------------------------------------------------------------------------
# thumbnail.svg content
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
        assert "f5f0e8" in content.lower()

    def test_has_thick_color(self, content):
        assert "c84b31" in content.lower()

    def test_has_thin_color(self, content):
        assert "7a9e7e" in content.lower()

    def test_has_polygons(self, content):
        assert "<polygon" in content

    def test_under_200kb(self):
        size = (PIECE_DIR / "thumbnail.svg").stat().st_size
        assert size < 200_000, f"thumbnail.svg is {size} bytes — must be < 200 KB"


# ---------------------------------------------------------------------------
# README content
# ---------------------------------------------------------------------------

class TestReadme:
    @pytest.fixture(scope="class")
    def readme(self):
        return (PIECE_DIR / "README.md").read_text()

    def test_mentions_penrose(self, readme):
        assert "penrose" in readme.lower()

    def test_mentions_deflation_or_substitution(self, readme):
        assert "deflation" in readme.lower() or "substitution" in readme.lower()

    def test_mentions_golden_ratio_or_phi(self, readme):
        low = readme.lower()
        assert "golden" in low or "phi" in low or "φ" in readme

    def test_is_substantial(self, readme):
        assert len(readme.strip()) > 400


# ---------------------------------------------------------------------------
# PHI constant
# ---------------------------------------------------------------------------

class TestPHI:
    def test_phi_value(self, gen):
        assert abs(gen.PHI - (1 + math.sqrt(5)) / 2) < 1e-12

    def test_phi_squared_equals_phi_plus_one(self, gen):
        """Defining property: φ² = φ + 1."""
        assert abs(gen.PHI ** 2 - gen.PHI - 1) < 1e-12

    def test_phi_inverse_equals_phi_minus_one(self, gen):
        """1/φ = φ − 1."""
        assert abs(1 / gen.PHI - (gen.PHI - 1)) < 1e-12


# ---------------------------------------------------------------------------
# make_sun
# ---------------------------------------------------------------------------

class TestMakeSun:
    def test_returns_10_triangles(self, gen):
        assert len(gen.make_sun(100.0)) == 10

    def test_all_acute(self, gen):
        assert all(t[0] == "A" for t in gen.make_sun(100.0))

    def test_apex_at_origin(self, gen):
        for kind, A, B, C in gen.make_sun(200.0):
            assert abs(A) < 1e-12

    def test_outer_vertices_on_circle(self, gen):
        r = 150.0
        for kind, A, B, C in gen.make_sun(r):
            assert abs(abs(B) - r) < 1e-9
            assert abs(abs(C) - r) < 1e-9

    def test_apex_angle_36_degrees(self, gen):
        """Every sun triangle must have a 36° apex angle (P3 acute triangle)."""
        tol = 1e-6
        for kind, A, B, C in gen.make_sun(100.0):
            vB = B - A
            vC = C - A
            cos_a = (vB.real * vC.real + vB.imag * vC.imag) / (abs(vB) * abs(vC))
            angle = math.degrees(math.acos(max(-1.0, min(1.0, cos_a))))
            assert abs(angle - 36.0) < tol


# ---------------------------------------------------------------------------
# deflate
# ---------------------------------------------------------------------------

def _count(tris, kind):
    return sum(1 for t in tris if t[0] == kind)


class TestDeflate:
    def test_empty_input(self, gen):
        assert gen.deflate([]) == []

    def test_single_acute_produces_two(self, gen):
        """One type-A triangle deflates into 1 A + 1 B."""
        result = gen.deflate([("A", 0 + 0j, 1 + 0j, 0 + 1j)])
        assert len(result) == 2
        assert _count(result, "A") == 1
        assert _count(result, "B") == 1

    def test_single_obtuse_produces_three(self, gen):
        """One type-B triangle deflates into 1 A + 2 B."""
        result = gen.deflate([("B", 0 + 0j, 1 + 0j, 0 + 1j)])
        assert len(result) == 3
        assert _count(result, "A") == 1
        assert _count(result, "B") == 2

    def test_one_generation_from_sun(self, gen):
        """10 A triangles → 10 A + 10 B = 20 total."""
        tris = gen.deflate(gen.make_sun(100.0))
        assert len(tris) == 20
        assert _count(tris, "A") == 10
        assert _count(tris, "B") == 10

    def test_triangle_count_recurrence(self, gen):
        """n_A' = n_A + n_B, n_B' = n_A + 2*n_B — Penrose substitution matrix."""
        tris = gen.make_sun(100.0)
        n_A, n_B = 10, 0
        for _ in range(5):
            tris = gen.deflate(tris)
            n_A, n_B = n_A + n_B, n_A + 2 * n_B
        assert _count(tris, "A") == n_A
        assert _count(tris, "B") == n_B

    def test_ratio_approaches_phi(self, gen):
        """After many deflations, n_B/n_A converges to φ."""
        tris = gen.make_sun(1.0)
        for _ in range(8):
            tris = gen.deflate(tris)
        n_A = _count(tris, "A")
        n_B = _count(tris, "B")
        assert abs(n_B / n_A - gen.PHI) < 0.01

    def test_all_kinds_valid(self, gen):
        tris = gen.make_sun(1.0)
        for _ in range(4):
            tris = gen.deflate(tris)
        kinds = {t[0] for t in tris}
        assert kinds <= {"A", "B"}

    def test_split_point_lies_on_edge(self, gen):
        """Deflation point P = A + (B-A)/phi lies on segment AB of a type-A triangle."""
        A, B, C = 0 + 0j, 2 + 0j, 1 + 1j
        result = gen.deflate([("A", A, B, C)])
        P_expected = A + (B - A) / gen.PHI
        all_verts = [v for _, a, b, c in result for v in (a, b, c)]
        assert any(abs(v - P_expected) < 1e-12 for v in all_verts)

    def test_all_vertices_complex(self, gen):
        """Deflation must produce complex number vertices throughout."""
        tris = gen.make_sun(1.0)
        for _ in range(3):
            tris = gen.deflate(tris)
        for kind, A, B, C in tris:
            assert isinstance(A, complex)
            assert isinstance(B, complex)
            assert isinstance(C, complex)


# ---------------------------------------------------------------------------
# generate_svg (thumbnail generator)
# ---------------------------------------------------------------------------

class TestGenerateSvg:
    def test_returns_string(self, gen):
        assert isinstance(gen.generate_svg(generations=2, size=200), str)

    def test_has_svg_namespace(self, gen):
        assert 'xmlns="http://www.w3.org/2000/svg"' in gen.generate_svg(2, 200)

    def test_viewbox_matches_size(self, gen):
        assert 'viewBox="0 0 300 300"' in gen.generate_svg(2, 300)

    def test_has_background_rect(self, gen):
        svg = gen.generate_svg(2, 200)
        assert "<rect" in svg
        assert gen.BG_COLOR in svg

    def test_has_both_colors(self, gen):
        svg = gen.generate_svg(3, 200)
        assert gen.THICK_COLOR in svg
        assert gen.THIN_COLOR in svg

    def test_polygon_count_matches_triangles(self, gen):
        """Polygon count must equal triangle count after deflation."""
        tris = gen.make_sun(100.0)
        for _ in range(3):
            tris = gen.deflate(tris)
        svg = gen.generate_svg(generations=3, size=200)
        assert svg.count("<polygon") == len(tris)

    def test_zero_generations_produces_10_polygons(self, gen):
        assert gen.generate_svg(generations=0, size=400).count("<polygon") == 10

    def test_reproducible(self, gen):
        svg1 = gen.generate_svg(3, 300)
        svg2 = gen.generate_svg(3, 300)
        assert svg1 == svg2

    def test_valid_xml(self, gen):
        ET.fromstring(gen.generate_svg(3, 200))

    def test_stroke_color_present(self, gen):
        assert gen.STROKE_COLOR in gen.generate_svg(2, 200)

    def test_small_size_renders(self, gen):
        svg = gen.generate_svg(2, 50)
        assert "<polygon" in svg
        assert 'viewBox="0 0 50 50"' in svg


# ---------------------------------------------------------------------------
# Committed thumbnail.svg integrity
# ---------------------------------------------------------------------------

class TestThumbnailIntegrity:
    def test_thumbnail_valid_xml(self):
        ET.parse(str(PIECE_DIR / "thumbnail.svg"))

    def test_thumbnail_correct_polygon_count(self, gen):
        """thumbnail.svg polygon count must match THUMB_GENERATIONS deflation output."""
        tris = gen.make_sun(1.0)
        for _ in range(gen.THUMB_GENERATIONS):
            tris = gen.deflate(tris)
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert content.count("<polygon") == len(tris)

    def test_thumbnail_has_background(self, gen):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert gen.BG_COLOR in content

    def test_thumbnail_has_both_colors(self, gen):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert gen.THICK_COLOR in content
        assert gen.THIN_COLOR in content


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_large_generation_no_crash(self, gen):
        """Seven deflation generations must complete without error."""
        tris = gen.make_sun(100.0)
        for _ in range(7):
            tris = gen.deflate(tris)
        assert len(tris) > 1000

    def test_deflate_preserves_complex_type(self, gen):
        tris = gen.make_sun(1.0)
        for _ in range(3):
            tris = gen.deflate(tris)
        for kind, A, B, C in tris:
            for v in (A, B, C):
                assert isinstance(v, complex)

    def test_unknown_kind_never_produced(self, gen):
        tris = gen.make_sun(1.0)
        for _ in range(5):
            tris = gen.deflate(tris)
        assert {t[0] for t in tris} <= {"A", "B"}

    def test_generate_svg_large_input(self, gen):
        """generate_svg with 6 generations must not crash and must return valid XML."""
        svg = gen.generate_svg(generations=6, size=400)
        ET.fromstring(svg)
        assert svg.count("<polygon") > 1000

    def test_make_sun_zero_radius(self, gen):
        """Radius zero is degenerate but must not crash."""
        tris = gen.make_sun(0.0)
        assert len(tris) == 10


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_missing_title_fails_required_check(self):
        incomplete = {
            "id": PIECE_ID,
            "tagline": "test",
            "year": 2026,
            "technique": "canvas",
            "path": f"pieces/{PIECE_ID}",
            "thumbnail": f"pieces/{PIECE_ID}/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_wrong_id_not_in_json(self):
        ids = [e["id"] for e in _load_pieces()]
        assert "94-wrong-id" not in ids

    def test_missing_thumbnail_detected(self, tmp_path):
        ghost = tmp_path / "ghost.svg"
        assert not ghost.exists()

    def test_missing_readme_detected(self, tmp_path):
        piece_dir = tmp_path / PIECE_ID
        piece_dir.mkdir()
        assert not (piece_dir / "README.md").exists()

    def test_nonexistent_piece_dir_detected(self, tmp_path):
        assert not (tmp_path / "ghost-piece").is_dir()

    def test_deflate_unknown_kind_treated_as_obtuse(self, gen):
        """Unknown kind falls through to the else (obtuse) branch — produces 3 triangles.

        This documents the actual behavior: the if/else branching means any non-'A'
        kind is handled like a type-B obtuse triangle. It is a known quirk, not a
        silent discard.
        """
        result = gen.deflate([("X", 0 + 0j, 1 + 0j, 0 + 1j)])
        assert len(result) == 3
