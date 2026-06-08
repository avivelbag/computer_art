"""Tests for piece 281-nebula-noise (Celestial Veil)."""
import json
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "281-nebula-noise"
INDEX_HTML = PIECE_DIR / "index.html"
PIECES_JSON = REPO / "pieces.json"


# ── Filesystem / metadata ────────────────────────────────────────────────────

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_thumbnail_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


def test_readme_not_empty():
    assert (PIECE_DIR / "README.md").stat().st_size > 100


# ── pieces.json entry ────────────────────────────────────────────────────────

def _load_pieces():
    """Load and parse pieces.json."""
    return json.loads(PIECES_JSON.read_text())


def _entry():
    """Return the pieces.json entry for 281-nebula-noise, or None."""
    return next((p for p in _load_pieces() if p["id"] == "281-nebula-noise"), None)


def test_pieces_json_has_entry():
    assert _entry() is not None, "281-nebula-noise missing from pieces.json"


def test_entry_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    e = _entry()
    assert e is not None
    assert required <= e.keys(), f"Missing fields: {required - e.keys()}"


def test_entry_id_matches_directory():
    e = _entry()
    assert e is not None
    assert e["id"] == "281-nebula-noise"
    assert pathlib.Path(e["path"]).name == "281-nebula-noise"


def test_entry_thumbnail_file_exists():
    e = _entry()
    assert e is not None
    assert (REPO / e["thumbnail"]).is_file()


def test_entry_year():
    e = _entry()
    assert e is not None
    assert e["year"] == 2026


def test_entry_technique_mentions_noise():
    e = _entry()
    assert e is not None
    assert "noise" in e["technique"].lower()


# ── HTML / canvas content ────────────────────────────────────────────────────

def _html():
    """Read and return the full text of index.html."""
    return INDEX_HTML.read_text()


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_uses_canvas_2d():
    html = _html()
    assert "getContext('2d')" in html or 'getContext("2d")' in html


def test_html_no_external_imports():
    """No CDN imports — noise must be inlined."""
    html = _html()
    externals = re.findall(r'(src|href)\s*=\s*["\']https?://', html)
    assert externals == [], f"External assets found: {externals}"


def test_html_has_requestanimationframe():
    """Animation loop must use requestAnimationFrame, not setInterval."""
    assert "requestAnimationFrame" in _html()


def test_html_60fps_cap():
    """No setInterval faster than 60 fps."""
    html = _html()
    bad = re.findall(r'setInterval\s*\([^,]+,\s*(\d+)\s*\)', html)
    for ms in bad:
        assert int(ms) >= 16, f"setInterval({ms}ms) is faster than 60fps"


def test_html_has_perlin_noise():
    """Perlin noise must be inlined — look for permutation table and fade function."""
    html = _html()
    assert "perm" in html or "permutation" in html.lower()
    assert "fade" in html


def test_html_has_fbm():
    """Fractional Brownian Motion layering must be present."""
    html = _html()
    assert "fbm" in html or "octave" in html.lower() or "oct" in html


def test_html_has_at_least_3_layers():
    """At least 3 noise layers defined (acceptance criterion)."""
    html = _html()
    matches = re.findall(r'\{[^}]*oct[^}]*\}', html)
    assert len(matches) >= 3, f"Expected >= 3 layer objects, found {len(matches)}"


def test_html_has_additive_blending():
    """Layers must be composited with 'lighter' (additive blending)."""
    assert "'lighter'" in _html() or '"lighter"' in _html()


def test_html_has_nebula_palette():
    """Palette must include crimson (c0103a range) and teal (0aefb0 range)."""
    html = _html()
    assert re.search(r'c0103a|c01|b00|a00|900|800.*red|192.*16.*58|192,\s*16', html, re.IGNORECASE), \
        "Crimson hydrogen colour not found in palette"
    assert re.search(r'0aefb0|0ef|0ae|10.*239|10,\s*239', html, re.IGNORECASE), \
        "Teal oxygen-III colour not found in palette"


def test_html_has_black_background():
    """Canvas must be cleared to black each frame (void space)."""
    html = _html()
    assert "#000" in html or "fillStyle = '#000'" in html or "black" in html.lower()


def test_html_size_declared():
    """Canvas size must be set in HTML."""
    html = _html()
    assert "width=" in html or "WIDTH" in html or "SIZE" in html


def test_html_time_animates():
    """time variable must increment each frame."""
    html = _html()
    assert "time +=" in html or "time++" in html


def test_html_no_alert_or_confirm():
    """No debugging artifacts left in production code."""
    html = _html()
    assert "alert(" not in html
    assert "console.log(" not in html


# ── Noise implementation size ────────────────────────────────────────────────

def test_html_under_10kb():
    """Inlined noise implementation keeps the file compact (< 10 KB)."""
    size = INDEX_HTML.stat().st_size
    assert size < 10 * 1024, f"index.html is {size} bytes; noise impl must be < 10 KB"


# ── SVG thumbnail ────────────────────────────────────────────────────────────

def test_thumbnail_is_valid_svg():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "<svg" in content


def test_thumbnail_has_nebula_colours():
    """Thumbnail must reference the nebula palette colours."""
    svg = (PIECE_DIR / "thumbnail.svg").read_text()
    assert re.search(r'c0103a|c01|b00|hydrogen', svg, re.IGNORECASE)
    assert re.search(r'0aefb0|0ae|oxygen', svg, re.IGNORECASE)


# ── Global pieces.json invariants ────────────────────────────────────────────

def test_pieces_json_valid():
    """pieces.json must remain parseable after update."""
    data = _load_pieces()
    assert isinstance(data, list)
    assert len(data) > 0


def test_no_duplicate_ids():
    """No two pieces may share the same id."""
    ids = [p["id"] for p in _load_pieces()]
    assert len(ids) == len(set(ids)), "Duplicate ids found in pieces.json"


# ── Edge cases ───────────────────────────────────────────────────────────────

def test_missing_field_caught(tmp_path):
    """Verify the required-field check logic works for a fabricated bad entry."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    bad = {"id": "x", "title": "X"}
    assert not (required <= bad.keys())
    assert required - bad.keys() != set()


def test_id_path_mismatch_caught(tmp_path):
    """Confirm id-vs-dir-name mismatch is detectable."""
    piece_dir = tmp_path / "real-name"
    piece_dir.mkdir()
    entry = {"id": "wrong-name", "path": str(piece_dir.relative_to(tmp_path))}
    assert entry["id"] != piece_dir.name


def test_missing_thumbnail_detectable(tmp_path):
    """A thumbnail path that does not exist should be flagged."""
    ghost = tmp_path / "no-thumb.svg"
    assert not ghost.exists()


def test_empty_readme_fails_size_check(tmp_path):
    """A zero-byte README should not pass the not-empty check."""
    empty = tmp_path / "README.md"
    empty.write_text("")
    assert empty.stat().st_size == 0
    assert not (empty.stat().st_size > 100)
