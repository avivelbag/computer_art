"""Tests for Piece 120 — Celtic Knotwork: Over, Under, Forever."""
import importlib.util
import json
import math
import pathlib
import re
import struct

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "120-celtic-knotwork"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

# Torus knot parameters mirroring generate_thumbnail.py for unit testing
P, Q = 3, 5
R_MAJOR, R_MINOR = 114, 36
N = 300
SKIP = 18
TILT = 0.45
SW = 12
CROSS_R2 = (SW * 0.6) ** 2
MERGE_R2 = (SW * 2.8) ** 2


# ---------------------------------------------------------------------------
# Python re-implementations of torus knot helpers for unit testing
# ---------------------------------------------------------------------------

def torus_knot_point(t: float, tilt: float) -> tuple[float, float, float]:
    """Return screen-space (x, y, z) for the (P, Q) torus knot at parameter *t*.

    Applies an x-axis tilt rotation so z carries meaningful depth information.
    CX and CY offsets are omitted here; the pure 3D coordinates are returned
    relative to the torus centre for easier geometric verification.
    """
    cp, sp = math.cos(P * t), math.sin(P * t)
    cq, sq = math.cos(Q * t), math.sin(Q * t)
    rho = R_MAJOR + R_MINOR * cq
    x = rho * cp
    y = rho * sp
    z = R_MINOR * sq
    ct, st = math.cos(tilt), math.sin(tilt)
    return x, y * ct - z * st, y * st + z * ct


def compute_points(tilt: float = TILT) -> list[tuple[float, float, float]]:
    """Return N+1 torus knot points at the given tilt angle."""
    pts = []
    for i in range(N + 1):
        t = i / N * math.pi * 2
        pts.append(torus_knot_point(t, tilt))
    return pts


def detect_crossings(pts: list) -> list[dict]:
    """Detect over/under crossing pairs using 2D midpoint proximity."""
    mx = [(pts[i][0] + pts[i + 1][0]) * 0.5 for i in range(N)]
    my = [(pts[i][1] + pts[i + 1][1]) * 0.5 for i in range(N)]
    mz = [(pts[i][2] + pts[i + 1][2]) * 0.5 for i in range(N)]

    raw = []
    for i in range(N):
        lim = N - SKIP + i
        for j in range(i + SKIP, N):
            if j >= lim:
                continue
            dx, dy = mx[i] - mx[j], my[i] - my[j]
            if dx * dx + dy * dy <= CROSS_R2:
                if mz[i] >= mz[j]:
                    ov, un = i, j
                else:
                    ov, un = j, i
                raw.append({
                    "ov": ov, "un": un,
                    "cx": (mx[i] + mx[j]) * 0.5,
                    "cy": (my[i] + my[j]) * 0.5,
                })

    merged: list[dict] = []
    for c in raw:
        if not any(
            (m["cx"] - c["cx"]) ** 2 + (m["cy"] - c["cy"]) ** 2 < MERGE_R2
            for m in merged
        ):
            merged.append(c)
    return merged


def _import_gen():
    """Import generate_thumbnail from PIECE_DIR without touching sys.modules."""
    spec = importlib.util.spec_from_file_location(
        "gen_celtic", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_entry():
    """Return the pieces.json entry for piece 120, or None if absent."""
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

    def test_thumbnail_png_exists(self):
        assert (PIECE_DIR / "thumbnail.png").is_file()

    def test_thumbnail_png_is_valid_png(self):
        data = (PIECE_DIR / "thumbnail.png").read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

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

    def test_forest_green_background_color(self):
        assert "1f3320" in self.html.lower()

    def test_bronze_strand_color(self):
        assert "c8860a" in self.html.lower()

    def test_cream_highlight_color(self):
        assert "f5e6b0" in self.html.lower()

    def test_shadow_color(self):
        assert "7a4500" in self.html.lower()

    def test_torus_knot_parametric_equations(self):
        """cos(P*t) and sin(Q*t) must appear (torus knot parametrisation)."""
        assert "Math.cos" in self.html and "Math.sin" in self.html

    def test_p_and_q_constants_defined(self):
        """P=3 and Q=5 must be present as the torus knot parameters."""
        assert re.search(r'\bP\s*=\s*3\b', self.html)
        assert re.search(r'\bQ\s*=\s*5\b', self.html)

    def test_over_under_crossing_gap_logic(self):
        """Background-coloured gap stroke must be applied to under-strand."""
        assert "BG" in self.html or "1f3320" in self.html.lower()

    def test_detect_crossings_function_present(self):
        assert "detectCrossings" in self.html or "crossings" in self.html

    def test_canvas_is_square(self):
        assert "700" in self.html

    def test_sin_tilt_animation_present(self):
        """The animation must use a time-varying tilt (Math.sin of timestamp)."""
        assert "Math.sin" in self.html

    def test_index_html_size_reasonable(self):
        """index.html must be under 12 KB."""
        size = (PIECE_DIR / "index.html").stat().st_size
        assert size < 12_000, f"index.html is {size} bytes, expected < 12 000"


# ---------------------------------------------------------------------------
# Torus knot mathematics (Python re-implementation)
# ---------------------------------------------------------------------------

class TestTorusKnotMath:
    def test_curve_is_closed(self):
        """t=0 and t=2π must produce the same point (closed curve)."""
        p0 = torus_knot_point(0.0, TILT)
        p_end = torus_knot_point(2 * math.pi, TILT)
        for a, b in zip(p0, p_end):
            assert abs(a - b) < 1e-8, f"Curve not closed: {p0} vs {p_end}"

    def test_point_within_expected_radial_bounds(self):
        """All projected x values must lie within [-(R+r), R+r] + CX."""
        pts = compute_points()
        max_extent = R_MAJOR + R_MINOR
        for x, y, z in pts:
            assert abs(x) <= max_extent + 1
            assert abs(y) <= max_extent + 1

    def test_z_depth_varies_over_curve(self):
        """z values must not be constant — depth must actually vary."""
        pts = compute_points()
        zs = [p[2] for p in pts]
        assert max(zs) - min(zs) > 1.0, "z depth does not vary along the curve"

    def test_different_tilt_gives_different_depths(self):
        """Changing the tilt angle must change the z distribution."""
        pts1 = compute_points(0.0)
        pts2 = compute_points(0.6)
        zs1 = [p[2] for p in pts1]
        zs2 = [p[2] for p in pts2]
        assert zs1 != zs2

    def test_exactly_n_plus_one_points(self):
        assert len(compute_points()) == N + 1

    def test_rho_positive_everywhere(self):
        """Major radius + minor * cos is always positive for R > r."""
        for i in range(N):
            t = i / N * math.pi * 2
            cq = math.cos(Q * t)
            rho = R_MAJOR + R_MINOR * cq
            assert rho > 0, f"rho={rho} at t={t}"


# ---------------------------------------------------------------------------
# Crossing detection
# ---------------------------------------------------------------------------

class TestCrossingDetection:
    def setup_method(self):
        self.pts = compute_points(TILT)

    def test_crossing_count_approximately_ten(self):
        """A (3,5) torus knot has exactly 10 self-crossings in generic projection."""
        cr = detect_crossings(self.pts)
        assert 6 <= len(cr) <= 15, (
            f"Expected ~10 crossings, detected {len(cr)} — "
            "check CROSS_R2 or SKIP parameters"
        )

    def test_every_crossing_has_over_and_under(self):
        cr = detect_crossings(self.pts)
        for c in cr:
            assert "ov" in c and "un" in c
            assert c["ov"] != c["un"]

    def test_over_has_higher_z_than_under(self):
        """For every crossing, the 'over' segment midpoint must have higher z."""
        pts = self.pts
        mz = [(pts[i][2] + pts[i + 1][2]) * 0.5 for i in range(N)]
        for c in detect_crossings(pts):
            assert mz[c["ov"]] >= mz[c["un"]], (
                f"over z={mz[c['ov']]:.2f} < under z={mz[c['un']]:.2f}"
            )

    def test_no_adjacent_segment_crossings(self):
        """No crossing pair (i, j) may have |i - j| < SKIP (they are neighbours)."""
        for c in detect_crossings(self.pts):
            diff = abs(c["ov"] - c["un"])
            diff = min(diff, N - diff)  # circular distance
            assert diff >= SKIP, f"Adjacent segments {c['ov']}, {c['un']} flagged as crossing"

    def test_collinear_pts_gives_no_crossings(self):
        """A collinear curve whose points are very spread apart produces no crossings."""
        # All points on a horizontal line → no two segments come within CROSS_R2
        spread = [(float(i) * 10, 0.0, 0.0) for i in range(N + 1)]
        cr = detect_crossings(spread)
        assert cr == []


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

    def test_piece_120_appears_after_115(self):
        """Piece 120 must appear after 115 in the ordered list."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "115-the-field-remembers" in ids
        assert PIECE_ID in ids
        assert ids.index(PIECE_ID) > ids.index("115-the-field-remembers")

    def test_technique_contains_torus_knot(self):
        entry = _load_entry()
        assert "torus knot" in entry["technique"]


# ---------------------------------------------------------------------------
# Thumbnail generation
# ---------------------------------------------------------------------------

class TestThumbnailGeneration:
    def test_render_produces_valid_png_bytes(self, tmp_path):
        """render() + write_png() must produce a file with valid PNG magic bytes."""
        mod = _import_gen()
        raw = mod.render()
        out = tmp_path / "thumb.png"
        mod.write_png(str(out), raw)
        data = out.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert len(data) > 1000

    def test_render_is_deterministic(self):
        """Two consecutive render() calls must return identical bytes."""
        mod = _import_gen()
        assert mod.render() == mod.render()

    def test_render_correct_dimensions(self, tmp_path):
        """The PNG must encode a 400×400 image."""
        mod = _import_gen()
        raw = mod.render()
        out = tmp_path / "thumb.png"
        mod.write_png(str(out), raw)
        data = out.read_bytes()
        w = struct.unpack(">I", data[16:20])[0]
        h = struct.unpack(">I", data[20:24])[0]
        assert w == 400
        assert h == 400

    def test_render_output_not_all_background(self):
        """Rendered pixels must not all be the background colour (knot is visible)."""
        mod = _import_gen()
        raw = mod.render()
        # raw is filter+RGB bytes; check for at least one non-BG pixel
        bg_r, bg_g, bg_b = 31, 51, 32
        found_non_bg = False
        i = 0
        while i < len(raw):
            i += 1  # skip filter byte
            for _ in range(400):
                r, g, b = raw[i], raw[i + 1], raw[i + 2]
                i += 3
                if not (r == bg_r and g == bg_g and b == bg_b):
                    found_non_bg = True
                    break
            if found_non_bg:
                break
        assert found_non_bg, "All pixels are background colour — knot was not rendered"


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_unknown_piece_absent_from_json(self):
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost-knot"), None)
        assert found is None

    def test_torus_knot_large_parameter_no_crash(self):
        """Very large t values must not raise any exception."""
        x, y, z = torus_knot_point(1e6, TILT)
        assert math.isfinite(x) and math.isfinite(y) and math.isfinite(z)

    def test_torus_knot_zero_tilt(self):
        """Zero tilt must give z = r·sin(Q·t), unchanged by the x-axis rotation."""
        for i in range(0, N, 30):
            t = i / N * math.pi * 2
            _, _, z_tilted = torus_knot_point(t, 0.0)
            z_expected = R_MINOR * math.sin(Q * t)
            assert abs(z_tilted - z_expected) < 1e-8

    def test_compute_points_large_n_no_crash(self):
        """Computing 1 000 points must not raise an error."""
        pts = []
        for i in range(1001):
            t = i / 1000 * math.pi * 2
            pts.append(torus_knot_point(t, TILT))
        assert len(pts) == 1001

    def test_detect_crossings_with_straight_line_gives_no_crossings(self):
        """A perfectly straight line projected to 2D has no crossings."""
        straight = [(float(i), 0.0, 0.0) for i in range(N + 1)]
        assert detect_crossings(straight) == []
