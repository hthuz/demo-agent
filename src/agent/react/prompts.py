"""Prompt templates for ReAct agent."""


class ReActPromptTemplate:
    """Manages prompt templates for ReAct agent."""

    SYSTEM_PROMPT = """You are a helpful AI assistant that uses tools to answer questions.

Available Tools:
{tools_description}

IMPORTANT: When you have the final answer, you MUST use the FinalAnswer tool to return it.

You should use the following format:

Thought: [your reasoning about what to do next]
Action: [tool name from available tools]
Action Input: {{"parameter_name": "value"}}
Observation: [tool result will appear here]
... (repeat Thought/Action/Observation as needed)
Thought: I now have the final answer
Action: FinalAnswer
Action Input: {{"answer": "your final answer here"}}

Rules:
1. Always start with a Thought to reason about the problem
2. Use tools by specifying Action and Action Input in JSON format
3. After each tool call, you'll receive an Observation
4. Continue reasoning until you can provide a final answer
5. MUST use FinalAnswer tool to conclude - do not just write the answer
6. Keep your reasoning focused and concise

Begin!

User Question: {user_input}"""

    CONTINUATION_PROMPT = """
{history}

Continue your reasoning. Remember to use FinalAnswer tool when you have the answer."""

    @staticmethod
    def format_system_prompt(tools_description: str, user_input: str) -> str:
        """Format the initial system prompt.

        Args:
            tools_description: Description of available tools
            user_input: User's question

        Returns:
            Formatted prompt string
        """
        return ReActPromptTemplate.SYSTEM_PROMPT.format(
            tools_description=tools_description,
            user_input=user_input,
        )

    @staticmethod
    def format_continuation_prompt(history: str) -> str:
        """Format continuation prompt with history.

        Args:
            history: Previous reasoning history

        Returns:
            Formatted prompt string
        """
        return ReActPromptTemplate.CONTINUATION_PROMPT.format(history=history)
