"""File management utilities."""

from __future__ import annotations

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from src.core.config import RAW_STOCKS_DIR, RAW_DAILY_DIR, PROCESSED_DIR, META_DIR, PROJECT_ROOT
from src.core.logger import get_logger


logger = get_logger(__name__)


def ensure_directories() -> None:
    """
    Ensure all required directories exist.
    """
    directories = [
        RAW_STOCKS_DIR,
        RAW_DAILY_DIR,
        PROCESSED_DIR,
        META_DIR,
        PROJECT_ROOT / "logs",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
    
    logger.info("All required directories are ready")


def clean_old_files(directory: Path, days_old: int = 90) -> None:
    """
    Clean files older than specified days.
    
    Args:
        directory: Directory to clean
        days_old: Files older than this will be deleted
    """
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    deleted_count = 0
    
    for file in directory.glob("*"):
        if file.is_file():
            # Get file modification time
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            
            if mtime < cutoff_date:
                try:
                    file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old file: {file}")
                except Exception as e:
                    logger.warning(f"Failed to delete {file}: {str(e)}")
    
    if deleted_count > 0:
        logger.info(f"Cleaned {deleted_count} files older than {days_old} days from {directory}")


def backup_file(filepath: Path, backup_dir: Path | None = None) -> Path | None:
    """
    Create a backup of a file.
    
    Args:
        filepath: File to backup
        backup_dir: Directory to store backup (default: same directory)
        
    Returns:
        Path to backup file, or None if backup failed
    """
    if not filepath.exists():
        logger.warning(f"Cannot backup non-existent file: {filepath}")
        return None
    
    if backup_dir is None:
        backup_dir = filepath.parent
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filepath.stem}_{timestamp}{filepath.suffix}"
    backup_path = backup_dir / backup_name
    
    try:
        shutil.copy2(filepath, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        return None


def get_file_size(filepath: Path) -> int:
    """
    Get file size in bytes.
    
    Args:
        filepath: File to check
        
    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    if not filepath.exists():
        return 0
    
    return filepath.stat().st_size


def get_file_size_human(filepath: Path) -> str:
    """
    Get human-readable file size.
    
    Args:
        filepath: File to check
        
    Returns:
        File size as string (e.g., "1.5 MB")
    """
    size = get_file_size(filepath)
    
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    
    return f"{size:.2f} TB"


def count_files(directory: Path, pattern: str = "*") -> int:
    """
    Count files in a directory.
    
    Args:
        directory: Directory to count files in
        pattern: Glob pattern for files to count
        
    Returns:
        Number of files matching pattern
    """
    if not directory.exists():
        return 0
    
    return len(list(directory.glob(pattern)))


def get_directory_size(directory: Path) -> int:
    """
    Get total size of all files in a directory.
    
    Args:
        directory: Directory to check
        
    Returns:
        Total size in bytes
    """
    if not directory.exists():
        return 0
    
    total_size = 0
    
    for file in directory.rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size
    
    return total_size


def get_directory_size_human(directory: Path) -> str:
    """
    Get human-readable directory size.
    
    Args:
        directory: Directory to check
        
    Returns:
        Directory size as string
    """
    size = get_directory_size(directory)
    
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    
    return f"{size:.2f} TB"


def create_gitkeep(directory: Path) -> None:
    """
    Create .gitkeep file in directory to track empty directories in git.
    
    Args:
        directory: Directory to create .gitkeep in
    """
    directory.mkdir(parents=True, exist_ok=True)
    gitkeep = directory / ".gitkeep"
    gitkeep.touch()
    logger.debug(f"Created .gitkeep in {directory}")
