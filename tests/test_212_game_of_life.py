"""Tests for Piece 212 — Game of Life: Four Rules, Infinite Complexity."""
import json
import pathlib
import re

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "212-game-of-life"
INDEX     = PIECE_DIR / "index.html"
README    = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID  = "212-game-of-life"


# ---------------------------------------------------------------------------
# Python mirror of the GoL simulation for logic tests
# (uses a set of (x,y) tuples — infinite toroidal-free grid)
# ---------------------------------------------------------------------------

def gol_step(live: set) -> set:
    """
    Advance one Game of Life generation on an infinite grid.

    For each cell in *live* and all of its neighbors, counts live neighbors
    and applies the four Conway rules:
      1. Alive with <2 neighbors → dies (underpopulation)
      2. Alive with 2-3 neighbors → survives
      3. Alive with >3 neighbors → dies (overpopulation)
      4. Dead with exactly 3 neighbors → born (reproduction)

    Returns the new set of live cells.
    """
    candidate_counts: dict[tuple[int, int], int] = {}
    for (x, y) in live:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nb = (x + dx, y + dy)
                candidate_counts[nb] = candidate_counts.get(nb, 0) + 1

    new_live: set[tuple[int, int]] = set()
    for pos, cnt in candidate_counts.items():
        if cnt == 3 or (cnt == 2 and pos in live):
            new_live.add(pos)
    return new_live


def run_n(live: set, n: int) -> set:
    """Run *n* GoL generations starting from *live* and return the final state."""
    for _ in range(n):
        live = gol_step(live)
    return live


# Standard pattern definitions (relative coordinates)
BLINKER_H = frozenset([(0, 0), (1, 0), (2, 0)])           # horizontal phase
BLINKER_V = frozenset([(0, 0), (0, 1), (0, 2)])           # vertical phase
BLOCK     = frozenset([(0, 0), (1, 0), (0, 1), (1, 1)])   # 2×2 still life
GLIDER    = frozenset([(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)])  # SE-moving phase-0

# After 4 steps the SE glider moves (+1, +1) from its original position
GLIDER_4  = frozenset([(x + 1, y + 1) for (x, y) in GLIDER])


def normalise(live: set) -> frozenset:
    """Translate a set of cells so its min x and y are both 0."""
    if not live:
        return frozenset()
    min_x = min(p[0] for p in live)
    min_y = min(p[1] for p in live)
    return frozenset((x - min_x, y - min_y) for (x, y) in live)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_pieces() -> list:
    """Return the parsed contents of pieces.json."""
    return json.loads(PIECES_JSON.read_text())


def get_entry() -> dict | None:
    """Return the pieces.json entry for 212-game-of-life, or None if absent."""
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

    def test_thumbnail_has_cells(self):
        content = THUMBNAIL.read_text()
        assert "<rect" in content, "Thumbnail has no rect elements (no cells rendered)"

    def test_thumbnail_has_amber_color(self):
        content = THUMBNAIL.read_text().lower()
        assert "c8a96e" in content or "e8d070" in content, "Amber palette missing from thumbnail"


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

    def test_technique_mentions_game_of_life(self):
        tech = get_entry()["technique"].lower()
        assert "game of life" in tech or "conway" in tech or "cellular" in tech

    def test_appears_after_208(self):
        """212-game-of-life must follow 208-double-pendulum in pieces.json."""
        pieces = load_pieces()
        idx_208 = next((i for i, p in enumerate(pieces) if p["id"] == "208-double-pendulum"), None)
        idx_212 = next((i for i, p in enumerate(pieces) if p["id"] == PIECE_ID), None)
        assert idx_208 is not None, "208-double-pendulum missing from pieces.json"
        assert idx_212 is not None, f"{PIECE_ID} missing from pieces.json"
        assert idx_212 > idx_208, "212-game-of-life must come after 208-double-pendulum"

    def test_no_duplicate_ids(self):
        ids = [p["id"] for p in load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate piece IDs in pieces.json"

    def test_prior_pieces_preserved(self):
        ids = {p["id"] for p in load_pieces()}
        for expected in ["01-amber-current", "208-double-pendulum", "207-lorenz-attractor"]:
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

    def test_has_play_pause_button(self):
        h = html().lower()
        assert "play" in h and "pause" in h

    def test_has_step_button(self):
        assert "step" in html().lower()

    def test_has_clear_button(self):
        assert "clear" in html().lower()

    def test_has_speed_slider(self):
        assert 'type="range"' in html() or "type='range'" in html()

    def test_has_generation_counter(self):
        h = html().lower()
        assert "gen" in h or "generation" in h

    def test_has_live_cell_count(self):
        h = html().lower()
        assert "live" in h or "count" in h

    def test_has_four_rules(self):
        h = html().lower()
        assert "underpopulation" in h or "< 2" in h or "&lt; 2" in h

    def test_has_reproduction_rule(self):
        h = html().lower()
        assert "reproduction" in h or "exactly 3" in h

    def test_has_glider_preset(self):
        assert "glider" in html().lower()

    def test_has_blinker_preset(self):
        assert "blinker" in html().lower()

    def test_has_pulsar_preset(self):
        assert "pulsar" in html().lower()

    def test_has_gun_preset(self):
        h = html().lower()
        assert "gun" in h or "gosper" in h

    def test_has_pattern_library_panel(self):
        h = html().lower()
        assert "pattern" in h and ("library" in h or "cnt-" in h or "found" in h)

    def test_has_amber_color(self):
        h = html().lower()
        assert "c8a96e" in h or "amber" in h

    def test_has_near_black_background(self):
        h = html().lower()
        assert "0a0a12" in h or "0a0a18" in h

    def test_has_heat_map_mode(self):
        h = html().lower()
        assert "heat" in h

    def test_has_info_pane(self):
        h = html().lower()
        assert "info" in h or "pane" in h or "about" in h

    def test_info_pane_mentions_conway(self):
        assert "conway" in html().lower()

    def test_info_pane_mentions_turing(self):
        assert "turing" in html().lower()

    def test_info_pane_mentions_gosper(self):
        assert "gosper" in html().lower()

    def test_info_pane_mentions_von_neumann(self):
        h = html().lower()
        assert "von neumann" in h or "neumann" in h

    def test_has_visibility_change_handler(self):
        assert "visibilitychange" in html()

    def test_has_120x80_grid(self):
        h = html()
        assert "W = 120" in h or "W=120" in h or "120," in h

    def test_has_imagedataapi(self):
        h = html().lower()
        assert "imagedata" in h or "putimagedata" in h or "createimagedata" in h


# ---------------------------------------------------------------------------
# GoL simulation logic tests (Python mirror)
# ---------------------------------------------------------------------------

class TestSimulationRules:
    def test_empty_grid_stays_empty(self):
        """An empty grid must remain empty after any number of steps."""
        assert gol_step(set()) == set()

    def test_single_cell_dies(self):
        """A lone live cell has 0 neighbors and must die (rule 1)."""
        assert gol_step({(5, 5)}) == set()

    def test_two_cells_die(self):
        """Two adjacent cells each have only 1 neighbor and both die."""
        result = gol_step({(0, 0), (1, 0)})
        assert result == set()

    def test_three_in_a_row_becomes_blinker(self):
        """
        Three cells in a horizontal line (blinker): the middle survives
        with 2 neighbors; the ends die; two new cells are born above/below
        the middle to form the vertical phase.
        """
        result = normalise(gol_step(BLINKER_H))
        assert result == normalise(BLINKER_V)

    def test_blinker_period_2(self):
        """A blinker must return to its original orientation after exactly 2 steps."""
        after_2 = run_n(set(BLINKER_H), 2)
        assert normalise(after_2) == normalise(BLINKER_H)

    def test_block_is_still_life(self):
        """
        A 2×2 block is a still life: every cell has exactly 3 neighbors,
        no adjacent dead cells have 3 live neighbors, so the grid is unchanged.
        """
        after_1 = gol_step(set(BLOCK))
        assert normalise(after_1) == normalise(BLOCK)

    def test_block_stable_after_100_steps(self):
        """The block must remain unchanged for 100 generations."""
        after = run_n(set(BLOCK), 100)
        assert normalise(after) == normalise(BLOCK)

    def test_glider_moves_one_cell_after_4_steps(self):
        """
        An SE glider has period 4 with a (+1,+1) spatial displacement.
        After 4 steps the normalised shape must match the original.
        """
        after_4 = run_n(set(GLIDER), 4)
        assert normalise(after_4) == normalise(GLIDER), (
            f"Glider shape changed after 4 steps: {normalise(after_4)} "
            f"!= {normalise(GLIDER)}"
        )

    def test_glider_actually_moved(self):
        """After 4 steps the glider must be at a different position (it really moved)."""
        after_4 = run_n(set(GLIDER), 4)
        assert after_4 != set(GLIDER), "Glider didn't move — still at original position"

    def test_cell_born_with_exactly_3_neighbors(self):
        """A dead cell surrounded by exactly 3 live neighbors is born (rule 4)."""
        # L-shaped 3-cell configuration: the corner of the L is the target dead cell
        live = {(0, 0), (1, 0), (0, 1)}
        result = gol_step(live)
        assert (1, 1) in result, "Cell at (1,1) should be born with 3 live neighbors"

    def test_overpopulation_kills_cell(self):
        """A live cell with 4+ live neighbors dies (rule 3)."""
        # Center cell (1,1) surrounded by 4 neighbors — must die
        live = {(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)}
        result = gol_step(live)
        assert (1, 1) not in result, "Center cell should die from overpopulation"

    def test_pulsar_is_period_3(self):
        """
        The pulsar is a well-known period-3 oscillator.
        After 3 steps from its canonical form, the normalised shape must match.
        """
        pulsar_cells = [
            (2,0),(3,0),(4,0),(8,0),(9,0),(10,0),
            (0,2),(5,2),(7,2),(12,2),
            (0,3),(5,3),(7,3),(12,3),
            (0,4),(5,4),(7,4),(12,4),
            (2,5),(3,5),(4,5),(8,5),(9,5),(10,5),
            (2,7),(3,7),(4,7),(8,7),(9,7),(10,7),
            (0,8),(5,8),(7,8),(12,8),
            (0,9),(5,9),(7,9),(12,9),
            (0,10),(5,10),(7,10),(12,10),
            (2,12),(3,12),(4,12),(8,12),(9,12),(10,12),
        ]
        live = set(pulsar_cells)
        after_3 = run_n(live, 3)
        assert normalise(after_3) == normalise(live), (
            "Pulsar is not period-3: shape changed after 3 generations"
        )

    def test_glider_gun_grows(self):
        """
        After 60 generations the Gosper gun should have fired two gliders;
        the population must be strictly larger than the gun's initial 36 cells.
        """
        gun_cells = [
            (24,0),(22,1),(24,1),
            (12,2),(13,2),(20,2),(21,2),(34,2),(35,2),
            (11,3),(15,3),(20,3),(21,3),(34,3),(35,3),
            (0,4),(1,4),(10,4),(16,4),(20,4),(21,4),
            (0,5),(1,5),(10,5),(14,5),(16,5),(17,5),(22,5),(24,5),
            (10,6),(16,6),(24,6),(11,7),(15,7),(12,8),(13,8),
        ]
        live = set(gun_cells)
        after = run_n(live, 60)
        assert len(after) > len(live), (
            f"Gun population should grow after 60 steps; got {len(after)} <= {len(live)}"
        )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_all_four_corners_of_2x2_survive(self):
        """A 2×2 block is the smallest stable pattern — all four cells must survive."""
        result = gol_step(set(BLOCK))
        for cell in BLOCK:
            assert cell in result, f"Block cell {cell} died unexpectedly"

    def test_large_random_like_grid_stays_finite(self):
        """A 50-cell dense grid must never produce NaN or infinite coordinates."""
        import random
        rng = random.Random(42)
        live = {(rng.randint(0, 20), rng.randint(0, 20)) for _ in range(50)}
        result = run_n(live, 20)
        for (x, y) in result:
            assert isinstance(x, int) and isinstance(y, int)
            assert -1000 < x < 1000 and -1000 < y < 1000, "Cell coordinate out of bounds"

    def test_wrong_piece_id_absent(self):
        """Typo-IDs must not exist in pieces.json."""
        ids = {p["id"] for p in load_pieces()}
        assert "212-game-of-life-wrong" not in ids
        assert "212-conways-game-of-life" not in ids

    def test_no_birth_from_two_neighbors(self):
        """Two live neighbors never birth a new cell (needs exactly 3)."""
        # Place two cells; the candidate positions adjacent to both have only 2 neighbors
        live = {(0, 0), (2, 0)}
        result = gol_step(live)
        # (1,0) has 2 neighbors — must NOT be born
        assert (1, 0) not in result

    def test_underpopulation_single_neighbor(self):
        """A live cell with exactly 1 live neighbor dies."""
        live = {(0, 0), (0, 1)}  # (0,1) neighbors: only (0,0)
        result = gol_step(live)
        assert (0, 0) not in result
        assert (0, 1) not in result


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

class TestReadme:
    def test_mentions_conway(self):
        assert "conway" in README.read_text().lower()

    def test_mentions_four_rules(self):
        text = README.read_text().lower()
        assert "rule" in text or "underpopulation" in text

    def test_mentions_glider(self):
        assert "glider" in README.read_text().lower()

    def test_mentions_turing(self):
        assert "turing" in README.read_text().lower()

    def test_mentions_gosper(self):
        assert "gosper" in README.read_text().lower()

    def test_mentions_emergence_or_complexity(self):
        text = README.read_text().lower()
        assert "emergenc" in text or "complex" in text
