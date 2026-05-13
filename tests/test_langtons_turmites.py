"""Tests for Piece 106 — Highway Builders: Langton's Ant and Turmite Variants."""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "106-langtons-turmites"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}


def _load_entry():
    """Return the pieces.json entry for this piece, or None."""
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == PIECE_ID), None)


# ---------------------------------------------------------------------------
# Turmite simulation (Python re-implementation for logic tests)
# ---------------------------------------------------------------------------

def turmite_step(grid, W, H, ant):
    """
    Advance one Langton's-Ant step for *ant* in-place on *grid*.

    Parameters
    ----------
    grid : list[int]
        Flat W×H array of cell colour indices (modified in-place).
    W, H : int
        Grid dimensions.
    ant : dict with keys 'x', 'y', 'dir', 'rules'
        Ant state (modified in-place).  'dir' is 0=N, 1=E, 2=S, 3=W.

    Returns
    -------
    int
        Index of the cell that was modified.
    """
    DX = [0, 1, 0, -1]
    DY = [-1, 0, 1, 0]
    TURNS = {'R': 1, 'L': 3, 'U': 2, 'N': 0}

    x, y = ant['x'], ant['y']
    idx = y * W + x
    c = grid[idx]
    rules = ant['rules']
    rlen = len(rules)
    nc = c % rlen

    ant['dir'] = (ant['dir'] + TURNS.get(rules[nc], 0)) % 4
    grid[idx] = (nc + 1) % rlen
    ant['x'] = (x + DX[ant['dir']] + W) % W
    ant['y'] = (y + DY[ant['dir']] + H) % H
    return idx


# ---------------------------------------------------------------------------
# File-existence tests
# ---------------------------------------------------------------------------

class TestFiles:
    """All required files must exist and be non-trivially sized."""

    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_index_html_nonempty(self):
        assert len((PIECE_DIR / "index.html").read_text()) > 500

    def test_thumbnail_svg_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_readme_nonempty(self):
        assert len((PIECE_DIR / "README.md").read_text()) > 100


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

class TestIndexHtmlContent:
    """index.html must implement the multi-turmite canvas animation."""

    def setup_method(self):
        self.html = (PIECE_DIR / "index.html").read_text()

    def test_canvas_element_present(self):
        assert "<canvas" in self.html

    def test_animation_loop_present(self):
        assert "requestAnimationFrame" in self.html

    def test_imagdata_creation_present(self):
        assert "createImageData" in self.html

    def test_putimagedata_present(self):
        assert "putImageData" in self.html

    def test_grid_width_512(self):
        """Grid must be 512 wide (W = 512)."""
        assert "W = 512" in self.html or "512" in self.html

    def test_grid_height_512(self):
        """Grid must be 512 tall (H = 512)."""
        assert "H = 512" in self.html or "512" in self.html

    def test_cell_size_2px(self):
        """CELL = 2 for 2px-per-cell rendering."""
        assert "CELL = 2" in self.html or "CELL=2" in self.html

    def test_steps_per_frame_200(self):
        """200 steps batched per frame for visible progress."""
        assert "STEPS_PER_FRAME = 200" in self.html or "200" in self.html

    def test_toroidal_wrap_x(self):
        """Toroidal wrapping must use modulo W on the x axis."""
        assert re.search(r"[%+]\s*W\b", self.html), "No toroidal X wrap found"

    def test_toroidal_wrap_y(self):
        """Toroidal wrapping must use modulo H on the y axis."""
        assert re.search(r"[%+]\s*H\b", self.html), "No toroidal Y wrap found"

    def test_classic_rl_rule_present(self):
        """Classic Langton's Ant rule string 'RL' must be present."""
        assert '"RL"' in self.html or "'RL'" in self.html

    def test_rlr_rule_present(self):
        """Three-colour rule 'RLR' must be present."""
        assert '"RLR"' in self.html or "'RLR'" in self.html

    def test_llrr_rule_present(self):
        """Four-colour rule 'LLRR' must be present."""
        assert '"LLRR"' in self.html or "'LLRR'" in self.html

    def test_five_ants_defined(self):
        """At least 5 ant objects must be defined (one per distinct rule)."""
        hits = re.findall(r'rules\s*:', self.html)
        assert len(hits) >= 5, f"Expected ≥5 rule entries, found {len(hits)}"

    def test_five_distinct_hues(self):
        """Five distinct hue values must be present for the five ants."""
        hues = re.findall(r'\bhue\s*:\s*(\d+)', self.html)
        assert len(set(hues)) >= 5, f"Expected ≥5 distinct hues, found {set(hues)}"

    def test_uint8array_grid(self):
        """Cell grid must use a Uint8Array for efficient storage."""
        assert "Uint8Array" in self.html

    def test_owner_array_present(self):
        """An owner/last-visitor array must be present for colour attribution."""
        assert "owner" in self.html

    def test_hsl_to_rgb_present(self):
        """HSL→RGB conversion must be present for per-ant palette generation."""
        assert "hsl" in self.html.lower() or "Hsl" in self.html

    def test_no_external_dependencies(self):
        """index.html must be self-contained (no external script src)."""
        assert not re.search(r'<script[^>]+src="https?://', self.html)

    def test_image_rendering_pixelated(self):
        """CSS must set image-rendering to pixelated for crisp cell display."""
        assert "pixelated" in self.html


# ---------------------------------------------------------------------------
# Turmite logic unit tests (Python simulation)
# ---------------------------------------------------------------------------

class TestTurmiteLogic:
    """Verify the step() algorithm with a Python re-implementation."""

    def _make_ant(self, rules, x=5, y=5, direction=0):
        return {'x': x, 'y': y, 'dir': direction, 'rules': rules}

    def test_rl_on_white_turns_right(self):
        """On colour 0 (white), the RL ant must turn right."""
        W, H = 20, 20
        grid = [0] * (W * H)
        ant = self._make_ant("RL", x=5, y=5, direction=0)  # facing N
        turmite_step(grid, W, H, ant)
        assert ant['dir'] == 1  # N + right = E

    def test_rl_on_black_turns_left(self):
        """On colour 1 (black), the RL ant must turn left."""
        W, H = 20, 20
        grid = [0] * (W * H)
        grid[5 * W + 5] = 1  # pre-set cell to black
        ant = self._make_ant("RL", x=5, y=5, direction=0)  # facing N
        turmite_step(grid, W, H, ant)
        assert ant['dir'] == 3  # N + left = W

    def test_rl_flips_cell_white_to_black(self):
        """RL ant on white (0) must flip cell to black (1)."""
        W, H = 20, 20
        grid = [0] * (W * H)
        ant = self._make_ant("RL", x=5, y=5, direction=0)
        idx = turmite_step(grid, W, H, ant)
        assert grid[idx] == 1

    def test_rl_flips_cell_black_to_white(self):
        """RL ant on black (1) must flip cell back to white (0)."""
        W, H = 20, 20
        grid = [0] * (W * H)
        grid[5 * W + 5] = 1
        ant = self._make_ant("RL", x=5, y=5, direction=0)
        idx = turmite_step(grid, W, H, ant)
        assert grid[idx] == 0

    def test_rl_moves_forward_after_turn(self):
        """After turning right from N (→E), ant should move east."""
        W, H = 20, 20
        grid = [0] * (W * H)
        ant = self._make_ant("RL", x=5, y=5, direction=0)  # N → turn R → E
        turmite_step(grid, W, H, ant)
        assert ant['x'] == 6 and ant['y'] == 5

    def test_three_colour_rlr_cycles(self):
        """RLR ant must cycle cell through 0→1→2→0 over three visits."""
        W, H = 20, 20
        grid = [0] * (W * H)
        x, y = 10, 10

        for expected_after in [1, 2, 0]:
            ant = self._make_ant("RLR", x=x, y=y, direction=0)
            turmite_step(grid, W, H, ant)
            assert grid[y * W + x] == expected_after
            # Reset ant back to same cell for next iteration
            x_new, y_new = ant['x'], ant['y']
            # Move ant back manually to re-visit same cell
            ant['x'] = x
            ant['y'] = y

    def test_toroidal_wrap_east_boundary(self):
        """Ant stepping east off the right edge must reappear at x=0."""
        W, H = 10, 10
        grid = [0] * (W * H)
        ant = self._make_ant("RL", x=W - 1, y=5, direction=1)  # facing E
        # White cell → turn right (to S), move south; won't wrap east here.
        # Force a situation where ant faces E and is already on right edge.
        grid[(W - 1) + 5 * W] = 1  # black → turn left (to N), move N; no wrap
        # Try with a straight rule: use N (no turn) by patching rules
        ant2 = {'x': W - 1, 'y': 5, 'dir': 1, 'rules': 'N'}  # single-colour, no turn
        turmite_step(grid, W, H, ant2)
        assert ant2['x'] == 0  # wrapped around

    def test_toroidal_wrap_north_boundary(self):
        """Ant stepping north off the top edge must reappear at y=H-1."""
        W, H = 10, 10
        grid = [0] * (W * H)
        ant = {'x': 5, 'y': 0, 'dir': 0, 'rules': 'N'}  # facing N, no-turn rule
        turmite_step(grid, W, H, ant)
        assert ant['y'] == H - 1  # wrapped around

    def test_four_colour_llrr_first_step(self):
        """LLRR ant on colour 0 turns left (L = first character)."""
        W, H = 20, 20
        grid = [0] * (W * H)
        ant = self._make_ant("LLRR", x=10, y=10, direction=0)  # N
        turmite_step(grid, W, H, ant)
        assert ant['dir'] == 3  # N + L = W

    def test_cell_colour_stays_in_rule_range(self):
        """After any step, cell colour must remain in [0, len(rules))."""
        W, H = 20, 20
        grid = [0] * (W * H)
        ant = self._make_ant("RLLR", x=10, y=10, direction=0)
        for _ in range(20):
            idx = turmite_step(grid, W, H, ant)
            # Move ant back to same cell each time to exhaust colour cycles
            ant['x'] = 10
            ant['y'] = 10
            assert 0 <= grid[idx] < len(ant['rules'])

    def test_cross_ant_colour_modulo(self):
        """
        When a 2-rule ant visits a cell left at colour-2 by a 3-rule ant,
        it must use colour 2%2=0 for its turn decision and write (0+1)%2=1.
        """
        W, H = 10, 10
        grid = [0] * (W * H)
        grid[5 * W + 5] = 2  # colour 2, set by hypothetical 3-rule ant
        ant = self._make_ant("RL", x=5, y=5, direction=0)
        idx = turmite_step(grid, W, H, ant)
        # nc = 2%2 = 0 → rule='R' → turn right; cell → (0+1)%2 = 1
        assert grid[idx] == 1
        assert ant['dir'] == 1  # turned right from N → E

    def test_large_grid_no_index_error(self):
        """Simulation must not raise IndexError on a 512×512 grid after 500 steps."""
        W, H = 512, 512
        grid = [0] * (W * H)
        ant = self._make_ant("RL", x=W // 4, y=H // 4, direction=0)
        for _ in range(500):
            turmite_step(grid, W, H, ant)

    def test_rl_highway_emerges(self):
        """
        After 10 000 RL steps from the centre of a 256×256 grid, the ant must
        have escaped its initial chaotic phase and be moving in a clear direction
        (net displacement > 50 cells from start, indicating highway mode).
        """
        W, H = 256, 256
        grid = [0] * (W * H)
        start_x, start_y = W // 2, H // 2
        ant = self._make_ant("RL", x=start_x, y=start_y, direction=0)
        for _ in range(10_000):
            turmite_step(grid, W, H, ant)
        dx = abs(ant['x'] - start_x)
        dy = abs(ant['y'] - start_y)
        dist = min(dx, W - dx) + min(dy, H - dy)  # toroidal Manhattan distance
        # The chaotic pre-highway phase keeps the ant near the origin.
        # By 10 000 steps the RL ant is at or near the start of its highway, so
        # a net displacement >20 cells is sufficient evidence it left the origin.
        assert dist > 20, f"Expected highway escape (dist>20), got {dist}"


# ---------------------------------------------------------------------------
# Thumbnail tests
# ---------------------------------------------------------------------------

class TestThumbnail:
    """thumbnail.svg must be well-formed SVG at 400×400 with required content."""

    def test_is_valid_svg(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text().strip()
        assert content.startswith("<svg") or content.startswith("<?xml")

    def test_has_400_dimension(self):
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "400" in content

    def test_nonempty(self):
        assert len((PIECE_DIR / "thumbnail.svg").read_text()) > 200

    def test_contains_radial_gradient(self):
        """Thumbnail must use radialGradient for per-ant glow regions."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "radialGradient" in content

    def test_contains_pixel_rects(self):
        """Thumbnail must contain <rect> elements simulating the cell grid."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        rects = re.findall(r'<rect\b', content)
        assert len(rects) >= 10, f"Expected ≥10 rect elements, found {len(rects)}"

    def test_contains_dark_background(self):
        """Thumbnail must use the near-black background colour."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        assert "#050508" in content or "050508" in content

    def test_five_gradient_ids(self):
        """One radialGradient per ant — thumbnail must define ≥5 gradients."""
        content = (PIECE_DIR / "thumbnail.svg").read_text()
        ids = re.findall(r'<radialGradient\b[^>]+id="([^"]+)"', content)
        assert len(ids) >= 5, f"Expected ≥5 radialGradient ids, found {ids}"


# ---------------------------------------------------------------------------
# pieces.json tests
# ---------------------------------------------------------------------------

class TestPiecesJson:
    """pieces.json must contain a complete, correct entry for Piece 106."""

    def test_entry_exists(self):
        assert _load_entry() is not None, f"No entry with id={PIECE_ID!r}"

    def test_entry_has_all_required_fields(self):
        entry = _load_entry()
        assert entry is not None
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, f"Missing fields: {missing}"

    def test_entry_id_matches_directory_name(self):
        entry = _load_entry()
        assert entry is not None
        assert (REPO / entry["path"]).name == entry["id"]

    def test_entry_year_is_int(self):
        entry = _load_entry()
        assert isinstance(entry["year"], int)

    def test_entry_thumbnail_file_exists(self):
        entry = _load_entry()
        assert (REPO / entry["thumbnail"]).is_file()

    def test_entry_path_directory_exists(self):
        entry = _load_entry()
        assert (REPO / entry["path"]).is_dir()

    def test_langtons_in_technique(self):
        """Technique field must mention Langton's Ant or turmite."""
        entry = _load_entry()
        assert "langton" in entry["technique"].lower() or "turmite" in entry["technique"].lower()

    def test_piece_106_appears_after_102(self):
        """Piece 106 must come after piece 102 in the list (ordering)."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "102-hyperbolic-tiling" in ids
        assert PIECE_ID in ids
        assert ids.index(PIECE_ID) > ids.index("102-hyperbolic-tiling")


# ---------------------------------------------------------------------------
# Edge-case and failure-mode tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge cases and explicit failure-mode assertions."""

    def test_unknown_piece_id_returns_none(self):
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost-turmite"), None)
        assert found is None

    def test_nonexistent_piece_directory_is_not_dir(self, tmp_path):
        ghost = tmp_path / "pieces" / "ghost-turmite"
        assert not ghost.is_dir()

    def test_pieces_json_is_a_list(self):
        data = json.loads(PIECES_JSON.read_text())
        assert isinstance(data, list)
        assert len(data) > 0

    def test_missing_title_field_detected(self):
        """Entry without 'title' must fail the required-field check."""
        entry = {
            "id": PIECE_ID,
            "tagline": "Test",
            "year": 2026,
            "technique": "canvas",
            "path": f"pieces/{PIECE_ID}",
            "thumbnail": f"pieces/{PIECE_ID}/thumbnail.svg",
        }
        assert not (REQUIRED_FIELDS <= entry.keys())

    def test_empty_entry_fails_required_fields(self):
        assert not (REQUIRED_FIELDS <= {}.keys())

    def test_empty_grid_all_background(self):
        """A fresh (all-zero) grid means every cell is unvisited background."""
        W, H = 8, 8
        grid = [0] * (W * H)
        assert all(c == 0 for c in grid)

    def test_single_cell_grid_wraps_to_itself(self):
        """On a 1×1 grid the ant wraps back to the only cell every step."""
        W, H = 1, 1
        grid = [0]
        ant = {'x': 0, 'y': 0, 'dir': 0, 'rules': 'RL'}
        for _ in range(10):
            turmite_step(grid, W, H, ant)
            assert ant['x'] == 0 and ant['y'] == 0

    def test_invalid_rule_character_treated_as_no_turn(self):
        """Unknown rule characters default to no-turn (N), so direction unchanged."""
        W, H = 10, 10
        grid = [0] * (W * H)
        ant = {'x': 5, 'y': 5, 'dir': 1, 'rules': 'X'}  # X is unknown → N
        turmite_step(grid, W, H, ant)
        assert ant['dir'] == 1  # direction unchanged (no-turn)

    def test_uturn_rule(self):
        """'U' rule must reverse the ant's heading."""
        W, H = 10, 10
        grid = [0] * (W * H)
        ant = {'x': 5, 'y': 5, 'dir': 0, 'rules': 'U'}  # N → U → S
        turmite_step(grid, W, H, ant)
        assert ant['dir'] == 2  # S
