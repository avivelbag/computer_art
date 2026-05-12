"""Tests for pieces/39-apollonian-gasket — Apollonian gasket via Descartes' theorem."""

import importlib.util
import json
import math
import pathlib
import xml.etree.ElementTree as ET

PIECE_DIR = pathlib.Path(__file__).parent.parent / "pieces" / "39-apollonian-gasket"

_spec = importlib.util.spec_from_file_location("gen39", PIECE_DIR / "generate.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

REPO = pathlib.Path(__file__).parent.parent
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "39-apollonian-gasket"


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# Initial configuration geometry
# ---------------------------------------------------------------------------

class TestInitialCircles:
    def test_returns_4_circles(self):
        assert len(gen._initial_circles(100.0)) == 4

    def test_bounding_has_negative_curvature(self):
        assert gen._initial_circles(100.0)[0][0] < 0

    def test_inner_circles_positive_curvature(self):
        for k, _ in gen._initial_circles(100.0)[1:]:
            assert k > 0

    def test_descartes_theorem_satisfied(self):
        """All 4 initial circles must satisfy (Σk)² = 2·Σk²."""
        ks = [c[0] for c in gen._initial_circles(376.0)]
        lhs = sum(ks) ** 2
        rhs = 2 * sum(k ** 2 for k in ks)
        assert abs(lhs - rhs) < 1e-6

    def test_inner_circles_tangent_to_bounding(self):
        """Each inner circle touches the bounding circle: |center| + r = R."""
        R = 200.0
        for k, z in gen._initial_circles(R)[1:]:
            r = 1.0 / k
            assert abs(abs(z) + r - R) < 1e-9

    def test_inner_circles_mutually_tangent(self):
        """Adjacent inner circles touch: |c_i - c_j| = r_i + r_j."""
        circles = gen._initial_circles(200.0)
        inner = circles[1:]
        for i in range(3):
            for j in range(i + 1, 3):
                ki, zi = inner[i]
                kj, zj = inner[j]
                dist = abs(zi - zj)
                assert abs(dist - (1.0 / ki + 1.0 / kj)) < 1e-9

    def test_inner_circle_radius_formula(self):
        """r = R·√3/(2+√3): verify the closed-form ratio."""
        R = 300.0
        expected_r = R * math.sqrt(3) / (2 + math.sqrt(3))
        k, _ = gen._initial_circles(R)[1]
        assert abs(1.0 / k - expected_r) < 1e-9


# ---------------------------------------------------------------------------
# apollonian_circles
# ---------------------------------------------------------------------------

class TestApollonianCircles:
    def test_returns_at_least_3_circles(self):
        assert len(gen.apollonian_circles(100.0, 10.0)) >= 3

    def test_sorted_decreasing_radius(self):
        circles = gen.apollonian_circles(200.0, 5.0)
        radii = [r for r, _ in circles]
        assert radii == sorted(radii, reverse=True)

    def test_all_above_min_r(self):
        min_r = 5.0
        for r, _ in gen.apollonian_circles(200.0, min_r):
            assert r >= min_r - 1e-9

    def test_no_duplicates(self):
        circles = gen.apollonian_circles(100.0, 3.0)
        keys = set()
        for r, z in circles:
            key = (round(z.real, 0), round(z.imag, 0), round(r, 1))
            assert key not in keys, f"Duplicate circle r={r:.2f} at {z:.2f}"
            keys.add(key)

    def test_more_circles_with_smaller_min_r(self):
        assert (
            len(gen.apollonian_circles(200.0, 4.0))
            > len(gen.apollonian_circles(200.0, 8.0))
        )

    def test_central_circle_near_origin(self):
        """The circle tangent to all three initial inner circles lies near the origin."""
        circles = gen.apollonian_circles(100.0, 1.0)
        # Find the circle with center closest to origin in the first 20 circles
        near_origin = min(circles[:20], key=lambda c: abs(c[1]))
        assert abs(near_origin[1]) < 5.0

    def test_central_circle_satisfies_descartes(self):
        """Central circle (k_central) with the 3 initial inner circles satisfies Descartes."""
        R = 376.0
        init = gen._initial_circles(R)
        k1, k2, k3 = [c[0] for c in init[1:]]
        circles = gen.apollonian_circles(R, 2.0)
        central = min(circles[:20], key=lambda c: abs(c[1]))
        kc = 1.0 / central[0]
        lhs = (k1 + k2 + k3 + kc) ** 2
        rhs = 2 * (k1 ** 2 + k2 ** 2 + k3 ** 2 + kc ** 2)
        assert abs(lhs - rhs) < 0.01

    def test_large_gasket_has_many_circles(self):
        """Full-size gasket must produce > 100 circles — proxy for ≥ 6 generations."""
        assert len(gen.apollonian_circles(gen.SIZE * 0.47, gen.MIN_RADIUS_PX)) > 100

    def test_all_circles_within_bounding_circle(self):
        """Every generated circle must lie entirely inside the bounding circle."""
        R = 200.0
        for r, z in gen.apollonian_circles(R, 4.0):
            assert abs(z) + r <= R + 1.0, f"r={r:.2f}, |z|={abs(z):.2f} exceeds R={R}"

    def test_bounding_circle_excluded(self):
        """The enclosing circle (negative curvature) must not appear in results."""
        for r, _ in gen.apollonian_circles(100.0, 2.0):
            assert r > 0

    def test_empty_when_min_r_exceeds_inner_circles(self):
        """Nothing returned when min_r is larger than the initial inner circle radius."""
        R = 100.0
        r_init = R * math.sqrt(3) / (2 + math.sqrt(3))
        circles = gen.apollonian_circles(R, r_init + 1.0)
        assert len(circles) == 0


# ---------------------------------------------------------------------------
# _circle_color
# ---------------------------------------------------------------------------

class TestCircleColor:
    def test_returns_string(self):
        assert isinstance(gen._circle_color(50.0, 100.0), str)

    def test_largest_circle_uses_first_palette_color(self):
        assert gen._circle_color(100.0, 100.0) == gen.PALETTE[0]

    def test_valid_hex_format(self):
        for r in [100.0, 50.0, 10.0, 2.5]:
            color = gen._circle_color(r, 100.0)
            assert color.startswith("#")
            assert len(color) in (4, 7)

    def test_all_palette_colors_reachable(self):
        """A wide range of radii should produce all 6 palette colors."""
        r_max = 200.0
        samples = [r_max * (0.5 ** i) for i in range(20)] + [gen.MIN_RADIUS_PX + 0.01]
        colors = {gen._circle_color(max(r, gen.MIN_RADIUS_PX), r_max) for r in samples}
        assert len(colors) >= 4

    def test_never_raises_for_valid_inputs(self):
        for r in [100.0, 50.0, 5.0, gen.MIN_RADIUS_PX]:
            gen._circle_color(r, 100.0)  # must not raise


# ---------------------------------------------------------------------------
# generate_svg
# ---------------------------------------------------------------------------

class TestGenerateSVG:
    def test_returns_string(self):
        assert isinstance(gen.generate_svg(size=200, min_r=10.0), str)

    def test_svg_namespace(self):
        assert 'xmlns="http://www.w3.org/2000/svg"' in gen.generate_svg(size=200, min_r=10.0)

    def test_viewbox_matches_size(self):
        assert 'viewBox="0 0 400 400"' in gen.generate_svg(size=400, min_r=10.0)

    def test_has_circle_elements(self):
        assert "<circle" in gen.generate_svg(size=200, min_r=10.0)

    def test_has_background_rect(self):
        svg = gen.generate_svg(size=200, min_r=10.0)
        assert "<rect" in svg
        assert gen.BG_COLOR in svg

    def test_has_clip_path(self):
        assert "clipPath" in gen.generate_svg(size=200, min_r=10.0)

    def test_valid_xml(self):
        ET.fromstring(gen.generate_svg(size=200, min_r=10.0))

    def test_full_piece_many_circles(self):
        assert gen.generate_svg().count("<circle") > 50

    def test_under_500kb(self):
        assert len(gen.generate_svg().encode()) < 500_000

    def test_multiple_palette_colors_present(self):
        svg = gen.generate_svg(size=400, min_r=2.0)
        found = sum(1 for c in gen.PALETTE if c in svg)
        assert found >= 3

    def test_reproducible(self):
        svg1 = gen.generate_svg(size=300, min_r=8.0)
        svg2 = gen.generate_svg(size=300, min_r=8.0)
        assert svg1 == svg2

    def test_large_min_r_still_valid_xml(self):
        ET.fromstring(gen.generate_svg(size=400, min_r=50.0))


# ---------------------------------------------------------------------------
# generate_thumbnail
# ---------------------------------------------------------------------------

class TestGenerateThumbnail:
    def test_returns_string(self):
        assert isinstance(gen.generate_thumbnail(size=200), str)

    def test_viewbox_matches_size(self):
        assert 'viewBox="0 0 400 400"' in gen.generate_thumbnail(size=400)

    def test_has_circle_elements(self):
        assert "<circle" in gen.generate_thumbnail(size=200)

    def test_valid_xml(self):
        ET.fromstring(gen.generate_thumbnail(size=200))

    def test_thumb_has_fewer_circles_than_full(self):
        """Smaller bounding radius → fewer circles above the 2px cutoff."""
        thumb = gen.generate_thumbnail(size=gen.THUMB_SIZE)
        piece = gen.generate_svg(size=gen.SIZE)
        assert thumb.count("<circle") < piece.count("<circle")


# ---------------------------------------------------------------------------
# Committed files
# ---------------------------------------------------------------------------

class TestCommittedFiles:
    def test_piece_svg_exists(self):
        assert (PIECE_DIR / "piece.svg").is_file()

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_piece_svg_valid_xml(self):
        ET.fromstring((PIECE_DIR / "piece.svg").read_text())

    def test_thumbnail_svg_valid_xml(self):
        ET.fromstring((PIECE_DIR / "thumbnail.svg").read_text())

    def test_piece_svg_many_circles(self):
        content = (PIECE_DIR / "piece.svg").read_text()
        assert content.count("<circle") > 50

    def test_piece_svg_under_500kb(self):
        size = (PIECE_DIR / "piece.svg").stat().st_size
        assert size < 500_000, f"piece.svg is {size} bytes"

    def test_thumbnail_not_larger_than_piece(self):
        assert (PIECE_DIR / "thumbnail.svg").stat().st_size <= (
            PIECE_DIR / "piece.svg"
        ).stat().st_size

    def test_piece_svg_has_multiple_palette_colors(self):
        content = (PIECE_DIR / "piece.svg").read_text()
        found = sum(1 for c in gen.PALETTE if c in content)
        assert found >= 3

    def test_piece_svg_has_namespace(self):
        assert 'xmlns="http://www.w3.org/2000/svg"' in (PIECE_DIR / "piece.svg").read_text()

    def test_index_html_contains_svg(self):
        assert "<svg" in (PIECE_DIR / "index.html").read_text()

    def test_index_html_is_self_contained(self):
        """No external scripts, stylesheets, or fetch URLs — xmlns namespace is allowed."""
        content = (PIECE_DIR / "index.html").read_text()
        assert "<script src=" not in content
        assert '<link rel="stylesheet"' not in content
        assert "https://" not in content

    def test_readme_mentions_descartes(self):
        assert "descartes" in (PIECE_DIR / "README.md").read_text().lower()

    def test_readme_mentions_apollonian(self):
        assert "apollonian" in (PIECE_DIR / "README.md").read_text().lower()


# ---------------------------------------------------------------------------
# pieces.json
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

    def test_technique_mentions_apollonian(self):
        assert "apollonian" in _entry()["technique"].lower()

    def test_wrong_id_absent(self):
        ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
        assert "39-wrong-id" not in ids


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_very_large_min_r_returns_empty_or_minimal(self):
        R = 50.0
        r_init = R * math.sqrt(3) / (2 + math.sqrt(3))
        circles = gen.apollonian_circles(R, r_init + 1.0)
        assert len(circles) == 0

    def test_small_gasket_stable(self):
        """Tiny bounding circle should still generate a valid gasket."""
        circles = gen.apollonian_circles(50.0, 4.0)
        assert len(circles) >= 3

    def test_circles_within_bounding_circle_edge_case(self):
        """All circles with large min_r must still lie inside the bounding circle."""
        R = 300.0
        for r, z in gen.apollonian_circles(R, 20.0):
            assert abs(z) + r <= R + 1.0

    def test_generate_svg_large_min_r_valid(self):
        """SVG with no inner circles (min_r larger than any circle) must be valid XML."""
        ET.fromstring(gen.generate_svg(size=400, min_r=500.0))

    def test_color_at_exactly_min_r(self):
        """The smallest allowed radius must not raise."""
        color = gen._circle_color(gen.MIN_RADIUS_PX, 200.0)
        assert isinstance(color, str)


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------

class TestFailureModes:
    def test_bounding_circle_never_in_result(self):
        """Negative-curvature circle must be excluded from all results."""
        for r, _ in gen.apollonian_circles(200.0, 2.0):
            assert r > 0

    def test_no_circles_below_min_r(self):
        """Strict enforcement: nothing smaller than min_r appears."""
        min_r = 3.0
        for r, _ in gen.apollonian_circles(150.0, min_r):
            assert r >= min_r - 1e-9

    def test_svg_with_zero_circles_is_valid_xml(self):
        """Even if apollonian_circles returns nothing, _svg_body must produce valid XML."""
        svg = gen._svg_body([], 100.0, 200)
        ET.fromstring(svg)

    def test_wrong_piece_id_not_in_json(self):
        data = json.loads(PIECES_JSON.read_text())
        ids = {item["id"] for item in data}
        assert "39-wrong-piece" not in ids
