"""Demo script showing how to use DeepSeek model with ReAct Agent.

This example demonstrates:
1. Loading DeepSeek API key from environment
2. Initializing DeepSeekModel
3. Running the ReAct Agent with DeepSeek
"""

from agent.config import get_config
from agent.models.deepseek_model import DeepSeekModel
from agent.react.agent import ReActAgent


def main():
    """Run demo with DeepSeek model."""
    print("=" * 60)
    print("DeepSeek ReAct Agent Demo")
    print("=" * 60)
    print()

    # Load configuration (will read DEEPSEEK_API_KEY from .env or environment)
    config = get_config()

    # Initialize DeepSeek model
    try:
        model = DeepSeekModel(
            config=config,
            model="deepseek-flash",  # or "deepseek-v4-pro" for complex tasks
        )
        print(f"✓ Model initialized: {model}")
        print()
    except ValueError as e:
        print(f"✗ Error: {e}")
        print()
        print("Please set DEEPSEEK_API_KEY in your .env file or environment:")
        print("  export DEEPSEEK_API_KEY='your-api-key-here'")
        return

    # Initialize ReAct Agent
    agent = ReActAgent(model=model, config=config)
    print(f"✓ Agent initialized with {len(agent.tools)} tools")
    print()

    # Example queries
    queries = [
        "Calculate 123 * 456",
        "What is 2^10?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 60)

        try:
            result = agent.run(query)
            print(f"\nFinal Answer: {result}")
        except Exception as e:
            print(f"\nError: {e}")

        print()
        print("=" * 60)
        print()


if __name__ == "__main__":
    main()
