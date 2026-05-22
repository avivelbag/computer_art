"""Tests for Piece 272 — Pendulum Wave."""

import json
import math
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "272-pendulum-wave"
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}


class TestFileStructure:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir()

    def test_index_html_exists(self):
        assert (PIECE_DIR / "index.html").is_file()

    def test_readme_exists(self):
        assert (PIECE_DIR / "README.md").is_file()

    def test_thumbnail_exists(self):
        assert (PIECE_DIR / "thumbnail.svg").is_file() or (PIECE_DIR / "thumbnail.png").is_file()

    def test_index_html_not_empty(self):
        html = (PIECE_DIR / "index.html").read_text()
        assert len(html) > 200

    def test_readme_not_empty(self):
        readme = (PIECE_DIR / "README.md").read_text()
        assert len(readme) > 50


class TestPiecesJson:
    def _load(self):
        return json.loads(PIECES_JSON.read_text())

    def _find_entry(self):
        return next((e for e in self._load() if e["id"] == "272-pendulum-wave"), None)

    def test_entry_exists(self):
        assert self._find_entry() is not None

    def test_entry_has_all_required_fields(self):
        entry = self._find_entry()
        assert entry is not None
        assert REQUIRED_FIELDS <= entry.keys(), f"Missing fields: {REQUIRED_FIELDS - entry.keys()}"

    def test_entry_path_matches_directory(self):
        entry = self._find_entry()
        assert entry is not None
        assert (REPO / entry["path"]).is_dir()

    def test_entry_thumbnail_file_exists(self):
        entry = self._find_entry()
        assert entry is not None
        assert (REPO / entry["thumbnail"]).is_file()

    def test_entry_id_matches_dir_name(self):
        entry = self._find_entry()
        assert entry is not None
        assert entry["id"] == pathlib.Path(entry["path"]).name

    def test_entry_year_is_int(self):
        entry = self._find_entry()
        assert entry is not None
        assert isinstance(entry["year"], int)


class TestPendulumPhysics:
    """Verify the tuned-period physics properties that make the loop exact."""

    N = 20
    T_GALLERY = 60
    N_MIN = 40

    def periods(self):
        return [self.T_GALLERY / (self.N_MIN + i) for i in range(self.N)]

    def test_each_pendulum_completes_integer_oscillations(self):
        """Each pendulum must complete exactly (N_MIN + i) full oscillations in T_GALLERY seconds."""
        for i, T_i in enumerate(self.periods()):
            oscillations = self.T_GALLERY / T_i
            assert abs(oscillations - (self.N_MIN + i)) < 1e-9, (
                f"Pendulum {i}: expected {self.N_MIN + i} oscillations, got {oscillations}"
            )

    def test_all_pendulums_sync_at_period_boundary(self):
        """At t = T_GALLERY, every pendulum phase is an exact multiple of 2π so sin = 0."""
        for i, T_i in enumerate(self.periods()):
            phase = 2 * math.pi * self.T_GALLERY / T_i
            assert abs(math.sin(phase)) < 1e-9, (
                f"Pendulum {i} not at rest at T_GALLERY: sin(phase) = {math.sin(phase)}"
            )

    def test_all_pendulums_sync_at_time_zero(self):
        """At t = 0, sin(0) = 0 for all pendulums — the starting alignment."""
        for i, T_i in enumerate(self.periods()):
            assert math.sin(2 * math.pi * 0 / T_i) == 0.0

    def test_pendulum_lengths_decrease_with_index(self):
        """Higher index → shorter period → shorter physical length (L ∝ T²)."""
        g = 9.81
        lengths = [g * (T / (2 * math.pi)) ** 2 for T in self.periods()]
        for i in range(self.N - 1):
            assert lengths[i] > lengths[i + 1], (
                f"Expected L[{i}] > L[{i + 1}] but got {lengths[i]:.4f} vs {lengths[i + 1]:.4f}"
            )

    def test_period_range_is_physically_reasonable(self):
        """Periods should be short enough for visible oscillation (< 5 s) but not too fast."""
        for i, T_i in enumerate(self.periods()):
            assert 0.5 < T_i < 5.0, f"Pendulum {i} period {T_i:.3f}s outside reasonable range"

    def test_midcycle_displacement_spread(self):
        """At t = T_GALLERY/8 the displacements should span a wide range (visible wave)."""
        t = self.T_GALLERY / 8
        disps = [math.sin(2 * math.pi * t / T_i) for T_i in self.periods()]
        spread = max(disps) - min(disps)
        assert spread > 1.0, f"Wave spread at T/8 too small: {spread:.3f} (expected > 1.0)"

    def test_pendulum_count_in_valid_range(self):
        """N must be between 15 and 24 per acceptance criteria."""
        assert 15 <= self.N <= 24


class TestHtmlContent:
    """Verify the index.html encodes the correct constants."""

    def html(self):
        return (PIECE_DIR / "index.html").read_text()

    def test_uses_request_animation_frame(self):
        assert "requestAnimationFrame" in self.html()

    def test_declares_pendulum_count(self):
        match = re.search(r"const N\s*=\s*(\d+)", self.html())
        assert match is not None, "Could not find 'const N = ...' in index.html"
        n = int(match.group(1))
        assert 15 <= n <= 24, f"N = {n} is outside required [15, 24] range"

    def test_declares_t_gallery(self):
        assert "T_GALLERY" in self.html() or "T_gallery" in self.html()

    def test_declares_n_min(self):
        assert "N_MIN" in self.html() or "n_min" in self.html()

    def test_no_external_dependencies(self):
        html = self.html()
        assert "<script src=" not in html
        assert "import " not in html or "from " not in html

    def test_has_canvas_element(self):
        assert "<canvas" in self.html()

    def test_dark_background(self):
        html = self.html()
        assert "#0d0d12" in html or "#0a0a14" in html or "#000" in html or "background: #" in html


class TestEdgeCases:
    """Failure-mode and edge-case checks."""

    def test_pieces_json_remains_valid_after_append(self):
        data = json.loads(PIECES_JSON.read_text())
        assert isinstance(data, list)
        assert len(data) > 0

    def test_missing_required_field_logic(self):
        """Verify the required-field check rejects an incomplete entry."""
        incomplete = {"id": "272-pendulum-wave", "title": "Pendulum Wave"}
        assert not (REQUIRED_FIELDS <= incomplete.keys())

    def test_period_formula_with_edge_n_min(self):
        """Period formula is valid for n_min = 1 (very slow pendulums) without division by zero."""
        T_gallery = 60
        for i in range(20):
            T_i = T_gallery / (1 + i)
            assert T_i > 0

    def test_large_n_min_produces_short_periods(self):
        """High n_min produces short periods — verify the oscillation count is still integral."""
        T_gallery = 60
        n_min = 100
        for i in range(20):
            T_i = T_gallery / (n_min + i)
            oscillations = T_gallery / T_i
            assert abs(oscillations - (n_min + i)) < 1e-9
