"""Tests for piece 284-loxodrome-navigator."""
import json
import math
import pathlib
import re


REPO = pathlib.Path(__file__).parent.parent
PIECE_ID = "284-loxodrome-navigator"
PIECE_DIR = REPO / "pieces" / PIECE_ID


# ---- Loxodrome math helpers (Python mirror of the JS implementation) ----

def gudermannian(t):
    """Map Mercator y-coordinate to latitude: lat(t) = 2*atan(exp(t)) - pi/2."""
    return 2 * math.atan(math.exp(t)) - math.pi / 2


def loxodrome_point(t, bearing_deg, lon0=0.0):
    """Return (lat, lon) on the loxodrome at Mercator parameter t."""
    lat = gudermannian(t)
    lon = lon0 + t * math.tan(math.radians(bearing_deg))
    return lat, lon


def lat_lon_to_3d(lat, lon):
    """Convert spherical coordinates to unit-sphere Cartesian (x, y, z)."""
    c = math.cos(lat)
    return c * math.cos(lon), math.sin(lat), c * math.sin(lon)


def rot_y(x, y, z, angle):
    """Rotate (x, y, z) around the Y axis by angle (radians)."""
    ca, sa = math.cos(angle), math.sin(angle)
    return x * ca + z * sa, y, z * ca - x * sa


# ---- File existence tests (happy path) ----

def test_piece_directory_exists():
    assert PIECE_DIR.is_dir(), f"Piece directory missing: {PIECE_DIR}"


def test_index_html_exists():
    assert (PIECE_DIR / "index.html").is_file(), "index.html missing"


def test_thumbnail_exists():
    thumb_svg = PIECE_DIR / "thumbnail.svg"
    thumb_png = PIECE_DIR / "thumbnail.png"
    assert thumb_svg.is_file() or thumb_png.is_file(), "Neither thumbnail.svg nor thumbnail.png found"


def test_readme_exists():
    assert (PIECE_DIR / "README.md").is_file(), "README.md missing"


# ---- pieces.json entry tests ----

def _load_pieces():
    return json.loads((REPO / "pieces.json").read_text())


def test_piece_in_pieces_json():
    ids = [p["id"] for p in _load_pieces()]
    assert PIECE_ID in ids, f"{PIECE_ID} not found in pieces.json"


def test_pieces_json_entry_has_required_fields():
    entry = next(p for p in _load_pieces() if p["id"] == PIECE_ID)
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    missing = required - entry.keys()
    assert not missing, f"Missing fields in pieces.json entry: {missing}"


def test_pieces_json_thumbnail_file_exists():
    entry = next(p for p in _load_pieces() if p["id"] == PIECE_ID)
    assert (REPO / entry["thumbnail"]).is_file(), f"Thumbnail file missing: {entry['thumbnail']}"


def test_pieces_json_path_matches_id():
    entry = next(p for p in _load_pieces() if p["id"] == PIECE_ID)
    assert entry["id"] == pathlib.Path(entry["path"]).name, \
        f"id {entry['id']!r} does not match path basename {pathlib.Path(entry['path']).name!r}"


# ---- Loxodrome math correctness tests ----

def test_gudermannian_at_zero():
    """t=0 should map to the equator."""
    assert abs(gudermannian(0)) < 1e-12


def test_gudermannian_positive_limit():
    """t=4 should be close to the north pole (lat ≈ +pi/2)."""
    lat = gudermannian(4)
    assert lat > 0
    assert abs(lat - math.pi / 2) < 0.05, f"Expected near pi/2, got {lat}"


def test_gudermannian_negative_limit():
    """t=-4 should be close to the south pole (lat ≈ -pi/2)."""
    lat = gudermannian(-4)
    assert lat < 0
    assert abs(lat + math.pi / 2) < 0.05, f"Expected near -pi/2, got {lat}"


def test_gudermannian_monotonic():
    """Latitude must increase strictly with t."""
    ts = [-4, -2, 0, 2, 4]
    lats = [gudermannian(t) for t in ts]
    assert lats == sorted(lats), "gudermannian must be monotonically increasing"


def test_loxodrome_meridian_bearing():
    """Bearing 0° gives tan=0, so longitude stays constant (meridian curve)."""
    lon0 = 1.23
    for t in [-3, -1, 0, 1, 3]:
        _, lon = loxodrome_point(t, 0.0, lon0)
        assert abs(lon - lon0) < 1e-12, f"Meridian loxodrome changed lon at t={t}"


def test_loxodrome_ne_spiral_longitude_increases():
    """Bearing 45° (NE) — longitude must increase as t increases."""
    pts = [loxodrome_point(t, 45.0) for t in [-3, -1, 0, 1, 3]]
    lons = [p[1] for p in pts]
    assert lons == sorted(lons), "NE spiral should have monotonically increasing longitude"


def test_loxodrome_nw_spiral_longitude_decreases():
    """Bearing 135° (NW in the param direction) — longitude must decrease as t increases."""
    pts = [loxodrome_point(t, 135.0) for t in [-3, -1, 0, 1, 3]]
    lons = [p[1] for p in pts]
    assert lons == sorted(lons, reverse=True), "NW spiral should have decreasing longitude"


def test_lat_lon_to_3d_unit_sphere():
    """All (lat, lon) pairs must map to points exactly on the unit sphere."""
    for lat_deg in range(-80, 81, 20):
        for lon_deg in range(0, 360, 45):
            x, y, z = lat_lon_to_3d(math.radians(lat_deg), math.radians(lon_deg))
            r = math.sqrt(x * x + y * y + z * z)
            assert abs(r - 1.0) < 1e-12, \
                f"Point not on unit sphere: lat={lat_deg} lon={lon_deg} r={r}"


def test_lat_lon_to_3d_north_pole():
    """North pole lat=+pi/2 should project to (0, 1, 0) regardless of longitude."""
    x, y, z = lat_lon_to_3d(math.pi / 2, 0.0)
    assert abs(x) < 1e-12 and abs(y - 1.0) < 1e-12 and abs(z) < 1e-12


def test_lat_lon_to_3d_south_pole():
    """South pole lat=-pi/2 should project to (0, -1, 0) regardless of longitude."""
    x, y, z = lat_lon_to_3d(-math.pi / 2, 0.0)
    assert abs(x) < 1e-12 and abs(y + 1.0) < 1e-12 and abs(z) < 1e-12


# ---- Edge cases ----

def test_loxodrome_steep_bearing_stays_finite():
    """Steep bearing (80°, tan≈5.67) over t∈[-4,4] must produce finite coordinates."""
    for t in [-4, -2, 0, 2, 4]:
        lat, lon = loxodrome_point(t, 80.0)
        assert math.isfinite(lat), f"lat not finite at t={t}"
        assert math.isfinite(lon), f"lon not finite at t={t}"
        assert -math.pi / 2 <= lat <= math.pi / 2, f"lat out of range at t={t}"


def test_rot_y_preserves_length():
    """Y-axis rotation must be a rigid transformation (preserve vector length)."""
    pts = [(1, 0, 0), (0, 1, 0), (0.6, 0.8, 0), (0.3, 0.5, 0.7)]
    for p in pts:
        r_in = math.sqrt(sum(c * c for c in p))
        rx, ry, rz = rot_y(*p, 1.23)
        r_out = math.sqrt(rx * rx + ry * ry + rz * rz)
        assert abs(r_in - r_out) < 1e-12, f"Rotation changed length for {p}"


def test_rot_y_full_circle_identity():
    """Rotating by 2π must return the original point."""
    x, y, z = 0.5, 0.3, 0.8
    rx, ry, rz = rot_y(x, y, z, 2 * math.pi)
    assert abs(rx - x) < 1e-12 and abs(ry - y) < 1e-12 and abs(rz - z) < 1e-12


def test_all_bearings_have_distinct_hues():
    """16 equally-spaced bearings must produce 16 distinct integer hue values."""
    n = 16
    bearings = [(k + 0.5) * 11.25 for k in range(n)]
    hues = [int((b * 2) % 360) for b in bearings]
    assert len(set(hues)) == n, f"Hue collisions detected: {hues}"


# ---- No external libraries ----

def test_no_external_scripts_in_index_html():
    """index.html must not load any external JavaScript libraries."""
    html = (PIECE_DIR / "index.html").read_text()
    external = re.findall(r'<script[^>]+src=["\']https?://', html, re.IGNORECASE)
    assert not external, f"External script src found: {external}"


# ---- Explicit failure modes ----

def test_missing_required_field_detected():
    """An entry without 'description' must fail the required-field check."""
    incomplete = {
        "id": "test-missing",
        "title": "Missing Description",
        "tagline": "No description",
        "year": 2026,
        "technique": "canvas",
        "path": "pieces/test-missing",
        "thumbnail": "pieces/test-missing/thumbnail.svg",
    }
    required = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}
    assert not (required <= incomplete.keys()), "Missing 'description' should have been caught"


def test_id_path_mismatch_detected():
    """Detecting when an entry's id does not match its path's directory name."""
    entry = {
        "id": "wrong-id",
        "path": "pieces/correct-id",
    }
    assert entry["id"] != pathlib.Path(entry["path"]).name


def test_loxodrome_equator_crossing():
    """The loxodrome must cross the equator (lat=0) at t=0 for any bearing."""
    for bearing_deg in [22.5, 45.0, 67.5, 112.5, 135.0, 157.5]:
        lat, _ = loxodrome_point(0.0, bearing_deg)
        assert abs(lat) < 1e-12, f"Loxodrome at bearing {bearing_deg}° missed equator at t=0"
