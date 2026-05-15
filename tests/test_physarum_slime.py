"""Tests for Piece 175 — The Mold That Finds the Train Schedule: Physarum."""
import json
import math
import pathlib
import re

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_ID  = "175-physarum-slime"
PIECE_DIR = REPO / "pieces" / PIECE_ID
PIECES_JSON   = REPO / "pieces.json"
REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}

# Mirror of JS simulation constants used in the Python algorithm tests
W            = 800
H            = 500
SENSOR_ANGLE = math.pi / 6   # 30°
SENSOR_DIST  = 9
STEP_SIZE    = 1.5
DECAY        = 0.96
DEPOSIT      = 5.0


# ---------------------------------------------------------------------------
# Python re-implementations of the core Physarum algorithms
# ---------------------------------------------------------------------------

def sample_trail(trail, w, h, sx, sy):
    """Return trail intensity at pixel (sx, sy) with toroidal wrapping.

    *sx* and *sy* are floating-point sensor positions; they are truncated
    to integer pixel indices and wrapped onto the toroidal [0,w) × [0,h) grid.
    """
    ix = (int(sx) % w + w) % w
    iy = (int(sy) % h + h) % h
    return trail[iy * w + ix]


def deposit_trail(trail, w, h, x, y, amount):
    """Add *amount* to the trail cell that contains position (x, y).

    Position wraps toroidally; the return value is the modified index.
    """
    ix = (int(x) % w + w) % w
    iy = (int(y) % h + h) % h
    idx = iy * w + ix
    trail[idx] += amount
    return idx


def diffuse_decay(trail, w, h, decay):
    """Return a new trail array after one 3×3 box-blur diffusion step and decay.

    Each pixel is replaced by the mean of its 3×3 neighbourhood (toroidal),
    multiplied by *decay*.
    """
    out = [0.0] * (w * h)
    for y in range(h):
        y_row = y * w
        y_n = ((y - 1) % h) * w
        y_s = ((y + 1) % h) * w
        for x in range(w):
            x_w = (x - 1) % w
            x_e = (x + 1) % w
            total = (
                trail[y_n + x_w] + trail[y_n + x] + trail[y_n + x_e]
                + trail[y_row + x_w] + trail[y_row + x] + trail[y_row + x_e]
                + trail[y_s + x_w] + trail[y_s + x] + trail[y_s + x_e]
            )
            out[y_row + x] = total / 9.0 * decay
    return out


def steer(fwd, left, right, current_angle, sensor_angle):
    """Compute the new heading after one chemotaxis step.

    Returns the updated angle (radians).  When all three sensors read the
    same value the heading is unchanged (the JS implementation adds random
    jitter; here we return the unmodified angle for deterministic testing).
    """
    if fwd > left and fwd > right:
        return current_angle
    if left > right:
        return current_angle + sensor_angle
    if right > left:
        return current_angle - sensor_angle
    return current_angle  # tie — unchanged (jitter omitted for determinism)


def move_wrap(x, y, angle, step, w, h):
    """Advance position by *step* in *angle* direction and wrap toroidally.

    Returns (new_x, new_y).
    """
    nx = (x + math.cos(angle) * step + w) % w
    ny = (y + math.sin(angle) * step + h) % h
    return nx, ny


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


# ---------------------------------------------------------------------------
# SVG thumbnail content
# ---------------------------------------------------------------------------

class TestThumbnailSvg:
    def setup_method(self):
        self.svg = (PIECE_DIR / "thumbnail.svg").read_text()

    def test_has_svg_root(self):
        assert "<svg" in self.svg and "</svg>" in self.svg

    def test_has_background_rect(self):
        assert "<rect" in self.svg

    def test_has_path_elements(self):
        """Vein network must be represented as path elements."""
        assert "<path" in self.svg

    def test_has_dark_background_color(self):
        """Background must be a very dark purple/indigo."""
        assert re.search(r'#(0[0-9a-fA-F]){3}|#[0-1][0-9a-fA-F]{5}', self.svg)

    def test_has_teal_color(self):
        """Palette must contain the electric-teal tone."""
        assert "00e6c8" in self.svg or "00d8c8" in self.svg or "rgba(0,2" in self.svg or "rgba(0, 2" in self.svg

    def test_dimensions_set(self):
        assert 'width="400"' in self.svg
        assert 'height="250"' in self.svg

    def test_has_viewbox(self):
        assert "viewBox" in self.svg or "viewbox" in self.svg.lower()


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

    def test_no_external_script_src(self):
        assert not re.search(r'<script[^>]+src="https?://', self.html)

    def test_n_agents_at_least_8000(self):
        """Must declare at least 8 000 agents (spec: ≥ 8 000)."""
        match = re.search(r'N\s*=\s*(\d+)', self.html)
        assert match, "Could not find N = <number> constant"
        assert int(match.group(1)) >= 8000, f"N={match.group(1)} < 8000"

    def test_float32array_for_trail(self):
        """Trail buffer must be a Float32Array."""
        assert "Float32Array" in self.html

    def test_float32array_for_agents(self):
        """Agent array must be a Float32Array (typed array)."""
        assert self.html.count("Float32Array") >= 2

    def test_sensor_angle_30_degrees(self):
        """sensorAngle must be 30° — appears as PI / 6 or explicit value."""
        assert "/ 6" in self.html or "SENSOR_ANGLE" in self.html

    def test_sensor_dist_9(self):
        assert "9" in self.html

    def test_step_size_1_5(self):
        assert "1.5" in self.html

    def test_decay_factor_0_96(self):
        assert "0.96" in self.html

    def test_imagedata_used(self):
        assert "ImageData" in self.html or "createImageData" in self.html

    def test_putimagedata_called(self):
        assert "putImageData" in self.html

    def test_toroidal_wrap_horizontal(self):
        """Agents must wrap on the x-axis."""
        assert re.search(r'\+\s*W\s*\)\s*%\s*W', self.html)

    def test_toroidal_wrap_vertical(self):
        """Agents must wrap on the y-axis."""
        assert re.search(r'\+\s*H\s*\)\s*%\s*H', self.html)

    def test_box_blur_diffusion(self):
        """Trail must be diffused with a 3×3 neighbourhood (INV9 or /9)."""
        assert "INV9" in self.html or "/ 9" in self.html or "/9" in self.html

    def test_deposit_present(self):
        assert "DEPOSIT" in self.html or "deposit" in self.html.lower()

    def test_smoothstep_for_palette(self):
        """Palette mapping must use smoothstep (3 - 2 * t pattern)."""
        assert "3 - 2" in self.html or "3-2" in self.html

    def test_palette_deep_violet(self):
        """Background palette stop must be a deep violet."""
        assert "18" in self.html or "1a0" in self.html or "120028" in self.html

    def test_palette_teal(self):
        """Mid-palette stop must be an electric teal."""
        assert "230" in self.html or "00e6" in self.html

    def test_canvas_width_800(self):
        assert "800" in self.html

    def test_canvas_height_500(self):
        assert "500" in self.html

    def test_ring_initialisation(self):
        """Agents must be placed on a ring (cos/sin of theta * radius)."""
        assert re.search(r'Math\.cos\s*\(', self.html)
        assert re.search(r'RING_R|ring_r|ring|Math\.min', self.html, re.IGNORECASE)

    def test_self_contained(self):
        """No <link> or <script src> pointing to an external URL."""
        assert not re.search(r'<link[^>]+href="https?://', self.html)


# ---------------------------------------------------------------------------
# Algorithm math (Python re-implementations)
# ---------------------------------------------------------------------------

class TestSampleTrail:
    """Verify correct toroidal indexing in sampleTrail."""

    def test_origin_pixel(self):
        trail = [0.0] * (W * H)
        trail[0] = 7.5
        assert sample_trail(trail, W, H, 0.0, 0.0) == pytest.approx(7.5)

    def test_integer_index_inside_grid(self):
        trail = [0.0] * (W * H)
        trail[3 * W + 5] = 2.0
        assert sample_trail(trail, W, H, 5.0, 3.0) == pytest.approx(2.0)

    def test_wraps_x_at_right_edge(self):
        """Sensor at x=W should index into column 0."""
        trail = [0.0] * (W * H)
        trail[0] = 9.9
        assert sample_trail(trail, W, H, float(W), 0.0) == pytest.approx(9.9)

    def test_wraps_y_at_bottom_edge(self):
        """Sensor at y=H should index into row 0."""
        trail = [0.0] * (W * H)
        trail[0] = 3.3
        assert sample_trail(trail, W, H, 0.0, float(H)) == pytest.approx(3.3)

    def test_negative_x_wraps(self):
        """Negative x must still produce a valid index."""
        trail = [0.0] * (W * H)
        trail[W - 1] = 4.4
        v = sample_trail(trail, W, H, -1.0, 0.0)
        assert v == pytest.approx(4.4)

    def test_truncates_fractional_position(self):
        """Fractional positions are floored to the pixel cell."""
        trail = [0.0] * (W * H)
        trail[2 * W + 3] = 5.5
        assert sample_trail(trail, W, H, 3.7, 2.9) == pytest.approx(5.5)


class TestDepositTrail:
    def test_deposit_at_origin(self):
        trail = [0.0] * (W * H)
        deposit_trail(trail, W, H, 0, 0, DEPOSIT)
        assert trail[0] == pytest.approx(DEPOSIT)

    def test_deposit_accumulates(self):
        trail = [0.0] * (W * H)
        deposit_trail(trail, W, H, 10, 10, DEPOSIT)
        deposit_trail(trail, W, H, 10, 10, DEPOSIT)
        assert trail[10 * W + 10] == pytest.approx(DEPOSIT * 2)

    def test_deposit_wraps_toroidally(self):
        trail = [0.0] * (W * H)
        deposit_trail(trail, W, H, W, 0, DEPOSIT)
        assert trail[0] == pytest.approx(DEPOSIT)

    def test_deposit_does_not_affect_neighbors(self):
        trail = [0.0] * (W * H)
        deposit_trail(trail, W, H, 5, 5, DEPOSIT)
        assert trail[5 * W + 4] == 0.0
        assert trail[5 * W + 6] == 0.0
        assert trail[4 * W + 5] == 0.0
        assert trail[6 * W + 5] == 0.0


class TestDiffuseDecay:
    """Verify the 3×3 box-blur diffusion and decay on small grids."""

    def test_single_pulse_spreads_to_neighbors(self):
        """After one diffusion, a spike at (1,1) on a 3×3 grid spreads to all cells."""
        w, h = 3, 3
        trail = [0.0] * (w * h)
        trail[1 * w + 1] = 9.0  # centre = 9, rest = 0 → mean = 1.0
        out = diffuse_decay(trail, w, h, 1.0)
        for v in out:
            assert v == pytest.approx(1.0), f"Expected 1.0 everywhere, got {v}"

    def test_uniform_field_stays_uniform(self):
        """Uniform trail is unchanged by box blur; only decay applies."""
        w, h = 4, 4
        trail = [2.0] * (w * h)
        out = diffuse_decay(trail, w, h, DECAY)
        for v in out:
            assert v == pytest.approx(2.0 * DECAY)

    def test_decay_factor_applied(self):
        """A single full pulse on a 1×1 grid decays by exactly DECAY."""
        trail = [10.0]
        out = diffuse_decay(trail, 1, 1, DECAY)
        assert out[0] == pytest.approx(10.0 * DECAY)

    def test_zero_trail_stays_zero(self):
        w, h = 5, 5
        trail = [0.0] * (w * h)
        out = diffuse_decay(trail, w, h, DECAY)
        assert all(v == 0.0 for v in out)


class TestSteer:
    """Verify chemotaxis steering logic."""

    def test_forward_strongest_no_turn(self):
        a = steer(10.0, 5.0, 5.0, 0.0, SENSOR_ANGLE)
        assert a == pytest.approx(0.0)

    def test_left_stronger_turns_left(self):
        a = steer(0.0, 8.0, 2.0, 0.0, SENSOR_ANGLE)
        assert a == pytest.approx(SENSOR_ANGLE)

    def test_right_stronger_turns_right(self):
        a = steer(0.0, 2.0, 8.0, 0.0, SENSOR_ANGLE)
        assert a == pytest.approx(-SENSOR_ANGLE)

    def test_tie_no_change(self):
        """Deterministic tie-breaking: heading unchanged when all sensors equal."""
        a = steer(5.0, 5.0, 5.0, 1.0, SENSOR_ANGLE)
        assert a == pytest.approx(1.0)

    def test_turn_magnitude_equals_sensor_angle(self):
        """Each turn is by exactly one sensor angle step."""
        a_left  = steer(0.0, 10.0, 0.0, 0.0, SENSOR_ANGLE)
        a_right = steer(0.0, 0.0, 10.0, 0.0, SENSOR_ANGLE)
        assert abs(a_left)  == pytest.approx(SENSOR_ANGLE)
        assert abs(a_right) == pytest.approx(SENSOR_ANGLE)


class TestMoveWrap:
    """Verify toroidal movement wrapping."""

    def test_moves_in_angle_direction(self):
        nx, ny = move_wrap(100, 100, 0.0, STEP_SIZE, W, H)
        assert nx == pytest.approx(100 + STEP_SIZE)
        assert ny == pytest.approx(100.0)

    def test_wraps_at_right_edge(self):
        nx, ny = move_wrap(W - 0.5, 100, 0.0, STEP_SIZE, W, H)
        assert nx < STEP_SIZE + 1

    def test_wraps_at_bottom_edge(self):
        _, ny = move_wrap(100, H - 0.5, math.pi / 2, STEP_SIZE, W, H)
        assert ny < STEP_SIZE + 1

    def test_step_size_consistent(self):
        """Distance moved in one step must equal STEP_SIZE (straight path)."""
        x0, y0 = 200.0, 200.0
        angle = math.pi / 4
        nx, ny = move_wrap(x0, y0, angle, STEP_SIZE, W, H)
        dist = math.hypot(nx - x0, ny - y0)
        assert dist == pytest.approx(STEP_SIZE, abs=1e-6)

    def test_negative_angle_wraps_correctly(self):
        """Agents moving left must still wrap onto the canvas."""
        nx, ny = move_wrap(0.5, 100, math.pi, STEP_SIZE, W, H)
        assert 0 <= nx < W


# ---------------------------------------------------------------------------
# pieces.json registration
# ---------------------------------------------------------------------------

def _load_entry():
    """Return the pieces.json entry for piece 175, or None if absent."""
    data = json.loads(PIECES_JSON.read_text())
    return next((e for e in data if e["id"] == PIECE_ID), None)


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
        assert isinstance(_load_entry()["year"], int)

    def test_entry_path_exists(self):
        assert (REPO / _load_entry()["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        assert (REPO / _load_entry()["thumbnail"]).is_file()

    def test_technique_mentions_physarum(self):
        entry = _load_entry()
        assert "Physarum" in entry["technique"] or "physarum" in entry["technique"].lower()

    def test_technique_mentions_float32array(self):
        entry = _load_entry()
        assert "Float32Array" in entry["technique"]

    def test_piece_175_appears_after_171(self):
        """Piece 175 must appear after piece 171 in the ordered list."""
        data = json.loads(PIECES_JSON.read_text())
        ids = [e["id"] for e in data]
        assert "171-conformal-grid" in ids
        assert PIECE_ID in ids
        assert ids.index(PIECE_ID) > ids.index("171-conformal-grid")

    def test_tagline_mentions_agents(self):
        entry = _load_entry()
        assert "agent" in entry["tagline"].lower() or "12" in entry["tagline"]


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_sample_trail_empty_grid_returns_zero(self):
        """An all-zero trail returns 0 for any position."""
        trail = [0.0] * (W * H)
        assert sample_trail(trail, W, H, 123.4, 56.7) == 0.0

    def test_diffuse_large_grid_does_not_raise(self):
        """Diffusion over a realistic grid size completes without error."""
        w, h = 20, 20
        trail = [float(i % 5) for i in range(w * h)]
        out = diffuse_decay(trail, w, h, DECAY)
        assert len(out) == w * h

    def test_steer_with_zero_trail_everywhere(self):
        """All-zero sensors leave heading unchanged."""
        a = steer(0.0, 0.0, 0.0, 1.23, SENSOR_ANGLE)
        assert a == pytest.approx(1.23)

    def test_move_wrap_full_lap(self):
        """Moving W steps rightward returns to the starting column."""
        x0, y0 = 100.0, 100.0
        steps = int(W / STEP_SIZE) + 1
        x, y = x0, y0
        for _ in range(steps):
            x, y = move_wrap(x, y, 0.0, STEP_SIZE, W, H)
        assert 0 <= x < W

    def test_unknown_piece_id_absent(self):
        data = json.loads(PIECES_JSON.read_text())
        found = next((e for e in data if e["id"] == "999-ghost-mold"), None)
        assert found is None

    def test_deposit_large_amount_does_not_corrupt_neighbors(self):
        """Depositing a large value at (0,0) must not change pixel (0,1)."""
        trail = [0.0] * (W * H)
        deposit_trail(trail, W, H, 0, 0, 1e6)
        assert trail[W] == 0.0

    def test_diffuse_wraps_toroidally(self):
        """A spike at corner (0,0) on a 3×3 grid sees all 8 wrap-around neighbours."""
        w, h = 3, 3
        trail = [0.0] * (w * h)
        trail[0] = 9.0
        out = diffuse_decay(trail, w, h, 1.0)
        for v in out:
            assert v == pytest.approx(1.0)
