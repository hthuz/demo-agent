"""Example usage of the ReAct Agent."""

import os
from dotenv import load_dotenv

from agent.models.openai_model import OpenAIModel
from agent.react.agent import ReActAgent


def main():
    """Run example queries."""
    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        return

    # Initialize model and agent
    print("Initializing ReAct Agent...")
    model = OpenAIModel(model="gpt-4")
    agent = ReActAgent(model=model, verbose=True)

    # Example 1: Simple calculation
    print("\n" + "=" * 80)
    print("Example 1: Simple Calculation")
    print("=" * 80)
    result = agent.run("Calculate (15 + 25) * 2")
    print(f"\nFinal Result: {result}")

    # Example 2: File reading
    print("\n" + "=" * 80)
    print("Example 2: File Reading")
    print("=" * 80)
    result = agent.run("Read the README.md file and tell me what this project is about")
    print(f"\nFinal Result: {result}")

    # Example 3: Directory listing
    print("\n" + "=" * 80)
    print("Example 3: Directory Listing")
    print("=" * 80)
    result = agent.run("List all files in the current directory")
    print(f"\nFinal Result: {result}")

    # Example 4: Multi-step reasoning
    print("\n" + "=" * 80)
    print("Example 4: Multi-step Reasoning")
    print("=" * 80)
    result = agent.run(
        "Calculate 12 * 8, then tell me if the result is greater than 90"
    )
    print(f"\nFinal Result: {result}")


if __name__ == "__main__":
    main()
