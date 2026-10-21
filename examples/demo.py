"""Example usage of the ReAct Agent."""

from agent.models.openai_model import OpenAIModel
from agent.react.agent import ReActAgent
from agent.config import get_config


def main():
    """Run example queries."""
    # Load and validate configuration
    config = get_config()
    is_valid, errors = config.validate()

    if not is_valid:
        print("Configuration Error:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease create a .env file with your configuration.")
        return

    # Initialize model and agent using config
    print("Initializing ReAct Agent...")
    print(f"  Model: {config.model_name}")
    print(f"  Temperature: {config.temperature}")
    print(f"  Max Iterations: {config.max_iterations}")
    print()

    model = OpenAIModel(config=config)
    agent = ReActAgent(model=model, config=config)

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
