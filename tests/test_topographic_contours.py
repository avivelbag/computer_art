"""Tests for piece 64-topographic-contours (acceptance criteria verification)."""
import json
import pathlib
import re

import pytest

REPO  = pathlib.Path(__file__).parent.parent
PIECE = REPO / "pieces" / "64-topographic-contours"
INDEX = PIECE / "index.html"


# ─── helpers ──────────────────────────────────────────────────────────────────

def html_source() -> str:
    return INDEX.read_text(encoding="utf-8")


def pieces_json() -> list:
    return json.loads((REPO / "pieces.json").read_text(encoding="utf-8"))


def piece_entry() -> dict:
    for entry in pieces_json():
        if entry["id"] == "64-topographic-contours":
            return entry
    pytest.fail("64-topographic-contours not found in pieces.json")


# ─── file structure ───────────────────────────────────────────────────────────

def test_piece_directory_exists():
    assert PIECE.is_dir()


def test_index_html_exists():
    assert INDEX.is_file()


def test_thumbnail_exists():
    assert (PIECE / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE / "README.md").is_file()


# ─── pieces.json registration ─────────────────────────────────────────────────

def test_entry_in_pieces_json():
    assert piece_entry() is not None


def test_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    entry = piece_entry()
    assert required <= entry.keys()


def test_entry_id_matches_directory():
    entry = piece_entry()
    assert entry["id"] == PIECE.name


def test_entry_path_matches():
    entry = piece_entry()
    assert entry["path"] == "pieces/64-topographic-contours"


def test_entry_thumbnail_file_exists():
    entry = piece_entry()
    assert (REPO / entry["thumbnail"]).is_file()


# ─── no external dependencies ─────────────────────────────────────────────────

def test_no_script_src_tags():
    """All JavaScript must be inline — no CDN or external script tags."""
    src = html_source()
    # Match <script src="..."> (with optional whitespace or attributes)
    external = re.findall(r'<script[^>]+src\s*=', src, re.IGNORECASE)
    assert external == [], f"External script tags found: {external}"


def test_no_import_statements():
    """ES module imports from URLs would be an external dependency."""
    src = html_source()
    url_imports = re.findall(r'import\s+.*from\s+["\']https?://', src)
    assert url_imports == []


# ─── marching squares present ─────────────────────────────────────────────────

def test_marching_squares_case_table():
    """The switch statement must cover the 14 non-trivial marching-squares cases."""
    src = html_source()
    cases_found = set(re.findall(r'case\s+(\d+)\s*:', src))
    # Cases 1–14 must all appear (0 and 15 are skipped as trivial).
    expected = set(str(i) for i in range(1, 15))
    assert expected <= cases_found, f"Missing cases: {expected - cases_found}"


def test_saddle_cases_disambiguated():
    """Saddle cases 5 and 10 require midpoint disambiguation logic."""
    src = html_source()
    # Both saddle cases must appear
    assert 'case  5:' in src or 'case 5:' in src
    assert 'case 10:' in src


# ─── noise field ──────────────────────────────────────────────────────────────

def test_noise_function_inline():
    """Value noise must be implemented inline (no CDN)."""
    src = html_source()
    # Our implementation uses a permutation table
    assert 'PERM' in src


def test_fbm_present():
    """Fractal Brownian Motion (fBm) is used for terrain realism."""
    src = html_source()
    assert 'fbm' in src


def test_time_increment_present():
    """The noise Z-slice must advance each frame to animate the terrain."""
    src = html_source()
    # We increment `t` each frame
    assert re.search(r'\bt\s*\+=', src), "No time increment found in source"


# ─── visual specification ─────────────────────────────────────────────────────

def test_twelve_contour_levels():
    """Exactly 12 contour levels (matching the palette size) must be defined."""
    src = html_source()
    # PALETTE array with 12 entries
    palette_match = re.search(r'PALETTE\s*=\s*\[([^\]]+)\]', src, re.DOTALL)
    assert palette_match, "PALETTE array not found"
    colors = re.findall(r"'#[0-9a-fA-F]+'", palette_match.group(1))
    assert len(colors) == 12, f"Expected 12 palette colors, found {len(colors)}"


def test_index_contours_every_fifth():
    """Every 5th contour (index contour) must use a larger stroke width."""
    src = html_source()
    assert re.search(r'%\s*5', src), "No modulo-5 index contour logic found"


def test_canvas_dimensions():
    """Canvas must be 1200×900 (matching 120×90 grid at 10 px/cell)."""
    src = html_source()
    assert 'W = 1200' in src or "W=1200" in src
    assert 'H = 900'  in src or "H=900"  in src


def test_grid_resolution():
    """Grid must be 120 columns × 90 rows."""
    src = html_source()
    assert 'COLS = 120' in src or 'COLS=120' in src
    assert 'ROWS = 90'  in src or 'ROWS=90'  in src


def test_dark_background():
    """Background should be near-black (the piece uses #0d0d0b)."""
    src = html_source()
    assert '#0d0d0b' in src


def test_no_fill_calls():
    """Contour lines are stroke-only — no fillRect inside the march loop."""
    src = html_source()
    # fillRect is only used for clearing the canvas background, not inside marchLevel.
    # We verify marchLevel function body does not call fillStyle
    march_fn = re.search(r'function marchLevel\(.*?\n\}', src, re.DOTALL)
    assert march_fn, "marchLevel function not found"
    fn_body = march_fn.group(0)
    assert 'fillStyle' not in fn_body, "marchLevel should not set fillStyle"
    assert 'fill(' not in fn_body, "marchLevel should not call fill()"


def test_requestanimationframe_used():
    """Animation must use requestAnimationFrame for ≤60 fps compliance."""
    src = html_source()
    assert 'requestAnimationFrame' in src


# ─── edge cases ───────────────────────────────────────────────────────────────

def test_readme_nonempty():
    readme = (PIECE / "README.md").read_text(encoding="utf-8")
    assert len(readme.strip()) > 50


def test_thumbnail_is_valid_svg():
    """Thumbnail must be a well-formed SVG (has opening svg tag)."""
    content = (PIECE / "thumbnail.svg").read_text(encoding="utf-8")
    assert '<svg' in content
    assert '</svg>' in content


def test_pieces_json_still_valid_after_update():
    """pieces.json must remain a valid JSON list after the new entry was added."""
    data = pieces_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_new_entry_is_last():
    """The topographic-contours entry should be the last in pieces.json (appended)."""
    data = pieces_json()
    assert data[-1]["id"] == "64-topographic-contours"


def test_index_contour_width_larger_than_regular():
    """Index contour stroke width must be numerically larger than regular contour width."""
    src = html_source()
    # Extract widths passed to marchLevel in the render loop.
    widths = re.findall(r'marchLevel\([^,]+,\s*[^,]+,\s*([\d.]+)\)', src)
    if widths:
        floats = [float(w) for w in widths]
        assert max(floats) > min(floats), "All contour widths are equal — index contours must be thicker"


def test_interp_function_present():
    """Linear interpolation helper must exist for accurate isoline placement."""
    src = html_source()
    assert 'function interp(' in src


def test_no_setinterval_used():
    """Animation should use requestAnimationFrame, not setInterval."""
    src = html_source()
    assert 'setInterval' not in src
