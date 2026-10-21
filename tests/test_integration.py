"""Integration tests for the complete ReAct Agent system."""

import pytest
import tempfile
from pathlib import Path

from agent.react.agent import ReActAgent
from agent.models.base import LLMBase


class SimpleMockLLM(LLMBase):
    """Simple mock LLM for integration testing."""

    def __init__(self):
        self.call_count = 0
        self.user_query = None

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate contextual response based on prompt."""
        self.call_count += 1

        # Extract user question from the prompt on first call
        if self.call_count == 1 and "User Question:" in prompt:
            self.user_query = prompt.split("User Question:")[-1].strip().lower()

        # Check if we have an observation (subsequent calls)
        # Look for actual observation with newline, not just the word in instructions
        has_observation = self.call_count > 1 and "\nObservation:" in prompt

        # Determine scenario based on original user query
        if self.user_query and "calculate" in self.user_query:
            if not has_observation:
                return """Thought: I need to use the Calculator tool to solve this
Action: Calculator
Action Input: {"math_expression": "15 * 8"}"""
            else:
                return """Thought: I have the calculation result, now I can provide the final answer
Action: FinalAnswer
Action Input: {"answer": "The result of 15 * 8 is 120"}"""

        elif self.user_query and "read" in self.user_query and "file" in self.user_query:
            if not has_observation:
                file_path = ""
                # Try to extract file path from query
                if "/tmp/" in prompt or "/temp" in prompt:
                    import re
                    match = re.search(r'/[/\w.-]+', self.user_query)
                    if match:
                        file_path = match.group(0)
                return f"""Thought: I need to read the file to answer this question
Action: FileReader
Action Input: {{"file_path": "{file_path if file_path else 'test.txt'}"}}"""
            else:
                return """Thought: I have read the file content
Action: FinalAnswer
Action Input: {"answer": "File content has been read successfully"}"""

        elif self.user_query and ("list" in self.user_query or "directory" in self.user_query):
            if not has_observation:
                return """Thought: I should list the directory contents
Action: Directory
Action Input: {"path": "."}"""
            else:
                return """Thought: I have the directory listing
Action: FinalAnswer
Action Input: {"answer": "Directory contents listed"}"""

        else:
            return """Thought: I can answer this directly
Action: FinalAnswer
Action Input: {"answer": "I understand your query"}"""

    def __repr__(self) -> str:
        return "<SimpleMockLLM>"


class TestIntegration:
    """Integration tests for the complete system."""

    def test_full_calculation_workflow(self):
        """Test complete workflow: calculation -> final answer."""
        model = SimpleMockLLM()
        agent = ReActAgent(model=model, verbose=False)

        result = agent.run("Calculate 15 * 8")

        assert "120" in result
        assert model.call_count >= 2  # At least calculation + final answer

    def test_multi_step_reasoning(self):
        """Test multi-step reasoning with multiple tool calls."""
        model = SimpleMockLLM()
        agent = ReActAgent(model=model, verbose=False)

        result = agent.run("List the current directory")

        assert "list" in result.lower() or "directory" in result.lower()
        assert model.call_count >= 2

    def test_file_reading_workflow(self):
        """Test file reading workflow."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_file = f.name

        try:
            model = SimpleMockLLM()
            agent = ReActAgent(model=model, verbose=False)

            result = agent.run(f"Read file {temp_file}")

            assert "file" in result.lower() or "read" in result.lower()
        finally:
            # Cleanup
            Path(temp_file).unlink(missing_ok=True)

    def test_all_tools_registered(self):
        """Test that all expected tools are registered."""
        model = SimpleMockLLM()
        agent = ReActAgent(model=model, verbose=False)

        tools = agent.tool_registry.list_tools()

        assert "Calculator" in tools
        assert "FileReader" in tools
        assert "Directory" in tools
        assert "FinalAnswer" in tools
        assert len(tools) == 4

    def test_tool_descriptions_available(self):
        """Test that tool descriptions are properly formatted."""
        model = SimpleMockLLM()
        agent = ReActAgent(model=model, verbose=False)

        description = agent.tool_registry.get_tools_description()

        assert "Calculator" in description
        assert "FileReader" in description
        assert "Directory" in description
        assert "FinalAnswer" in description
        assert "Parameters" in description

    def test_agent_stops_at_final_answer(self):
        """Test that agent properly stops when FinalAnswer is called."""
        model = SimpleMockLLM()
        agent = ReActAgent(model=model, max_iterations=10, verbose=False)

        result = agent.run("Say hello")

        # Should stop immediately with FinalAnswer, not use all iterations
        assert model.call_count <= 2
        assert "Maximum iterations" not in result

    def test_error_handling_in_workflow(self):
        """Test error handling during workflow execution."""
        class ErrorLLM(LLMBase):
            def __init__(self):
                self.call_count = 0

            def generate(self, prompt: str, **kwargs) -> str:
                self.call_count += 1
                if self.call_count == 1:
                    # First call: invalid tool
                    return """Thought: Testing error handling
Action: InvalidTool
Action Input: {"param": "value"}"""
                else:
                    # Recover with final answer
                    return """Thought: Recovering from error
Action: FinalAnswer
Action Input: {"answer": "Recovered successfully"}"""

            def __repr__(self) -> str:
                return "<ErrorLLM>"

        model = ErrorLLM()
        agent = ReActAgent(model=model, verbose=False)

        result = agent.run("Test error handling")

        assert "Recovered successfully" in result
        assert model.call_count == 2


class TestEndToEnd:
    """End-to-end tests simulating real usage."""

    def test_realistic_calculation_scenario(self):
        """Test realistic calculation scenario."""
        class RealisticLLM(LLMBase):
            def __init__(self):
                self.responses = [
                    """Thought: The user wants to calculate (12 + 8) * 3. I'll use the Calculator tool.
Action: Calculator
Action Input: {"math_expression": "(12 + 8) * 3"}""",
                    """Thought: The calculator returned 60. Now I can provide the final answer.
Action: FinalAnswer
Action Input: {"answer": "The result of (12 + 8) * 3 is 60"}"""
                ]
                self.idx = 0

            def generate(self, prompt: str, **kwargs) -> str:
                response = self.responses[min(self.idx, len(self.responses) - 1)]
                self.idx += 1
                return response

            def __repr__(self) -> str:
                return "<RealisticLLM>"

        model = RealisticLLM()
        agent = ReActAgent(model=model, verbose=False)

        result = agent.run("What is (12 + 8) * 3?")

        assert "60" in result

    def test_multi_tool_scenario(self):
        """Test scenario using multiple different tools."""
        class MultiToolLLM(LLMBase):
            def __init__(self):
                self.step = 0

            def generate(self, prompt: str, **kwargs) -> str:
                self.step += 1
                if self.step == 1:
                    return """Thought: First, I'll calculate the math
Action: Calculator
Action Input: {"math_expression": "5 * 5"}"""
                elif self.step == 2:
                    return """Thought: Now I'll list the directory
Action: Directory
Action Input: {"path": "."}"""
                else:
                    return """Thought: I have all the information
Action: FinalAnswer
Action Input: {"answer": "Calculation done (25) and directory listed"}"""

            def __repr__(self) -> str:
                return "<MultiToolLLM>"

        model = MultiToolLLM()
        agent = ReActAgent(model=model, verbose=False)

        result = agent.run("Calculate 5*5 and list current directory")

        assert "25" in result or "Calculation" in result
        assert model.step == 3
