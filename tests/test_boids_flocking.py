"""Tests for Piece 113 — Murmuration: Three Rules and a Sky."""
import json
import math
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "113-boids-flocking"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

W, H = 800, 500
PERCEPTION = 60
SEP_DIST = 20
MAX_SPEED = 2.5
MIN_SPEED = 0.8


def _load_entry():
    """Return the pieces.json entry for piece 113, or None if absent."""
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == PIECE_ID), None)


# ---------------------------------------------------------------------------
# Python re-implementation of boids rules for unit testing
# ---------------------------------------------------------------------------

def toroidal_delta(a, b, span):
    """Return signed distance a→b on a toroidal axis of length *span*.

    Picks the shorter of the two possible paths around the torus.
    """
    d = b - a
    if d > span / 2:
        d -= span
    elif d < -span / 2:
        d += span
    return d


def separation_force(boid_x, boid_y, neighbors):
    """Compute separation: sum of unit vectors away from too-close neighbors.

    *neighbors* is a list of (nx, ny) positions already within PERCEPTION.
    Only neighbors within SEP_DIST contribute.  Returns (fx, fy).
    """
    sx, sy, n = 0.0, 0.0, 0
    for nx, ny in neighbors:
        dx = toroidal_delta(nx, boid_x, W)
        dy = toroidal_delta(ny, boid_y, H)
        d = math.hypot(dx, dy)
        if 0 < d < SEP_DIST:
            sx += dx / d
            sy += dy / d
            n += 1
    if n == 0:
        return (0.0, 0.0)
    return (sx / n, sy / n)


def alignment_force(boid_vx, boid_vy, neighbor_velocities):
    """Compute alignment: steer toward average neighbor velocity.

    Returns (fx, fy) = (avg_vx - boid_vx, avg_vy - boid_vy).
    Returns (0, 0) when *neighbor_velocities* is empty.
    """
    if not neighbor_velocities:
        return (0.0, 0.0)
    avg_vx = sum(v[0] for v in neighbor_velocities) / len(neighbor_velocities)
    avg_vy = sum(v[1] for v in neighbor_velocities) / len(neighbor_velocities)
    return (avg_vx - boid_vx, avg_vy - boid_vy)


def cohesion_force(boid_x, boid_y, neighbors):
    """Compute cohesion: steer toward the toroidal center of mass of neighbors.

    Returns (fx, fy) as the average displacement vector toward neighbors.
    Returns (0, 0) when *neighbors* is empty.
    """
    if not neighbors:
        return (0.0, 0.0)
    cx = sum(toroidal_delta(boid_x, nx, W) for nx, ny in neighbors) / len(neighbors)
    cy = sum(toroidal_delta(boid_y, ny, H) for nx, ny in neighbors) / len(neighbors)
    return (cx, cy)


def clamp_speed(vx, vy, max_s):
    """Scale velocity so its magnitude does not exceed *max_s*."""
    s = math.hypot(vx, vy)
    return (vx * max_s / s, vy * max_s / s) if s > max_s else (vx, vy)


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

    def test_thumbnail_svg_starts_with_svg_tag(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "<svg" in content

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_readme_nonempty(self):
        assert len((PIECE_DIR / "README.md").read_text()) > 100

    def test_generate_thumbnail_script_exists(self):
        assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# SVG thumbnail content
# ---------------------------------------------------------------------------

class TestThumbnailSvg:
    def setup_method(self):
        self.svg = (PIECE_DIR / "thumbnail.svg").read_text()

    def test_svg_has_polygon_elements(self):
        """Each boid must be represented as a polygon element."""
        assert "<polygon" in self.svg

    def test_svg_has_background_rect(self):
        assert "<rect" in self.svg

    def test_svg_has_gradient(self):
        assert "linearGradient" in self.svg

    def test_svg_has_100_boids(self):
        """The fixed-seed thumbnail must contain exactly 100 polygon elements."""
        count = len(re.findall(r'<polygon', self.svg))
        assert count == 100, f"Expected 100 boid polygons, got {count}"

    def test_svg_dimensions_set(self):
        assert 'width="400"' in self.svg
        assert 'height="250"' in self.svg

    def test_svg_midnight_blue_palette(self):
        assert "#0a0a2e" in self.svg or "0a0a2e" in self.svg


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

    def test_no_external_dependencies(self):
        assert not re.search(r'<script[^>]+src="https?://', self.html)

    def test_boid_count_300(self):
        assert "300" in self.html

    def test_perception_radius_present(self):
        """Perception radius constant must appear in the JS."""
        assert "60" in self.html

    def test_separation_dist_present(self):
        assert "20" in self.html

    def test_max_speed_present(self):
        assert "2.5" in self.html

    def test_toroidal_wrap_in_code(self):
        """Both W and H modulo wraps must appear (toroidal wrapping)."""
        assert re.search(r'\+\s*W\s*\)\s*%\s*W', self.html)
        assert re.search(r'\+\s*H\s*\)\s*%\s*H', self.html)

    def test_triangle_boid_drawing(self):
        """Boid must be drawn with moveTo/lineTo forming a triangle."""
        assert "moveTo" in self.html
        assert "lineTo" in self.html
        assert "closePath" in self.html

    def test_atan2_for_heading(self):
        """Triangle rotation must use Math.atan2 to derive heading angle."""
        assert "atan2" in self.html

    def test_separation_force_implemented(self):
        """Separation: steer away from close neighbors using inverse distance."""
        assert re.search(r'sx\s*-=', self.html) or re.search(r'sx\s*\+=', self.html)

    def test_alignment_force_implemented(self):
        """Alignment: accumulate neighbor velocities (ax/ay accumulators)."""
        assert re.search(r'ax\s*\+=', self.html) and re.search(r'ay\s*\+=', self.html)

    def test_cohesion_force_implemented(self):
        """Cohesion: accumulate position offsets (cx/cy accumulators)."""
        assert re.search(r'cx\s*\+=', self.html) and re.search(r'cy\s*\+=', self.html)

    def test_midnight_blue_background(self):
        assert "060614" in self.html or "6,6,20" in self.html

    def test_canvas_dimensions(self):
        assert "800" in self.html and "500" in self.html

    def test_motion_trail_via_alpha_fill(self):
        """Semi-transparent fill creates motion trails."""
        assert "rgba" in self.html and "0.25" in self.html


# ---------------------------------------------------------------------------
# Boids algorithm math (Python re-implementation)
# ---------------------------------------------------------------------------

class TestSeparationRule:
    def test_no_neighbors_gives_zero_force(self):
        fx, fy = separation_force(100, 100, [])
        assert fx == 0.0 and fy == 0.0

    def test_neighbor_beyond_sep_dist_gives_zero(self):
        """A neighbor at SEP_DIST or beyond must not contribute."""
        fx, fy = separation_force(0, 0, [(SEP_DIST, 0)])
        assert fx == 0.0 and fy == 0.0

    def test_neighbor_too_close_pushes_away(self):
        """A neighbor directly to the right should push force leftward (negative x)."""
        fx, fy = separation_force(0, 0, [(SEP_DIST / 2, 0)])
        assert fx < 0, f"Expected leftward separation force, got fx={fx}"
        assert abs(fy) < 1e-9

    def test_multiple_neighbors_averaged(self):
        """Two equidistant opposite neighbors cancel out to zero force."""
        bx, by = 100, 100
        d = SEP_DIST / 2
        neighbors = [(bx + d, by), (bx - d, by)]
        fx, fy = separation_force(bx, by, neighbors)
        assert abs(fx) < 1e-9, f"Expected zero net x force, got {fx}"

    def test_toroidal_separation_at_wrap(self):
        """Boid at x=1 and neighbor at x=W-1 should be treated as 2 px apart."""
        bx, by = 1, 100
        nx, ny = W - 1, 100
        neighbors = [(nx, ny)]
        fx, fy = separation_force(bx, by, neighbors)
        assert fx > 0, "Should push rightward since neighbor is 2 px to the left via torus"


class TestAlignmentRule:
    def test_no_neighbors_gives_zero(self):
        fx, fy = alignment_force(1.0, 0.5, [])
        assert fx == 0.0 and fy == 0.0

    def test_same_velocity_gives_zero_force(self):
        """No steering needed when boid already matches neighbor velocity."""
        fx, fy = alignment_force(1.0, 0.5, [(1.0, 0.5)])
        assert abs(fx) < 1e-9 and abs(fy) < 1e-9

    def test_steering_toward_neighbor_velocity(self):
        """Force should point from boid velocity toward neighbor velocity."""
        bvx, bvy = 0.0, 0.0
        fx, fy = alignment_force(bvx, bvy, [(2.0, 1.0)])
        assert fx == pytest.approx(2.0) and fy == pytest.approx(1.0)

    def test_average_of_multiple_neighbors(self):
        fx, fy = alignment_force(0.0, 0.0, [(2.0, 0.0), (0.0, 2.0)])
        assert fx == pytest.approx(1.0) and fy == pytest.approx(1.0)


class TestCohesionRule:
    def test_no_neighbors_gives_zero(self):
        fx, fy = cohesion_force(100, 100, [])
        assert fx == 0.0 and fy == 0.0

    def test_single_neighbor_pull_direction(self):
        """Cohesion should pull the boid toward the neighbor."""
        fx, fy = cohesion_force(100, 100, [(200, 100)])
        assert fx > 0, "Expected rightward pull toward neighbor at x=200"
        assert abs(fy) < 1e-9

    def test_symmetric_neighbors_cancel(self):
        """Two neighbors equidistant left and right give zero net cohesion."""
        bx, by = 100, 100
        fx, fy = cohesion_force(bx, by, [(bx + 30, by), (bx - 30, by)])
        assert abs(fx) < 1e-9

    def test_toroidal_cohesion_at_wrap(self):
        """Boid at x=5 and neighbor at x=W-5: shorter path is leftward via torus."""
        bx, by = 5, 100
        nx, ny = W - 5, 100
        fx, fy = cohesion_force(bx, by, [(nx, ny)])
        assert fx < 0, "Should pull leftward via the short toroidal path"


class TestClampSpeed:
    def test_speed_below_max_unchanged(self):
        vx, vy = clamp_speed(1.0, 0.0, 2.5)
        assert vx == pytest.approx(1.0) and vy == pytest.approx(0.0)

    def test_speed_above_max_clamped(self):
        vx, vy = clamp_speed(10.0, 0.0, 2.5)
        assert math.hypot(vx, vy) == pytest.approx(2.5)

    def test_zero_vector_unchanged(self):
        vx, vy = clamp_speed(0.0, 0.0, 2.5)
        assert vx == 0.0 and vy == 0.0

    def test_diagonal_clamped(self):
        vx, vy = clamp_speed(3.0, 4.0, 2.5)
        assert math.hypot(vx, vy) == pytest.approx(2.5)
        assert vx / vy == pytest.approx(3.0 / 4.0)


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

    def test_technique_is_boids(self):
        entry = _load_entry()
        assert entry["technique"] == "Boids / Particle System"

    def test_entry_year_is_int(self):
        entry = _load_entry()
        assert isinstance(entry["year"], int)

    def test_entry_path_exists(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        entry = _load_entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_piece_113_appears_after_111(self):
        """Piece 113 must appear after piece 111 in the ordered list."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "111-bifurcation" in ids
        assert PIECE_ID in ids
        assert ids.index(PIECE_ID) > ids.index("111-bifurcation")


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_separation_with_single_boid_at_origin(self):
        """Single boid with no neighbors produces zero force."""
        fx, fy = separation_force(0, 0, [])
        assert fx == 0.0 and fy == 0.0

    def test_alignment_large_neighbor_set(self):
        """Alignment over 100 identical velocities equals that velocity minus boid's."""
        neighbors = [(1.5, 0.5)] * 100
        fx, fy = alignment_force(0.0, 0.0, neighbors)
        assert fx == pytest.approx(1.5) and fy == pytest.approx(0.5)

    def test_unknown_piece_id_absent_from_json(self):
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost-boids"), None)
        assert found is None

    def test_generate_thumbnail_produces_valid_svg(self, tmp_path):
        """Running generate_thumbnail.py must produce a non-empty SVG file."""
        sys.path.insert(0, str(PIECE_DIR))
        try:
            import generate_thumbnail
            svg = generate_thumbnail.render()
        finally:
            sys.path.pop(0)
        assert svg.startswith("<svg")
        assert "</svg>" in svg
        assert len(svg) > 200

    def test_generate_thumbnail_deterministic(self):
        """Calling render() twice with the same seed gives identical output."""
        sys.path.insert(0, str(PIECE_DIR))
        try:
            import generate_thumbnail
            a = generate_thumbnail.render()
            b = generate_thumbnail.render()
        finally:
            sys.path.pop(0)
        assert a == b

    def test_toroidal_delta_wraps_correctly(self):
        """toroidal_delta must return the shorter-path distance."""
        assert toroidal_delta(0, W - 1, W) == pytest.approx(-1.0)
        assert toroidal_delta(W - 1, 0, W) == pytest.approx(1.0)
        assert toroidal_delta(0, W // 2, W) == pytest.approx(W // 2)

    def test_clamp_speed_preserves_direction(self):
        """Clamping should not change the direction of travel."""
        vx, vy = clamp_speed(6.0, 8.0, 2.5)
        original_angle = math.atan2(8.0, 6.0)
        clamped_angle = math.atan2(vy, vx)
        assert clamped_angle == pytest.approx(original_angle)
