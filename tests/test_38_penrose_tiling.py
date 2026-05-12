"""Tests for pieces/38-no-pattern-repeats — P3 Penrose tiling via substitution deflation."""

import importlib.util
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "38-no-pattern-repeats"

# Load by file path to avoid sys.modules collision with other pieces' generate.py
_spec = importlib.util.spec_from_file_location("gen38", PIECE_DIR / "generate.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

REPO = pathlib.Path(__file__).parent.parent
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "38-no-pattern-repeats"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_type(tris: list, kind: str) -> int:
    """Count triangles of the given kind ('A' or 'B') in the list."""
    return sum(1 for t in tris if t[0] == kind)


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# Golden ratio / PHI properties
# ---------------------------------------------------------------------------

class TestPHI:
    def test_phi_value(self):
        assert abs(gen.PHI - (1 + math.sqrt(5)) / 2) < 1e-12

    def test_phi_squared_equals_phi_plus_one(self):
        """Defining property of the golden ratio: φ² = φ + 1."""
        assert abs(gen.PHI ** 2 - gen.PHI - 1) < 1e-12

    def test_phi_inverse_equals_phi_minus_one(self):
        """1/φ = φ − 1 (since φ² = φ+1 → divide by φ)."""
        assert abs(1 / gen.PHI - (gen.PHI - 1)) < 1e-12


# ---------------------------------------------------------------------------
# make_sun
# ---------------------------------------------------------------------------

class TestMakeSun:
    def test_returns_10_triangles(self):
        tris = gen.make_sun(100.0)
        assert len(tris) == 10

    def test_all_acute(self):
        tris = gen.make_sun(100.0)
        assert all(t[0] == "A" for t in tris)

    def test_apex_at_origin(self):
        """Every triangle in the sun has its apex at the complex origin."""
        for t in gen.make_sun(200.0):
            kind, A, B, C = t
            assert abs(A) < 1e-12, f"Apex not at origin: {A}"

    def test_outer_vertices_on_circle(self):
        """B and C of each sun triangle lie on the rim circle at the given radius."""
        r = 150.0
        for kind, A, B, C in gen.make_sun(r):
            assert abs(abs(B) - r) < 1e-9, f"|B| = {abs(B)}, expected {r}"
            assert abs(abs(C) - r) < 1e-9, f"|C| = {abs(C)}, expected {r}"

    def test_apex_angle_is_36_degrees(self):
        """Each sun triangle must have a 36° apex angle (P3 acute triangle)."""
        tol = 1e-6
        for kind, A, B, C in gen.make_sun(100.0):
            vB = B - A
            vC = C - A
            cos_angle = (vB.real * vC.real + vB.imag * vC.imag) / (abs(vB) * abs(vC))
            angle_deg = math.degrees(math.acos(max(-1.0, min(1.0, cos_angle))))
            assert abs(angle_deg - 36.0) < tol, f"Apex angle = {angle_deg:.4f}°"


# ---------------------------------------------------------------------------
# deflate — counting / recurrence
# ---------------------------------------------------------------------------

class TestDeflate:
    def test_empty_list(self):
        assert gen.deflate([]) == []

    def test_single_acute_produces_two(self):
        """One acute triangle deflates into 1 acute + 1 obtuse."""
        result = gen.deflate([("A", 0 + 0j, 1 + 0j, 0 + 1j)])
        assert len(result) == 2
        assert _count_type(result, "A") == 1
        assert _count_type(result, "B") == 1

    def test_single_obtuse_produces_three(self):
        """One obtuse triangle deflates into 2 obtuse + 1 acute."""
        result = gen.deflate([("B", 0 + 0j, 1 + 0j, 0 + 1j)])
        assert len(result) == 3
        assert _count_type(result, "A") == 1
        assert _count_type(result, "B") == 2

    def test_one_generation_from_sun(self):
        """10 acute triangles → 10 acute + 10 obtuse = 20 total after one deflation."""
        tris = gen.deflate(gen.make_sun(100.0))
        assert len(tris) == 20
        assert _count_type(tris, "A") == 10
        assert _count_type(tris, "B") == 10

    def test_triangle_count_recurrence(self):
        """n_A and n_B follow: n_A' = n_A + n_B, n_B' = n_A + 2*n_B."""
        tris = gen.make_sun(100.0)
        n_A, n_B = 10, 0
        for _ in range(5):
            tris = gen.deflate(tris)
            n_A, n_B = n_A + n_B, n_A + 2 * n_B
        assert _count_type(tris, "A") == n_A
        assert _count_type(tris, "B") == n_B

    def test_ratio_approaches_phi(self):
        """After many deflations n_B/n_A converges to φ (Penrose property)."""
        tris = gen.make_sun(1.0)
        for _ in range(8):
            tris = gen.deflate(tris)
        n_A = _count_type(tris, "A")
        n_B = _count_type(tris, "B")
        assert abs(n_B / n_A - gen.PHI) < 0.01

    def test_all_output_kinds_valid(self):
        """Every produced triangle must be type 'A' or 'B'."""
        tris = gen.make_sun(1.0)
        for _ in range(4):
            tris = gen.deflate(tris)
        for t in tris:
            assert t[0] in ("A", "B"), f"Unknown kind: {t[0]}"

    def test_new_vertex_on_edge(self):
        """The deflation point P lies exactly on segment AB of the acute triangle."""
        A, B, C = 0 + 0j, 2 + 0j, 1 + 1j
        result = gen.deflate([("A", A, B, C)])
        # P = A + (B-A)/phi = 2/phi ≈ 1.236
        P_expected = A + (B - A) / gen.PHI
        # P should appear as a vertex in one of the two new triangles
        all_vertices = [v for _, a, b, c in result for v in (a, b, c)]
        assert any(abs(v - P_expected) < 1e-12 for v in all_vertices)


# ---------------------------------------------------------------------------
# generate_svg
# ---------------------------------------------------------------------------

class TestGenerateSVG:
    def test_returns_string(self):
        assert isinstance(gen.generate_svg(generations=2, size=200), str)

    def test_has_svg_namespace(self):
        svg = gen.generate_svg(generations=2, size=200)
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_viewbox_matches_size(self):
        svg = gen.generate_svg(generations=2, size=600)
        assert 'viewBox="0 0 600 600"' in svg

    def test_has_background_rect(self):
        svg = gen.generate_svg(generations=2, size=200)
        assert "<rect" in svg
        assert gen.BG_COLOR in svg

    def test_has_both_tile_colors(self):
        svg = gen.generate_svg(generations=3, size=200)
        assert gen.THICK_COLOR in svg
        assert gen.THIN_COLOR in svg

    def test_polygon_count_matches_triangles(self):
        """SVG polygon count must equal the number of triangles after deflation."""
        tris = gen.make_sun(100.0)
        for _ in range(3):
            tris = gen.deflate(tris)
        svg = gen.generate_svg(generations=3, size=200)
        assert svg.count("<polygon") == len(tris)

    def test_zero_generations_has_10_polygons(self):
        """No deflation = the original 10-triangle sun."""
        svg = gen.generate_svg(generations=0, size=400)
        assert svg.count("<polygon") == 10

    def test_default_svg_under_400kb(self):
        svg = gen.generate_svg()
        assert len(svg.encode()) < 400_000

    def test_one_decimal_coordinate_precision(self):
        """All floating-point coordinates must have at most 1 decimal place."""
        svg = gen.generate_svg(generations=2, size=200)
        for coord in re.findall(r"\d+\.\d+", svg):
            _, _, dec = coord.partition(".")
            assert len(dec) <= 1, f"Too many decimals: {coord}"

    def test_valid_xml(self):
        ET.fromstring(gen.generate_svg(generations=3, size=200))

    def test_stroke_color_present(self):
        svg = gen.generate_svg(generations=2, size=200)
        assert gen.STROKE_COLOR in svg

    def test_small_size_renders(self):
        svg = gen.generate_svg(generations=2, size=50)
        assert "<polygon" in svg
        assert 'viewBox="0 0 50 50"' in svg


# ---------------------------------------------------------------------------
# generate_thumbnail
# ---------------------------------------------------------------------------

class TestGenerateThumbnail:
    def test_returns_string(self):
        assert isinstance(gen.generate_thumbnail(size=200, generations=2), str)

    def test_has_svg_root(self):
        assert "<svg" in gen.generate_thumbnail(size=200, generations=2)

    def test_viewbox_matches_size(self):
        thumb = gen.generate_thumbnail(size=300, generations=2)
        assert 'viewBox="0 0 300 300"' in thumb

    def test_has_both_colors(self):
        thumb = gen.generate_thumbnail(size=200, generations=3)
        assert gen.THICK_COLOR in thumb
        assert gen.THIN_COLOR in thumb

    def test_fewer_triangles_than_default_piece(self):
        """Thumbnail (fewer generations) must have fewer polygons than full piece."""
        thumb = gen.generate_thumbnail(
            size=gen.THUMB_SIZE, generations=gen.THUMB_GENERATIONS
        )
        piece = gen.generate_svg(
            generations=gen.GENERATIONS, size=gen.SIZE
        )
        assert thumb.count("<polygon") < piece.count("<polygon")

    def test_valid_xml(self):
        ET.fromstring(gen.generate_thumbnail(size=200, generations=2))


# ---------------------------------------------------------------------------
# Committed file checks
# ---------------------------------------------------------------------------

class TestCommittedFiles:
    def test_piece_svg_exists(self):
        assert (PIECE_DIR / "piece.svg").is_file()

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_generate_py_exists(self):
        assert (PIECE_DIR / "generate.py").is_file()

    def test_piece_svg_has_both_colors(self):
        content = (PIECE_DIR / "piece.svg").read_text()
        assert gen.THICK_COLOR in content
        assert gen.THIN_COLOR in content

    def test_piece_svg_under_400kb(self):
        size = (PIECE_DIR / "piece.svg").stat().st_size
        assert size < 400_000, f"piece.svg is {size} bytes — must be < 400 KB"

    def test_piece_svg_valid_xml(self):
        ET.fromstring((PIECE_DIR / "piece.svg").read_text())

    def test_thumbnail_svg_valid_xml(self):
        ET.fromstring((PIECE_DIR / "thumbnail.svg").read_text())

    def test_thumbnail_smaller_than_piece(self):
        piece_size = (PIECE_DIR / "piece.svg").stat().st_size
        thumb_size = (PIECE_DIR / "thumbnail.svg").stat().st_size
        assert thumb_size < piece_size

    def test_piece_svg_has_background(self):
        content = (PIECE_DIR / "piece.svg").read_text()
        assert "<rect" in content
        assert gen.BG_COLOR in content

    def test_piece_svg_correct_triangle_count(self):
        """Committed piece.svg polygon count must match expected deflation output."""
        tris = gen.make_sun(1.0)
        for _ in range(gen.GENERATIONS):
            tris = gen.deflate(tris)
        content = (PIECE_DIR / "piece.svg").read_text()
        assert content.count("<polygon") == len(tris)

    def test_readme_mentions_penrose(self):
        readme = (PIECE_DIR / "README.md").read_text().lower()
        assert "penrose" in readme

    def test_readme_mentions_deflation(self):
        readme = (PIECE_DIR / "README.md").read_text().lower()
        assert "deflation" in readme or "substitution" in readme

    def test_readme_mentions_golden_ratio(self):
        readme = (PIECE_DIR / "README.md").read_text().lower()
        assert "golden" in readme or "phi" in readme or "φ" in readme


# ---------------------------------------------------------------------------
# pieces.json contract
# ---------------------------------------------------------------------------

class TestPiecesJSON:
    def test_entry_exists(self):
        _entry()

    def test_required_fields(self):
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
        assert required <= _entry().keys()

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

    def test_wrong_id_absent(self):
        ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
        assert "38-wrong-id" not in ids


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_large_generation_no_crash(self):
        """7 deflation generations must complete without error."""
        tris = gen.make_sun(100.0)
        for _ in range(7):
            tris = gen.deflate(tris)
        assert len(tris) > 1000

    def test_deflate_preserves_complex_vertex_type(self):
        """All vertices produced by deflation must be complex numbers."""
        tris = gen.make_sun(1.0)
        for _ in range(3):
            tris = gen.deflate(tris)
        for kind, A, B, C in tris:
            assert isinstance(A, complex)
            assert isinstance(B, complex)
            assert isinstance(C, complex)

    def test_generate_svg_reproducible(self):
        """Calling generate_svg twice with the same args must return identical output."""
        svg1 = gen.generate_svg(generations=3, size=300)
        svg2 = gen.generate_svg(generations=3, size=300)
        assert svg1 == svg2

    def test_thumbnail_generations_less_than_piece(self):
        """THUMB_GENERATIONS must be strictly less than GENERATIONS."""
        assert gen.THUMB_GENERATIONS < gen.GENERATIONS

    def test_piece_svg_has_svg_namespace(self):
        content = (PIECE_DIR / "piece.svg").read_text()
        assert 'xmlns="http://www.w3.org/2000/svg"' in content

    def test_unknown_triangle_kind_not_produced(self):
        """Deflation must never produce a triangle with a kind other than A or B."""
        tris = gen.make_sun(1.0)
        for _ in range(5):
            tris = gen.deflate(tris)
        kinds = {t[0] for t in tris}
        assert kinds <= {"A", "B"}
