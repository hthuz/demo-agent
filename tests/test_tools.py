"""Unit tests for tools."""

import pytest
import tempfile
import os
from pathlib import Path

from agent.tools import Calculator, FileReader, Directory, FinalAnswer, ToolRegistry


class TestCalculator:
    """Test Calculator tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = Calculator()

    def test_basic_addition(self):
        """Test basic addition."""
        result = self.calculator.execute(math_expression="2 + 3")
        assert result == "5"

    def test_complex_expression(self):
        """Test complex mathematical expression."""
        result = self.calculator.execute(math_expression="(12 + 8) * 3")
        assert result == "60"

    def test_division(self):
        """Test division."""
        result = self.calculator.execute(math_expression="20 / 4")
        assert result == "5.0"

    def test_division_by_zero(self):
        """Test division by zero error handling."""
        result = self.calculator.execute(math_expression="10 / 0")
        assert "Error" in result
        assert "zero" in result.lower()

    def test_power_operation(self):
        """Test power operation."""
        result = self.calculator.execute(math_expression="2 ** 3")
        assert result == "8"

    def test_invalid_expression(self):
        """Test invalid expression handling."""
        result = self.calculator.execute(math_expression="2 +")
        assert "Error" in result

    def test_empty_expression(self):
        """Test empty expression."""
        result = self.calculator.execute(math_expression="")
        assert "Error" in result

    def test_modulo_operation(self):
        """Test modulo operation."""
        result = self.calculator.execute(math_expression="10 % 3")
        assert result == "1"


class TestFileReader:
    """Test FileReader tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.file_reader = FileReader(base_path=self.temp_dir)

    def test_read_existing_file(self):
        """Test reading an existing file."""
        # Create a test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)

        result = self.file_reader.execute(file_path=str(test_file))
        assert result == test_content

    def test_read_nonexistent_file(self):
        """Test reading a non-existent file."""
        # Use a path within the temp_dir to pass security check
        nonexistent_path = str(Path(self.temp_dir) / "nonexistent.txt")
        result = self.file_reader.execute(file_path=nonexistent_path)
        assert "Error" in result
        assert "not found" in result.lower()

    def test_read_directory_as_file(self):
        """Test trying to read a directory as a file."""
        result = self.file_reader.execute(file_path=self.temp_dir)
        assert "Error" in result
        assert "not a file" in result.lower()

    def test_empty_file_path(self):
        """Test with empty file path."""
        result = self.file_reader.execute(file_path="")
        assert "Error" in result

    def test_file_with_multiline_content(self):
        """Test reading a file with multiple lines."""
        test_file = Path(self.temp_dir) / "multiline.txt"
        test_content = "Line 1\nLine 2\nLine 3"
        test_file.write_text(test_content)

        result = self.file_reader.execute(file_path=str(test_file))
        assert result == test_content

    def test_large_file_truncation(self):
        """Test that large files are truncated."""
        test_file = Path(self.temp_dir) / "large.txt"
        test_content = "x" * 15000  # Larger than 10000 char limit
        test_file.write_text(test_content)

        result = self.file_reader.execute(file_path=str(test_file))
        assert "truncated" in result.lower()
        assert len(result) < len(test_content)


class TestDirectory:
    """Test Directory tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.directory = Directory(base_path=self.temp_dir)

    def test_list_directory_with_files(self):
        """Test listing a directory with files."""
        # Create some test files
        (Path(self.temp_dir) / "file1.txt").write_text("content1")
        (Path(self.temp_dir) / "file2.txt").write_text("content2")

        result = self.directory.execute(path=self.temp_dir)
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "FILE" in result

    def test_list_directory_with_subdirs(self):
        """Test listing a directory with subdirectories."""
        # Create a subdirectory
        subdir = Path(self.temp_dir) / "subdir"
        subdir.mkdir()

        result = self.directory.execute(path=self.temp_dir)
        assert "subdir" in result
        assert "DIR" in result

    def test_list_empty_directory(self):
        """Test listing an empty directory."""
        result = self.directory.execute(path=self.temp_dir)
        assert "empty" in result.lower()

    def test_list_nonexistent_directory(self):
        """Test listing a non-existent directory."""
        # Use a path within the temp_dir to pass security check
        nonexistent_path = str(Path(self.temp_dir) / "nonexistent")
        result = self.directory.execute(path=nonexistent_path)
        assert "Error" in result
        assert "not found" in result.lower()

    def test_list_file_as_directory(self):
        """Test trying to list a file as a directory."""
        test_file = Path(self.temp_dir) / "file.txt"
        test_file.write_text("content")

        result = self.directory.execute(path=str(test_file))
        assert "Error" in result
        assert "not a directory" in result.lower()

    def test_default_current_directory(self):
        """Test listing with default current directory."""
        # Use the temp_dir as the default path
        result = self.directory.execute(path=self.temp_dir)
        # Should work without error
        assert "Error" not in result or "Contents of" in result


class TestFinalAnswer:
    """Test FinalAnswer tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.final_answer = FinalAnswer()

    def test_return_answer(self):
        """Test returning a final answer."""
        answer = "The answer is 42"
        result = self.final_answer.execute(answer=answer)
        assert result == answer

    def test_empty_answer(self):
        """Test with empty answer."""
        result = self.final_answer.execute(answer="")
        assert "Error" in result

    def test_multiline_answer(self):
        """Test with multiline answer."""
        answer = "Line 1\nLine 2\nLine 3"
        result = self.final_answer.execute(answer=answer)
        assert result == answer


class TestToolRegistry:
    """Test ToolRegistry."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ToolRegistry()

    def test_register_tool(self):
        """Test registering a tool."""
        calc = Calculator()
        self.registry.register(calc)
        assert "Calculator" in self.registry.list_tools()

    def test_get_tool(self):
        """Test retrieving a tool."""
        calc = Calculator()
        self.registry.register(calc)
        retrieved = self.registry.get("Calculator")
        assert retrieved is calc

    def test_get_nonexistent_tool(self):
        """Test retrieving a non-existent tool."""
        result = self.registry.get("NonExistent")
        assert result is None

    def test_list_tools(self):
        """Test listing all tools."""
        self.registry.register(Calculator())
        self.registry.register(FinalAnswer())
        tools = self.registry.list_tools()
        assert "Calculator" in tools
        assert "FinalAnswer" in tools
        assert len(tools) == 2

    def test_get_tools_description(self):
        """Test getting formatted tools description."""
        self.registry.register(Calculator())
        description = self.registry.get_tools_description()
        assert "Calculator" in description
        assert "mathematical" in description.lower()

    def test_registry_length(self):
        """Test registry length."""
        assert len(self.registry) == 0
        self.registry.register(Calculator())
        assert len(self.registry) == 1
        self.registry.register(FinalAnswer())
        assert len(self.registry) == 2
