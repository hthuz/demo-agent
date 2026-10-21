"""Final Answer tool for terminating the ReAct loop."""

from agent.tools.base import Tool


class FinalAnswer(Tool):
    """Special tool that signals the end of the ReAct loop."""

    def __init__(self):
        super().__init__()
        self.name = "FinalAnswer"
        self.description = (
            "Use this tool when you have the final answer to the user's question. "
            "This will end the reasoning loop and return the answer to the user. "
            "You MUST use this tool to provide your final answer."
        )
        self.parameters = {
            "answer": {
                "type": "string",
                "description": "The final answer to return to the user",
                "required": True,
            }
        }

    def execute(self, answer: str = "", **kwargs) -> str:
        """Return the final answer.

        Args:
            answer: The final answer string

        Returns:
            The final answer (this signals loop termination)
        """
        if not answer:
            return "Error: No answer provided to FinalAnswer tool"

        return answer
