"""Directory listing tool."""

import os
from pathlib import Path
from typing import Optional

from agent.tools.base import Tool
from agent.config import Config, get_config


class Directory(Tool):
    """Tool for listing directory contents."""

    def __init__(self, base_path: Optional[str] = None, config: Optional[Config] = None):
        """Initialize Directory tool.

        Args:
            base_path: Base directory for access (if None, reads from config)
            config: Config instance (if None, uses global config)
        """
        super().__init__()

        # Get configuration
        if config is None:
            config = get_config()

        self.name = "Directory"
        self.description = (
            "Lists files and subdirectories in a directory. "
            "If no path is provided, lists the current directory."
        )
        self.parameters = {
            "path": {
                "type": "string",
                "description": "Directory path to list (default: current directory)",
                "required": False,
            }
        }
        self.base_path = Path(base_path or config.directory_base_path).resolve()

    def execute(self, path: str = ".", **kwargs) -> str:
        """List directory contents.

        Args:
            path: Directory path to list (default: current directory)

        Returns:
            Formatted list of files and directories, or error message
        """
        try:
            target_path = Path(path).resolve()

            # Security check: ensure path is within allowed base path
            if not self._is_safe_path(target_path):
                return f"Error: Access denied - directory is outside allowed path"

            # Check if path exists
            if not target_path.exists():
                return f"Error: Directory not found - {path}"

            # Check if it's a directory
            if not target_path.is_dir():
                return f"Error: Path is not a directory - {path}"

            # List contents
            items = []
            try:
                for item in sorted(target_path.iterdir()):
                    item_type = "DIR " if item.is_dir() else "FILE"
                    item_name = item.name
                    if item.is_file():
                        size = item.stat().st_size
                        size_str = self._format_size(size)
                        items.append(f"{item_type} {item_name:40s} {size_str:>10s}")
                    else:
                        items.append(f"{item_type} {item_name}/")
            except PermissionError:
                return f"Error: Permission denied - cannot list {path}"

            if not items:
                return f"Directory is empty: {target_path}"

            header = f"Contents of {target_path}:\n" + "=" * 60
            return header + "\n" + "\n".join(items)

        except Exception as e:
            return f"Error: Failed to list directory - {str(e)}"

    def _is_safe_path(self, target_path: Path) -> bool:
        """Check if target path is within allowed base path.

        Args:
            target_path: Path to check

        Returns:
            True if path is safe, False otherwise
        """
        try:
            target_path.relative_to(self.base_path)
            return True
        except ValueError:
            return False

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format.

        Args:
            size: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
