"""Tests for Piece 259 — Pursuit Curves: The Spider and the Fly."""
import json
import math
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "259-pursuit-curves"
INDEX = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "259-pursuit-curves"


# ---------------------------------------------------------------------------
# Python mirror of the pursuit-curve step for logic tests
# ---------------------------------------------------------------------------


def pursuit_step(agents: list[tuple[float, float]], speed: float) -> list[tuple[float, float]]:
    """
    Advance n pursuit agents one step.

    Each agent moves `speed` of the way toward its clockwise neighbour.
    All new positions are computed before any are written back (simultaneous
    update), preserving the n-fold rotational symmetry of the configuration.

    Args:
        agents: list of (x, y) positions, length n ≥ 2
        speed:  pursuit fraction in (0, 1)

    Returns:
        New list of (x, y) positions after one step.
    """
    n = len(agents)
    new_pos = []
    for i in range(n):
        tx, ty = agents[(i + 1) % n]
        ax, ay = agents[i]
        new_pos.append((ax + speed * (tx - ax), ay + speed * (ty - ay)))
    return new_pos


def regular_ngon(n: int, cx: float, cy: float, r: float, angle_offset: float = 0.0
                 ) -> list[tuple[float, float]]:
    """
    Return the vertices of a regular n-gon centred at (cx, cy) with radius r.

    Vertex i is at angle (angle_offset + 2π·i/n) from the positive x-axis.
    """
    return [
        (cx + r * math.cos(angle_offset + 2 * math.pi * i / n),
         cy + r * math.sin(angle_offset + 2 * math.pi * i / n))
        for i in range(n)
    ]


def centroid(agents: list[tuple[float, float]]) -> tuple[float, float]:
    """Return the arithmetic mean (centroid) of a list of (x, y) positions."""
    n = len(agents)
    return (sum(x for x, _ in agents) / n, sum(y for _, y in agents) / n)


def radius_from_centre(agents: list[tuple[float, float]], cx: float, cy: float) -> float:
    """Return the mean distance of agents from (cx, cy)."""
    return sum(math.hypot(x - cx, y - cy) for x, y in agents) / len(agents)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_pieces() -> list:
    """Return the parsed contents of pieces.json."""
    return json.loads(PIECES_JSON.read_text())


def get_entry() -> dict | None:
    """Return the pieces.json entry for 259-pursuit-curves, or None."""
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

    def test_thumbnail_within_400px(self):
        content = THUMBNAIL.read_text()
        assert 'width="400"' in content or 'width="400' in content


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

    def test_technique_mentions_pursuit(self):
        assert "pursuit" in get_entry()["technique"].lower()

    def test_technique_mentions_spiral(self):
        assert "spiral" in get_entry()["technique"].lower()

    def test_appears_after_257(self):
        """259-pursuit-curves must follow 257-billiard-chaos in pieces.json."""
        pieces = load_pieces()
        idx_257 = next((i for i, p in enumerate(pieces) if p["id"] == "257-billiard-chaos"), None)
        idx_259 = next((i for i, p in enumerate(pieces) if p["id"] == PIECE_ID), None)
        assert idx_257 is not None, "257-billiard-chaos missing from pieces.json"
        assert idx_259 is not None, f"{PIECE_ID} missing from pieces.json"
        assert idx_259 > idx_257, "259-pursuit-curves must come after 257-billiard-chaos"

    def test_no_duplicate_ids(self):
        ids = [p["id"] for p in load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate piece IDs in pieces.json"

    def test_prior_pieces_preserved(self):
        ids = {p["id"] for p in load_pieces()}
        for expected in ["01-amber-current", "255-islamic-stars", "257-billiard-chaos"]:
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

    def test_has_speed_constant(self):
        """SPEED constant (pursuit fraction) must be defined in the script."""
        assert "SPEED" in html()

    def test_has_multiple_n_values(self):
        """index.html must reference multiple n values (3 through 8) for distinct swarms."""
        h = html()
        assert "n: 3" in h or "{ n: 3" in h or "n:3" in h
        assert "n: 8" in h or "{ n: 8" in h or "n:8" in h

    def test_has_hsl_colors(self):
        """Each swarm must use a committed HSL palette."""
        assert "hsl(" in html()

    def test_has_fade_mechanism(self):
        """Trails must fade via globalAlpha or rgba fill."""
        h = html()
        assert "globalAlpha" in h or "rgba" in h

    def test_has_dark_background(self):
        h = html().lower()
        assert "060812" in h or "0a0a" in h or "#000" in h

    def test_has_convergence_check(self):
        """Piece must detect swarm convergence and respawn."""
        h = html().lower()
        assert "converge" in h or "respawn" in h or "spawn" in h

    def test_has_hypot_or_sqrt(self):
        """Distance-to-centre check for convergence must use Math.hypot or Math.sqrt."""
        h = html()
        assert "Math.hypot" in h or "Math.sqrt" in h

    def test_has_angle_offset_respawn(self):
        """Respawn must vary the initial angle so new spirals offset previous ones."""
        h = html()
        assert "angleOffset" in h or "angle_offset" in h or "Offset" in h


# ---------------------------------------------------------------------------
# Pursuit-curve physics tests (Python mirror)
# ---------------------------------------------------------------------------


class TestPursuitPhysics:
    CX, CY = 0.0, 0.0
    SPEED = 0.015

    def test_centroid_preserved_symmetric_ngon(self):
        """For a regular n-gon the centroid stays at the centre after every step."""
        for n in range(3, 9):
            agents = regular_ngon(n, self.CX, self.CY, 100.0)
            cx0, cy0 = centroid(agents)
            agents = pursuit_step(agents, self.SPEED)
            cx1, cy1 = centroid(agents)
            assert abs(cx1 - cx0) < 1e-9, f"n={n}: centroid x drifted"
            assert abs(cy1 - cy0) < 1e-9, f"n={n}: centroid y drifted"

    def test_radius_strictly_decreasing(self):
        """Every step must bring agents closer to the centre."""
        for n in range(3, 9):
            agents = regular_ngon(n, self.CX, self.CY, 100.0)
            r0 = radius_from_centre(agents, self.CX, self.CY)
            agents = pursuit_step(agents, self.SPEED)
            r1 = radius_from_centre(agents, self.CX, self.CY)
            assert r1 < r0, f"n={n}: radius did not decrease after one step"

    def test_convergence_to_centre(self):
        """
        All agents of every n-gon must converge to within 5 px of centre.

        Step budget is 1100 to accommodate n=8 which has the slowest contraction
        ratio (~0.99566/step) and needs ~690 steps to drop from r=100 to r=5.
        """
        for n in range(3, 9):
            agents = regular_ngon(n, self.CX, self.CY, 100.0)
            for _ in range(1100):
                agents = pursuit_step(agents, self.SPEED)
                if all(math.hypot(x - self.CX, y - self.CY) < 5.0 for x, y in agents):
                    break
            else:
                pytest.fail(f"n={n}: did not converge within 1100 steps")

    def test_rotational_symmetry_preserved(self):
        """
        After k steps a regular n-gon remains a regular n-gon (all inter-agent
        distances equal) up to floating-point tolerance.
        """
        n = 5
        agents = regular_ngon(n, self.CX, self.CY, 80.0)
        for _ in range(50):
            agents = pursuit_step(agents, self.SPEED)
        dists = [math.hypot(agents[(i+1) % n][0] - agents[i][0],
                            agents[(i+1) % n][1] - agents[i][1])
                 for i in range(n)]
        assert max(dists) - min(dists) < 1e-9, "Rotational symmetry lost after 50 steps"

    def test_simultaneous_update(self):
        """
        The step must use simultaneous (not sequential) updates: agent 0's new
        position must be based on agent 1's *old* position, not updated position.
        """
        n = 4
        agents = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
        speed = 0.5
        result = pursuit_step(agents, speed)
        # Agent 0 pursues agent 1 (10,0): new x = 0 + 0.5*(10-0) = 5, y = 0
        assert abs(result[0][0] - 5.0) < 1e-9
        assert abs(result[0][1] - 0.0) < 1e-9
        # Agent 1 pursues agent 2 (10,10): new = (10,0)+0.5*((10,10)-(10,0)) = (10,5)
        assert abs(result[1][0] - 10.0) < 1e-9
        assert abs(result[1][1] - 5.0) < 1e-9

    def test_triangle_converges_faster_than_octagon(self):
        """Triangle (n=3) should converge more quickly than octagon (n=8) at same radius."""
        def steps_to_converge(n, threshold=1.0):
            agents = regular_ngon(n, 0.0, 0.0, 100.0)
            for k in range(2000):
                agents = pursuit_step(agents, self.SPEED)
                if all(math.hypot(x, y) < threshold for x, y in agents):
                    return k
            return 2000

        t3 = steps_to_converge(3)
        t8 = steps_to_converge(8)
        assert t3 < t8, f"Expected triangle to converge faster, got t3={t3}, t8={t8}"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_speed_zero_no_movement(self):
        """With speed=0 agents must not move."""
        agents = regular_ngon(5, 0.0, 0.0, 50.0)
        after = pursuit_step(agents, 0.0)
        for (x0, y0), (x1, y1) in zip(agents, after):
            assert x0 == x1 and y0 == y1

    def test_speed_one_reaches_target(self):
        """With speed=1 every agent jumps directly onto its target in one step."""
        agents = regular_ngon(4, 0.0, 0.0, 50.0)
        after = pursuit_step(agents, 1.0)
        for i, (x1, y1) in enumerate(after):
            tx, ty = agents[(i + 1) % 4]
            assert abs(x1 - tx) < 1e-9 and abs(y1 - ty) < 1e-9

    def test_large_n_converges(self):
        """
        A 10-gon must converge to within 1 px of centre at speed=0.05 in ≤ 600 steps.

        n=32 is not used because its per-step contraction is ~0.99971 (2π/32 ≈ 11°
        gives very little sideways pull), requiring ~13 000 steps to converge — not
        a useful edge-case assertion.  n=10 at speed=0.05 converges in ~430 steps.
        """
        n = 10
        agents = regular_ngon(n, 0.0, 0.0, 50.0)
        for _ in range(600):
            agents = pursuit_step(agents, 0.05)
            if all(math.hypot(x, y) < 1.0 for x, y in agents):
                return
        pytest.fail("10-gon did not converge within 600 steps at speed=0.05")

    def test_large_radius_no_nan(self):
        """Very large initial radius must not produce NaN after 500 steps."""
        agents = regular_ngon(6, 0.0, 0.0, 1e6)
        for _ in range(500):
            agents = pursuit_step(agents, 0.015)
        assert all(not math.isnan(x) and not math.isnan(y) for x, y in agents)

    def test_already_at_centre(self):
        """Agents collapsed at the centre must stay there."""
        agents = [(0.0, 0.0)] * 5
        after = pursuit_step(agents, 0.015)
        assert all(x == 0.0 and y == 0.0 for x, y in after)

    def test_non_symmetric_init_still_contracts(self):
        """Even a non-symmetric arrangement must have non-increasing average radius."""
        agents = [(10.0, 0.0), (0.0, 7.0), (-5.0, -3.0)]
        r0 = sum(math.hypot(x, y) for x, y in agents) / 3
        for _ in range(50):
            agents = pursuit_step(agents, 0.02)
        r50 = sum(math.hypot(x, y) for x, y in agents) / 3
        assert r50 < r0, "Non-symmetric arrangement did not contract"

    def test_wrong_piece_id_absent(self):
        """Typo variants of the piece ID must not appear in pieces.json."""
        ids = {p["id"] for p in load_pieces()}
        assert "260-pursuit-curves" not in ids
        assert "259-pursuit" not in ids
        assert "259-curves" not in ids


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------


class TestReadme:
    def test_mentions_logarithmic_spiral(self):
        text = README.read_text().lower()
        assert "logarithmic spiral" in text or "logarithmic" in text

    def test_mentions_pursuit(self):
        text = README.read_text().lower()
        assert "pursuit" in text

    def test_mentions_n_agents(self):
        text = README.read_text().lower()
        assert "agent" in text or "n-gon" in text or "ngon" in text

    def test_mentions_palette(self):
        text = README.read_text().lower()
        assert "palette" in text or "colour" in text or "color" in text

    def test_mentions_simultaneous_update(self):
        text = README.read_text().lower()
        assert "simultaneous" in text or "same time" in text or "written back" in text
