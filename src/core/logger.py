"""Logging configuration for MBI project."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

from src.core.config import PROJECT_ROOT, IST


# Custom theme for rich console
CUSTOM_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
})

# Console for rich output
console = Console(theme=CUSTOM_THEME)


def setup_logger(
    name: str = "mbi",
    level: int = logging.INFO,
    log_to_file: bool = True,
) -> logging.Logger:
    """
    Setup logger with rich console output and optional file logging.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_to_file: Whether to also log to file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Rich console handler
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        show_time=True,
        show_path=True,
    )
    console_handler.setLevel(level)
    
    # Format for console
    console_format = "%(message)s"
    console_handler.setFormatter(logging.Formatter(console_format))
    
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        log_dir = PROJECT_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create log file with IST timestamp
        timestamp = datetime.now(IST).strftime("%Y%m%d")
        log_file = log_dir / f"mbi_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        
        # Format for file (more detailed)
        file_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        file_handler.setFormatter(logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S"))
        
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "mbi") -> logging.Logger:
    """
    Get existing logger or create new one.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        logger = setup_logger(name)
    
    return logger


# Convenience functions for pretty printing
def print_success(message: str) -> None:
    """Print success message in green."""
    console.print(f"✓ {message}", style="success")


def print_error(message: str) -> None:
    """Print error message in red."""
    console.print(f"✗ {message}", style="error")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    console.print(f"⚠ {message}", style="warning")


def print_info(message: str) -> None:
    """Print info message in cyan."""
    console.print(f"ℹ {message}", style="info")


def print_header(title: str) -> None:
    """Print a formatted header."""
    console.rule(f"[bold cyan]{title}[/bold cyan]")


def print_separator() -> None:
    """Print a separator line."""
    console.print("─" * console.width)


# Create default logger
logger = setup_logger()
