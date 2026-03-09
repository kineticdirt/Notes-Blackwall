"""
Safe file handling utilities.
"""
import os
import stat
from pathlib import Path
from typing import Optional


class SafePathHandler:
    """Safe file path handling."""
    
    @staticmethod
    def validate_and_resolve(path: str, base: Path,
                            follow_symlinks: bool = False) -> Path:
        """
        Validate and resolve path relative to base directory.
        
        Args:
            path: Relative path string
            base: Base directory (must be absolute)
            follow_symlinks: Whether to follow symlinks (default: False)
        
        Returns:
            Resolved Path object
        
        Raises:
            ValueError: If path is invalid or outside base
        """
        # Ensure base is absolute
        base = base.resolve()
        
        # Validate input
        if not isinstance(path, str):
            raise ValueError('Path must be a string')
        
        # Reject empty path
        if not path:
            raise ValueError('Path cannot be empty')
        
        # Reject absolute paths
        if os.path.isabs(path):
            raise ValueError('Absolute paths not allowed')
        
        # Reject path traversal
        if '..' in path or path.startswith('../'):
            raise ValueError('Path traversal not allowed')
        
        # Reject control characters (except tab, newline, carriage return)
        if any(ord(c) < 32 and c not in '\t\n\r' for c in path):
            raise ValueError('Control characters not allowed')
        
        # Reject null bytes
        if '\x00' in path:
            raise ValueError('Null bytes not allowed')
        
        # Join and resolve
        joined = base / path
        
        if follow_symlinks:
            resolved = joined.resolve()
        else:
            # Resolve without following symlinks
            resolved = Path(os.path.normpath(str(joined)))
            # Check if any component is a symlink
            parts = resolved.parts
            current = base
            for part in parts[len(base.parts):]:
                current = current / part
                if current.is_symlink():
                    raise ValueError(f'Symlink not allowed: {current}')
        
        # Ensure resolved path is within base
        try:
            resolved.relative_to(base)
        except ValueError:
            raise ValueError(f'Path outside base directory: {path}')
        
        return resolved
    
    @staticmethod
    def safe_write(file_path: Path, content: bytes,
                  mode: int = 0o600) -> None:
        """
        Atomic file write with safe permissions.
        
        Args:
            file_path: Target file path
            content: Content to write
            mode: File permissions (default: 0600)
        
        Raises:
            OSError: If write fails
        """
        # Create parent directories with safe permissions
        file_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        # Write to temp file
        temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(content)
            os.chmod(temp_path, mode)
            
            # Atomic rename
            temp_path.replace(file_path)
        except Exception:
            # Cleanup on error
            if temp_path.exists():
                temp_path.unlink()
            raise
    
    @staticmethod
    def safe_read(file_path: Path, max_size: int = 10 * 1024 * 1024) -> bytes:
        """
        Safe file read with size limits.
        
        Args:
            file_path: File to read
            max_size: Maximum file size in bytes (default: 10MB)
        
        Returns:
            File content
        
        Raises:
            ValueError: If file is too large
            FileNotFoundError: If file doesn't exist
        """
        # Check file exists
        if not file_path.exists():
            raise FileNotFoundError(f'File not found: {file_path}')
        
        # Check file size
        stat_info = file_path.stat()
        if stat_info.st_size > max_size:
            raise ValueError(f'File too large: {stat_info.st_size} bytes (max: {max_size})')
        
        # Read file
        with open(file_path, 'rb') as f:
            return f.read()
    
    @staticmethod
    def set_safe_permissions(path: Path, is_dir: bool = False) -> None:
        """
        Set safe file permissions.
        
        Args:
            path: File or directory path
            is_dir: True if path is a directory
        """
        if is_dir:
            os.chmod(path, 0o700)  # rwx------
        else:
            os.chmod(path, 0o600)  # rw-------
