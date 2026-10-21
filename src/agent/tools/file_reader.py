"""File reader tool for reading file contents."""

import os
from pathlib import Path

from agent.tools.base import Tool


class FileReader(Tool):
    """Tool for reading file contents."""

    def __init__(self, base_path: str = "."):
        """Initialize FileReader.

        Args:
            base_path: Base directory for file access (security constraint)
        """
        super().__init__()
        self.name = "FileReader"
        self.description = (
            "Reads the contents of a file. Provide the file path relative to "
            "the current directory or as an absolute path."
        )
        self.parameters = {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read",
                "required": True,
            }
        }
        self.base_path = Path(base_path).resolve()

    def execute(self, file_path: str = "", **kwargs) -> str:
        """Read and return file contents.

        Args:
            file_path: Path to the file to read

        Returns:
            File contents as a string, or error message
        """
        if not file_path:
            return "Error: No file path provided"

        try:
            target_path = Path(file_path).resolve()

            # Security check: ensure file is within allowed base path
            if not self._is_safe_path(target_path):
                return f"Error: Access denied - file is outside allowed directory"

            # Check if file exists
            if not target_path.exists():
                return f"Error: File not found - {file_path}"

            # Check if it's a file (not a directory)
            if not target_path.is_file():
                return f"Error: Path is not a file - {file_path}"

            # Read the file
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Limit output size for very large files
            max_size = 10000  # characters
            if len(content) > max_size:
                content = content[:max_size] + f"\n\n[... truncated, file is too large ({len(content)} chars)]"

            return content

        except PermissionError:
            return f"Error: Permission denied - cannot read {file_path}"
        except UnicodeDecodeError:
            return f"Error: Cannot read file - file is not text or uses unsupported encoding"
        except Exception as e:
            return f"Error: Failed to read file - {str(e)}"

    def _is_safe_path(self, target_path: Path) -> bool:
        """Check if target path is within allowed base path.

        Args:
            target_path: Path to check

        Returns:
            True if path is safe, False otherwise
        """
        try:
            # Check if target is within base_path
            target_path.relative_to(self.base_path)
            return True
        except ValueError:
            # Path is outside base_path
            return False
