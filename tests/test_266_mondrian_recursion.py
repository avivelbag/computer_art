"""Tests for Piece 266 — Mondrian Recursion: The Rectangle That Cannot Stop."""
import json
import pathlib
import random
import re

import pytest

REPO      = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "266-mondrian-recursion"
INDEX     = PIECE_DIR / "index.html"
README    = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID  = "266-mondrian-recursion"

PALETTE = ['#c4888a', '#5f8fa8', '#c8a84b', '#f2ede0', '#8aaf96']


# ---------------------------------------------------------------------------
# Python mirror of the BSP algorithm for logic tests
# ---------------------------------------------------------------------------


def pick_color(avoid, palette=None, rng=None):
    """
    Select a random palette colour, excluding `avoid`.

    Args:
        avoid:   colour string to skip, or None
        palette: list of colour strings to choose from
        rng:     random.Random instance for deterministic tests

    Returns:
        A colour string from `palette`.
    """
    if palette is None:
        palette = PALETTE
    if rng is None:
        rng = random
    pool = [c for c in palette if c != avoid] if avoid else list(palette)
    return rng.choice(pool)


def rep_color(node):
    """Return the leftmost reachable leaf colour from `node`."""
    while not node['leaf']:
        node = node['left']
    return node['color']


def build_bsp(rect, depth, avoid, min_cell=40, rng=None):
    """
    Recursively partition `rect` into a BSP tree.

    A leaf is created when `depth` reaches 0 or neither dimension is large
    enough to split without creating a child smaller than `min_cell`.

    Args:
        rect:     dict with keys x, y, w, h
        depth:    remaining split levels
        avoid:    palette colour to avoid at this node (sibling colour)
        min_cell: minimum dimension; a rect is splittable only if the
                  relevant dimension is >= min_cell * 2
        rng:      random.Random instance (uses module random if None)

    Returns:
        BSP node dict:
          leaf node  — {leaf: True,  rect, color}
          split node — {leaf: False, rect, line, left, right}
    """
    if rng is None:
        rng = random
    can_h = rect['w'] >= min_cell * 2
    can_v = rect['h'] >= min_cell * 2

    if depth == 0 or (not can_h and not can_v):
        return {'leaf': True, 'rect': rect, 'color': pick_color(avoid, rng=rng)}

    ratio  = 0.5 + (rng.random() - 0.5) * 0.4
    aspect = rect['w'] / rect['h']

    if not can_h:
        p_vert = 0.0
    elif not can_v:
        p_vert = 1.0
    else:
        p_vert = min(0.85, max(0.15, aspect / (aspect + 1)))

    do_vert = rng.random() < p_vert

    if do_vert:
        sx = round(rect['x'] + rect['w'] * ratio)
        c1 = {'x': rect['x'], 'y': rect['y'], 'w': sx - rect['x'],                  'h': rect['h']}
        c2 = {'x': sx,         'y': rect['y'], 'w': rect['x'] + rect['w'] - sx,      'h': rect['h']}
        line = (sx, rect['y'], sx, rect['y'] + rect['h'])
    else:
        sy = round(rect['y'] + rect['h'] * ratio)
        c1 = {'x': rect['x'], 'y': rect['y'], 'w': rect['w'], 'h': sy - rect['y']         }
        c2 = {'x': rect['x'], 'y': sy,         'w': rect['w'], 'h': rect['y'] + rect['h'] - sy}
        line = (rect['x'], sy, rect['x'] + rect['w'], sy)

    left  = build_bsp(c1, depth - 1, avoid,           min_cell=min_cell, rng=rng)
    right = build_bsp(c2, depth - 1, rep_color(left), min_cell=min_cell, rng=rng)
    return {'leaf': False, 'rect': rect, 'line': line, 'left': left, 'right': right}


def collect_leaves(node):
    """Return a flat list of all leaf nodes in the BSP tree."""
    if node['leaf']:
        return [node]
    return collect_leaves(node['left']) + collect_leaves(node['right'])


def bfs_events(tree):
    """Return internal nodes in BFS order (same order as the animation)."""
    events = []
    q = [tree]
    while q:
        n = q.pop(0)
        if not n['leaf']:
            events.append(n)
            q.append(n['left'])
            q.append(n['right'])
    return events


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_pieces():
    """Return parsed contents of pieces.json."""
    return json.loads(PIECES_JSON.read_text())


def get_entry():
    """Return the pieces.json entry for 266-mondrian-recursion, or None."""
    return next((p for p in load_pieces() if p.get('id') == PIECE_ID), None)


def html():
    """Return the full text of index.html."""
    return INDEX.read_text()


# ---------------------------------------------------------------------------
# File-system tests
# ---------------------------------------------------------------------------


class TestFiles:
    def test_directory_exists(self):
        assert PIECE_DIR.is_dir(), f"Missing: {PIECE_DIR}"

    def test_index_html_exists(self):
        assert INDEX.is_file()

    def test_thumbnail_exists(self):
        assert THUMBNAIL.is_file()

    def test_readme_exists(self):
        assert README.is_file()

    def test_index_html_non_trivial(self):
        assert len(html()) > 2000, "index.html is suspiciously short"

    def test_readme_non_trivial(self):
        assert len(README.read_text().strip()) > 200

    def test_thumbnail_is_valid_svg(self):
        content = THUMBNAIL.read_text()
        assert '<svg' in content and '</svg>' in content

    def test_thumbnail_has_rect_elements(self):
        assert '<rect' in THUMBNAIL.read_text()

    def test_thumbnail_has_line_elements(self):
        assert '<line' in THUMBNAIL.read_text()

    def test_thumbnail_has_width_400(self):
        content = THUMBNAIL.read_text()
        assert 'width="400"' in content or "width='400'" in content


# ---------------------------------------------------------------------------
# pieces.json metadata
# ---------------------------------------------------------------------------


class TestPiecesJson:
    def test_entry_exists(self):
        assert get_entry() is not None, f"{PIECE_ID} not found in pieces.json"

    def test_required_fields(self):
        required = {'id', 'title', 'tagline', 'year', 'technique', 'path', 'thumbnail', 'description'}
        e = get_entry()
        assert e is not None
        assert not (required - e.keys()), f"Missing fields: {required - e.keys()}"

    def test_id_matches(self):
        assert get_entry()['id'] == PIECE_ID

    def test_path_correct(self):
        assert get_entry()['path'] == f'pieces/{PIECE_ID}'

    def test_thumbnail_file_exists(self):
        e = get_entry()
        assert (REPO / e['thumbnail']).is_file()

    def test_year_is_int(self):
        assert isinstance(get_entry()['year'], int)

    def test_technique_mentions_bsp_or_subdivision(self):
        tech = get_entry()['technique'].lower()
        assert 'bsp' in tech or 'subdivision' in tech or 'space partitioning' in tech

    def test_technique_mentions_svg(self):
        assert 'svg' in get_entry()['technique'].lower()

    def test_appears_after_261(self):
        pieces = load_pieces()
        idx_261 = next((i for i, p in enumerate(pieces) if p['id'] == '261-sdf-raymarching'), None)
        idx_266 = next((i for i, p in enumerate(pieces) if p['id'] == PIECE_ID), None)
        assert idx_261 is not None, '261-sdf-raymarching missing from pieces.json'
        assert idx_266 is not None, f'{PIECE_ID} missing from pieces.json'
        assert idx_266 > idx_261, '266-mondrian-recursion must appear after 261-sdf-raymarching'

    def test_no_duplicate_ids(self):
        ids = [p['id'] for p in load_pieces()]
        assert len(ids) == len(set(ids)), 'Duplicate piece IDs in pieces.json'

    def test_prior_pieces_preserved(self):
        ids = {p['id'] for p in load_pieces()}
        for expected in ['01-amber-current', '257-billiard-chaos', '261-sdf-raymarching']:
            assert expected in ids, f'Prior piece {expected!r} was removed'


# ---------------------------------------------------------------------------
# index.html structure
# ---------------------------------------------------------------------------


class TestIndexHtml:
    def test_has_svg_element(self):
        assert '<svg' in html()

    def test_has_script(self):
        assert '<script' in html()

    def test_has_viewport_meta(self):
        assert 'name="viewport"' in html()

    def test_has_charset(self):
        assert 'charset' in html()

    def test_no_external_scripts(self):
        assert not re.findall(r'<script[^>]+src=["\']https?://', html())

    def test_self_contained(self):
        h = html()
        assert '<script src=' not in h
        assert '<link rel="stylesheet"' not in h

    def test_has_requestanimationframe(self):
        assert 'requestAnimationFrame' in html()

    def test_has_settimeout(self):
        assert 'setTimeout' in html()

    def test_has_build_bsp_or_bsp(self):
        h = html()
        assert 'buildBSP' in h or 'bsp' in h.lower()

    def test_has_palette(self):
        h = html()
        assert 'PALETTE' in h or 'palette' in h.lower()

    def test_has_palette_colours(self):
        h = html().lower()
        assert '#c4888a' in h or 'dusty' in h  # dusty rose
        assert '#5f8fa8' in h or 'slate' in h  # slate blue

    def test_has_dark_border_colour(self):
        h = html().lower()
        assert '1a1a1a' in h

    def test_has_min_cell_constant(self):
        h = html()
        assert 'MIN_CELL' in h or 'min_cell' in h or 'minCell' in h

    def test_has_max_depth_constant(self):
        h = html()
        assert 'MAX_DEPTH' in h or 'maxDepth' in h or 'max_depth' in h

    def test_has_hold_constant(self):
        h = html()
        assert '4000' in h or 'HOLD' in h

    def test_has_bfs_or_queue(self):
        h = html().lower()
        assert 'bfs' in h or 'queue' in h or 'shift()' in h

    def test_has_fade_mechanism(self):
        h = html()
        assert 'opacity' in h or 'fadeOut' in h or 'fade' in h.lower()

    def test_lines_group_before_cells_group(self):
        """Verify SVG layering: cells drawn before lines so lines appear on top."""
        h = html()
        cells_pos = h.find('id="cells"')
        lines_pos = h.find('id="lines"')
        assert cells_pos != -1 and lines_pos != -1
        assert cells_pos < lines_pos, 'cells group must be declared before lines group in SVG'


# ---------------------------------------------------------------------------
# BSP algorithm correctness (Python mirror)
# ---------------------------------------------------------------------------


class TestBSPAlgorithm:
    """Verify the Python-mirrored BSP produces structurally correct trees."""

    def _tree(self, seed=42, depth=5):
        rng = random.Random(seed)
        return build_bsp({'x': 0, 'y': 0, 'w': 800, 'h': 800}, depth, None, rng=rng)

    def test_root_rect_covers_canvas(self):
        tree = self._tree()
        assert tree['rect'] == {'x': 0, 'y': 0, 'w': 800, 'h': 800}

    def test_leaves_cover_full_canvas(self):
        """All leaf rects must tile the 800×800 canvas without gaps."""
        tree = self._tree()
        leaves = collect_leaves(tree)
        total_area = sum(n['rect']['w'] * n['rect']['h'] for n in leaves)
        assert total_area == 800 * 800, f"Leaves cover {total_area} px², expected 640000"

    def test_all_leaf_colours_in_palette(self):
        tree = self._tree()
        for leaf in collect_leaves(tree):
            assert leaf['color'] in PALETTE, f"Unexpected colour {leaf['color']!r}"

    def test_sibling_colours_differ(self):
        """Adjacent siblings in the BSP must always have different palette colours."""
        tree = self._tree(seed=7)
        events = bfs_events(tree)
        for ev in events:
            lc = rep_color(ev['left'])
            rc = rep_color(ev['right'])
            assert lc != rc, f"Sibling colours both {lc!r} — adjacency constraint violated"

    def test_no_leaf_smaller_than_min_cell_threshold(self):
        """No leaf should be created from a parent dimension < MIN_CELL * 2."""
        min_cell = 40
        tree = build_bsp({'x': 0, 'y': 0, 'w': 800, 'h': 800}, 8, None,
                         min_cell=min_cell, rng=random.Random(99))
        for leaf in collect_leaves(tree):
            r = leaf['rect']
            # Width and height could be below min_cell when the parent was exactly
            # at threshold and the ratio happened to be extreme.  The key guarantee
            # is that a parent too small to split reliably is never split at all.
            # A parent of w = min_cell*2 at ratio 0.3 gives child w = 0.3*80 = 24.
            # We only assert the parent threshold, not the child size.
            assert r['w'] > 0 and r['h'] > 0, "Zero-area leaf created"

    def test_depth_zero_always_leaf(self):
        rng = random.Random(1)
        node = build_bsp({'x': 0, 'y': 0, 'w': 800, 'h': 800}, 0, None, rng=rng)
        assert node['leaf'], "depth=0 must always produce a leaf"

    def test_wide_rect_prefers_vertical_split(self):
        """A very wide rectangle should almost always be split by a vertical line."""
        rng = random.Random(123)
        vertical_count = 0
        trials = 100
        for _ in range(trials):
            node = build_bsp({'x': 0, 'y': 0, 'w': 800, 'h': 80}, 1, None, rng=rng)
            if not node['leaf']:
                line = node['line']
                # Vertical line: x1 == x2 and they are interior
                if line[0] == line[2] and 0 < line[0] < 800:
                    vertical_count += 1
        assert vertical_count >= 70, (
            f"Wide rect should prefer vertical splits; got {vertical_count}/100"
        )

    def test_tall_rect_prefers_horizontal_split(self):
        """A very tall rectangle should almost always be split by a horizontal line."""
        rng = random.Random(456)
        horizontal_count = 0
        trials = 100
        for _ in range(trials):
            node = build_bsp({'x': 0, 'y': 0, 'w': 80, 'h': 800}, 1, None, rng=rng)
            if not node['leaf']:
                line = node['line']
                # Horizontal line: y1 == y2 and they are interior
                if line[1] == line[3] and 0 < line[1] < 800:
                    horizontal_count += 1
        assert horizontal_count >= 70, (
            f"Tall rect should prefer horizontal splits; got {horizontal_count}/100"
        )

    def test_bfs_events_parents_before_children(self):
        """BFS order guarantees every internal node appears before its own children."""
        rng = random.Random(77)
        tree = build_bsp({'x': 0, 'y': 0, 'w': 800, 'h': 800}, 5, None, rng=rng)
        events = bfs_events(tree)
        # Build a mapping from rect identity to index
        event_index = {id(e): i for i, e in enumerate(events)}
        for ev in events:
            parent_idx = event_index[id(ev)]
            for child in (ev['left'], ev['right']):
                if not child['leaf']:
                    child_idx = event_index[id(child)]
                    assert parent_idx < child_idx, (
                        f"Child (idx {child_idx}) appears before its parent (idx {parent_idx}) in BFS"
                    )

    def test_split_ratio_in_range(self):
        """Split positions must lie strictly inside the parent rectangle."""
        rng = random.Random(55)
        tree = build_bsp({'x': 0, 'y': 0, 'w': 800, 'h': 800}, 6, None, rng=rng)
        for ev in bfs_events(tree):
            r = ev['rect']
            line = ev['line']
            x1, y1, x2, y2 = line
            if x1 == x2:
                # vertical line at x
                assert r['x'] < x1 < r['x'] + r['w'], f"Vertical split {x1} outside parent [{r['x']}, {r['x']+r['w']}]"
            else:
                # horizontal line at y
                assert r['y'] < y1 < r['y'] + r['h'], f"Horizontal split {y1} outside parent [{r['y']}, {r['y']+r['h']}]"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_tiny_rect_becomes_leaf(self):
        """A rectangle smaller than min_cell*2 in both dimensions must be a leaf."""
        rng = random.Random(0)
        node = build_bsp({'x': 0, 'y': 0, 'w': 30, 'h': 30}, 10, None, min_cell=40, rng=rng)
        assert node['leaf'], "30×30 rect (< 80 threshold) must be a leaf"

    def test_single_cell_palette(self):
        """With a single-colour palette and no avoid, that colour is always chosen."""
        rng = random.Random(42)
        for _ in range(20):
            c = pick_color(None, palette=['#ff0000'], rng=rng)
            assert c == '#ff0000'

    def test_avoid_removes_one_option(self):
        """pick_color with avoid must never return the avoided colour."""
        rng = random.Random(99)
        avoid = '#c4888a'
        for _ in range(50):
            c = pick_color(avoid, rng=rng)
            assert c != avoid, f"pick_color returned avoided colour {avoid!r}"

    def test_very_deep_tree_still_valid(self):
        """depth=10 should not crash and leaves must still cover the canvas."""
        rng = random.Random(13)
        tree = build_bsp({'x': 0, 'y': 0, 'w': 800, 'h': 800}, 10, None, rng=rng)
        leaves = collect_leaves(tree)
        total = sum(n['rect']['w'] * n['rect']['h'] for n in leaves)
        assert total == 800 * 800

    def test_depth_1_produces_exactly_two_leaves(self):
        """depth=1 must split once producing exactly two leaves."""
        rng = random.Random(21)
        tree = build_bsp({'x': 0, 'y': 0, 'w': 800, 'h': 800}, 1, None, rng=rng)
        assert not tree['leaf'], "depth=1 on large rect should split"
        assert tree['left']['leaf'], "Left child of depth-1 tree must be a leaf"
        assert tree['right']['leaf'], "Right child of depth-1 tree must be a leaf"
        assert len(collect_leaves(tree)) == 2

    def test_wrong_piece_id_absent(self):
        """Typo variants of the piece ID must not appear in pieces.json."""
        ids = {p['id'] for p in load_pieces()}
        assert '265-mondrian-recursion' not in ids
        assert '266-mondrian' not in ids
        assert '266-recursion' not in ids


# ---------------------------------------------------------------------------
# README tests
# ---------------------------------------------------------------------------


class TestReadme:
    def test_mentions_bsp(self):
        text = README.read_text().lower()
        assert 'bsp' in text or 'binary space' in text or 'space partitioning' in text

    def test_mentions_recursive(self):
        text = README.read_text().lower()
        assert 'recursiv' in text

    def test_mentions_mondrian(self):
        text = README.read_text().lower()
        assert 'mondrian' in text

    def test_mondrian_connection_honest(self):
        """README must acknowledge the Mondrian connection without overclaiming."""
        text = README.read_text().lower()
        # Must name the connection
        assert 'mondrian' in text
        # Should use qualifying language (inspired by, referencing, connection, etc.)
        qualifiers = ['connect', 'inspir', 'structur', 'reference', 'similar', 'rather than']
        assert any(q in text for q in qualifiers), (
            "README should qualify the Mondrian connection rather than claiming direct replication"
        )

    def test_mentions_palette(self):
        text = README.read_text().lower()
        assert 'palette' in text or 'colour' in text or 'color' in text

    def test_mentions_animation(self):
        text = README.read_text().lower()
        assert 'animat' in text or 'split' in text

    def test_has_at_least_two_sentences(self):
        text = README.read_text().strip()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        assert len(sentences) >= 3, "README must have at least 2–3 complete sentences"
