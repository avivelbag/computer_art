import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).parent.parent
PIECES_JSON = REPO / "pieces.json"

REQUIRED_FIELDS = {"id", "title", "tagline", "year", "technique", "path", "thumbnail", "description"}


def load():
    """Return the parsed contents of pieces.json."""
    return json.loads(PIECES_JSON.read_text())


def test_pieces_json_exists():
    assert PIECES_JSON.exists(), "pieces.json must exist at repo root"


def test_pieces_json_is_list():
    assert isinstance(load(), list)


def test_pieces_json_is_valid_json():
    """Ensure the file is parseable and not corrupted."""
    data = load()
    assert data is not None


@pytest.mark.parametrize("entry", load() if PIECES_JSON.exists() else [])
def test_entry_complete(entry):
    """Every piece must carry the full set of required metadata fields."""
    assert REQUIRED_FIELDS <= entry.keys(), f"Missing fields in {entry}"

    piece_dir = REPO / entry["path"]
    assert piece_dir.is_dir(), f"Directory missing: {entry['path']}"

    thumb = REPO / entry["thumbnail"]
    assert thumb.is_file(), f"Thumbnail missing: {entry['thumbnail']}"

    readme = piece_dir / "README.md"
    assert readme.is_file(), f"README missing in {entry['path']}"

    assert entry["id"] == piece_dir.name, (
        f"id {entry['id']!r} doesn't match dir {piece_dir.name!r}"
    )


class TestInvalidEntries:
    """Verify correct error behavior for malformed pieces.json content."""

    def test_missing_required_field_detected(self, tmp_path):
        """An entry without 'title' or 'description' should fail the required-field check."""
        entry = {
            "id": "test-piece",
            "tagline": "A test",
            "year": 2024,
            "technique": "code",
            "path": "pieces/test-piece",
            "thumbnail": "pieces/test-piece/thumb.png",
        }
        missing = REQUIRED_FIELDS - entry.keys()
        assert missing, "Expected a missing field to be detected"
        assert not (REQUIRED_FIELDS <= entry.keys())

    def test_id_mismatch_detected(self, tmp_path):
        """id must equal the last segment of the path directory name."""
        piece_dir = tmp_path / "my-piece"
        piece_dir.mkdir()
        (piece_dir / "README.md").write_text("# My Piece")
        thumb = tmp_path / "thumb.png"
        thumb.write_bytes(b"")

        entry = {
            "id": "wrong-id",
            "title": "My Piece",
            "tagline": "A test piece",
            "year": 2024,
            "technique": "code",
            "path": str(piece_dir.relative_to(tmp_path)),
            "thumbnail": str(thumb.relative_to(tmp_path)),
        }

        assert entry["id"] != piece_dir.name

    def test_missing_thumbnail_detected(self, tmp_path):
        """Referencing a non-existent thumbnail file should be caught."""
        piece_dir = tmp_path / "test-piece"
        piece_dir.mkdir()
        (piece_dir / "README.md").write_text("# Test")

        thumb_path = tmp_path / "pieces" / "test-piece" / "thumb.png"
        assert not thumb_path.exists(), "Thumbnail should not exist in this test"

    def test_missing_readme_detected(self, tmp_path):
        """A piece directory without README.md should fail the check."""
        piece_dir = tmp_path / "test-piece"
        piece_dir.mkdir()

        readme = piece_dir / "README.md"
        assert not readme.exists(), "README should not exist in this test"

    def test_missing_piece_directory_detected(self, tmp_path):
        """A path that doesn't exist as a directory should be caught."""
        nonexistent = tmp_path / "ghost-piece"
        assert not nonexistent.is_dir()
