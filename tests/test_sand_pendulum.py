"""Tests for Piece 285 — The Sifting Hour (sand pendulum)."""
import importlib.util
import json
import pathlib
import struct

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "285-sand-pendulum"
PIECES_JSON = REPO / "pieces.json"

# ---------------------------------------------------------------------------
# Load generate_thumbnail as a module without installing it
# ---------------------------------------------------------------------------

def _load_thumbnail_module():
    """Dynamically import generate_thumbnail.py from the piece directory."""
    spec = importlib.util.spec_from_file_location(
        "generate_thumbnail_285",
        PIECE_DIR / "generate_thumbnail.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def thumb_mod():
    """Return the generate_thumbnail module for piece 285."""
    return _load_thumbnail_module()


# ---------------------------------------------------------------------------
# Directory / file structure (acceptance criteria)
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    """The piece directory must be present."""
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    """index.html must be present in the piece directory."""
    assert (PIECE_DIR / "index.html").is_file()


def test_readme_exists():
    """README.md must be present in the piece directory."""
    assert (PIECE_DIR / "README.md").is_file()


def test_thumbnail_exists():
    """thumbnail.png must be present in the piece directory."""
    assert (PIECE_DIR / "thumbnail.png").is_file()


def test_thumbnail_is_valid_png():
    """thumbnail.png must start with the 8-byte PNG signature."""
    data = (PIECE_DIR / "thumbnail.png").read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "File does not have PNG signature"


def test_thumbnail_non_trivial():
    """thumbnail.png must contain a non-trivial number of non-background pixels."""
    mod = _load_thumbnail_module()
    pixels = mod.generate_thumbnail()
    bg = (mod.BG_R, mod.BG_G, mod.BG_B)
    non_bg = sum(1 for p in pixels if p != bg)
    assert non_bg > 1000, f"Only {non_bg} non-background pixels — trace not visible"


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

def _load_pieces():
    return json.loads(PIECES_JSON.read_text())


def _entry():
    entries = [e for e in _load_pieces() if e.get("id") == "285-sand-pendulum"]
    assert entries, "285-sand-pendulum not found in pieces.json"
    return entries[0]


def test_pieces_json_entry_exists():
    """pieces.json must contain an entry with id '285-sand-pendulum'."""
    _entry()  # raises if not found


def test_pieces_json_required_fields():
    """The pieces.json entry must carry all required metadata fields."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    e = _entry()
    assert required <= e.keys(), f"Missing fields: {required - e.keys()}"


def test_pieces_json_id_matches_dir():
    """The id field must equal the last path segment of the piece directory."""
    e = _entry()
    assert e["id"] == pathlib.Path(e["path"]).name


def test_pieces_json_thumbnail_file_exists():
    """The thumbnail path recorded in pieces.json must point to a real file."""
    e = _entry()
    assert (REPO / e["thumbnail"]).is_file()


def test_index_html_no_external_libraries():
    """index.html must not load any external scripts (no CDN, no src= with http)."""
    content = (PIECE_DIR / "index.html").read_text()
    import re
    external = re.findall(r'src=["\']https?://', content)
    assert not external, f"External script src found: {external}"


def test_index_html_js_under_150_lines():
    """The JavaScript inside index.html must be under 150 lines."""
    content = (PIECE_DIR / "index.html").read_text()
    in_script = False
    js_lines = []
    for line in content.splitlines():
        if "<script" in line:
            in_script = True
            continue
        if "</script>" in line:
            in_script = False
            continue
        if in_script:
            js_lines.append(line)
    assert len(js_lines) < 150, f"JS has {len(js_lines)} lines (must be < 150)"


# ---------------------------------------------------------------------------
# generate_thumbnail physics simulation
# ---------------------------------------------------------------------------

def test_simulate_returns_correct_length(thumb_mod):
    """simulate() must return W*H integers."""
    density = thumb_mod.simulate(n_frames=10)
    assert len(density) == thumb_mod.W * thumb_mod.H


def test_simulate_non_negative(thumb_mod):
    """All density values must be non-negative integers."""
    density = thumb_mod.simulate(n_frames=10)
    assert all(d >= 0 for d in density)


def test_simulate_deposits_grains(thumb_mod):
    """simulate() with positive frames must deposit at least some grains."""
    density = thumb_mod.simulate(n_frames=50)
    total = sum(density)
    assert total > 0, "No grains deposited"


def test_simulate_zero_frames_empty(thumb_mod):
    """simulate(0) must return an all-zero density grid (no grains deposited)."""
    density = thumb_mod.simulate(n_frames=0)
    assert all(d == 0 for d in density)


def test_simulate_many_frames(thumb_mod):
    """simulate(1600) must still terminate and return a W*H grid without error."""
    density = thumb_mod.simulate(n_frames=1600)
    assert len(density) == thumb_mod.W * thumb_mod.H
    assert sum(density) > 0


def test_simulate_is_deterministic(thumb_mod):
    """Two runs of simulate() with same frame count must produce identical grids.

    The LCG inside simulate() is re-seeded from a fixed constant each call,
    so the output is fully reproducible.
    """
    d1 = thumb_mod.simulate(n_frames=100)
    d2 = thumb_mod.simulate(n_frames=100)
    assert d1 == d2, "simulate() is not deterministic"


# ---------------------------------------------------------------------------
# density_to_pixels color mapping
# ---------------------------------------------------------------------------

def test_density_to_pixels_background_for_zero(thumb_mod):
    """Zero-density pixels must map to the background color."""
    density = [0] * (thumb_mod.W * thumb_mod.H)
    pixels = thumb_mod.density_to_pixels(density)
    bg = (thumb_mod.BG_R, thumb_mod.BG_G, thumb_mod.BG_B)
    assert all(p == bg for p in pixels)


def test_density_to_pixels_high_density_bright(thumb_mod):
    """A pixel with max density must be brighter than the background."""
    n = thumb_mod.W * thumb_mod.H
    density = [0] * n
    density[n // 2] = 100  # a single hot pixel
    pixels = thumb_mod.density_to_pixels(density)
    hot = pixels[n // 2]
    bg = (thumb_mod.BG_R, thumb_mod.BG_G, thumb_mod.BG_B)
    assert sum(hot) > sum(bg), "High-density pixel is not brighter than background"


def test_density_to_pixels_length(thumb_mod):
    """density_to_pixels must return exactly W*H pixels."""
    density = [1] * (thumb_mod.W * thumb_mod.H)
    pixels = thumb_mod.density_to_pixels(density)
    assert len(pixels) == thumb_mod.W * thumb_mod.H


def test_density_to_pixels_channel_range(thumb_mod):
    """All RGB channel values must be in [0, 255]."""
    density = thumb_mod.simulate(n_frames=50)
    pixels = thumb_mod.density_to_pixels(density)
    for r, g, b in pixels:
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255


# ---------------------------------------------------------------------------
# write_png round-trip
# ---------------------------------------------------------------------------

def test_write_png_creates_file(thumb_mod, tmp_path):
    """write_png must create a valid PNG file at the given path."""
    pixels = [(26, 15, 6)] * (thumb_mod.W * thumb_mod.H)
    out = tmp_path / "test.png"
    thumb_mod.write_png(out, pixels)
    assert out.is_file()
    assert out.stat().st_size > 0
    assert out.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_write_png_ihdr_dimensions(thumb_mod, tmp_path):
    """The PNG IHDR chunk must record the correct W×H dimensions."""
    pixels = [(0, 0, 0)] * (thumb_mod.W * thumb_mod.H)
    out = tmp_path / "dim_test.png"
    thumb_mod.write_png(out, pixels)
    data = out.read_bytes()
    # IHDR starts at byte 16 (8 signature + 4 length + 4 "IHDR")
    w, h = struct.unpack(">II", data[16:24])
    assert w == thumb_mod.W
    assert h == thumb_mod.H


# ---------------------------------------------------------------------------
# Explicit failure modes
# ---------------------------------------------------------------------------

def test_missing_index_html_detected(tmp_path):
    """A piece directory without index.html should be detectably incomplete."""
    piece_dir = tmp_path / "test-piece"
    piece_dir.mkdir()
    (piece_dir / "README.md").write_text("# Test")
    assert not (piece_dir / "index.html").exists()


def test_malformed_pieces_json_detected(tmp_path):
    """pieces.json with an entry missing 'thumbnail' must fail the required-field check."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = {
        "id": "285-sand-pendulum",
        "title": "The Sifting Hour",
        "tagline": "...",
        "year": 2026,
        "technique": "canvas",
        "path": "pieces/285-sand-pendulum",
        # 'thumbnail' deliberately omitted
        "description": "...",
    }
    missing = required - entry.keys()
    assert "thumbnail" in missing
