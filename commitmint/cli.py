import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from . import git_handler
from .generator import generate_messages

app = typer.Typer(help="CommitMent - the freshest AI-Powered Git Commit Message Generator")
console = Console()


@app.command()
def generate(
    use_unstaged: bool = typer.Option(False, "--unstaged", "-u", help="Use unstaged changes instead of staged"),
    auto_commit: bool = typer.Option(False, "--commit", "-c", help="Automatically commit with selected message"),
    model: str = typer.Option("gpt-5-mini", "--model", "-m", help="OpenAI model to use"),
):

    console.print("[bold blue]Generating commit message...\n[/bold blue]")

    try:
        if use_unstaged:
            diff = git_handler.get_unstaged_diff()
            if not diff:
                console.print("[yellow]No unstaged changes found.[/yellow]")
                raise typer.Exit()
        else:
            if not git_handler.has_staged_changes():
                console.print("[yellow]No staged changes found. Stage your changes with 'git add' first.[/yellow]")
                raise typer.Exit()
            diff = git_handler.get_staged_diff()

        analysis = git_handler.parse_diff(diff)

        # generate commit messages
        with console.status("[bold green]Analyzing changes and generating messages..."):
            options = generate_messages(diff, analysis, model_name=model)

        if not options or not options.options:
            console.print("[red]Failed to generate commit messages.[/red]")
            raise typer.Exit(1)

        # then display them
        console.print("\n[bold green]Generated commit messages:\n[/bold green]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Message", min_width=50)
        table.add_column("Confidence", justify="right", width=10)

        for i, msg in enumerate(options.options, 1):
            formatted = msg.format(include_body=False)
            confidence = f"{msg.confidence:.0%}"
            table.add_row(str(i), formatted, confidence)

        console.print(table)

        # user selection time
        choice = Prompt.ask(
            "\nSelect an option:",
            choices=[str(i) for i in range(1, len(options.options) + 1)] + ["quit."],
            default="1"
        )

        if choice == "quit.":
            console.print("[yellow]Cancelled.[/yellow]")
            return

        selected = options.options[int(choice) - 1]

        # show the message
        console.print("\n[bold]Selected commit message:[/bold]")
        console.print(Panel(selected.format(), border_style="green"))

        # give them the power to edit
        if Confirm.ask("Do you want to edit this message?", default=False):
            edited = typer.edit(selected.format())
            if edited:
                message_to_use = edited.strip()
                console.print("[green]Message has been edited.[/green]")
            else:
                message_to_use = selected.format()
        else:
            message_to_use = selected.format()

        if auto_commit or Confirm.ask("Do you want to commit this message?", default=True):
            repo = git_handler.get_repo()
            repo.index.commit(message_to_use)
            console.print("[green]Committed successfully![/green]")
        else:
            console.print("\n[dim]Copy this message to commit manually:[/dim]")
            console.print(Panel(message_to_use, border_style="dim"))

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()