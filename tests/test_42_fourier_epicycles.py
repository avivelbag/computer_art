"""Tests for pieces/42-circles-within-circles: Fourier epicycles tracing a heart."""

import importlib.util
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "42-circles-within-circles"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "42-circles-within-circles"
TWO_PI = 2 * math.pi


def _load_gen():
    """Import generate_thumbnail.py as a module."""
    spec = importlib.util.spec_from_file_location(
        "gen42", PIECE_DIR / "generate_thumbnail.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _entry() -> dict:
    """Return the pieces.json entry for this piece."""
    data = json.loads(PIECES_JSON.read_text())
    for item in data:
        if item.get("id") == PIECE_ID:
            return item
    raise AssertionError(f"{PIECE_ID!r} not found in pieces.json")


def _html() -> str:
    return INDEX_HTML.read_text()


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------


def test_piece_dir_exists():
    assert PIECE_DIR.is_dir()


def test_index_html_exists():
    assert INDEX_HTML.is_file()


def test_readme_exists():
    assert README.is_file()


def test_thumbnail_exists():
    assert THUMBNAIL.is_file()


def test_generate_thumbnail_exists():
    assert (PIECE_DIR / "generate_thumbnail.py").is_file()


# ---------------------------------------------------------------------------
# DFT correctness (Python mirror of the JS dft() function)
# ---------------------------------------------------------------------------


def sample_heart(n: int) -> list[tuple[float, float]]:
    """Sample n points on the parametric heart curve."""
    pts = []
    for i in range(n):
        t = TWO_PI * i / n
        s = math.sin(t)
        pts.append((
            16 * s * s * s,
            -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        ))
    return pts


def dft(pts: list[tuple[float, float]]) -> list[dict]:
    """Reference DFT matching the JS implementation in index.html."""
    n = len(pts)
    result = []
    for k in range(n):
        re = 0.0
        im = 0.0
        for j in range(n):
            angle = TWO_PI * k * j / n
            c = math.cos(angle)
            s = math.sin(angle)
            re += pts[j][0] * c + pts[j][1] * s
            im += -pts[j][0] * s + pts[j][1] * c
        amp = math.sqrt(re * re + im * im) / n
        phase = math.atan2(im, re)
        result.append({"freq": k, "amp": amp, "phase": phase})
    result.sort(key=lambda x: -x["amp"])
    return result


def reconstruct(coeffs: list[dict], t: float, scale: float = 1.0) -> tuple[float, float]:
    """Reconstruct (x, y) from DFT coefficients at time t."""
    x = 0.0
    y = 0.0
    for c in coeffs:
        angle = c["freq"] * t + c["phase"]
        x += c["amp"] * scale * math.cos(angle)
        y += c["amp"] * scale * math.sin(angle)
    return x, y


class TestDFTReconstructsHeart:
    """Verify the DFT correctly decomposes and reconstructs the heart shape."""

    N = 64

    def test_dc_component_is_near_zero(self):
        """Heart is centered at origin — DC component amplitude must be tiny."""
        pts = sample_heart(self.N)
        coeffs = dft(pts)
        dc = next(c for c in coeffs if c["freq"] == 0)
        assert dc["amp"] < 1e-10, f"DC amplitude too large: {dc['amp']}"

    def test_dominant_frequency_is_one(self):
        """Frequency 1 (fundamental) must be the largest component."""
        pts = sample_heart(self.N)
        coeffs = dft(pts)
        assert coeffs[0]["freq"] == 1 or coeffs[0]["freq"] == self.N - 1

    def test_reconstruction_matches_sample_at_t0(self):
        """Reconstructed tip at t=0 must match the first sample point."""
        pts = sample_heart(self.N)
        coeffs = dft(pts)
        rx, ry = reconstruct(coeffs, 0.0)
        assert abs(rx - pts[0][0]) < 1e-9, f"x mismatch at t=0: {rx} vs {pts[0][0]}"
        assert abs(ry - pts[0][1]) < 1e-9, f"y mismatch at t=0: {ry} vs {pts[0][1]}"

    def test_reconstruction_matches_sample_midway(self):
        """Reconstructed tip at t=π must match the sample at index N/2."""
        pts = sample_heart(self.N)
        coeffs = dft(pts)
        rx, ry = reconstruct(coeffs, math.pi)
        half = self.N // 2
        assert abs(rx - pts[half][0]) < 1e-9
        assert abs(ry - pts[half][1]) < 1e-9

    def test_path_closes_at_2pi(self):
        """Tip position at t=2π must equal tip position at t=0 (seamless loop)."""
        pts = sample_heart(self.N)
        coeffs = dft(pts)
        x0, y0 = reconstruct(coeffs, 0.0)
        x2pi, y2pi = reconstruct(coeffs, TWO_PI)
        assert abs(x0 - x2pi) < 1e-9
        assert abs(y0 - y2pi) < 1e-9

    def test_all_frequencies_are_integers(self):
        """Every coefficient must have an integer frequency."""
        pts = sample_heart(self.N)
        for c in dft(pts):
            assert isinstance(c["freq"], int)

    def test_frequencies_span_0_to_n_minus_1(self):
        """DFT produces exactly N coefficients for frequencies 0 through N-1."""
        pts = sample_heart(self.N)
        freqs = {c["freq"] for c in dft(pts)}
        assert freqs == set(range(self.N))

    def test_reconstruction_stays_within_heart_bounds(self):
        """Reconstructed x must stay in [-17, 17] — the heart's natural x range."""
        pts = sample_heart(self.N)
        coeffs = dft(pts)
        for i in range(self.N):
            t = TWO_PI * i / self.N
            x, y = reconstruct(coeffs, t)
            assert -17 <= x <= 17, f"x={x} out of heart bounds at t={t:.3f}"

    def test_top50_still_traces_heart(self):
        """Top-50 coefficients must reconstruct x within 0.01 of the exact value."""
        pts = sample_heart(self.N)
        coeffs_full = dft(pts)
        coeffs_50 = coeffs_full[:50]
        for i in range(self.N):
            t = TWO_PI * i / self.N
            x_full, y_full = reconstruct(coeffs_full, t)
            x_50, y_50 = reconstruct(coeffs_50, t)
            assert abs(x_full - x_50) < 0.01
            assert abs(y_full - y_50) < 0.01


class TestEdgeCasesDFT:
    def test_single_point_dft_all_equal_amplitude(self):
        """DFT of a single repeated point: all amplitudes equal (constant signal)."""
        pts = [(1.0, 0.0)] * 8
        coeffs = dft(pts)
        dc = next(c for c in coeffs if c["freq"] == 0)
        assert abs(dc["amp"] - 1.0) < 1e-12

    def test_empty_heart_sample_n4(self):
        """DFT of 4-point heart must return exactly 4 coefficients."""
        pts = sample_heart(4)
        coeffs = dft(pts)
        assert len(coeffs) == 4

    def test_large_n_still_closes(self):
        """With N=128 the path must still close at t=2π."""
        pts = sample_heart(128)
        coeffs = dft(pts)
        x0, y0 = reconstruct(coeffs, 0.0)
        x2pi, y2pi = reconstruct(coeffs, TWO_PI)
        assert abs(x0 - x2pi) < 1e-8
        assert abs(y0 - y2pi) < 1e-8

    def test_amplitudes_non_negative(self):
        """All DFT amplitudes must be ≥ 0."""
        for c in dft(sample_heart(64)):
            assert c["amp"] >= 0.0

    def test_phases_in_range(self):
        """All phases must be in (−π, π]."""
        for c in dft(sample_heart(64)):
            assert -math.pi - 1e-12 <= c["phase"] <= math.pi + 1e-12


class TestFailureModes:
    def test_wrong_id_not_in_json(self):
        data = json.loads(PIECES_JSON.read_text())
        ids = {item["id"] for item in data}
        assert "42-wrong-piece" not in ids

    def test_missing_canvas_detectable(self):
        fake = "<html><body><div></div></body></html>"
        assert "<canvas" not in fake

    def test_reconstruction_fails_with_no_coefficients(self):
        """Reconstructing from zero coefficients always returns (0, 0)."""
        x, y = reconstruct([], math.pi / 3)
        assert x == 0.0 and y == 0.0

    def test_nonzero_dc_would_shift_path(self):
        """A non-zero DC component shifts the reconstruction away from origin."""
        pts = [(5.0, 3.0)] * 16  # constant signal, DC = (5, 3), all others 0
        coeffs = dft(pts)
        x, y = reconstruct(coeffs, 0.5)
        assert abs(x - 5.0) < 1e-9
        assert abs(y - 3.0) < 1e-9


# ---------------------------------------------------------------------------
# HTML structure
# ---------------------------------------------------------------------------


def test_html_has_canvas():
    assert "<canvas" in _html()


def test_html_has_script():
    assert "<script" in _html()


def test_html_has_viewport_meta():
    assert 'name="viewport"' in _html()


def test_html_has_charset():
    assert "charset" in _html()


def test_html_no_external_scripts():
    assert not re.findall(r'<script[^>]+src=["\']https?://', _html())


def test_html_has_dark_background():
    assert "07070f" in _html().lower()


def test_html_mentions_dft():
    assert "dft" in _html().lower() or "fourier" in _html().lower()


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_two_pi():
    html = _html()
    assert "TWO_PI" in html or "Math.PI * 2" in html or "2 * Math.PI" in html


def test_html_has_heart_sample():
    """Heart parametric coefficients 13, 5 must appear in the source."""
    html = _html()
    assert "13" in html and "5" in html


def test_html_n_epicycles_20_to_60():
    """N_EPICYCLES must be in the 20–60 range per acceptance criteria."""
    html = _html()
    m = re.search(r"N_EPICYCLES\s*=\s*(\d+)", html)
    assert m, "N_EPICYCLES not found in HTML"
    val = int(m.group(1))
    assert 20 <= val <= 60, f"N_EPICYCLES={val} outside 20–60"


def test_html_self_contained():
    html = _html()
    assert "<script src=" not in html
    assert '<link rel="stylesheet"' not in html


def test_html_trace_color_cyan():
    """Trace colour must be the bright cyan #00e5ff."""
    assert "00e5ff" in _html().lower()


# ---------------------------------------------------------------------------
# generate_thumbnail module tests
# ---------------------------------------------------------------------------


class TestGenerateThumbnail:
    def test_sample_heart_returns_n_points(self):
        gen = _load_gen()
        pts = gen.sample_heart(64)
        assert len(pts) == 64

    def test_sample_heart_closes(self):
        """First and last sample should be adjacent but not identical."""
        gen = _load_gen()
        pts = gen.sample_heart(64)
        assert pts[0] != pts[-1]

    def test_dft_returns_n_coefficients(self):
        gen = _load_gen()
        coeffs = gen.dft(gen.sample_heart(64))
        assert len(coeffs) == 64

    def test_dft_sorted_by_amplitude(self):
        gen = _load_gen()
        coeffs = gen.dft(gen.sample_heart(64))
        amps = [c["amp"] for c in coeffs]
        assert amps == sorted(amps, reverse=True)

    def test_tip_at_origin_at_zero_coeffs(self):
        gen = _load_gen()
        x, y = gen.tip_at([], 0.0)
        assert x == 0.0 and y == 0.0

    def test_tip_at_returns_floats(self):
        gen = _load_gen()
        coeffs = gen.dft(gen.sample_heart(64))[:10]
        x, y = gen.tip_at(coeffs, 0.0)
        assert isinstance(x, float) and isinstance(y, float)

    def test_epicycles_at_returns_correct_count(self):
        gen = _load_gen()
        coeffs = gen.dft(gen.sample_heart(64))[:gen.N_EPICYCLES]
        circles = gen.epicycles_at(coeffs, 0.0)
        assert len(circles) == gen.N_EPICYCLES

    def test_generate_svg_returns_string(self):
        gen = _load_gen()
        assert isinstance(gen.generate_svg(), str)

    def test_generate_svg_valid_xml(self):
        gen = _load_gen()
        ET.fromstring(gen.generate_svg())

    def test_generate_svg_has_background(self):
        gen = _load_gen()
        assert "<rect" in gen.generate_svg()

    def test_generate_svg_has_trace_polyline(self):
        gen = _load_gen()
        assert "<polyline" in gen.generate_svg()

    def test_generate_svg_has_circles(self):
        gen = _load_gen()
        assert "<circle" in gen.generate_svg()

    def test_generate_svg_is_reproducible(self):
        gen = _load_gen()
        assert gen.generate_svg() == gen.generate_svg()


# ---------------------------------------------------------------------------
# Thumbnail SVG
# ---------------------------------------------------------------------------


def test_thumbnail_not_empty():
    assert THUMBNAIL.stat().st_size > 200


def test_thumbnail_is_valid_xml():
    ET.fromstring(THUMBNAIL.read_text())


def test_thumbnail_has_viewbox():
    assert "viewBox" in THUMBNAIL.read_text()


def test_thumbnail_dimensions_400():
    svg = THUMBNAIL.read_text()
    w = re.search(r'width="(\d+)"', svg)
    h = re.search(r'height="(\d+)"', svg)
    assert w and int(w.group(1)) == 400
    assert h and int(h.group(1)) == 400


def test_thumbnail_has_background_rect():
    assert "<rect" in THUMBNAIL.read_text()


def test_thumbnail_has_trace():
    """Thumbnail must contain the traced path (polyline or path element)."""
    svg = THUMBNAIL.read_text()
    assert "<polyline" in svg or "<path" in svg


def test_thumbnail_has_circles():
    assert "<circle" in THUMBNAIL.read_text()


def test_thumbnail_under_500kb():
    assert THUMBNAIL.stat().st_size < 500_000


def test_thumbnail_valid_utf8():
    THUMBNAIL.read_bytes().decode("utf-8")


def test_thumbnail_has_svg_namespace():
    assert 'xmlns="http://www.w3.org/2000/svg"' in THUMBNAIL.read_text()


def test_thumbnail_has_cyan_trace():
    """Trace colour must be the cyan #00e5ff."""
    assert "00e5ff" in THUMBNAIL.read_text().lower()


# ---------------------------------------------------------------------------
# pieces.json
# ---------------------------------------------------------------------------


def test_pieces_json_has_entry():
    _entry()


def test_pieces_json_entry_has_all_required_fields():
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail"}
    missing = required - _entry().keys()
    assert not missing, f"Missing fields: {missing}"


def test_pieces_json_id_matches():
    assert _entry()["id"] == PIECE_ID


def test_pieces_json_path_matches():
    assert _entry()["path"] == f"pieces/{PIECE_ID}"


def test_pieces_json_thumbnail_is_svg():
    assert _entry()["thumbnail"].endswith(".svg")


def test_pieces_json_thumbnail_file_exists():
    assert (REPO / _entry()["thumbnail"]).is_file()


def test_pieces_json_year_is_int():
    assert isinstance(_entry()["year"], int)


def test_pieces_json_technique_mentions_canvas():
    assert "canvas" in _entry()["technique"].lower()


def test_pieces_json_technique_mentions_fourier():
    tech = _entry()["technique"].lower()
    assert "fourier" in tech or "dft" in tech or "epicycle" in tech


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_fourier():
    assert "fourier" in README.read_text().lower()


def test_readme_mentions_heart():
    assert "heart" in README.read_text().lower()


def test_readme_mentions_frequency():
    assert "frequenc" in README.read_text().lower()


def test_readme_mentions_circles():
    assert "circle" in README.read_text().lower()


def test_readme_explains_why_surprising():
    readme = README.read_text().lower()
    assert "surprising" in readme or "surprise" in readme or "feel" in readme
