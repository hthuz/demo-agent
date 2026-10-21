"""Base class for tools and tool registry."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Tool(ABC):
    """Abstract base class for all tools."""

    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.parameters: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            str: Result of the tool execution
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format for LLM.

        Returns:
            dict: Tool schema including name, description, and parameters
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool.

        Args:
            tool: Tool instance to register
        """
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Get a tool by name.

        Args:
            name: Name of the tool

        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """Get list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def get_tools_description(self) -> str:
        """Get formatted description of all tools for LLM prompt.

        Returns:
            Formatted string describing all available tools
        """
        descriptions = []
        for tool in self.tools.values():
            param_desc = ", ".join(
                f"{k}: {v.get('type', 'string')}"
                for k, v in tool.parameters.items()
            )
            descriptions.append(
                f"- {tool.name}: {tool.description}\n"
                f"  Parameters: {{{param_desc}}}"
            )
        return "\n".join(descriptions)

    def __len__(self) -> int:
        return len(self.tools)

    def __repr__(self) -> str:
        return f"<ToolRegistry: {len(self.tools)} tools>"
