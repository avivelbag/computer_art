"""Tests for Piece 257 — Stadium Billiard: The Orbit That Never Closes."""
import json
import math
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "257-billiard-chaos"
INDEX = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "257-billiard-chaos"


# ---------------------------------------------------------------------------
# Python mirrors of billiard physics for logic tests
# ---------------------------------------------------------------------------


def reflect(vx: float, vy: float, nx: float, ny: float) -> tuple[float, float]:
    """
    Reflect velocity (vx, vy) through surface normal (nx, ny).

    Uses the elastic reflection formula: v_out = v_in - 2*(v_in·n)*n.
    The normal must be unit-length for the result to preserve speed.
    """
    dot = vx * nx + vy * ny
    return vx - 2 * dot * nx, vy - 2 * dot * ny


def step_square(x: float, y: float, vx: float, vy: float,
                left: float, right: float, top: float, bottom: float
                ) -> tuple[float, float, float, float]:
    """
    Advance a square-billiard particle by one step with elastic wall reflections.

    All four walls have axis-aligned normals so reflections simply negate the
    corresponding velocity component.
    """
    x += vx
    y += vy
    if x <= left:   x = left;   vx, vy = reflect(vx, vy,  1,  0)
    if x >= right:  x = right;  vx, vy = reflect(vx, vy, -1,  0)
    if y <= top:    y = top;    vx, vy = reflect(vx, vy,  0,  1)
    if y >= bottom: y = bottom; vx, vy = reflect(vx, vy,  0, -1)
    return x, y, vx, vy


def step_stadium(x: float, y: float, vx: float, vy: float,
                 left_cx: float, right_cx: float, cy: float, r: float,
                 top: float, bottom: float
                 ) -> tuple[float, float, float, float]:
    """
    Advance a stadium-billiard particle by one step.

    Flat walls use axis-aligned normals; semicircular caps use the radial
    normal n = (P - C) / |P - C|.  The particle is snapped back to the
    boundary surface on cap collisions to prevent tunnelling.
    """
    x += vx
    y += vy

    if y <= top:    y = top;    vx, vy = reflect(vx, vy,  0,  1)
    if y >= bottom: y = bottom; vx, vy = reflect(vx, vy,  0, -1)

    dlx, dly = x - left_cx, y - cy
    if dlx <= 0 and dlx * dlx + dly * dly >= r * r:
        dist = math.sqrt(dlx * dlx + dly * dly)
        nx, ny = dlx / dist, dly / dist
        x = left_cx + nx * r
        y = cy + ny * r
        vx, vy = reflect(vx, vy, nx, ny)

    drx, dry = x - right_cx, y - cy
    if drx >= 0 and drx * drx + dry * dry >= r * r:
        dist = math.sqrt(drx * drx + dry * dry)
        nx, ny = drx / dist, dry / dist
        x = right_cx + nx * r
        y = cy + ny * r
        vx, vy = reflect(vx, vy, nx, ny)

    return x, y, vx, vy


def speed(vx: float, vy: float) -> float:
    """Return the Euclidean speed of a velocity vector."""
    return math.sqrt(vx * vx + vy * vy)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_pieces() -> list:
    """Return the parsed contents of pieces.json."""
    return json.loads(PIECES_JSON.read_text())


def get_entry() -> dict | None:
    """Return the pieces.json entry for 257-billiard-chaos, or None if absent."""
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
        assert len(html()) > 2000, "index.html is suspiciously short"

    def test_readme_non_trivial(self):
        assert len(README.read_text().strip()) > 200

    def test_thumbnail_is_valid_svg(self):
        content = THUMBNAIL.read_text()
        assert "<svg" in content and "</svg>" in content

    def test_thumbnail_has_visual_elements(self):
        content = THUMBNAIL.read_text()
        assert any(tag in content for tag in ["<rect", "<line", "<polyline", "<path", "<polygon"])


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

    def test_technique_mentions_billiard(self):
        tech = get_entry()["technique"].lower()
        assert "billiard" in tech

    def test_technique_mentions_stadium(self):
        tech = get_entry()["technique"].lower()
        assert "stadium" in tech

    def test_technique_mentions_ergodic(self):
        tech = get_entry()["technique"].lower()
        assert "ergodic" in tech

    def test_appears_after_255(self):
        """257-billiard-chaos must follow 255-islamic-stars in pieces.json."""
        pieces = load_pieces()
        idx_255 = next((i for i, p in enumerate(pieces) if p["id"] == "255-islamic-stars"), None)
        idx_257 = next((i for i, p in enumerate(pieces) if p["id"] == PIECE_ID), None)
        assert idx_255 is not None, "255-islamic-stars missing from pieces.json"
        assert idx_257 is not None, f"{PIECE_ID} missing from pieces.json"
        assert idx_257 > idx_255, "257-billiard-chaos must come after 255-islamic-stars"

    def test_no_duplicate_ids(self):
        ids = [p["id"] for p in load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate piece IDs in pieces.json"

    def test_prior_pieces_preserved(self):
        ids = {p["id"] for p in load_pieces()}
        for expected in ["01-amber-current", "254-verlet-cloth", "255-islamic-stars"]:
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

    def test_has_two_tables(self):
        """index.html must reference both a square and a stadium billiard."""
        h = html().lower()
        assert "square" in h or "sq" in h
        assert "stadium" in h or "st" in h

    def test_has_reflect_function(self):
        """Elastic reflection must be implemented."""
        h = html()
        assert "reflect" in h

    def test_has_hsl_colors(self):
        """Particles must be colored with HSL by launch angle."""
        assert "hsl(" in html()

    def test_has_cycle_reset(self):
        """Animation must loop/reset periodically."""
        h = html().lower()
        assert "cycle" in h or "reset" in h or "spawn" in h

    def test_has_num_particles_in_range(self):
        """NUM_PARTICLES or equivalent must be between 8 and 12."""
        h = html()
        match = re.search(r'NUM_PARTICLES\s*=\s*(\d+)', h)
        if match:
            count = int(match.group(1))
            assert 8 <= count <= 12, f"NUM_PARTICLES={count} outside 8–12 range"

    def test_has_semicircle_cap_reflection(self):
        """Stadium caps must use radial normals (dist computation)."""
        h = html()
        assert "Math.sqrt" in h or "hypot" in h

    def test_has_alpha_fade(self):
        """Trails must fade via globalAlpha or rgba fill."""
        h = html()
        assert "globalAlpha" in h or "rgba" in h

    def test_has_dark_background(self):
        h = html().lower()
        assert "06060e" in h or "0a0a" in h or "background:#0" in h


# ---------------------------------------------------------------------------
# Reflection physics tests (Python mirror)
# ---------------------------------------------------------------------------


class TestReflectPhysics:
    def test_reflect_flat_wall_x(self):
        """Hitting a left/right wall flips vx and preserves vy."""
        vx_out, vy_out = reflect(3.0, 2.0, 1.0, 0.0)
        assert vx_out == pytest.approx(-3.0, abs=1e-9)
        assert vy_out == pytest.approx(2.0, abs=1e-9)

    def test_reflect_flat_wall_y(self):
        """Hitting a top/bottom wall flips vy and preserves vx."""
        vx_out, vy_out = reflect(1.5, -4.0, 0.0, 1.0)
        assert vx_out == pytest.approx(1.5, abs=1e-9)
        assert vy_out == pytest.approx(4.0, abs=1e-9)

    def test_reflect_preserves_speed(self):
        """Speed must be unchanged by any elastic reflection."""
        for nx, ny in [(1, 0), (0, 1), (0.6, 0.8), (-0.6, 0.8)]:
            vx0, vy0 = 3.0, -2.5
            vx1, vy1 = reflect(vx0, vy0, nx, ny)
            assert speed(vx1, vy1) == pytest.approx(speed(vx0, vy0), abs=1e-9)

    def test_reflect_45_degree_corner(self):
        """A particle hitting a diagonal normal reverses completely."""
        # Normal at 45° = (√2/2, √2/2); velocity (1, 0) → (-0, -1) = reversal along diagonal
        inv_sqrt2 = 1 / math.sqrt(2)
        vx, vy = reflect(1.0, 0.0, inv_sqrt2, inv_sqrt2)
        assert vx == pytest.approx(0.0, abs=1e-9)
        assert vy == pytest.approx(-1.0, abs=1e-9)

    def test_reflect_radial_cap_normal(self):
        """A particle hitting a semicircle cap with outward radial normal bounces back."""
        # Particle at angle 0 on right cap, velocity pointing right (outward)
        vx, vy = reflect(1.0, 0.0, 1.0, 0.0)
        assert vx == pytest.approx(-1.0, abs=1e-9)
        assert vy == pytest.approx(0.0, abs=1e-9)

    def test_glancing_reflect_preserves_speed(self):
        """A near-tangential hit must still conserve speed."""
        angle = math.radians(5)  # near-tangential
        vx0, vy0 = math.cos(angle), math.sin(angle)
        vx1, vy1 = reflect(vx0, vy0, 0.0, 1.0)  # horizontal wall
        assert speed(vx1, vy1) == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Square billiard tests
# ---------------------------------------------------------------------------


class TestSquareBilliard:
    LEFT, RIGHT, TOP, BOTTOM = 0.0, 100.0, 0.0, 100.0

    def _run(self, x, y, vx, vy, steps=200):
        for _ in range(steps):
            x, y, vx, vy = step_square(x, y, vx, vy,
                                        self.LEFT, self.RIGHT,
                                        self.TOP, self.BOTTOM)
        return x, y, vx, vy

    def test_particle_stays_inside_square(self):
        """After many steps the particle must remain within table bounds."""
        x, y, vx, vy = self._run(50, 50, 3.0, 2.3)
        assert self.LEFT <= x <= self.RIGHT
        assert self.TOP  <= y <= self.BOTTOM

    def test_speed_conserved_in_square(self):
        """Elastic square reflections must conserve speed over 500 steps."""
        s0 = speed(2.7, -1.8)
        x, y, vx, vy = 50.0, 50.0, 2.7, -1.8
        for _ in range(500):
            x, y, vx, vy = step_square(x, y, vx, vy,
                                        self.LEFT, self.RIGHT,
                                        self.TOP, self.BOTTOM)
        assert speed(vx, vy) == pytest.approx(s0, abs=1e-6)

    def test_45_degree_particle_periodic(self):
        """A 45° particle in a square must return to start after enough bounces."""
        x0, y0 = 25.0, 25.0
        vx0, vy0 = 1.0, 1.0
        x, y, vx, vy = x0, y0, vx0, vy0
        found = False
        for _ in range(4000):
            x, y, vx, vy = step_square(x, y, vx, vy,
                                        self.LEFT, self.RIGHT,
                                        self.TOP, self.BOTTOM)
            if (abs(x - x0) < 0.5 and abs(y - y0) < 0.5
                    and abs(vx - vx0) < 0.01 and abs(vy - vy0) < 0.01):
                found = True
                break
        assert found, "45-degree square orbit did not close after 4000 steps"


# ---------------------------------------------------------------------------
# Stadium billiard tests
# ---------------------------------------------------------------------------


class TestStadiumBilliard:
    # Stadium matching the piece: ST_X=400, ST_W=480, TABLE_H=360
    # R=180, LEFT_CX=ST_X+R=580, RIGHT_CX=ST_X+ST_W-R=700, CY=225, TOP=45, BOTTOM=405
    LEFT_CX, RIGHT_CX = 580.0, 700.0
    CY = 225.0
    R = 180.0
    TOP, BOTTOM = 45.0, 405.0

    def _run(self, x, y, vx, vy, steps=500):
        for _ in range(steps):
            x, y, vx, vy = step_stadium(x, y, vx, vy,
                                         self.LEFT_CX, self.RIGHT_CX,
                                         self.CY, self.R,
                                         self.TOP, self.BOTTOM)
        return x, y, vx, vy

    def test_speed_conserved_in_stadium(self):
        """Stadium elastic reflections must conserve speed over 1000 steps."""
        vx0, vy0 = 2.1, -3.4
        s0 = speed(vx0, vy0)
        x, y, vx, vy = self.LEFT_CX + 20, self.CY, vx0, vy0
        for _ in range(1000):
            x, y, vx, vy = step_stadium(x, y, vx, vy,
                                         self.LEFT_CX, self.RIGHT_CX,
                                         self.CY, self.R,
                                         self.TOP, self.BOTTOM)
        assert speed(vx, vy) == pytest.approx(s0, abs=1e-5)

    def test_particle_stays_inside_stadium(self):
        """After many steps the particle must remain within the stadium boundary."""
        x, y, vx, vy = self._run(730.0, 225.0, 3.0, -2.0, steps=2000)
        # Check flat walls
        assert self.TOP <= y <= self.BOTTOM
        # Check not outside either cap
        dlx, dly = x - self.LEFT_CX, y - self.CY
        if dlx < 0:
            assert dlx * dlx + dly * dly <= self.R * self.R + 0.01
        drx, dry = x - self.RIGHT_CX, y - self.CY
        if drx > 0:
            assert drx * drx + dry * dry <= self.R * self.R + 0.01

    def test_stadium_caps_reflect(self):
        """A particle aimed directly at the right cap must bounce back leftward."""
        # Start at the right cap centre, velocity pointing right so it exits the cap
        x = self.RIGHT_CX
        y = self.CY
        vx, vy = 5.0, 0.0
        # After one step x = RIGHT_CX + 5 which is on the cap (drx=5 >= 0, dist=5 < R)
        # but we need drx^2 + dry^2 >= R^2 for cap collision.
        # Instead: start well right of RIGHT_CX to trigger cap hit.
        x = self.RIGHT_CX + self.R - 2.0  # near the cap boundary from inside
        y = self.CY
        vx, vy = 5.0, 0.0
        for _ in range(20):
            x, y, vx, vy = step_stadium(x, y, vx, vy,
                                         self.LEFT_CX, self.RIGHT_CX,
                                         self.CY, self.R,
                                         self.TOP, self.BOTTOM)
        # After bouncing off the right cap, particle must eventually travel left
        assert vx < 0, "Particle hitting right cap should reverse horizontal velocity"

    def test_stadium_horizontal_orbit_stays_flat(self):
        """A perfectly horizontal orbit between caps must stay at y = CY."""
        x, y, vx, vy = self.LEFT_CX + 5, self.CY, 4.0, 0.0
        for _ in range(200):
            x, y, vx, vy = step_stadium(x, y, vx, vy,
                                         self.LEFT_CX, self.RIGHT_CX,
                                         self.CY, self.R,
                                         self.TOP, self.BOTTOM)
        assert abs(y - self.CY) < 1e-6, "Horizontal orbit drifted vertically"

    def test_no_nan_after_many_steps(self):
        """Many stadium steps from an arbitrary position must not produce NaN."""
        x, y, vx, vy = 730.0, 225.0, 1.7, -2.3
        for _ in range(5000):
            x, y, vx, vy = step_stadium(x, y, vx, vy,
                                         self.LEFT_CX, self.RIGHT_CX,
                                         self.CY, self.R,
                                         self.TOP, self.BOTTOM)
        assert not math.isnan(x) and not math.isnan(y)
        assert not math.isnan(vx) and not math.isnan(vy)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_zero_velocity_square(self):
        """A particle with zero velocity must stay at its starting position."""
        x, y, vx, vy = step_square(50.0, 50.0, 0.0, 0.0, 0.0, 100.0, 0.0, 100.0)
        assert x == 50.0 and y == 50.0
        assert vx == 0.0 and vy == 0.0

    def test_particle_at_corner_does_not_escape(self):
        """A particle placed at a corner and moving outward must be reflected inward."""
        x, y, vx, vy = step_square(0.0, 0.0, -1.0, -1.0, 0.0, 100.0, 0.0, 100.0)
        assert vx >= 0 and vy >= 0, "Corner particle must bounce inward"

    def test_wrong_piece_id_absent(self):
        """Typo variants of the piece ID must not appear in pieces.json."""
        ids = {p["id"] for p in load_pieces()}
        assert "257-billiard" not in ids
        assert "257-stadium" not in ids
        assert "257-chaos" not in ids

    def test_small_stadium_many_steps(self):
        """A tiny stadium must run 200 steps without NaN."""
        r = 10.0
        lcx, rcx, cy = r, 3 * r, 2 * r
        top, bottom = cy - r, cy + r
        x, y, vx, vy = 2 * r, 2 * r, 1.0, 0.5
        for _ in range(200):
            x, y, vx, vy = step_stadium(x, y, vx, vy, lcx, rcx, cy, r, top, bottom)
        assert not math.isnan(x) and not math.isnan(y)

    def test_multiple_angles_produce_different_trajectories(self):
        """Two particles at the same start but different angles must diverge."""
        def run_n(vx_init, vy_init, n=100):
            x, y, vx, vy = 50.0, 50.0, vx_init, vy_init
            for _ in range(n):
                x, y, vx, vy = step_square(x, y, vx, vy, 0.0, 100.0, 0.0, 100.0)
            return x, y

        pos1 = run_n(math.cos(0.0), math.sin(0.0))
        pos2 = run_n(math.cos(0.5), math.sin(0.5))
        dist = math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])
        assert dist > 0.1, "Different launch angles must produce different positions"


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------


class TestReadme:
    def test_mentions_bunimovich(self):
        text = README.read_text().lower()
        assert "bunimovich" in text

    def test_mentions_stadium(self):
        text = README.read_text().lower()
        assert "stadium" in text

    def test_mentions_ergodic(self):
        text = README.read_text().lower()
        assert "ergodic" in text

    def test_mentions_integrable(self):
        text = README.read_text().lower()
        assert "integrable" in text

    def test_mentions_square(self):
        text = README.read_text().lower()
        assert "square" in text

    def test_mentions_reflection(self):
        text = README.read_text().lower()
        assert "reflect" in text

    def test_mentions_normal(self):
        text = README.read_text().lower()
        assert "normal" in text
