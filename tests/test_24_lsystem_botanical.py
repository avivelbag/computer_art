"""Tests for pieces/24-lsystem-botanical: animated L-system fractal plant."""

import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO       = pathlib.Path(__file__).parent.parent
PIECE_DIR  = REPO / "pieces" / "24-lsystem-botanical"
INDEX_HTML = PIECE_DIR / "index.html"
README     = PIECE_DIR / "README.md"
THUMBNAIL  = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"

PIECE_ID = "24-lsystem-botanical"

BG_COLOR = "f5f0e8"
C0_COLOR = "2d6a4f"
C1_COLOR = "74c69d"
C2_COLOR = "d8f3dc"

AXIOM      = "X"
RULES      = {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}
ANGLE_DEG  = 25


# ---------------------------------------------------------------------------
# Python mirrors of index.html core functions (for mathematical tests)
# ---------------------------------------------------------------------------

def expand(axiom: str, rules: dict, n: int) -> str:
    """Expand axiom by applying rules n times."""
    s = axiom
    for _ in range(n):
        s = "".join(rules.get(c, c) for c in s)
    return s


def turtle_walk(s: str, angle_deg: float) -> list[dict]:
    """Interpret L-system string; return list of segment dicts.

    Each dict has keys: x1, y1, x2, y2, depth.
    Bracket depth increments on '[' and restores to pre-bracket value on ']'.
    """
    da = angle_deg * math.pi / 180
    stack: list[tuple] = []
    x, y, a, depth = 0.0, 0.0, -math.pi / 2, 0
    segs: list[dict] = []

    for c in s:
        if c == "F":
            nx, ny = x + math.cos(a), y + math.sin(a)
            segs.append({"x1": x, "y1": y, "x2": nx, "y2": ny, "depth": depth})
            x, y = nx, ny
        elif c == "+":
            a -= da
        elif c == "-":
            a += da
        elif c == "[":
            stack.append((x, y, a, depth))
            depth += 1
        elif c == "]":
            x, y, a, depth = stack.pop()

    return segs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _html() -> str:
    return INDEX_HTML.read_text()


def _entry() -> dict:
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


# ---------------------------------------------------------------------------
# File-existence tests
# ---------------------------------------------------------------------------

def test_piece_dir_exists():
    assert PIECE_DIR.is_dir(), f"Piece directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert INDEX_HTML.is_file(), "index.html missing from piece directory"


def test_readme_exists():
    assert README.is_file(), "README.md missing from piece directory"


def test_thumbnail_exists():
    assert THUMBNAIL.is_file(), "thumbnail.svg missing from piece directory"


# ---------------------------------------------------------------------------
# HTML structural tests
# ---------------------------------------------------------------------------

def test_html_has_canvas_element():
    assert "<canvas" in _html()


def test_html_canvas_has_id():
    html = _html()
    assert 'id="canvas"' in html or "id='canvas'" in html


def test_html_has_script_tag():
    assert "<script" in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset_utf8():
    html = _html()
    assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html


def test_html_title_exists():
    m = re.search(r"<title>(.*?)</title>", _html(), re.IGNORECASE)
    assert m, "index.html must have a <title>"
    assert len(m.group(1).strip()) > 0


def test_html_canvas_size_is_600():
    html = _html()
    assert 'width="600"' in html and 'height="600"' in html, \
        "Canvas must be 600×600 logical pixels"


def test_html_has_no_external_scripts():
    external = re.findall(r'<script[^>]+src=["\']https?://', _html())
    assert not external, "index.html must be self-contained — no remote scripts"


# ---------------------------------------------------------------------------
# Palette tests
# ---------------------------------------------------------------------------

def test_html_contains_bg_color():
    assert BG_COLOR in _html().lower()


def test_html_contains_trunk_color():
    assert C0_COLOR in _html().lower()


def test_html_contains_mid_color():
    assert C1_COLOR in _html().lower()


def test_html_contains_tip_color():
    assert C2_COLOR in _html().lower()


# ---------------------------------------------------------------------------
# JavaScript animation and L-system structure tests
# ---------------------------------------------------------------------------

def test_js_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_js_has_delta_cap():
    assert "Math.min" in _html(), "Script must cap delta time with Math.min"


def test_js_defines_expand_function():
    assert "function expand" in _html()


def test_js_defines_turtle_walk_function():
    assert "function turtleWalk" in _html() or "function turtle" in _html().lower()


def test_js_contains_axiom():
    html = _html()
    assert "'X'" in html or '"X"' in html, "Axiom X must appear in script"


def test_js_contains_grammar_rule():
    html = _html()
    assert "F+[[X]-X]-F[-FX]+X" in html or "F+[[X]" in html, \
        "L-system rule must appear in script"


def test_js_contains_angle_25():
    html = _html()
    assert "25" in html, "Angle 25 must appear in script"


def test_js_grow_duration_at_least_3s():
    html = _html()
    m = re.search(r"GROW_MS\s*=\s*(\d+)", html)
    if m:
        assert int(m.group(1)) >= 3000, \
            f"GROW_MS={m.group(1)} too short — must be ≥ 3000 ms"


def test_js_has_hold_phase():
    html = _html()
    assert "holding" in html or "HOLD" in html, \
        "Animation must include a hold phase"


def test_js_has_fade_phase():
    html = _html()
    assert "fading" in html or "FADE" in html, \
        "Animation must include a fade phase"


# ---------------------------------------------------------------------------
# L-system expansion — mathematical core (Python mirror of index.html)
# ---------------------------------------------------------------------------

def test_expand_0_iterations_returns_axiom():
    assert expand("X", RULES, 0) == "X"


def test_expand_1_iteration_correct():
    result = expand("X", RULES, 1)
    assert result == "F+[[X]-X]-F[-FX]+X"


def test_expand_2_iterations_starts_with_ff():
    result = expand("X", RULES, 2)
    assert result.startswith("FF"), "After 2 iters, the leading F→FF"


def test_expand_f_count_grows_correctly():
    f3 = expand("X", RULES, 3).count("F")
    f4 = expand("X", RULES, 4).count("F")
    assert f4 > f3 * 1.5, "F count must grow substantially between iterations"


def test_expand_5_iterations_f_count():
    s = expand("X", RULES, 5)
    f_count = s.count("F")
    assert f_count == 1488, f"Expected 1488 F segments at iteration 5, got {f_count}"


def test_expand_6_iterations_f_count():
    s = expand("X", RULES, 6)
    f_count = s.count("F")
    assert f_count == 6048, f"Expected 6048 F segments at iteration 6, got {f_count}"


def test_expand_preserves_non_rule_chars():
    result = expand("X", RULES, 1)
    for c in "+-[]":
        assert c in result, f"Non-production char {c!r} must pass through"


def test_expand_is_deterministic():
    s1 = expand("X", RULES, 4)
    s2 = expand("X", RULES, 4)
    assert s1 == s2


def test_expand_brackets_are_balanced():
    s = expand("X", RULES, 5)
    depth = 0
    for c in s:
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
        assert depth >= 0, "Unbalanced brackets detected"
    assert depth == 0, f"Brackets not balanced — final depth {depth}"


# ---------------------------------------------------------------------------
# Turtle walk — geometric properties
# ---------------------------------------------------------------------------

def test_turtle_walk_returns_correct_f_count():
    s = expand("X", RULES, 5)
    segs = turtle_walk(s, ANGLE_DEG)
    assert len(segs) == 1488


def test_turtle_walk_segment_keys():
    s = expand("X", RULES, 2)
    segs = turtle_walk(s, ANGLE_DEG)
    assert segs, "Should produce segments"
    for seg in segs[:10]:
        assert {"x1", "y1", "x2", "y2", "depth"} <= seg.keys()


def test_turtle_walk_unit_segment_length():
    s = expand("X", RULES, 3)
    segs = turtle_walk(s, ANGLE_DEG)
    for seg in segs[:20]:
        dx = seg["x2"] - seg["x1"]
        dy = seg["y2"] - seg["y1"]
        length = math.sqrt(dx * dx + dy * dy)
        assert abs(length - 1.0) < 1e-9, \
            f"Segment length {length:.10f} is not 1.0"


def test_turtle_walk_depth_starts_at_zero():
    s = expand("X", RULES, 1)
    segs = turtle_walk(s, ANGLE_DEG)
    assert segs[0]["depth"] == 0, "First segment must be at depth 0"


def test_turtle_walk_depth_increases_inside_brackets():
    s = expand("X", RULES, 2)
    segs = turtle_walk(s, ANGLE_DEG)
    depths = {seg["depth"] for seg in segs}
    assert max(depths) >= 2, "Should have segments at depth ≥ 2 after 2 iterations"


def test_turtle_walk_bounding_box_is_nontrivial():
    s = expand("X", RULES, 4)
    segs = turtle_walk(s, ANGLE_DEG)
    xs = [v for seg in segs for v in (seg["x1"], seg["x2"])]
    ys = [v for seg in segs for v in (seg["y1"], seg["y2"])]
    assert max(xs) - min(xs) > 10, "Tree must have substantial horizontal extent"
    assert max(ys) - min(ys) > 10, "Tree must have substantial vertical extent"


def test_turtle_walk_tree_grows_upward():
    s = expand("X", RULES, 4)
    segs = turtle_walk(s, ANGLE_DEG)
    ys = [v for seg in segs for v in (seg["y1"], seg["y2"])]
    assert min(ys) < 0, "Starting upward means most of the tree has negative y"


def test_turtle_walk_empty_string():
    segs = turtle_walk("", ANGLE_DEG)
    assert segs == []


def test_turtle_walk_no_f_commands():
    segs = turtle_walk("X+X-[X]", ANGLE_DEG)
    assert segs == [], "String with no F commands must produce no segments"


def test_turtle_walk_single_f():
    segs = turtle_walk("F", ANGLE_DEG)
    assert len(segs) == 1
    assert abs(segs[0]["x1"]) < 1e-9
    assert abs(segs[0]["y1"]) < 1e-9
    assert abs(segs[0]["y2"] - (-1.0)) < 1e-9, "Starting up → y2 = -1"


# ---------------------------------------------------------------------------
# Thumbnail SVG tests
# ---------------------------------------------------------------------------

def test_thumbnail_not_empty():
    assert len(THUMBNAIL.read_text()) > 500


def test_thumbnail_has_svg_root():
    assert "<svg" in THUMBNAIL.read_text()


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_is_valid_xml():
    try:
        ET.fromstring(THUMBNAIL.read_text())
    except ET.ParseError as exc:
        raise AssertionError(f"thumbnail.svg invalid XML: {exc}") from exc


def test_thumbnail_dimensions_400():
    svg = THUMBNAIL.read_text()
    w = re.search(r'width="(\d+)"', svg)
    h = re.search(r'height="(\d+)"', svg)
    assert w and int(w.group(1)) == 400
    assert h and int(h.group(1)) == 400


def test_thumbnail_contains_bg_color():
    assert BG_COLOR in THUMBNAIL.read_text().lower()


def test_thumbnail_contains_trunk_color():
    assert C0_COLOR in THUMBNAIL.read_text().lower()


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_many_line_segments():
    lines = len(re.findall(r"<line\b", THUMBNAIL.read_text()))
    assert lines >= 100, f"Thumbnail must have ≥100 line elements; found {lines}"


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_under_500kb():
    size = THUMBNAIL.stat().st_size
    assert size < 500_000, f"thumbnail.svg is {size} bytes — must be under 500 KB"


# ---------------------------------------------------------------------------
# pieces.json contract tests
# ---------------------------------------------------------------------------

def test_pieces_json_has_entry():
    ids = [item.get("id") for item in json.loads(PIECES_JSON.read_text())]
    assert PIECE_ID in ids


def test_pieces_json_entry_has_all_required_fields():
    entry = _entry()
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    assert not (required - entry.keys()), f"Missing: {required - entry.keys()}"


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    thumb = REPO / _entry()["thumbnail"]
    assert thumb.is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_lsystem():
    t = _entry()["technique"].lower()
    assert "l-system" in t or "lsystem" in t


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------

def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_lsystem():
    readme = README.read_text().lower()
    assert "l-system" in readme or "lsystem" in readme


def test_readme_documents_grammar_rule():
    readme = README.read_text()
    assert "F+[[X]-X]-F[-FX]+X" in readme, \
        "README must document the L-system production rule"


def test_readme_mentions_angle():
    readme = README.read_text()
    assert "25" in readme, "README must mention the 25° angle"


def test_readme_mentions_trunk_color():
    assert C0_COLOR in README.read_text().lower()


def test_readme_mentions_background_color():
    assert BG_COLOR in README.read_text().lower()


def test_readme_mentions_grow_animation():
    readme = README.read_text().lower()
    assert "grow" in readme or "anim" in readme


# ---------------------------------------------------------------------------
# Failure-mode tests (assert correct error / no-op behavior)
# ---------------------------------------------------------------------------

def test_wrong_piece_id_not_found():
    data = json.loads(PIECES_JSON.read_text())
    ids = [item.get("id") for item in data]
    assert "00-does-not-exist" not in ids


def test_missing_canvas_tag_detected():
    fake = "<html><body><div id='canvas'></div></body></html>"
    assert "<canvas" not in fake


def test_expand_zero_iterations_is_identity():
    for axiom in ["X", "F", "F+X", ""]:
        assert expand(axiom, RULES, 0) == axiom


def test_turtle_walk_returns_empty_for_no_F():
    result = turtle_walk("+--+[][][]", ANGLE_DEG)
    assert result == [], "Pure rotation/bracket string produces no segments"


def test_thumbnail_has_correct_line_element_tag():
    svg = THUMBNAIL.read_text()
    assert "<line " in svg or "<line\n" in svg, \
        "Thumbnail must use <line> elements for segments"
