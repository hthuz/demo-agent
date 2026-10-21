"""Unit tests for ReAct Agent."""

import pytest
from unittest.mock import Mock, MagicMock

from agent.react.agent import ReActAgent
from agent.react.prompts import ReActPromptTemplate
from agent.models.base import LLMBase
from agent.tools import Calculator, FinalAnswer


class MockLLM(LLMBase):
    """Mock LLM for testing."""

    def __init__(self, responses=None):
        """Initialize mock LLM.

        Args:
            responses: List of responses to return in sequence
        """
        self.responses = responses or []
        self.call_count = 0

    def generate(self, prompt: str, **kwargs) -> str:
        """Return next mock response."""
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        return "Thought: I don't know\nAction: FinalAnswer\nAction Input: {\"answer\": \"Error\"}"

    def __repr__(self) -> str:
        return "<MockLLM>"


class TestReActAgent:
    """Test ReAct Agent."""

    def test_agent_initialization(self):
        """Test agent initialization with default tools."""
        model = MockLLM()
        agent = ReActAgent(model=model, verbose=False)

        assert len(agent.tool_registry) >= 4  # Calculator, FileReader, Directory, FinalAnswer
        assert agent.tool_registry.get("Calculator") is not None
        assert agent.tool_registry.get("FinalAnswer") is not None

    def test_agent_with_custom_tools(self):
        """Test agent initialization with custom tools."""
        model = MockLLM()
        tools = [Calculator(), FinalAnswer()]
        agent = ReActAgent(model=model, tools=tools, verbose=False)

        assert len(agent.tool_registry) == 2
        assert agent.tool_registry.get("Calculator") is not None
        assert agent.tool_registry.get("FinalAnswer") is not None

    def test_simple_calculation(self):
        """Test simple calculation using Calculator."""
        responses = [
            "Thought: I need to calculate 2 + 3\nAction: Calculator\nAction Input: {\"math_expression\": \"2 + 3\"}",
            "Thought: I have the answer\nAction: FinalAnswer\nAction Input: {\"answer\": \"The result is 5\"}"
        ]
        model = MockLLM(responses=responses)
        agent = ReActAgent(model=model, verbose=False)

        result = agent.run("What is 2 + 3?")
        assert result == "The result is 5"

    def test_direct_final_answer(self):
        """Test agent providing direct final answer."""
        responses = [
            "Thought: This is a simple question\nAction: FinalAnswer\nAction Input: {\"answer\": \"Hello, World!\"}"
        ]
        model = MockLLM(responses=responses)
        agent = ReActAgent(model=model, verbose=False)

        result = agent.run("Say hello")
        assert result == "Hello, World!"

    def test_max_iterations(self):
        """Test that agent stops at max iterations."""
        # Always return non-FinalAnswer action
        responses = [
            "Thought: Calculating\nAction: Calculator\nAction Input: {\"math_expression\": \"1 + 1\"}"
        ] * 15  # More than max_iterations

        model = MockLLM(responses=responses)
        agent = ReActAgent(model=model, max_iterations=3, verbose=False)

        result = agent.run("Calculate something")
        assert "Maximum iterations" in result

    def test_unknown_tool_handling(self):
        """Test handling of unknown tool."""
        responses = [
            "Thought: Using unknown tool\nAction: UnknownTool\nAction Input: {\"param\": \"value\"}",
            "Thought: Fixing mistake\nAction: FinalAnswer\nAction Input: {\"answer\": \"Fixed\"}"
        ]
        model = MockLLM(responses=responses)
        agent = ReActAgent(model=model, verbose=False)

        result = agent.run("Test unknown tool")
        assert result == "Fixed"

    def test_parse_response(self):
        """Test parsing LLM response."""
        model = MockLLM()
        agent = ReActAgent(model=model, verbose=False)

        response = """Thought: I need to calculate
Action: Calculator
Action Input: {"math_expression": "2 + 2"}"""

        thought, action, action_input = agent._parse_response(response)
        assert thought == "I need to calculate"
        assert action == "Calculator"
        assert '{"math_expression": "2 + 2"}' in action_input

    def test_parse_action_input(self):
        """Test parsing action input JSON."""
        model = MockLLM()
        agent = ReActAgent(model=model, verbose=False)

        action_input = '{"math_expression": "2 + 2"}'
        params = agent._parse_action_input(action_input)
        assert params == {"math_expression": "2 + 2"}

    def test_parse_invalid_action_input(self):
        """Test parsing invalid action input."""
        model = MockLLM()
        agent = ReActAgent(model=model, verbose=False)

        action_input = '{"invalid json'
        with pytest.raises(ValueError):
            agent._parse_action_input(action_input)

    def test_tool_execution_error_recovery(self):
        """Test that agent can recover from tool execution errors."""
        responses = [
            "Thought: Calculate\nAction: Calculator\nAction Input: {\"math_expression\": \"invalid\"}",
            "Thought: Fixing error\nAction: FinalAnswer\nAction Input: {\"answer\": \"Recovered\"}"
        ]
        model = MockLLM(responses=responses)
        agent = ReActAgent(model=model, verbose=False)

        result = agent.run("Test error recovery")
        assert result == "Recovered"


class TestReActPromptTemplate:
    """Test ReActPromptTemplate."""

    def test_format_system_prompt(self):
        """Test formatting system prompt."""
        tools_desc = "Tool1: Description1\nTool2: Description2"
        user_input = "What is 2 + 2?"

        prompt = ReActPromptTemplate.format_system_prompt(tools_desc, user_input)

        assert "Tool1" in prompt
        assert "Tool2" in prompt
        assert "What is 2 + 2?" in prompt
        assert "FinalAnswer" in prompt

    def test_format_continuation_prompt(self):
        """Test formatting continuation prompt."""
        history = "Thought: Previous thought\nAction: SomeAction"
        prompt = ReActPromptTemplate.format_continuation_prompt(history)

        assert "Previous thought" in prompt
        assert "Continue" in prompt
