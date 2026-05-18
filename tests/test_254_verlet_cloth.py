"""Tests for Piece 254 — Cloth: What Falls Together."""
import json
import math
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "254-verlet-cloth"
INDEX = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "254-verlet-cloth"


# ---------------------------------------------------------------------------
# Python mirror of Verlet cloth physics for logic tests
# ---------------------------------------------------------------------------


def make_cloth(rows: int, cols: int, rest: float, start_x: float = 0.0, start_y: float = 0.0):
    """
    Initialise a flat cloth grid and return (px, py, ppx, ppy, pin).

    px[r][c] and py[r][c] are current positions; ppx/ppy are previous positions
    (equal to current at rest).  pin[r][c] is 1 when the particle is immovable.
    The top row is pinned at every 5th column plus the last column, matching the
    piece's logic.
    """
    px  = [[start_x + c * rest for c in range(cols)] for r in range(rows)]
    py  = [[start_y + r * rest for c in range(cols)] for r in range(rows)]
    ppx = [row[:] for row in px]
    ppy = [row[:] for row in py]
    pin = [[False] * cols for _ in range(rows)]
    for c in range(cols):
        if c % 5 == 0 or c == cols - 1:
            pin[0][c] = True
    return px, py, ppx, ppy, pin


def build_constraints(rows: int, cols: int, rest: float):
    """
    Build structural (horizontal + vertical) and shear (diagonal) spring constraints.

    Returns list of (a_row, a_col, b_row, b_col, rest_length) tuples.
    """
    constraints = []
    diag_rest = rest * math.sqrt(2)
    # Horizontal
    for r in range(rows):
        for c in range(cols - 1):
            constraints.append((r, c, r, c + 1, rest))
    # Vertical
    for r in range(rows - 1):
        for c in range(cols):
            constraints.append((r, c, r + 1, c, rest))
    # Shear diagonals
    for r in range(rows - 1):
        for c in range(cols - 1):
            constraints.append((r, c,     r + 1, c + 1, diag_rest))
            constraints.append((r, c + 1, r + 1, c,     diag_rest))
    return constraints


def verlet_step(px, py, ppx, ppy, pin, gravity: float, damp: float = 0.997,
                wind_amp: float = 0.0, t: int = 0,
                wind_freq: float = 0.0015, wind_k: float = 0.055):
    """
    One Verlet integration step: infer velocity from position delta, apply forces.

    Modifies px, py, ppx, ppy in place.  Pinned particles are untouched.
    Wind force Fx = wind_amp * sin(t * wind_freq + x * wind_k).
    """
    rows = len(px)
    cols = len(px[0])
    for r in range(rows):
        for c in range(cols):
            if pin[r][c]:
                continue
            vx = (px[r][c] - ppx[r][c]) * damp
            vy = (py[r][c] - ppy[r][c]) * damp
            wx = wind_amp * math.sin(t * wind_freq + px[r][c] * wind_k)
            ppx[r][c] = px[r][c]
            ppy[r][c] = py[r][c]
            px[r][c] += vx + wx
            py[r][c] += vy + gravity


def constraint_step(px, py, pin, constraints, iters: int = 5):
    """
    Iteratively project all constraints to enforce rest lengths.

    Each iteration corrects particle positions by half the length error on each
    end of the spring (full correction for unpinned particles, zero for pinned).
    Modifies px and py in place.
    """
    for _ in range(iters):
        for ar, ac, br, bc, rest_len in constraints:
            dx = px[br][bc] - px[ar][ac]
            dy = py[br][bc] - py[ar][ac]
            d = math.hypot(dx, dy)
            if d < 1e-9:
                continue
            corr = (d - rest_len) / d * 0.5
            cx, cy = dx * corr, dy * corr
            if not pin[ar][ac]:
                px[ar][ac] += cx
                py[ar][ac] += cy
            if not pin[br][bc]:
                px[br][bc] -= cx
                py[br][bc] -= cy


def surface_normal_z(x0, y0, x1, y1, x2, y2, x3, y3, rest: float) -> float:
    """
    Compute the normalised z-component of the proxy surface normal for a quad.

    Uses the cross product of the two diagonals (A→C and B→D), divided by
    2 × rest² so that a flat undeformed quad returns exactly 1.0.
    """
    d1x, d1y = x2 - x0, y2 - y0
    d2x, d2y = x3 - x1, y3 - y1
    return (d1x * d2y - d1y * d2x) / (2 * rest * rest)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_pieces() -> list:
    """Return the parsed contents of pieces.json."""
    return json.loads(PIECES_JSON.read_text())


def get_entry() -> dict | None:
    """Return the pieces.json entry for 254-verlet-cloth, or None if absent."""
    return next((p for p in load_pieces() if p.get("id") == PIECE_ID), None)


def html() -> str:
    """Return the full text of index.html."""
    return INDEX.read_text()


# ---------------------------------------------------------------------------
# File-system tests
# ---------------------------------------------------------------------------


class TestFiles:
    def test_directory_exists(self):
        assert PIECE_DIR.is_dir(), f"Missing directory: {PIECE_DIR}"

    def test_index_html_exists(self):
        assert INDEX.is_file()

    def test_thumbnail_exists(self):
        assert THUMBNAIL.is_file()

    def test_readme_exists(self):
        assert README.is_file()

    def test_index_html_non_trivial(self):
        assert len(html()) > 3000, "index.html is suspiciously short"

    def test_readme_non_trivial(self):
        assert len(README.read_text().strip()) > 200

    def test_thumbnail_is_valid_svg(self):
        content = THUMBNAIL.read_text()
        assert "<svg" in content and "</svg>" in content

    def test_thumbnail_has_rect_or_polygon(self):
        content = THUMBNAIL.read_text()
        assert "<rect" in content or "<polygon" in content, \
            "Thumbnail should have rect or polygon elements"


# ---------------------------------------------------------------------------
# pieces.json metadata
# ---------------------------------------------------------------------------


class TestPiecesJson:
    def test_entry_exists(self):
        assert get_entry() is not None, f"{PIECE_ID} not found in pieces.json"

    def test_required_fields(self):
        required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
        e = get_entry()
        assert e is not None
        missing = required - e.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_id_matches(self):
        assert get_entry()["id"] == PIECE_ID

    def test_path_correct(self):
        assert get_entry()["path"] == f"pieces/{PIECE_ID}"

    def test_thumbnail_file_exists(self):
        e = get_entry()
        assert (REPO / e["thumbnail"]).is_file()

    def test_year_is_int(self):
        assert isinstance(get_entry()["year"], int)

    def test_technique_mentions_canvas(self):
        assert "canvas" in get_entry()["technique"].lower()

    def test_technique_mentions_verlet(self):
        tech = get_entry()["technique"].lower()
        assert "verlet" in tech

    def test_appears_after_247(self):
        """254-verlet-cloth must follow 247-smooth-life in pieces.json."""
        pieces = load_pieces()
        idx_247 = next((i for i, p in enumerate(pieces) if p["id"] == "247-smooth-life"), None)
        idx_254 = next((i for i, p in enumerate(pieces) if p["id"] == PIECE_ID), None)
        assert idx_247 is not None, "247-smooth-life missing from pieces.json"
        assert idx_254 is not None, f"{PIECE_ID} missing from pieces.json"
        assert idx_254 > idx_247, "254-verlet-cloth must come after 247-smooth-life"

    def test_no_duplicate_ids(self):
        ids = [p["id"] for p in load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate piece IDs in pieces.json"

    def test_prior_pieces_preserved(self):
        ids = {p["id"] for p in load_pieces()}
        for expected in ["01-amber-current", "247-smooth-life", "244-spirolaterals"]:
            assert expected in ids, f"Prior piece {expected!r} was removed"


# ---------------------------------------------------------------------------
# index.html structure
# ---------------------------------------------------------------------------


class TestIndexHtml:
    def test_has_canvas(self):
        assert "<canvas" in html()

    def test_has_script(self):
        assert "<script" in html()

    def test_has_viewport_meta(self):
        assert 'name="viewport"' in html()

    def test_has_charset(self):
        assert "charset" in html()

    def test_no_external_scripts(self):
        assert not re.findall(r'<script[^>]+src=["\']https?://', html())

    def test_self_contained(self):
        h = html()
        assert '<script src=' not in h
        assert '<link rel="stylesheet"' not in h

    def test_has_requestanimationframe(self):
        assert "requestAnimationFrame" in html()

    def test_has_float32array(self):
        assert "Float32Array" in html()

    def test_has_gravity_constant(self):
        h = html().lower()
        assert "gravity" in h

    def test_has_constraint_iterations(self):
        """The piece must run multiple constraint iterations per frame."""
        h = html()
        assert "ITERS" in h or "iters" in h or "iterations" in h.lower()

    def test_constraint_count_at_least_3(self):
        """Constraint iteration count must be >= 3."""
        h = html()
        match = re.search(r'ITERS\s*=\s*(\d+)', h)
        assert match is not None, "ITERS constant not found in index.html"
        assert int(match.group(1)) >= 3, "ITERS must be at least 3"

    def test_has_verlet_integration(self):
        """Must use previous positions (ppx/ppy or similar) for Verlet."""
        h = html()
        assert "ppx" in h or "prevX" in h or "oldX" in h or "ox" in h

    def test_grid_at_least_30x30(self):
        """Grid must have at least 30 rows and 30 columns."""
        h = html()
        rows_match = re.search(r'ROWS\s*=\s*(\d+)', h)
        cols_match = re.search(r'COLS\s*=\s*(\d+)', h)
        assert rows_match is not None, "ROWS constant not found"
        assert cols_match is not None, "COLS constant not found"
        assert int(rows_match.group(1)) >= 30, "ROWS must be at least 30"
        assert int(cols_match.group(1)) >= 30, "COLS must be at least 30"

    def test_has_wind(self):
        h = html().lower()
        assert "wind" in h or "sin(" in h

    def test_has_shear_springs(self):
        """Shear diagonal springs must be present."""
        h = html().lower()
        assert "shear" in h or "sqrt2" in h or "sqrt(2)" in h or "diag" in h

    def test_has_pinned_top_row(self):
        h = html().lower()
        assert "pin" in h or "pinned" in h

    def test_has_surface_normal_shading(self):
        """Must compute a surface normal (cross product) for shading quads."""
        h = html()
        assert "NORM_SCALE" in h or "nz" in h or "normalScale" in h or "norm" in h.lower()

    def test_has_color_lut(self):
        h = html()
        assert "LUT" in h or "lut" in h.lower() or "colorLUT" in h

    def test_has_burgundy_color(self):
        h = html().lower()
        assert "8b1a3a" in h or "burgundy" in h or (
            ("139" in h or "8b" in h) and ("26" in h or "1a" in h)
        )

    def test_has_dark_background(self):
        h = html().lower()
        assert "080810" in h or "0a0a" in h or "background:#0" in h

    def test_has_fill_path(self):
        """Quads must be drawn as filled paths."""
        h = html()
        assert "ctx.fill()" in h

    def test_has_moveto_lineto(self):
        h = html()
        assert "moveTo" in h and "lineTo" in h


# ---------------------------------------------------------------------------
# Verlet physics tests (Python mirror)
# ---------------------------------------------------------------------------


class TestVerletIntegration:
    def test_pinned_particles_do_not_move(self):
        """Verlet step must not displace pinned particles."""
        rows, cols, rest = 3, 3, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest)
        # Record pinned positions before step
        pinned_before = [(px[0][c], py[0][c]) for c in range(cols) if pin[0][c]]
        verlet_step(px, py, ppx, ppy, pin, gravity=0.4, damp=0.997)
        pinned_after = [(px[0][c], py[0][c]) for c in range(cols) if pin[0][c]]
        assert pinned_before == pinned_after, "Pinned particles moved"

    def test_free_particles_fall_under_gravity(self):
        """Unpinned particles must move downward after a step with gravity."""
        rows, cols, rest = 4, 4, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest)
        y_before = py[rows - 1][cols // 2]
        verlet_step(px, py, ppx, ppy, pin, gravity=0.5, damp=0.997)
        y_after = py[rows - 1][cols // 2]
        assert y_after > y_before, "Bottom particle did not fall under gravity"

    def test_velocity_damping_reduces_speed(self):
        """Applying damp < 1 must reduce the effective velocity between steps."""
        rows, cols, rest = 3, 3, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest)
        # Give the bottom-right particle an initial velocity by offsetting previous pos
        px[2][2] += 5.0
        v_initial = 5.0
        verlet_step(px, py, ppx, ppy, pin, gravity=0.0, damp=0.5)
        # Velocity in x should now be damp * initial = 2.5 → new displacement
        # After step 1: ppx = px_old + 5, px = px_old + 5 + 0.5*5 = px_old + 7.5
        # The new velocity = px - ppx = 2.5 (damped)
        vx_new = abs(px[2][2] - ppx[2][2])
        assert vx_new < v_initial, "Damping did not reduce velocity"

    def test_no_nan_after_steps(self):
        """Many Verlet steps on a small cloth must not produce NaN positions."""
        rows, cols, rest = 5, 5, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest)
        constraints = build_constraints(rows, cols, rest)
        for t in range(200):
            verlet_step(px, py, ppx, ppy, pin, gravity=0.38, damp=0.997, wind_amp=1.6, t=t)
            constraint_step(px, py, pin, constraints, iters=5)
        for r in range(rows):
            for c in range(cols):
                assert not math.isnan(px[r][c]), f"NaN in px[{r}][{c}] after 200 steps"
                assert not math.isnan(py[r][c]), f"NaN in py[{r}][{c}] after 200 steps"

    def test_wind_force_has_spatial_variation(self):
        """
        Wind is a function of particle x position, so two particles at different
        x coordinates but the same time step must receive different wind forces.
        """
        rows, cols, rest = 3, 6, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest, start_x=0.0)
        # Choose two unpinned particles far apart in x
        x_left  = px[2][0]
        x_right = px[2][5]
        wind_left  = 1.6 * math.sin(0 * 0.0015 + x_left  * 0.055)
        wind_right = 1.6 * math.sin(0 * 0.0015 + x_right * 0.055)
        assert wind_left != pytest.approx(wind_right, abs=1e-6), \
            "Wind force must vary with particle x position"


class TestConstraintProjection:
    def test_single_constraint_converges_to_rest_length(self):
        """After enough iterations a stretched spring must reach its rest length."""
        rows, cols, rest = 2, 2, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest)
        # Stretch the bottom-left particle downward and to the right significantly
        px[1][0] += 20.0
        py[1][0] += 20.0
        constraints = build_constraints(rows, cols, rest)
        # Run many iterations
        constraint_step(px, py, pin, constraints, iters=50)
        # The distance from (0,0) top-left to (1,0) bottom-left should be near rest
        d = math.hypot(px[1][0] - px[0][0], py[1][0] - py[0][0])
        assert abs(d - rest) < 1.0, f"Spring length {d:.2f} not near rest {rest}"

    def test_pinned_particles_unchanged_during_projection(self):
        """Constraint projection must not move pinned particles."""
        rows, cols, rest = 3, 3, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest)
        before = {(0, c): (px[0][c], py[0][c]) for c in range(cols) if pin[0][c]}
        constraints = build_constraints(rows, cols, rest)
        constraint_step(px, py, pin, constraints, iters=10)
        for (r, c), (bx, by) in before.items():
            assert px[r][c] == pytest.approx(bx, abs=1e-9)
            assert py[r][c] == pytest.approx(by, abs=1e-9)

    def test_constraint_count_correct(self):
        """Verify the total number of constraints for a 32×32 grid."""
        rows, cols, rest = 32, 32, 11.0
        constraints = build_constraints(rows, cols, rest)
        # horizontal: 32×31, vertical: 31×32, shear: 2×31×31
        expected = rows * (cols - 1) + (rows - 1) * cols + 2 * (rows - 1) * (cols - 1)
        assert len(constraints) == expected

    def test_rest_lengths_correct(self):
        """Shear constraints must have rest length = REST × √2."""
        rows, cols, rest = 4, 4, 10.0
        constraints = build_constraints(rows, cols, rest)
        diag_rest = rest * math.sqrt(2)
        structural_rests = {rest}
        shear_rests = {diag_rest}
        for ar, ac, br, bc, r in constraints:
            dr = abs(br - ar)
            dc = abs(bc - ac)
            if dr == 0 or dc == 0:
                assert r == pytest.approx(rest, abs=1e-9), \
                    f"Structural spring ({ar},{ac})→({br},{bc}) has wrong rest {r}"
            else:
                assert r == pytest.approx(diag_rest, abs=1e-9), \
                    f"Shear spring ({ar},{ac})→({br},{bc}) has wrong rest {r}"


class TestSurfaceNormal:
    def test_flat_quad_facing_viewer_gives_one(self):
        """An undeformed axis-aligned quad must return nz = 1.0."""
        rest = 10.0
        nz = surface_normal_z(0, 0, rest, 0, rest, rest, 0, rest, rest)
        assert nz == pytest.approx(1.0, abs=1e-9)

    def test_inverted_quad_gives_negative_nz(self):
        """A quad whose winding is reversed must produce negative nz."""
        rest = 10.0
        # Swap two corners to invert winding
        nz = surface_normal_z(rest, 0, 0, 0, 0, rest, rest, rest, rest)
        assert nz < 0, f"Inverted quad should give nz < 0, got {nz}"

    def test_degenerate_quad_gives_zero(self):
        """A collapsed (zero-area) quad must return nz = 0."""
        rest = 10.0
        # All four corners at the same point → diagonals are zero vectors
        nz = surface_normal_z(5, 5, 5, 5, 5, 5, 5, 5, rest)
        assert nz == pytest.approx(0.0, abs=1e-9)

    def test_nz_increases_with_area(self):
        """A 2× scaled flat quad returns nz = 4.0 (normalisation uses fixed rest²)."""
        rest = 10.0
        nz_2x = surface_normal_z(0, 0, 2*rest, 0, 2*rest, 2*rest, 0, 2*rest, rest)
        # d1 = (2r, 2r), d2 = (-2r, 2r)
        # cross_z = 2r*2r - 2r*(-2r) = 4r² + 4r² = 8r²
        # normalised by 2*r² → 4.0
        assert nz_2x == pytest.approx(4.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Pinning logic tests
# ---------------------------------------------------------------------------


class TestPinning:
    def test_top_row_pinned_at_intervals(self):
        """Top row must be pinned at every 5th column and at the last column."""
        rows, cols, rest = 10, 32, 11.0
        _, _, _, _, pin = make_cloth(rows, cols, rest)
        for c in range(cols):
            expected = (c % 5 == 0) or (c == cols - 1)
            assert pin[0][c] == expected, \
                f"Column {c} pinned={pin[0][c]}, expected={expected}"

    def test_non_top_rows_not_pinned(self):
        """Only the top row should have pinned particles."""
        rows, cols, rest = 5, 10, 10.0
        _, _, _, _, pin = make_cloth(rows, cols, rest)
        for r in range(1, rows):
            for c in range(cols):
                assert not pin[r][c], f"Non-top particle ({r},{c}) is pinned"

    def test_at_least_two_pins_in_top_row(self):
        """There must be at least two pinned particles in the top row."""
        rows, cols, rest = 5, 32, 11.0
        _, _, _, _, pin = make_cloth(rows, cols, rest)
        pin_count = sum(1 for c in range(cols) if pin[0][c])
        assert pin_count >= 2, f"Only {pin_count} pinned particles in top row"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_minimal_cloth_runs(self):
        """A 2×2 cloth must complete 50 verlet+constraint steps without error."""
        rows, cols, rest = 2, 2, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest)
        constraints = build_constraints(rows, cols, rest)
        for t in range(50):
            verlet_step(px, py, ppx, ppy, pin, gravity=0.38, t=t)
            constraint_step(px, py, pin, constraints, iters=5)

    def test_large_cloth_runs(self):
        """A 40×40 cloth must complete 10 steps without NaN."""
        rows, cols, rest = 40, 40, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest)
        constraints = build_constraints(rows, cols, rest)
        for t in range(10):
            verlet_step(px, py, ppx, ppy, pin, gravity=0.38, t=t)
            constraint_step(px, py, pin, constraints, iters=5)
        for r in range(rows):
            for c in range(cols):
                assert not math.isnan(px[r][c])

    def test_zero_gravity_cloth_stays_flat(self):
        """With gravity=0 and no wind a cloth should remain near its initial shape."""
        rows, cols, rest = 4, 4, 10.0
        px, py, ppx, ppy, pin = make_cloth(rows, cols, rest)
        constraints = build_constraints(rows, cols, rest)
        initial_y = [py[r][c] for r in range(rows) for c in range(cols)]
        for _ in range(50):
            verlet_step(px, py, ppx, ppy, pin, gravity=0.0, damp=1.0, wind_amp=0.0)
            constraint_step(px, py, pin, constraints, iters=5)
        for r in range(rows):
            for c in range(cols):
                assert py[r][c] == pytest.approx(initial_y[r * cols + c], abs=1e-3), \
                    f"Particle ({r},{c}) moved without gravity or wind"

    def test_wrong_piece_id_absent(self):
        """Typo variants of the piece ID must not appear in pieces.json."""
        ids = {p["id"] for p in load_pieces()}
        assert "254-cloth" not in ids
        assert "254-verlet" not in ids
        assert "254-verlet-cloth-wrong" not in ids


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------


class TestReadme:
    def test_mentions_verlet(self):
        text = README.read_text().lower()
        assert "verlet" in text

    def test_mentions_constraint(self):
        text = README.read_text().lower()
        assert "constraint" in text

    def test_mentions_spring_or_spring_mass(self):
        text = README.read_text().lower()
        assert "spring" in text

    def test_mentions_gravity(self):
        text = README.read_text().lower()
        assert "gravity" in text

    def test_mentions_why_verlet_preferred(self):
        """README must explain why Verlet is preferred over explicit springs."""
        text = README.read_text().lower()
        assert "preferred" in text or "stable" in text or "stiff" in text

    def test_mentions_shear(self):
        text = README.read_text().lower()
        assert "shear" in text

    def test_mentions_surface_normal_or_shading(self):
        text = README.read_text().lower()
        assert "normal" in text or "shading" in text or "shade" in text

    def test_mentions_wind(self):
        text = README.read_text().lower()
        assert "wind" in text
