"""Tests for Piece 221 — Ulam Spiral."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent
PIECE_DIR = ROOT / "pieces" / "221-ulam-spiral"
INDEX_HTML = PIECE_DIR / "index.html"


# ---------------------------------------------------------------------------
# File presence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_thumbnail_svg_exists():
    assert (PIECE_DIR / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file()


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    data = json.loads((ROOT / "pieces.json").read_text())
    ids = [p["id"] for p in data]
    assert "221-ulam-spiral" in ids


def test_pieces_json_entry_fields():
    data = json.loads((ROOT / "pieces.json").read_text())
    entry = next(p for p in data if p["id"] == "221-ulam-spiral")
    for field in ("id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"):
        assert field in entry, f"Missing field: {field}"


def test_pieces_json_path_matches_directory():
    data = json.loads((ROOT / "pieces.json").read_text())
    entry = next(p for p in data if p["id"] == "221-ulam-spiral")
    assert (ROOT / entry["path"]).is_dir()


def test_pieces_json_thumbnail_exists():
    data = json.loads((ROOT / "pieces.json").read_text())
    entry = next(p for p in data if p["id"] == "221-ulam-spiral")
    assert (ROOT / entry["thumbnail"]).is_file()


def test_pieces_json_year():
    data = json.loads((ROOT / "pieces.json").read_text())
    entry = next(p for p in data if p["id"] == "221-ulam-spiral")
    assert entry["year"] == 2026


# ---------------------------------------------------------------------------
# index.html content checks
# ---------------------------------------------------------------------------

def _html():
    return INDEX_HTML.read_text()


def test_html_references_panel_css():
    assert "panel.css" in _html()


def test_html_references_panel_js():
    assert "panel.js" in _html()


def test_html_uses_gallery_panel_init():
    assert "GalleryPanel.init" in _html()


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_has_color_mode_select():
    html = _html()
    assert 'id="color-mode"' in html
    assert "mono" in html
    assert "mod4" in html
    assert "spf" in html


def test_html_has_reset_button():
    assert 'id="reset-btn"' in _html()


def test_html_mentions_n_200000():
    # The piece must handle up to 200 000 integers
    html = _html()
    assert "200000" in html or "200_000" in html


def test_html_builds_sieve():
    # Sieve construction must be present
    assert "buildSieve" in _html() or "spf" in _html()


def test_html_builds_spiral():
    assert "buildSpiral" in _html()


def test_html_has_zoom_handler():
    assert "wheel" in _html()


def test_html_has_pan_handler():
    html = _html()
    assert "mousedown" in html
    assert "mousemove" in html


def test_html_has_tooltip():
    html = _html()
    assert "tooltip" in html
    assert "factorString" in html or "factorization" in html.lower() or "factorStr" in html


def test_html_has_gallery_panel_sections():
    html = _html()
    # Must have multiple educational sections
    assert html.count("heading:") >= 4


def test_html_dirichlet_mention():
    assert "Dirichlet" in _html()


def test_html_residue_mod4_palette():
    # Residue mod 4 colouring is a specific acceptance criterion
    html = _html()
    assert "mod4" in html
    assert "% 4" in html


# ---------------------------------------------------------------------------
# Spiral algorithm correctness (Python re-implementation)
# ---------------------------------------------------------------------------

def _build_spiral_py(N):
    """Python port of the JS buildSpiral function for verification."""
    RANGE = 500
    HALF = 250
    grid = {}
    x, y = 0, 0
    dx, dy = 1, 0
    seg_len, seg_pos, turns = 1, 0, 0
    grid[(0, 0)] = 1
    for n in range(2, N + 1):
        x += dx; y += dy
        seg_pos += 1
        grid[(x, y)] = n
        if seg_pos == seg_len:
            seg_pos = 0
            dx, dy = dy, -dx
            turns += 1
            if turns % 2 == 0:
                seg_len += 1
    return grid


def _sieve_py(limit):
    spf = list(range(limit + 1))
    for i in range(2, int(math.isqrt(limit)) + 1):
        if spf[i] == i:
            for j in range(i * i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    return spf


def test_spiral_n1_at_origin():
    g = _build_spiral_py(10)
    assert g[(0, 0)] == 1


def test_spiral_n2_right_of_centre():
    """n=2 must be placed to the right of n=1 (the spiral starts rightward)."""
    g = _build_spiral_py(10)
    assert g[(1, 0)] == 2


def test_spiral_standard_5x5():
    """Verify the classic 5×5 Ulam spiral layout exactly."""
    g = _build_spiral_py(25)
    # Standard layout (row y=-2 = topmost on screen):
    # 17 16 15 14 13
    # 18  5  4  3 12
    # 19  6  1  2 11
    # 20  7  8  9 10
    # 21 22 23 24 25
    expected = {
        ( 0,  0):  1, ( 1,  0):  2, ( 1, -1):  3,
        ( 0, -1):  4, (-1, -1):  5, (-1,  0):  6,
        (-1,  1):  7, ( 0,  1):  8, ( 1,  1):  9,
        ( 2,  1): 10, ( 2,  0): 11, ( 2, -1): 12,
        ( 2, -2): 13, ( 1, -2): 14, ( 0, -2): 15,
        (-1, -2): 16, (-2, -2): 17, (-2, -1): 18,
        (-2,  0): 19, (-2,  1): 20, (-2,  2): 21,
        (-1,  2): 22, ( 0,  2): 23, ( 1,  2): 24,
        ( 2,  2): 25,
    }
    for coord, expected_n in expected.items():
        assert g[coord] == expected_n, f"At {coord}: expected {expected_n}, got {g.get(coord)}"


def test_spiral_no_duplicate_coordinates():
    """Each coordinate must hold exactly one integer."""
    g = _build_spiral_py(1000)
    assert len(g) == 1000


def test_spiral_all_integers_placed():
    """Every integer 1..N must appear exactly once."""
    N = 500
    g = _build_spiral_py(N)
    assert set(g.values()) == set(range(1, N + 1))


def test_spiral_prime_2_position():
    """2 is to the right of 1; it must be marked prime by the sieve."""
    g = _build_spiral_py(10)
    spf = _sieve_py(10)
    n_at_right = g[(1, 0)]  # n=2
    assert spf[n_at_right] == n_at_right  # is prime


def test_spiral_bounding_box_n200000():
    """For N=200 000, all coordinates must fit within ±250 (HALF_RANGE)."""
    N = 200000
    g = _build_spiral_py(N)
    max_coord = max(max(abs(x), abs(y)) for x, y in g)
    assert max_coord <= 250, f"Max coordinate {max_coord} exceeds HALF_RANGE=250"


# ---------------------------------------------------------------------------
# Sieve correctness
# ---------------------------------------------------------------------------

def test_sieve_primes_to_30():
    spf = _sieve_py(30)
    primes = [n for n in range(2, 31) if spf[n] == n]
    assert primes == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]


def test_sieve_composite_spf():
    spf = _sieve_py(20)
    assert spf[12] == 2  # 12 = 2^2 * 3
    assert spf[15] == 3  # 15 = 3 * 5
    assert spf[7]  == 7  # 7 is prime


def test_sieve_count_primes_to_200000():
    """By the prime counting function, π(200000) = 17984."""
    spf = _sieve_py(200000)
    count = sum(1 for n in range(2, 200001) if spf[n] == n)
    assert count == 17984


# ---------------------------------------------------------------------------
# Colour-mode correctness
# ---------------------------------------------------------------------------

def test_mod4_prime_residues():
    """Every prime > 2 is either 1 or 3 mod 4 — never 0 or 2."""
    spf = _sieve_py(1000)
    for n in range(3, 1001):
        if spf[n] == n:  # prime
            assert n % 4 in (1, 3), f"Prime {n} has unexpected residue {n % 4}"


def test_mod4_dirichlet_rough_balance():
    """Both residue classes should each contain at least 40% of primes up to 1000."""
    spf = _sieve_py(1000)
    class1 = sum(1 for n in range(3, 1001) if spf[n] == n and n % 4 == 1)
    class3 = sum(1 for n in range(3, 1001) if spf[n] == n and n % 4 == 3)
    total  = class1 + class3
    assert class1 / total >= 0.40
    assert class3 / total >= 0.40


def test_spf_mode_prime_self_factor():
    """For a prime p, its smallest factor must equal itself."""
    spf = _sieve_py(100)
    for n in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        assert spf[n] == n


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_spiral_n1_only():
    """Single-integer spiral: only (0,0)=1."""
    g = _build_spiral_py(1)
    assert g == {(0, 0): 1}


def test_spiral_n4_forms_L():
    """After 4 integers the spiral has turned twice."""
    g = _build_spiral_py(4)
    assert len(g) == 4
    assert g[(0, 0)] == 1
    assert g[(1, 0)] == 2
    assert g[(1, -1)] == 3
    assert g[(0, -1)] == 4


def test_sieve_n2_is_prime():
    spf = _sieve_py(2)
    assert spf[2] == 2


def test_sieve_n1_sentinel():
    spf = _sieve_py(10)
    assert spf[0] == 0
    assert spf[1] == 1  # left at index 1; 1 is not prime (spf[1] != 1 is checked externally)


# ---------------------------------------------------------------------------
# thumbnail SVG sanity
# ---------------------------------------------------------------------------

def test_thumbnail_is_valid_svg():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert content.strip().startswith("<svg")
    assert "</svg>" in content


def test_thumbnail_contains_prime_color():
    """Amber prime cells (#f59e0b) must appear in the thumbnail."""
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#f59e0b" in content


def test_thumbnail_contains_composite_color():
    content = (PIECE_DIR / "thumbnail.svg").read_text()
    assert "#1a1a2e" in content
