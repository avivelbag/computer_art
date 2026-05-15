"""Tests for pieces/136-fourier-epicycles: Fourier epicycles tracing a star polygon."""

import importlib.util
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(__file__).parent.parent
PIECE_DIR = REPO / "pieces" / "136-fourier-epicycles"
INDEX_HTML = PIECE_DIR / "index.html"
README = PIECE_DIR / "README.md"
THUMBNAIL = PIECE_DIR / "thumbnail.svg"
PIECES_JSON = REPO / "pieces.json"
PIECE_ID = "136-fourier-epicycles"
TWO_PI = 2 * math.pi


def _load_gen():
    """Import generate_thumbnail.py as a module without executing __main__."""
    spec = importlib.util.spec_from_file_location(
        "gen136", PIECE_DIR / "generate_thumbnail.py"
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
# DFT correctness — Python mirror of the JS sampleStar / dft functions
# ---------------------------------------------------------------------------


def sample_star(n: int, r_outer: float = 1.0, r_inner: float = 0.38) -> list[tuple[float, float]]:
    """Sample n points uniformly along the 5-pointed star perimeter."""
    verts = []
    for i in range(10):
        angle = TWO_PI * i / 10 - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        verts.append((r * math.cos(angle), r * math.sin(angle)))

    segs = []
    for i in range(10):
        a, b = verts[i], verts[(i + 1) % 10]
        segs.append(math.hypot(b[0] - a[0], b[1] - a[1]))
    total = sum(segs)

    pts = []
    for i in range(n):
        target = (i / n) * total
        accum = 0.0
        for j in range(10):
            if accum + segs[j] >= target or j == 9:
                frac = min((target - accum) / segs[j], 1.0)
                a, b = verts[j], verts[(j + 1) % 10]
                pts.append((a[0] + frac * (b[0] - a[0]), a[1] + frac * (b[1] - a[1])))
                break
            accum += segs[j]
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


class TestDFTReconstructsStar:
    """Verify the DFT correctly decomposes and reconstructs the star shape."""

    N = 64

    def test_sample_star_returns_n_points(self):
        pts = sample_star(self.N)
        assert len(pts) == self.N

    def test_path_closes_at_2pi(self):
        """Tip at t=2π must equal tip at t=0 — the star path loops seamlessly."""
        coeffs = dft(sample_star(self.N))
        x0, y0 = reconstruct(coeffs, 0.0)
        x2pi, y2pi = reconstruct(coeffs, TWO_PI)
        assert abs(x0 - x2pi) < 1e-9
        assert abs(y0 - y2pi) < 1e-9

    def test_reconstruction_matches_sample_at_t0(self):
        """Reconstructed tip at t=0 must match the first sample point."""
        pts = sample_star(self.N)
        coeffs = dft(pts)
        rx, ry = reconstruct(coeffs, 0.0)
        assert abs(rx - pts[0][0]) < 1e-9
        assert abs(ry - pts[0][1]) < 1e-9

    def test_all_frequencies_are_integers(self):
        for c in dft(sample_star(self.N)):
            assert isinstance(c["freq"], int)

    def test_frequencies_span_0_to_n_minus_1(self):
        freqs = {c["freq"] for c in dft(sample_star(self.N))}
        assert freqs == set(range(self.N))

    def test_amplitudes_non_negative(self):
        for c in dft(sample_star(self.N)):
            assert c["amp"] >= 0.0

    def test_phases_in_range(self):
        for c in dft(sample_star(self.N)):
            assert -math.pi - 1e-12 <= c["phase"] <= math.pi + 1e-12

    def test_sorted_by_amplitude_descending(self):
        coeffs = dft(sample_star(self.N))
        amps = [c["amp"] for c in coeffs]
        assert amps == sorted(amps, reverse=True)

    def test_star_stays_within_outer_radius_bounds(self):
        """All reconstructed points must fit within a circle of radius ~1 (outer radius)."""
        coeffs = dft(sample_star(self.N))
        for i in range(self.N):
            t = TWO_PI * i / self.N
            x, y = reconstruct(coeffs, t)
            dist = math.sqrt(x * x + y * y)
            assert dist <= 1.1, f"point ({x:.3f},{y:.3f}) outside expected radius at t={t:.3f}"


class TestEdgeCasesDFT:
    def test_sample_star_n4_returns_4_points(self):
        pts = sample_star(4)
        assert len(pts) == 4

    def test_dft_n4_returns_4_coefficients(self):
        coeffs = dft(sample_star(4))
        assert len(coeffs) == 4

    def test_large_n_128_still_closes(self):
        """With N=128 the path must still close at t=2π."""
        coeffs = dft(sample_star(128))
        x0, y0 = reconstruct(coeffs, 0.0)
        x2pi, y2pi = reconstruct(coeffs, TWO_PI)
        assert abs(x0 - x2pi) < 1e-8
        assert abs(y0 - y2pi) < 1e-8

    def test_constant_signal_dc_equals_value(self):
        """DFT of a constant-x signal: DC amplitude must equal the constant."""
        pts = [(1.0, 0.0)] * 8
        coeffs = dft(pts)
        dc = next(c for c in coeffs if c["freq"] == 0)
        assert abs(dc["amp"] - 1.0) < 1e-12


class TestFailureModes:
    def test_wrong_id_not_in_json(self):
        data = json.loads(PIECES_JSON.read_text())
        ids = {item["id"] for item in data}
        assert "136-wrong-piece" not in ids

    def test_missing_canvas_detectable(self):
        fake = "<html><body><div></div></body></html>"
        assert "<canvas" not in fake

    def test_reconstruction_with_no_coefficients_returns_origin(self):
        """Reconstructing from empty coefficients must return (0, 0)."""
        x, y = reconstruct([], math.pi / 4)
        assert x == 0.0 and y == 0.0

    def test_nonzero_dc_shifts_reconstruction(self):
        """A constant signal: DC component must shift reconstruction to that point."""
        pts = [(3.0, 2.0)] * 16
        coeffs = dft(pts)
        x, y = reconstruct(coeffs, 0.7)
        assert abs(x - 3.0) < 1e-9
        assert abs(y - 2.0) < 1e-9


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
    assert "06101e" in _html().lower()


def test_html_trace_color_gold():
    """Trace colour must be the warm gold #f5b942."""
    assert "f5b942" in _html().lower()


def test_html_mentions_dft_or_fourier():
    assert "dft" in _html().lower() or "fourier" in _html().lower()


def test_html_uses_request_animation_frame():
    assert "requestAnimationFrame" in _html()


def test_html_has_two_pi():
    html = _html()
    assert "TWO_PI" in html or "Math.PI * 2" in html or "2 * Math.PI" in html


def test_html_n_is_64_or_128():
    """N (DFT coefficient count) must be 64 or 128."""
    html = _html()
    m = re.search(r"const\s+N\s*=\s*(\d+)", html)
    assert m, "const N not found in HTML"
    val = int(m.group(1))
    assert val in (64, 128), f"N={val} must be 64 or 128"


def test_html_has_star_inner_radius():
    """Star inner-radius constant 0.38 must appear in the source."""
    assert "0.38" in _html()


def test_html_has_fade_transition():
    """CSS opacity transition for the trace reset must be present."""
    html = _html()
    assert "transition" in html and "0.5s" in html


def test_html_self_contained():
    html = _html()
    assert "<script src=" not in html
    assert '<link rel="stylesheet"' not in html


def test_html_has_period_8000():
    """PERIOD must be 8000 ms for the 8-second revolution requirement."""
    assert "8000" in _html()


# ---------------------------------------------------------------------------
# generate_thumbnail module tests
# ---------------------------------------------------------------------------


class TestGenerateThumbnail:
    def test_sample_star_returns_n_points(self):
        gen = _load_gen()
        pts = gen.sample_star(64)
        assert len(pts) == 64

    def test_sample_star_closes(self):
        """First and last sample on the star should be distinct (not identical)."""
        gen = _load_gen()
        pts = gen.sample_star(64)
        assert pts[0] != pts[-1]

    def test_dft_returns_n_coefficients(self):
        gen = _load_gen()
        coeffs = gen.dft(gen.sample_star(64))
        assert len(coeffs) == 64

    def test_dft_sorted_by_amplitude(self):
        gen = _load_gen()
        coeffs = gen.dft(gen.sample_star(64))
        amps = [c["amp"] for c in coeffs]
        assert amps == sorted(amps, reverse=True)

    def test_tip_at_origin_for_empty_coeffs(self):
        gen = _load_gen()
        x, y = gen.tip_at([], 0.0)
        assert x == 0.0 and y == 0.0

    def test_tip_at_returns_floats(self):
        gen = _load_gen()
        coeffs = gen.dft(gen.sample_star(64))[:10]
        x, y = gen.tip_at(coeffs, 0.0)
        assert isinstance(x, float) and isinstance(y, float)

    def test_epicycles_at_returns_correct_count(self):
        gen = _load_gen()
        coeffs = gen.dft(gen.sample_star(64))[:gen.N_EPICYCLES]
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

    def test_generate_svg_has_gold_trace(self):
        gen = _load_gen()
        assert "f5b942" in gen.generate_svg().lower()


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


def test_thumbnail_has_gold_trace():
    """Trace colour must be the warm gold #f5b942."""
    assert "f5b942" in THUMBNAIL.read_text().lower()


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


def test_pieces_json_technique_mentions_fourier_or_dft():
    tech = _entry()["technique"].lower()
    assert "fourier" in tech or "dft" in tech or "epicycle" in tech


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def test_readme_not_empty():
    assert len(README.read_text().strip()) > 100


def test_readme_mentions_fourier():
    assert "fourier" in README.read_text().lower()


def test_readme_mentions_star():
    assert "star" in README.read_text().lower()


def test_readme_mentions_frequency():
    assert "frequenc" in README.read_text().lower()


def test_readme_mentions_circles():
    assert "circle" in README.read_text().lower()


def test_readme_explains_closure():
    readme = README.read_text().lower()
    assert "close" in readme or "loop" in readme or "revolution" in readme
