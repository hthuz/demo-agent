"""CLI interface for ReAct Agent."""

import sys
import argparse

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from agent.models.openai_model import OpenAIModel
from agent.react.agent import ReActAgent
from agent.config import Config, get_config


console = Console()


def print_welcome():
    """Print welcome message."""
    welcome_text = """
[bold cyan]ReAct Agent Demo[/bold cyan]

A minimal ReAct Agent with tool-calling capabilities.

Available commands:
  - Type your question to start
  - Type 'quit' or 'exit' to leave
  - Type 'help' for more information

Available tools: Calculator, FileReader, Directory, FinalAnswer
"""
    console.print(Panel(welcome_text, title="Welcome", border_style="cyan"))


def print_help():
    """Print help information."""
    help_text = """
[bold]Available Tools:[/bold]

1. [yellow]Calculator[/yellow] - Perform mathematical calculations
   Example: "Calculate 25 * 4 + 10"

2. [yellow]FileReader[/yellow] - Read file contents
   Example: "Read the README.md file"

3. [yellow]Directory[/yellow] - List directory contents
   Example: "List all files in the current directory"

4. [yellow]FinalAnswer[/yellow] - Return final answer (used automatically by agent)

[bold]Example Queries:[/bold]
  - "Calculate (12 + 8) * 3"
  - "Read the pyproject.toml file and tell me the project name"
  - "List all Python files in the src directory"
  - "Calculate the square of 15, then tell me if it's greater than 200"
"""
    console.print(Panel(help_text, title="Help", border_style="green"))


def run_interactive_mode():
    """Run interactive CLI mode."""
    print_welcome()

    # Load configuration
    config = get_config()

    # Validate configuration
    is_valid, errors = config.validate()
    if not is_valid:
        console.print("[bold red]Configuration Error:[/bold red]", style="red")
        for error in errors:
            console.print(f"  - {error}", style="red")
        console.print("\nPlease check your .env file and environment variables.")
        sys.exit(1)

    # Initialize agent
    try:
        model = OpenAIModel(config=config)
        agent = ReActAgent(model=model, config=config)
        console.print("✅ Agent initialized successfully!", style="green")
        console.print(f"   Model: {config.model_name}", style="dim")
        console.print(f"   Temperature: {config.temperature}", style="dim")
        console.print(f"   Max iterations: {config.max_iterations}\n", style="dim")
    except Exception as e:
        console.print(f"[bold red]Error initializing agent:[/bold red] {str(e)}")
        sys.exit(1)

    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

            # Handle commands
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("\n👋 Goodbye!", style="bold cyan")
                break
            elif user_input.lower() == "help":
                print_help()
                continue
            elif not user_input.strip():
                continue

            # Run agent
            console.print()  # Empty line
            result = agent.run(user_input)

            # Print result in a panel
            console.print(
                Panel(
                    result,
                    title="[bold green]Agent Response[/bold green]",
                    border_style="green",
                )
            )

        except KeyboardInterrupt:
            console.print("\n\n👋 Goodbye!", style="bold cyan")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}", style="red")


def run_single_query(query: str):
    """Run a single query and exit.

    Args:
        query: User query to execute
    """
    # Load configuration
    config = get_config()

    # Validate configuration
    is_valid, errors = config.validate()
    if not is_valid:
        console.print("[bold red]Configuration Error:[/bold red]", style="red")
        for error in errors:
            console.print(f"  - {error}", style="red")
        sys.exit(1)

    # Initialize agent
    try:
        model = OpenAIModel(config=config)
        agent = ReActAgent(model=model, config=config)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

    # Run query
    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}\n")
    result = agent.run(query)

    # Print result
    console.print(
        Panel(
            result,
            title="[bold green]Final Answer[/bold green]",
            border_style="green",
        )
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ReAct Agent - A minimal reasoning and acting agent"
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Single query to execute (non-interactive mode)",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="gpt-4",
        help="OpenAI model to use (default: gpt-4)",
    )

    args = parser.parse_args()

    if args.query:
        run_single_query(args.query)
    else:
        run_interactive_mode()


if __name__ == "__main__":
    main()
