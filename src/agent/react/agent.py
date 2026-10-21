"""Core ReAct Agent implementation."""

import json
import re
from typing import Dict, Any, List, Optional, Tuple

from agent.models.base import LLMBase
from agent.tools.base import Tool, ToolRegistry
from agent.tools import Calculator, FileReader, Directory, FinalAnswer
from agent.react.prompts import ReActPromptTemplate
from agent.config import Config, get_config


class ReActAgent:
    """ReAct Agent that performs reasoning and action loops."""

    def __init__(
        self,
        model: LLMBase,
        tools: Optional[List[Tool]] = None,
        max_iterations: Optional[int] = None,
        verbose: Optional[bool] = None,
        config: Optional[Config] = None,
    ):
        """Initialize ReAct Agent.

        Args:
            model: LLM model instance
            tools: List of tools (if None, uses default tools)
            max_iterations: Maximum number of reasoning iterations (if None, reads from config)
            verbose: Whether to print execution steps (if None, reads from config)
            config: Config instance (if None, uses global config)
        """
        # Get configuration
        if config is None:
            config = get_config()

        self.model = model
        self.max_iterations = max_iterations if max_iterations is not None else config.max_iterations
        self.verbose = verbose if verbose is not None else config.verbose

        # Initialize tool registry
        self.tool_registry = ToolRegistry()

        # Register tools
        if tools is None:
            # Register default tools
            self.tool_registry.register(Calculator())
            self.tool_registry.register(FileReader())
            self.tool_registry.register(Directory())
            self.tool_registry.register(FinalAnswer())
        else:
            for tool in tools:
                self.tool_registry.register(tool)

        # Ensure FinalAnswer tool is always present
        if not self.tool_registry.get("FinalAnswer"):
            self.tool_registry.register(FinalAnswer())

    def run(self, user_input: str) -> str:
        """Execute the ReAct loop for a user query.

        Args:
            user_input: User's question or request

        Returns:
            Final answer string
        """
        # Initialize
        tools_description = self.tool_registry.get_tools_description()
        prompt = ReActPromptTemplate.format_system_prompt(
            tools_description=tools_description,
            user_input=user_input,
        )

        history = []
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            if self.verbose:
                print(f"\n{'='*60}")
                print(f"Iteration {iteration}/{self.max_iterations}")
                print(f"{'='*60}")

            # Generate LLM response
            if history:
                # Build history string
                history_str = "\n".join(history)
                full_prompt = prompt + "\n" + history_str
            else:
                full_prompt = prompt

            try:
                response = self.model.generate(full_prompt)
            except Exception as e:
                return f"Error: LLM generation failed - {str(e)}"

            # Parse response
            thought, action, action_input = self._parse_response(response)

            if not thought or not action:
                error_msg = "Error: Failed to parse LLM response. Expected Thought and Action."
                if self.verbose:
                    print(f"\n❌ {error_msg}")
                    print(f"Response was: {response[:200]}...")
                history.append(f"Observation: {error_msg}")
                continue

            # Display thought and action
            if self.verbose:
                print(f"\n🤔 Thought: {thought}")
                print(f"🔧 Action: {action}")
                print(f"📝 Input: {action_input}")

            # Execute action
            tool = self.tool_registry.get(action)
            if not tool:
                observation = f"Error: Unknown tool '{action}'. Available tools: {', '.join(self.tool_registry.list_tools())}"
                if self.verbose:
                    print(f"❌ {observation}")
                history.append(f"Thought: {thought}")
                history.append(f"Action: {action}")
                history.append(f"Action Input: {action_input}")
                history.append(f"Observation: {observation}")
                continue

            # Parse action input
            try:
                params = self._parse_action_input(action_input)
            except Exception as e:
                observation = f"Error: Invalid action input format - {str(e)}"
                if self.verbose:
                    print(f"❌ {observation}")
                history.append(f"Thought: {thought}")
                history.append(f"Action: {action}")
                history.append(f"Action Input: {action_input}")
                history.append(f"Observation: {observation}")
                continue

            # Execute tool
            if self.verbose:
                print(f"⏳ Executing...")

            try:
                observation = tool.execute(**params)
            except Exception as e:
                observation = f"Error: Tool execution failed - {str(e)}"

            # Check if this is FinalAnswer
            if action == "FinalAnswer":
                if self.verbose:
                    print(f"\n✅ Final Answer: {observation}")
                    print(f"{'='*60}\n")
                return observation

            # Display observation
            if self.verbose:
                # Truncate long observations for display
                display_obs = observation if len(observation) <= 500 else observation[:500] + "..."
                print(f"📊 Observation: {display_obs}")

            # Add to history
            history.append(f"Thought: {thought}")
            history.append(f"Action: {action}")
            history.append(f"Action Input: {action_input}")
            history.append(f"Observation: {observation}")

        # Max iterations reached
        final_msg = (
            f"Maximum iterations ({self.max_iterations}) reached. "
            "Unable to complete the task."
        )
        if self.verbose:
            print(f"\n⚠️ {final_msg}")
        return final_msg

    def _parse_response(self, response: str) -> Tuple[str, str, str]:
        """Parse LLM response to extract Thought, Action, and Action Input.

        Args:
            response: Raw LLM response

        Returns:
            Tuple of (thought, action, action_input)
        """
        thought = ""
        action = ""
        action_input = ""

        # Extract Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\nAction:|\Z)", response, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()

        # Extract Action
        action_match = re.search(r"Action:\s*(\w+)", response)
        if action_match:
            action = action_match.group(1).strip()

        # Extract Action Input
        action_input_match = re.search(r"Action Input:\s*(\{.+?\})", response, re.DOTALL)
        if action_input_match:
            action_input = action_input_match.group(1).strip()

        return thought, action, action_input

    def _parse_action_input(self, action_input: str) -> Dict[str, Any]:
        """Parse action input JSON string.

        Args:
            action_input: JSON string of parameters

        Returns:
            Dictionary of parameters
        """
        if not action_input:
            return {}

        try:
            return json.loads(action_input)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")

    def __repr__(self) -> str:
        return (
            f"<ReActAgent: {len(self.tool_registry)} tools, "
            f"max_iterations={self.max_iterations}>"
        )
