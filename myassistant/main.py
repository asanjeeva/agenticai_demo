"""CLI entry point for MyAssistant."""

import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from .agent import MyAssistantAgent


console = Console()


def print_welcome():
    """Print the welcome message."""
    welcome_text = """
# MyAssistant

I'm your AI assistant for **JIRA** and **GitHub** operations.

**What I can do:**
- Create JIRA tickets from natural language descriptions
- Search for existing JIRA tickets
- Commit code files to GitHub repositories
- List your GitHub repositories
- Read files from GitHub repositories

**Commands:**
- Type your request in natural language
- `/help` - Show this help message
- `/reset` - Reset conversation history
- `/quit` or `/exit` - Exit the assistant
"""
    console.print(Panel(Markdown(welcome_text), title="Welcome", border_style="blue"))


def print_help():
    """Print the help message."""
    help_text = """
**Example Requests:**

**JIRA:**
- "Create a high priority bug ticket for login page not loading"
- "Log a task to implement user authentication with 5 story points"
- "Search for tickets related to payment processing"

**GitHub:**
- "List my repositories"
- "Commit this code to myrepo: [paste your code]"
- "Show me the contents of README.md in user/repo"

**Tips:**
- Be descriptive when creating tickets - I'll extract fields automatically
- For commits, specify the repo name, file path, and content
- I'll ask for clarification if I need more details
"""
    console.print(Panel(Markdown(help_text), title="Help", border_style="green"))


def main():
    """Main entry point for the CLI."""
    console.print()
    print_welcome()

    try:
        agent = MyAssistantAgent()
    except ValueError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        console.print("\nPlease ensure your .env file is properly configured.")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Failed to initialize agent:[/red] {e}")
        sys.exit(1)

    console.print()

    while True:
        try:
            # Get user input
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

            if not user_input.strip():
                continue

            # Handle commands
            command = user_input.strip().lower()

            if command in ["/quit", "/exit"]:
                console.print("\n[yellow]Goodbye![/yellow]\n")
                break

            if command == "/help":
                print_help()
                continue

            if command == "/reset":
                agent.reset()
                console.print("[yellow]Conversation history cleared.[/yellow]\n")
                continue

            # Process with agent
            console.print()
            with console.status("[bold green]Thinking...[/bold green]"):
                response = agent.chat(user_input)

            # Display response
            console.print(Panel(
                Markdown(response),
                title="[bold blue]MyAssistant[/bold blue]",
                border_style="blue",
            ))
            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Use /quit to exit[/yellow]\n")
            continue
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {e}\n")
            continue


if __name__ == "__main__":
    main()
