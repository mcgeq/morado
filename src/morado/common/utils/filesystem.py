"""Cross-platform file system utility module.

This module provides the FileSystemUtil class with static methods for common
file system operations that work consistently across Windows, Linux, and macOS.
"""

from pathlib import Path
from typing import Union, List, Optional
from datetime import datetime
import shutil

from .exceptions import FileSystemError, FileNotFoundError as CustomFileNotFoundError, FileExistsError as CustomFileExistsError


PathLike = Union[str, Path]


class FileSystemUtil:
    """Cross-platform file system utility class.
    
    This class provides static methods for common file system operations,
    using pathlib.Path internally to ensure cross-platform compatibility.
    
    Example:
        >>> from morado.common.utils.filesystem import FileSystemUtil
        >>> FileSystemUtil.exists("/path/to/file")
        True
        >>> size = FileSystemUtil.get_size("/path/to/file")
        >>> print(f"File size: {size} bytes")
    """
    
    @staticmethod
    def exists(path: PathLike) -> bool:
        """Check if a path exists in the file system.
        
        Args:
            path: Path to check (string or Path object)
            
        Returns:
            True if the path exists, False otherwise
            
        Example:
            >>> FileSystemUtil.exists("/tmp/myfile.txt")
            True
            >>> FileSystemUtil.exists("/nonexistent/path")
            False
        """
        return Path(path).exists()
    
    @staticmethod
    def get_size(path: PathLike) -> int:
        """Get the size of a file in bytes.
        
        Args:
            path: Path to the file (string or Path object)
            
        Returns:
            File size in bytes (non-negative integer)
            
        Raises:
            FileNotFoundError: If the file does not exist
            IsADirectoryError: If the path is a directory
            
        Example:
            >>> size = FileSystemUtil.get_size("/tmp/myfile.txt")
            >>> print(f"File is {size} bytes")
            File is 1024 bytes
        """
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        if path_obj.is_dir():
            raise IsADirectoryError(f"Path is a directory, not a file: {path}")
        return path_obj.stat().st_size
    
    @staticmethod
    def get_modified_time(path: PathLike) -> datetime:
        """Get the last modification time of a file or directory.
        
        Args:
            path: Path to the file or directory (string or Path object)
            
        Returns:
            Datetime object representing the last modification time (timezone-aware, UTC)
            
        Raises:
            FileNotFoundError: If the path does not exist
            
        Example:
            >>> mod_time = FileSystemUtil.get_modified_time("/tmp/myfile.txt")
            >>> print(f"Last modified: {mod_time}")
            Last modified: 2024-01-15 10:30:45+00:00
        """
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        timestamp = path_obj.stat().st_mtime
        return datetime.fromtimestamp(timestamp, tz=datetime.now().astimezone().tzinfo)
    
    @staticmethod
    def get_extension(path: PathLike) -> str:
        """Get the file extension from a path.
        
        Args:
            path: Path to extract extension from (string or Path object)
            
        Returns:
            File extension including the dot (e.g., '.txt', '.py')
            Returns empty string if no extension
            
        Example:
            >>> FileSystemUtil.get_extension("/path/to/file.txt")
            '.txt'
            >>> FileSystemUtil.get_extension("/path/to/file")
            ''
        """
        return Path(path).suffix
    
    @staticmethod
    def get_directory(path: PathLike) -> Path:
        """Get the parent directory of a path.
        
        Args:
            path: Path to extract directory from (string or Path object)
            
        Returns:
            Path object representing the parent directory
            
        Example:
            >>> FileSystemUtil.get_directory("/path/to/file.txt")
            PosixPath('/path/to')
            >>> FileSystemUtil.get_directory("/path/to/dir/")
            PosixPath('/path/to')
        """
        return Path(path).parent
    
    @staticmethod
    def get_absolute_path(path: PathLike) -> Path:
        """Get the absolute path from a relative or absolute path.
        
        Args:
            path: Path to convert (string or Path object)
            
        Returns:
            Path object representing the absolute path
            
        Example:
            >>> FileSystemUtil.get_absolute_path("./relative/path")
            PosixPath('/current/working/dir/relative/path')
            >>> FileSystemUtil.get_absolute_path("/already/absolute")
            PosixPath('/already/absolute')
        """
        return Path(path).resolve()
    
    @staticmethod
    def join_path(*parts: PathLike) -> Path:
        """Join multiple path components into a single path.
        
        Args:
            *parts: Variable number of path components (strings or Path objects)
            
        Returns:
            Path object representing the joined path
            
        Example:
            >>> FileSystemUtil.join_path("/base", "subdir", "file.txt")
            PosixPath('/base/subdir/file.txt')
            >>> FileSystemUtil.join_path("relative", "path", "to", "file")
            PosixPath('relative/path/to/file')
        """
        if not parts:
            return Path()
        
        base = Path(parts[0])
        for part in parts[1:]:
            base = base / part
        return base
    
    @staticmethod
    def create_directory(path: PathLike, parents: bool = True, exist_ok: bool = True) -> Path:
        """Create a directory, optionally creating parent directories.
        
        Args:
            path: Path to the directory to create (string or Path object)
            parents: If True, create parent directories as needed (default: True)
            exist_ok: If True, don't raise an error if directory already exists (default: True)
            
        Returns:
            Path object representing the created directory
            
        Raises:
            FileExistsError: If directory exists and exist_ok is False
            FileSystemError: If directory creation fails
            ValueError: If path is None or empty string
            
        Example:
            >>> FileSystemUtil.create_directory("/tmp/new/nested/dir")
            PosixPath('/tmp/new/nested/dir')
            >>> FileSystemUtil.create_directory("/tmp/existing", exist_ok=True)
            PosixPath('/tmp/existing')
        """
        if path is None or (isinstance(path, str) and not path.strip()):
            raise ValueError("Path cannot be None or empty string")
        
        path_obj = Path(path)
        
        try:
            if path_obj.exists() and not exist_ok:
                raise CustomFileExistsError(str(path))
            
            path_obj.mkdir(parents=parents, exist_ok=exist_ok)
            return path_obj
        except OSError as e:
            raise FileSystemError(f"Failed to create directory '{path}': {e}") from e
    
    @staticmethod
    def delete(path: PathLike, missing_ok: bool = True) -> None:
        """Delete a file or directory.
        
        Args:
            path: Path to the file or directory to delete (string or Path object)
            missing_ok: If True, don't raise an error if path doesn't exist (default: True)
            
        Raises:
            FileNotFoundError: If path doesn't exist and missing_ok is False
            FileSystemError: If deletion fails
            ValueError: If path is None or empty string
            
        Example:
            >>> FileSystemUtil.delete("/tmp/file.txt")
            >>> FileSystemUtil.delete("/tmp/directory", missing_ok=True)
        """
        if path is None or (isinstance(path, str) and not path.strip()):
            raise ValueError("Path cannot be None or empty string")
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            if not missing_ok:
                raise CustomFileNotFoundError(str(path))
            return
        
        try:
            if path_obj.is_dir():
                shutil.rmtree(path_obj)
            else:
                path_obj.unlink()
        except OSError as e:
            raise FileSystemError(f"Failed to delete '{path}': {e}") from e
    
    @staticmethod
    def copy_file(src: PathLike, dst: PathLike, overwrite: bool = False) -> Path:
        """Copy a file from source to destination.
        
        Args:
            src: Source file path (string or Path object)
            dst: Destination file path (string or Path object)
            overwrite: If True, overwrite destination if it exists (default: False)
            
        Returns:
            Path object representing the destination file
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            FileExistsError: If destination exists and overwrite is False
            FileSystemError: If copy operation fails
            ValueError: If src or dst is None or empty string
            IsADirectoryError: If source is a directory
            
        Example:
            >>> FileSystemUtil.copy_file("/tmp/source.txt", "/tmp/dest.txt")
            PosixPath('/tmp/dest.txt')
            >>> FileSystemUtil.copy_file("/tmp/file.txt", "/tmp/copy.txt", overwrite=True)
            PosixPath('/tmp/copy.txt')
        """
        if src is None or (isinstance(src, str) and not src.strip()):
            raise ValueError("Source path cannot be None or empty string")
        if dst is None or (isinstance(dst, str) and not dst.strip()):
            raise ValueError("Destination path cannot be None or empty string")
        
        src_obj = Path(src)
        dst_obj = Path(dst)
        
        if not src_obj.exists():
            raise CustomFileNotFoundError(str(src))
        
        if src_obj.is_dir():
            raise IsADirectoryError(f"Source is a directory, not a file: {src}")
        
        if dst_obj.exists() and not overwrite:
            raise CustomFileExistsError(str(dst))
        
        try:
            shutil.copy2(src_obj, dst_obj)
            return dst_obj
        except OSError as e:
            raise FileSystemError(f"Failed to copy '{src}' to '{dst}': {e}") from e
    
    @staticmethod
    def move(src: PathLike, dst: PathLike, overwrite: bool = False) -> Path:
        """Move a file or directory from source to destination.
        
        Args:
            src: Source path (string or Path object)
            dst: Destination path (string or Path object)
            overwrite: If True, overwrite destination if it exists (default: False)
            
        Returns:
            Path object representing the destination path
            
        Raises:
            FileNotFoundError: If source doesn't exist
            FileExistsError: If destination exists and overwrite is False
            FileSystemError: If move operation fails
            ValueError: If src or dst is None or empty string
            
        Example:
            >>> FileSystemUtil.move("/tmp/old.txt", "/tmp/new.txt")
            PosixPath('/tmp/new.txt')
            >>> FileSystemUtil.move("/tmp/dir1", "/tmp/dir2", overwrite=True)
            PosixPath('/tmp/dir2')
        """
        if src is None or (isinstance(src, str) and not src.strip()):
            raise ValueError("Source path cannot be None or empty string")
        if dst is None or (isinstance(dst, str) and not dst.strip()):
            raise ValueError("Destination path cannot be None or empty string")
        
        src_obj = Path(src)
        dst_obj = Path(dst)
        
        if not src_obj.exists():
            raise CustomFileNotFoundError(str(src))
        
        if dst_obj.exists() and not overwrite:
            raise CustomFileExistsError(str(dst))
        
        try:
            # If destination exists and overwrite is True, remove it first
            if dst_obj.exists() and overwrite:
                if dst_obj.is_dir():
                    shutil.rmtree(dst_obj)
                else:
                    dst_obj.unlink()
            
            shutil.move(str(src_obj), str(dst_obj))
            return dst_obj
        except OSError as e:
            raise FileSystemError(f"Failed to move '{src}' to '{dst}': {e}") from e
    
    @staticmethod
    def list_files(directory: PathLike, pattern: Optional[str] = None, recursive: bool = False) -> List[Path]:
        """List files in a directory with optional filtering.
        
        Args:
            directory: Directory path to list files from (string or Path object)
            pattern: Optional glob pattern to filter files (e.g., "*.txt", "**/*.py")
            recursive: If True, search recursively in subdirectories (default: False)
            
        Returns:
            List of Path objects representing the matching files
            
        Raises:
            FileNotFoundError: If directory doesn't exist
            FileSystemError: If listing operation fails
            ValueError: If directory is None or empty string
            NotADirectoryError: If path is not a directory
            
        Example:
            >>> FileSystemUtil.list_files("/tmp")
            [PosixPath('/tmp/file1.txt'), PosixPath('/tmp/file2.py')]
            >>> FileSystemUtil.list_files("/tmp", pattern="*.txt")
            [PosixPath('/tmp/file1.txt')]
            >>> FileSystemUtil.list_files("/tmp", pattern="**/*.py", recursive=True)
            [PosixPath('/tmp/subdir/file.py')]
        """
        if directory is None or (isinstance(directory, str) and not directory.strip()):
            raise ValueError("Directory path cannot be None or empty string")
        
        dir_obj = Path(directory)
        
        if not dir_obj.exists():
            raise CustomFileNotFoundError(str(directory))
        
        if not dir_obj.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")
        
        try:
            if pattern:
                if recursive:
                    # Use rglob for recursive pattern matching
                    return [p for p in dir_obj.rglob(pattern) if p.is_file()]
                else:
                    # Use glob for non-recursive pattern matching
                    return [p for p in dir_obj.glob(pattern) if p.is_file()]
            else:
                if recursive:
                    # List all files recursively
                    return [p for p in dir_obj.rglob("*") if p.is_file()]
                else:
                    # List all files in directory (non-recursive)
                    return [p for p in dir_obj.iterdir() if p.is_file()]
        except OSError as e:
            raise FileSystemError(f"Failed to list files in '{directory}': {e}") from e
