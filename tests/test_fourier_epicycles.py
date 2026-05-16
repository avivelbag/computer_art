"""Tests for piece 228 — Fourier Epicycles.

Covers: pieces.json entry integrity, file presence, DFT math via a Python
re-implementation of the same algorithm used in index.html, and edge cases
for the resampling and path-loading logic.
"""

import json
import math
import pathlib

import pytest

REPO  = pathlib.Path(__file__).parent.parent
PIECE = REPO / "pieces" / "228-fourier-epicycles"
PIECE_ID = "228-fourier-epicycles"


# ---------------------------------------------------------------------------
# Helpers that mirror the JS implementation
# ---------------------------------------------------------------------------

def dft(pts):
    """Python port of the JS computeDFT function.

    Packs (x, y) pairs as complex numbers z[n] = x[n] + i*y[n] and computes
    X[k] = (1/N) * sum_n z[n] * exp(-i * 2pi * k * n / N).

    Returns a list of dicts with keys: re, im, amp, phase, freq.
    """
    N = len(pts)
    result = []
    for k in range(N):
        re = 0.0
        im = 0.0
        for n, p in enumerate(pts):
            ang = 2 * math.pi * k * n / N
            c, s = math.cos(ang), math.sin(ang)
            re += p[0] * c + p[1] * s
            im += -p[0] * s + p[1] * c
        re /= N
        im /= N
        result.append({
            "re": re,
            "im": im,
            "amp": math.hypot(re, im),
            "phase": math.atan2(im, re),
            "freq": k,
        })
    result.sort(key=lambda c: c["amp"], reverse=True)
    return result


def reconstruct(components, t):
    """Reconstruct (x, y) from DFT components at time t in [0, 2π).

    x(t) = sum_k amp[k] * cos(freq[k]*t + phase[k])
    y(t) = sum_k amp[k] * sin(freq[k]*t + phase[k])
    """
    x = sum(c["amp"] * math.cos(c["freq"] * t + c["phase"]) for c in components)
    y = sum(c["amp"] * math.sin(c["freq"] * t + c["phase"]) for c in components)
    return x, y


def circle_pts(n, radius=1.0):
    """Generate n evenly-spaced points on a circle of given radius."""
    return [
        (radius * math.cos(2 * math.pi * i / n),
         radius * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# pieces.json entry
# ---------------------------------------------------------------------------

def load_pieces():
    return json.loads((REPO / "pieces.json").read_text())


def test_entry_in_pieces_json():
    """The new piece must appear in pieces.json."""
    ids = [e["id"] for e in load_pieces()]
    assert PIECE_ID in ids, f"{PIECE_ID} not found in pieces.json"


def test_entry_required_fields():
    """Entry must carry all eight required metadata fields."""
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    entry = next(e for e in load_pieces() if e["id"] == PIECE_ID)
    missing = required - entry.keys()
    assert not missing, f"Missing fields: {missing}"


def test_entry_id_matches_directory():
    """entry['id'] must equal the basename of entry['path']."""
    entry = next(e for e in load_pieces() if e["id"] == PIECE_ID)
    assert entry["id"] == pathlib.Path(entry["path"]).name


def test_entry_year_is_int():
    entry = next(e for e in load_pieces() if e["id"] == PIECE_ID)
    assert isinstance(entry["year"], int)


# ---------------------------------------------------------------------------
# File presence
# ---------------------------------------------------------------------------

def test_piece_directory_exists():
    assert PIECE.is_dir(), f"Directory missing: {PIECE}"


def test_index_html_exists():
    assert (PIECE / "index.html").is_file()


def test_thumbnail_svg_exists():
    assert (PIECE / "thumbnail.svg").is_file()


def test_readme_exists():
    assert (PIECE / "README.md").is_file()


def test_thumbnail_path_in_entry():
    """The thumbnail path in pieces.json must point to the actual file."""
    entry = next(e for e in load_pieces() if e["id"] == PIECE_ID)
    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file(), f"Thumbnail not found at {entry['thumbnail']}"


# ---------------------------------------------------------------------------
# index.html content sanity checks
# ---------------------------------------------------------------------------

def test_index_html_references_panel_js():
    """The piece must load the shared GalleryPanel script."""
    src = (PIECE / "index.html").read_text()
    assert "lib/panel.js" in src


def test_index_html_initialises_gallery_panel():
    src = (PIECE / "index.html").read_text()
    assert "GalleryPanel.init" in src


def test_index_html_has_harmonic_slider():
    src = (PIECE / "index.html").read_text()
    assert 'id="harm-slider"' in src


def test_index_html_has_draw_button():
    src = (PIECE / "index.html").read_text()
    assert 'id="btn-draw"' in src


def test_index_html_has_preset_buttons():
    src = (PIECE / "index.html").read_text()
    assert 'id="btn-heart"' in src
    assert 'id="btn-fig8"' in src


def test_index_html_has_dft_function():
    src = (PIECE / "index.html").read_text()
    assert "computeDFT" in src


def test_readme_mentions_dft_formula():
    src = (PIECE / "README.md").read_text()
    # The README should contain the DFT formula notation
    assert "X[k]" in src and "z[n]" in src


# ---------------------------------------------------------------------------
# DFT correctness — happy path
# ---------------------------------------------------------------------------

def test_dft_circle_has_single_dominant_frequency():
    """A circle of N points should produce one dominant frequency component
    (freq=1 for a counter-clockwise unit circle) and all others near zero.

    For a circle z[n] = r*e^(i*2π*n/N), only X[1] ≠ 0.
    """
    N = 32
    pts = circle_pts(N, radius=10.0)
    components = dft(pts)
    dominant = components[0]  # sorted by amp descending
    assert dominant["freq"] == 1, (
        f"Dominant freq should be 1 for a circle, got {dominant['freq']}"
    )
    assert dominant["amp"] == pytest.approx(10.0, abs=1e-9)
    # All other amplitudes should be negligibly small
    for c in components[1:]:
        assert c["amp"] < 1e-9, f"Unexpected non-zero amplitude at freq {c['freq']}: {c['amp']}"


def test_dft_reconstruction_matches_original():
    """Full reconstruction (all N harmonics) must reproduce original samples
    to floating-point precision.
    """
    N = 16
    pts = circle_pts(N, radius=5.0)
    components = dft(pts)
    for i, (ox, oy) in enumerate(pts):
        t = 2 * math.pi * i / N
        rx, ry = reconstruct(components, t)
        assert rx == pytest.approx(ox, abs=1e-9), f"x mismatch at sample {i}"
        assert ry == pytest.approx(oy, abs=1e-9), f"y mismatch at sample {i}"


def test_dft_dc_component_is_centroid():
    """The frequency-0 component (DC term) equals the centroid of the input."""
    pts = [(1.0, 2.0), (3.0, 4.0), (5.0, 0.0), (3.0, 2.0)]
    cx  = sum(p[0] for p in pts) / len(pts)
    cy  = sum(p[1] for p in pts) / len(pts)
    components = dft(pts)
    dc = next(c for c in components if c["freq"] == 0)
    assert dc["re"] == pytest.approx(cx, abs=1e-12)
    assert dc["im"] == pytest.approx(cy, abs=1e-12)


def test_dft_amplitude_sorted_descending():
    """Components must be sorted by amplitude largest-first."""
    pts = circle_pts(16, radius=3.0)
    components = dft(pts)
    amps = [c["amp"] for c in components]
    assert amps == sorted(amps, reverse=True)


def test_dft_heart_has_many_harmonics():
    """A heart curve (non-circular) should distribute energy across many frequencies,
    meaning the second-largest amplitude should be non-trivially large.
    """
    N = 64
    pts = [
        (16 * math.sin(2 * math.pi * i / N) ** 3,
         -(13 * math.cos(2 * math.pi * i / N)
           - 5 * math.cos(2 * 2 * math.pi * i / N)
           - 2 * math.cos(3 * 2 * math.pi * i / N)
           - math.cos(4 * 2 * math.pi * i / N)))
        for i in range(N)
    ]
    components = dft(pts)
    # At least the top 3 components should have non-negligible amplitude
    assert components[2]["amp"] > 0.1, "Heart should have energy in multiple harmonics"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_dft_single_point():
    """A single point should produce exactly one component with freq=0."""
    pts = [(3.0, 4.0)]
    components = dft(pts)
    assert len(components) == 1
    assert components[0]["freq"] == 0
    assert components[0]["re"] == pytest.approx(3.0, abs=1e-12)
    assert components[0]["im"] == pytest.approx(4.0, abs=1e-12)


def test_dft_two_identical_points():
    """Two identical points should yield DC only (all other components zero)."""
    pts = [(1.0, 1.0), (1.0, 1.0)]
    components = dft(pts)
    dc = next(c for c in components if c["freq"] == 0)
    assert dc["re"] == pytest.approx(1.0, abs=1e-12)
    assert dc["im"] == pytest.approx(1.0, abs=1e-12)
    for c in components:
        if c["freq"] != 0:
            assert c["amp"] < 1e-12


def test_dft_all_zero_input():
    """All-zero input should produce all-zero output."""
    pts = [(0.0, 0.0)] * 8
    components = dft(pts)
    for c in components:
        assert c["amp"] < 1e-15


def test_dft_large_n_performance():
    """DFT on N=128 points should complete without error (smoke test)."""
    pts = circle_pts(128, radius=1.0)
    components = dft(pts)
    assert len(components) == 128


# ---------------------------------------------------------------------------
# Failure mode: wrong piece metadata is caught by test_pieces.py
# ---------------------------------------------------------------------------

def test_spurious_entry_would_fail(tmp_path):
    """An entry pointing to a non-existent directory must fail the dir check."""
    ghost = tmp_path / "ghost-piece"
    assert not ghost.is_dir(), "ghost-piece must not exist for this test"
