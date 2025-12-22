"""Basic tests for FileSystemUtil directory and file manipulation methods."""

import shutil
import tempfile
from pathlib import Path

import pytest
from morado.common.utils.exceptions import (
    FileExistsError,
    FileNotFoundError,
)
from morado.common.utils.filesystem import FileSystemUtil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


def test_create_directory_basic(temp_dir):
    """Test basic directory creation."""
    new_dir = temp_dir / "test_dir"
    result = FileSystemUtil.create_directory(new_dir)

    assert result.exists()
    assert result.is_dir()
    assert result == new_dir


def test_create_directory_nested(temp_dir):
    """Test nested directory creation with parents=True."""
    nested_dir = temp_dir / "level1" / "level2" / "level3"
    result = FileSystemUtil.create_directory(nested_dir, parents=True)

    assert result.exists()
    assert result.is_dir()


def test_create_directory_exist_ok(temp_dir):
    """Test that exist_ok=True doesn't raise error for existing directory."""
    new_dir = temp_dir / "existing"
    new_dir.mkdir()

    # Should not raise error
    result = FileSystemUtil.create_directory(new_dir, exist_ok=True)
    assert result.exists()


def test_create_directory_exist_not_ok(temp_dir):
    """Test that exist_ok=False raises error for existing directory."""
    new_dir = temp_dir / "existing"
    new_dir.mkdir()

    with pytest.raises(FileExistsError):
        FileSystemUtil.create_directory(new_dir, exist_ok=False)


def test_delete_file(temp_dir):
    """Test deleting a file."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")

    assert test_file.exists()
    FileSystemUtil.delete(test_file)
    assert not test_file.exists()


def test_delete_directory(temp_dir):
    """Test deleting a directory."""
    test_dir = temp_dir / "test_dir"
    test_dir.mkdir()
    (test_dir / "file.txt").write_text("content")

    assert test_dir.exists()
    FileSystemUtil.delete(test_dir)
    assert not test_dir.exists()


def test_delete_missing_ok(temp_dir):
    """Test that missing_ok=True doesn't raise error for non-existent path."""
    non_existent = temp_dir / "does_not_exist.txt"

    # Should not raise error
    FileSystemUtil.delete(non_existent, missing_ok=True)


def test_delete_missing_not_ok(temp_dir):
    """Test that missing_ok=False raises error for non-existent path."""
    non_existent = temp_dir / "does_not_exist.txt"

    with pytest.raises(FileNotFoundError):
        FileSystemUtil.delete(non_existent, missing_ok=False)


def test_copy_file_basic(temp_dir):
    """Test basic file copying."""
    src = temp_dir / "source.txt"
    dst = temp_dir / "dest.txt"
    content = "test content"

    src.write_text(content)
    result = FileSystemUtil.copy_file(src, dst)

    assert result == dst
    assert dst.exists()
    assert dst.read_text() == content
    assert src.exists()  # Source should still exist


def test_copy_file_overwrite_false(temp_dir):
    """Test that overwrite=False raises error when destination exists."""
    src = temp_dir / "source.txt"
    dst = temp_dir / "dest.txt"

    src.write_text("source")
    dst.write_text("dest")

    with pytest.raises(FileExistsError):
        FileSystemUtil.copy_file(src, dst, overwrite=False)


def test_copy_file_overwrite_true(temp_dir):
    """Test that overwrite=True replaces existing destination."""
    src = temp_dir / "source.txt"
    dst = temp_dir / "dest.txt"

    src.write_text("new content")
    dst.write_text("old content")

    FileSystemUtil.copy_file(src, dst, overwrite=True)
    assert dst.read_text() == "new content"


def test_copy_file_source_not_found(temp_dir):
    """Test that copying non-existent source raises error."""
    src = temp_dir / "nonexistent.txt"
    dst = temp_dir / "dest.txt"

    with pytest.raises(FileNotFoundError):
        FileSystemUtil.copy_file(src, dst)


def test_move_file_basic(temp_dir):
    """Test basic file moving."""
    src = temp_dir / "source.txt"
    dst = temp_dir / "dest.txt"
    content = "test content"

    src.write_text(content)
    result = FileSystemUtil.move(src, dst)

    assert result == dst
    assert dst.exists()
    assert dst.read_text() == content
    assert not src.exists()  # Source should not exist after move


def test_move_directory(temp_dir):
    """Test moving a directory."""
    src = temp_dir / "src_dir"
    dst = temp_dir / "dst_dir"

    src.mkdir()
    (src / "file.txt").write_text("content")

    FileSystemUtil.move(src, dst)

    assert dst.exists()
    assert (dst / "file.txt").exists()
    assert not src.exists()


def test_move_overwrite_false(temp_dir):
    """Test that overwrite=False raises error when destination exists."""
    src = temp_dir / "source.txt"
    dst = temp_dir / "dest.txt"

    src.write_text("source")
    dst.write_text("dest")

    with pytest.raises(FileExistsError):
        FileSystemUtil.move(src, dst, overwrite=False)


def test_move_overwrite_true(temp_dir):
    """Test that overwrite=True replaces existing destination."""
    src = temp_dir / "source.txt"
    dst = temp_dir / "dest.txt"

    src.write_text("new content")
    dst.write_text("old content")

    FileSystemUtil.move(src, dst, overwrite=True)
    assert dst.read_text() == "new content"
    assert not src.exists()


def test_list_files_basic(temp_dir):
    """Test basic file listing."""
    (temp_dir / "file1.txt").write_text("content1")
    (temp_dir / "file2.txt").write_text("content2")
    (temp_dir / "subdir").mkdir()

    files = FileSystemUtil.list_files(temp_dir)

    assert len(files) == 2
    assert all(f.is_file() for f in files)


def test_list_files_with_pattern(temp_dir):
    """Test file listing with pattern filter."""
    (temp_dir / "file1.txt").write_text("content1")
    (temp_dir / "file2.py").write_text("content2")
    (temp_dir / "file3.txt").write_text("content3")

    txt_files = FileSystemUtil.list_files(temp_dir, pattern="*.txt")

    assert len(txt_files) == 2
    assert all(f.suffix == ".txt" for f in txt_files)


def test_list_files_recursive(temp_dir):
    """Test recursive file listing."""
    (temp_dir / "file1.txt").write_text("content1")
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "file2.txt").write_text("content2")

    files = FileSystemUtil.list_files(temp_dir, recursive=True)

    assert len(files) == 2


def test_list_files_recursive_with_pattern(temp_dir):
    """Test recursive file listing with pattern."""
    (temp_dir / "file1.txt").write_text("content1")
    (temp_dir / "file2.py").write_text("content2")
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("content3")
    (subdir / "file4.py").write_text("content4")

    txt_files = FileSystemUtil.list_files(temp_dir, pattern="*.txt", recursive=True)

    assert len(txt_files) == 2
    assert all(f.suffix == ".txt" for f in txt_files)


def test_list_files_not_directory(temp_dir):
    """Test that listing files on a non-directory raises error."""
    test_file = temp_dir / "file.txt"
    test_file.write_text("content")

    with pytest.raises(NotADirectoryError):
        FileSystemUtil.list_files(test_file)


def test_invalid_input_validation():
    """Test that invalid inputs raise ValueError."""
    with pytest.raises(ValueError):
        FileSystemUtil.create_directory(None)

    with pytest.raises(ValueError):
        FileSystemUtil.create_directory("")

    with pytest.raises(ValueError):
        FileSystemUtil.delete(None)

    with pytest.raises(ValueError):
        FileSystemUtil.copy_file(None, "/tmp/dest")

    with pytest.raises(ValueError):
        FileSystemUtil.copy_file("/tmp/src", None)

    with pytest.raises(ValueError):
        FileSystemUtil.move(None, "/tmp/dest")

    with pytest.raises(ValueError):
        FileSystemUtil.list_files("")
