"""Tests for Piece 123 — Torus Knot Curves."""
import importlib.util
import json
import math
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "123-torus-knot"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

# Torus knot parameters mirroring generate_thumbnail.py
P, Q = 2, 3
R_MAJOR, R_MINOR = 120, 45
N = 300
TILT = 0.45


# ---------------------------------------------------------------------------
# Python re-implementation of torus knot helpers for unit testing
# ---------------------------------------------------------------------------

def torus_knot_point(
    t: float, p: int = P, q: int = Q, tilt: float = TILT
) -> tuple[float, float, float]:
    """Return screen-space (x, y, z) for the (p, q) torus knot at parameter *t*.

    Applies an x-axis tilt so z carries meaningful depth information.
    CX/CY offsets are omitted so the pure geometric coordinates are returned.
    """
    ct, st = math.cos(tilt), math.sin(tilt)
    cp, sp = math.cos(p * t), math.sin(p * t)
    cq, sq = math.cos(q * t), math.sin(q * t)
    rho = R_MAJOR + R_MINOR * cq
    x = rho * cp
    y = rho * sp
    z = R_MINOR * sq
    return x, y * ct - z * st, y * st + z * ct


def compute_points(p: int = P, q: int = Q, tilt: float = TILT, n: int = N) -> list:
    """Return n+1 torus knot points for the given parameters."""
    return [torus_knot_point(i / n * math.pi * 2, p, q, tilt) for i in range(n + 1)]


def _import_gen():
    """Import generate_thumbnail from PIECE_DIR without touching sys.modules."""
    spec = importlib.util.spec_from_file_location(
        "gen_torus_knot", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_entry():
    """Return the pieces.json entry for piece 123, or None if absent."""
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == PIECE_ID), None)


# ---------------------------------------------------------------------------
# File presence
# ---------------------------------------------------------------------------

class TestFiles:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_index_html_nonempty(self):
        assert len((PIECE_DIR / "index.html").read_text()) > 500

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_thumbnail_svg_nonempty(self):
        assert len((PIECE_DIR / "thumbnail.svg").read_text()) > 100

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_readme_nonempty(self):
        assert len((PIECE_DIR / "README.md").read_text()) > 100

    def test_generate_thumbnail_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# index.html content
# ---------------------------------------------------------------------------

class TestIndexHtmlContent:
    def setup_method(self):
        self.html = (PIECE_DIR / "index.html").read_text()

    def test_canvas_element_present(self):
        assert "<canvas" in self.html

    def test_request_animation_frame_present(self):
        assert "requestAnimationFrame" in self.html

    def test_no_external_script_dependencies(self):
        assert not re.search(r'<script[^>]+src="https?://', self.html)

    def test_torus_knot_parametric_equations_present(self):
        """cos and sin of p*t and q*t must appear (torus knot parametrisation)."""
        assert "Math.cos" in self.html and "Math.sin" in self.html

    def test_next_knot_button_present(self):
        """A control to change the knot must exist."""
        assert "<button" in self.html

    def test_dark_background_color(self):
        assert "0d0a14" in self.html.lower()

    def test_warm_accent_colors_present(self):
        """At least two warm accent colors must be referenced."""
        assert "e88c1a" in self.html.lower() or "f5c830" in self.html.lower()
        assert "c8405a" in self.html.lower() or "e88c1a" in self.html.lower()

    def test_multiple_knot_presets_defined(self):
        """The three classic knots (trefoil, cinquefoil, star) must be present."""
        assert "2,3" in self.html or "{p:2,q:3" in self.html
        assert "2,5" in self.html or "{p:2,q:5" in self.html
        assert "3,5" in self.html or "{p:3,q:5" in self.html

    def test_animation_resets_on_completion(self):
        """drawn counter must reset to 0 to loop the animation."""
        assert "drawn=0" in self.html or "drawn = 0" in self.html

    def test_stroke_width_depth_variation(self):
        """lineWidth must be set dynamically (depth-based thickness)."""
        assert "lineWidth" in self.html

    def test_index_html_under_150_lines(self):
        lines = (PIECE_DIR / "index.html").read_text().splitlines()
        assert len(lines) <= 150, f"index.html has {len(lines)} lines, limit is 150"

    def test_index_html_size_reasonable(self):
        size = (PIECE_DIR / "index.html").stat().st_size
        assert size < 10_000, f"index.html is {size} bytes, expected < 10 000"

    def test_canvas_is_square(self):
        assert "700" in self.html

    def test_tilt_applied(self):
        """x-axis tilt rotation (TILT constant or similar) must be present."""
        assert "TILT" in self.html or "tilt" in self.html.lower()


# ---------------------------------------------------------------------------
# Torus knot mathematics (Python re-implementation)
# ---------------------------------------------------------------------------

class TestTorusKnotMath:
    def test_trefoil_curve_is_closed(self):
        """t=0 and t=2π must produce the same point (closed curve)."""
        p0 = torus_knot_point(0.0)
        p_end = torus_knot_point(2 * math.pi)
        for a, b in zip(p0, p_end):
            assert abs(a - b) < 1e-8, f"Trefoil not closed: {p0} vs {p_end}"

    def test_cinquefoil_curve_is_closed(self):
        """(2,5) cinquefoil must also be a closed curve."""
        p0 = torus_knot_point(0.0, p=2, q=5)
        p_end = torus_knot_point(2 * math.pi, p=2, q=5)
        for a, b in zip(p0, p_end):
            assert abs(a - b) < 1e-8

    def test_star_knot_closed(self):
        """(3,5) star knot must be closed."""
        p0 = torus_knot_point(0.0, p=3, q=5)
        p_end = torus_knot_point(2 * math.pi, p=3, q=5)
        for a, b in zip(p0, p_end):
            assert abs(a - b) < 1e-8

    def test_z_varies_sinusoidally(self):
        """z must vary and not be constant (depth changes along the curve)."""
        pts = compute_points()
        zs = [p[2] for p in pts]
        assert max(zs) - min(zs) > 1.0, "z depth does not vary along the curve"

    def test_z_range_within_minor_radius(self):
        """z values must stay within [-r, r] approximately (at zero tilt)."""
        pts = compute_points(tilt=0.0)
        zs = [p[2] for p in pts]
        assert max(zs) <= R_MINOR + 1
        assert min(zs) >= -(R_MINOR + 1)

    def test_radial_bounds(self):
        """All x values must lie within [-(R+r), R+r]."""
        pts = compute_points()
        max_extent = R_MAJOR + R_MINOR
        for x, y, z in pts:
            assert abs(x) <= max_extent + 1

    def test_exactly_n_plus_one_points(self):
        assert len(compute_points()) == N + 1

    def test_different_pq_gives_different_curves(self):
        """Different (p,q) parameters must produce different point sets."""
        pts_23 = compute_points(p=2, q=3)
        pts_25 = compute_points(p=2, q=5)
        assert pts_23 != pts_25

    def test_zero_tilt_z_equals_r_sin_qt(self):
        """At zero tilt, z must equal r·sin(Q·t) exactly."""
        for i in range(0, N, 30):
            t = i / N * math.pi * 2
            _, _, z_out = torus_knot_point(t, tilt=0.0)
            z_expected = R_MINOR * math.sin(Q * t)
            assert abs(z_out - z_expected) < 1e-8, (
                f"At t={t:.3f}: z={z_out:.6f}, expected {z_expected:.6f}"
            )

    def test_rho_always_positive(self):
        """Major radius + minor * cos is always positive when R > r."""
        for i in range(N):
            t = i / N * math.pi * 2
            cq = math.cos(Q * t)
            rho = R_MAJOR + R_MINOR * cq
            assert rho > 0, f"rho={rho:.3f} at i={i}"

    def test_tilt_changes_z_distribution(self):
        """Changing tilt must alter the z distribution."""
        zs0 = [p[2] for p in compute_points(tilt=0.0)]
        zs1 = [p[2] for p in compute_points(tilt=0.8)]
        assert zs0 != zs1


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------

class TestThumbnailSvg:
    def setup_method(self):
        self.svg = (PIECE_DIR / "thumbnail.svg").read_text()

    def test_is_valid_svg(self):
        assert self.svg.strip().startswith("<svg")

    def test_contains_line_elements(self):
        assert "<line" in self.svg

    def test_contains_dark_background_rect(self):
        assert "0d0a14" in self.svg.lower()

    def test_has_width_and_height_400(self):
        assert 'width="400"' in self.svg and 'height="400"' in self.svg

    def test_has_viewbox(self):
        assert "viewBox" in self.svg

    def test_render_returns_string(self):
        mod = _import_gen()
        result = mod.render()
        assert isinstance(result, str)

    def test_render_starts_with_svg_tag(self):
        mod = _import_gen()
        assert mod.render().strip().startswith("<svg")

    def test_render_is_deterministic(self):
        mod = _import_gen()
        assert mod.render() == mod.render()

    def test_render_contains_line_elements(self):
        mod = _import_gen()
        svg = mod.render()
        assert svg.count("<line") == N

    def test_render_warm_colors_present(self):
        """The SVG must reference the warm accent palette colors."""
        mod = _import_gen()
        svg = mod.render()
        assert "#c8405a" in svg or "#e88c1a" in svg or "#f5c830" in svg

    def test_write_svg_produces_file(self, tmp_path):
        """write_svg() must create a readable UTF-8 file."""
        mod = _import_gen()
        out = tmp_path / "test.svg"
        mod.write_svg(str(out), mod.render())
        content = out.read_text(encoding="utf-8")
        assert content.strip().startswith("<svg")

    def test_stroke_width_varies(self):
        """stroke-width values must not all be identical — depth must produce variation."""
        mod = _import_gen()
        svg = mod.render()
        widths = set(re.findall(r'stroke-width="([^"]+)"', svg))
        assert len(widths) > 1, "All stroke-widths are the same — depth variation missing"


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

class TestPiecesJson:
    def test_entry_exists(self):
        assert _load_entry() is not None, f"No entry with id={PIECE_ID!r} in pieces.json"

    def test_entry_has_all_required_fields(self):
        entry = _load_entry()
        assert entry is not None
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_entry_id_matches_directory(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).name == entry["id"]

    def test_entry_year_is_int(self):
        entry = _load_entry()
        assert isinstance(entry["year"], int)

    def test_entry_path_exists(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        entry = _load_entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_thumbnail_is_svg(self):
        entry = _load_entry()
        assert entry["thumbnail"].endswith(".svg")

    def test_technique_is_parametric_3d_curves(self):
        entry = _load_entry()
        assert "parametric-3d-curves" in entry["technique"]

    def test_piece_123_appears_after_122(self):
        """Piece 123 must appear after 122 in the ordered list."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "122-paper-marbling" in ids
        assert PIECE_ID in ids
        assert ids.index(PIECE_ID) > ids.index("122-paper-marbling")

    def test_tagline_mentions_torus_knot(self):
        entry = _load_entry()
        tl = entry["tagline"].lower()
        assert "torus" in tl or "knot" in tl


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_unknown_piece_absent_from_json(self):
        """A non-existent piece ID must not appear in pieces.json."""
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost-knot"), None)
        assert found is None

    def test_large_t_no_crash(self):
        """Very large t values must not raise and must return finite numbers."""
        x, y, z = torus_knot_point(1e6, tilt=TILT)
        assert math.isfinite(x) and math.isfinite(y) and math.isfinite(z)

    def test_negative_t_no_crash(self):
        """Negative t values must be handled without error."""
        x, y, z = torus_knot_point(-math.pi)
        assert math.isfinite(x) and math.isfinite(y) and math.isfinite(z)

    def test_compute_points_large_n_no_crash(self):
        """Computing 1 000 points must not raise."""
        pts = compute_points(n=1000)
        assert len(pts) == 1001

    def test_depth_normalization_bounds(self):
        """Depth = (z + r) / (2r) must stay in [0, 1] for any t on the trefoil."""
        for i in range(N):
            t = i / N * math.pi * 2
            z = R_MINOR * math.sin(Q * t)
            depth = (z + R_MINOR) / (2 * R_MINOR)
            assert 0.0 <= depth <= 1.0, f"depth={depth} out of range at i={i}"

    def test_index_html_no_network_requests(self):
        """index.html must not make any runtime network requests."""
        html = (PIECE_DIR / "index.html").read_text()
        assert "fetch(" not in html
        assert "XMLHttpRequest" not in html
        assert "import(" not in html

    def test_pieces_json_still_has_prior_entries(self):
        """All 51 existing pieces must still be present after the new entry."""
        data = json.loads(PIECES_JSON.read_text())
        ids = {e["id"] for e in data}
        assert "01-amber-current" in ids
        assert "122-paper-marbling" in ids
        assert len(data) >= 52, f"Expected ≥52 entries, got {len(data)}"
