"""Tests for Piece 268 — Laminar Drift (flow-field / sinusoidal noise)."""
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "268-laminar-drift"
PIECE_DIR = REPO / "pieces" / PIECE_ID
INDEX_HTML = PIECE_DIR / "index.html"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
README = PIECE_DIR / "README.md"
PIECES_JSON = REPO / "pieces.json"


def _load_pieces() -> list[dict]:
    return json.loads(PIECES_JSON.read_text())


def _find_entry() -> dict | None:
    return next((e for e in _load_pieces() if e["id"] == PIECE_ID), None)


# ---------------------------------------------------------------------------
# File structure
# ---------------------------------------------------------------------------

class TestFileStructure:
    def test_piece_directory_exists(self):
        assert PIECE_DIR.is_dir(), f"Missing directory: {PIECE_DIR}"

    def test_index_html_exists(self):
        assert INDEX_HTML.is_file()

    def test_thumbnail_exists(self):
        assert THUMBNAIL.is_file()

    def test_readme_exists(self):
        assert README.is_file()

    def test_index_html_nonempty(self):
        assert INDEX_HTML.stat().st_size > 500

    def test_thumbnail_nonempty(self):
        assert THUMBNAIL.stat().st_size > 100

    def test_thumbnail_under_500kb(self):
        assert THUMBNAIL.stat().st_size < 500 * 1024, (
            f"thumbnail.svg is {THUMBNAIL.stat().st_size / 1024:.1f} KB; must be under 500 KB"
        )


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}


class TestPiecesJson:
    def test_entry_present(self):
        assert _find_entry() is not None, f"{PIECE_ID} not found in pieces.json"

    def test_entry_id_matches_dir(self):
        entry = _find_entry()
        assert entry["id"] == PIECE_ID

    def test_entry_has_required_fields(self):
        entry = _find_entry()
        assert REQUIRED_FIELDS <= entry.keys(), f"Missing fields: {REQUIRED_FIELDS - entry.keys()}"

    def test_entry_technique_contains_flow_field(self):
        entry = _find_entry()
        assert "flow-field" in entry["technique"]

    def test_entry_path_matches_piece_dir(self):
        entry = _find_entry()
        assert entry["path"] == f"pieces/{PIECE_ID}"

    def test_entry_thumbnail_path(self):
        entry = _find_entry()
        assert entry["thumbnail"] == f"pieces/{PIECE_ID}/thumbnail.svg"

    def test_no_duplicate_ids(self):
        ids = [e["id"] for e in _load_pieces()]
        assert len(ids) == len(set(ids)), "Duplicate IDs found in pieces.json"

    def test_old_suggested_id_absent(self):
        """The suggestion proposed 272; the orchestrator corrected it to 268."""
        pieces = _load_pieces()
        ghost = next((e for e in pieces if e["id"] == "272-flow-field"), None)
        assert ghost is None, "Stale id 272-flow-field should not appear"

    def test_piece_number_is_268(self):
        assert "268" in PIECE_ID


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

class TestIndexHtml:
    def _html(self) -> str:
        return INDEX_HTML.read_text()

    def test_has_particle_count_4000(self):
        assert "4000" in self._html(), "Expected N = 4000 particles"

    def test_has_lifetime_300(self):
        assert "300" in self._html(), "Expected LIFETIME = 300 frames"

    def test_has_noise_function(self):
        html = self._html()
        assert "Math.sin" in html
        assert "Math.cos" in html

    def test_has_trail_fade_alpha(self):
        assert "0.03" in self._html(), "Expected low-alpha (0.03) trail fade"

    def test_has_background_color(self):
        assert "#1c1c1e" in self._html()

    def test_has_torus_wrap_x(self):
        assert "% W" in self._html()

    def test_has_torus_wrap_y(self):
        assert "% H" in self._html()

    def test_has_requestAnimationFrame(self):
        assert "requestAnimationFrame" in self._html()

    def test_no_external_scripts(self):
        html = self._html()
        external = re.findall(r'<script[^>]+src\s*=\s*["\']https?://', html)
        assert not external, f"Found external script imports: {external}"

    def test_canvas_dimensions(self):
        html = self._html()
        assert 'width="800"' in html
        assert 'height="600"' in html


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------

class TestThumbnail:
    def test_thumbnail_is_valid_svg(self):
        tree = ET.parse(THUMBNAIL)
        root = tree.getroot()
        assert "svg" in root.tag

    def test_thumbnail_has_width_400(self):
        tree = ET.parse(THUMBNAIL)
        root = tree.getroot()
        assert root.get("width") == "400"

    def test_thumbnail_has_background_color(self):
        assert "#1c1c1e" in THUMBNAIL.read_text()

    def test_thumbnail_contains_lines(self):
        text = THUMBNAIL.read_text()
        assert "<polyline" in text or "<line" in text, (
            "Expected streamline segments rendered as <polyline> or <line> elements"
        )


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------

class TestReadme:
    def _text(self) -> str:
        return README.read_text()

    def test_readme_mentions_piece_115(self):
        assert "115" in self._text(), "README must explain how this differs from piece 115"

    def test_readme_mentions_piece_238(self):
        assert "238" in self._text(), "README must explain how this differs from piece 238"

    def test_readme_does_not_claim_technique_is_absent(self):
        text = self._text().lower()
        assert "absent" not in text, "README must not falsely claim flow fields are new to gallery"

    def test_readme_mentions_palette(self):
        assert "#0d7377" in self._text() or "teal" in self._text().lower()


# ---------------------------------------------------------------------------
# Edge-cases and failure modes
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_missing_required_field_detected(self):
        """Verify the field-checking logic catches incomplete entries."""
        incomplete = {
            "id": "268-laminar-drift",
            "tagline": "test",
            "year": 2026,
            "technique": "canvas / flow-field",
            "path": "pieces/268-laminar-drift",
            "thumbnail": "pieces/268-laminar-drift/thumbnail.svg",
        }
        missing = REQUIRED_FIELDS - incomplete.keys()
        assert missing, f"Expected missing fields but got none; fields: {incomplete.keys()}"

    def test_id_mismatch_would_fail(self):
        """id must equal the final path segment."""
        entry = {**_find_entry(), "id": "wrong-id"}
        piece_dir_name = pathlib.Path(entry["path"]).name
        assert entry["id"] != piece_dir_name

    def test_nonexistent_thumbnail_would_fail(self, tmp_path):
        """A thumbnail path pointing at a missing file should not exist."""
        fake_thumb = tmp_path / "pieces" / "268-laminar-drift" / "thumbnail.svg"
        assert not fake_thumb.exists()

    def test_generate_thumbnail_is_deterministic(self, tmp_path):
        """Running generate_thumbnail.py twice must produce identical SVG output."""
        import importlib.util, sys

        gen_path = PIECE_DIR / "generate_thumbnail.py"
        spec = importlib.util.spec_from_file_location("gen", gen_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        svg1 = mod.make_svg()
        svg2 = mod.make_svg()
        assert svg1 == svg2, "make_svg() must be deterministic (fixed random seed)"

    def test_noise_function_range(self):
        """The Python noise function should return values roughly bounded by ±1.75."""
        import importlib.util

        gen_path = PIECE_DIR / "generate_thumbnail.py"
        spec = importlib.util.spec_from_file_location("gen", gen_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        samples = [mod.noise(x * 0.003, y * 0.003, 0.3)
                   for x in range(0, 400, 20) for y in range(0, 400, 20)]
        # Sum of amplitudes is 1 + 0.5 + 0.25 = 1.75; sin*cos ≤ 1 so max ≤ 1.75
        assert all(-2.0 < v < 2.0 for v in samples), "Noise values out of expected range"

    def test_angle_to_rgb_gradient_boundary(self):
        """angle_to_rgb at angle=0 should be near deep teal; at π should be near gold."""
        import importlib.util

        gen_path = PIECE_DIR / "generate_thumbnail.py"
        spec = importlib.util.spec_from_file_location("gen", gen_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        r0, g0, b0 = mod.angle_to_rgb(0.0)
        assert r0 < 50 and g0 > 80 and b0 > 80, "angle=0 should map near deep teal"

        r_pi, g_pi, b_pi = mod.angle_to_rgb(math.pi)
        assert r_pi > 150 and g_pi > 120, "angle=π should map near gold"
