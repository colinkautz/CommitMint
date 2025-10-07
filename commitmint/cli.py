from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from . import git_handler
from .generator import generate_messages
from .providers import Provider, check_api_key, get_provider_info, DEFAULT_MODELS
from .config import load_config, save_config, create_default_config, get_config_path

app = typer.Typer(help="CommitMint - the freshest AI-Powered Git Commit Message Generator",
                  add_completion=False,
                  rich_markup_mode="rich")
console = Console()


@app.command(help="Generated commit messages from your git changes")
def generate(
        use_unstaged: bool = typer.Option(False, "--unstaged", "-u", help="Use unstaged changes instead of staged"),
        auto_commit: bool = typer.Option(None, "--commit", "-c", help="Automatically commit with selected message"),
        provider: Provider = typer.Option(None, "--provider", "-p", help="LLM provider to use"),
        model: str = typer.Option(None, "--model", "-m", help="Model name (uses provider default if not specified)"),
        temperature: float = typer.Option(None, "--temp", "-t", help="Generation temperature (0.0 - 1.0)"),
):
    # Load config and override with CLI args
    cfg = load_config()

    if provider is not None:
        cfg.provider = provider
    if model is not None:
        cfg.model = model
    if temperature is not None:
        cfg.temperature = temperature
    if auto_commit is not None:
        cfg.auto_commit = auto_commit

    console.print("[bold blue]mint[/bold blue] - Generating commit messages...\n")

    # Check API key for provider
    if not check_api_key(cfg.provider):
        provider_info = get_provider_info(cfg.provider)
        console.print(f"[red]Error: {provider_info['api_key_var']} not set![/red]")
        console.print(f"[yellow]Set your API key in .env file:[/yellow]")
        console.print(f"  {provider_info['api_key_var']}=your-api-key-here")
        raise typer.Exit(1)

    model_name = cfg.get_model()
    console.print(f"[dim]Using {cfg.provider.value} with model: {model_name}[/dim]\n")

    try:
        # Get diff
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

        # Generate commit messages
        with console.status("[bold green]Analyzing changes and generating messages..."):
            options = generate_messages(diff, analysis)

        if not options or not options.options:
            console.print("[red]Failed to generate commit messages.[/red]")
            raise typer.Exit(1)

        # Display options
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

        # User selection
        while True:
            choice = Prompt.ask(
                "\nSelect an option:",
                choices=[str(i) for i in range(1, len(options.options) + 1)] + ["preview", "quit"],
                default="1"
            )

            if choice == "quit":
                console.print("[yellow]Cancelled.[/yellow]")
                return

            if choice == "preview":
                console.print("\n[bold]Full message previews:[/bold]\n")
                for i, msg in enumerate(options.options, 1):
                    console.print(f"[bold cyan]Option {i}:[/bold cyan]")
                    console.print(Panel(msg.format(), border_style="dim"))
                    console.print()
                continue  # Go back to selection prompt

            # If we get here, it's a valid number selection
            break

        selected = options.options[int(choice) - 1]


        # Show full message
        console.print("\n[bold]Selected commit message:[/bold]")
        console.print(Panel(selected.format(), border_style="green"))

        # Edit option
        if Confirm.ask("Do you want to edit this message?", default=False):
            edited = typer.edit(selected.format())
            if edited:
                message_to_use = edited.strip()
                console.print("[green]Message has been edited.[/green]")
            else:
                message_to_use = selected.format()
        else:
            message_to_use = selected.format()

        # if --unstaged, do not commit, otherwise full speed ahead
        if use_unstaged:
            console.print("\n[yellow]Note: you cannot auto-commit with --unstaged.[/yellow]")
            console.print("[dim]Stage your changes and run without --unstaged to commit.[/dim]")
            console.print("\n[dim]Copy this message to commit manually:[/dim]")
            console.print(Panel(message_to_use, border_style="dim"))
        elif cfg.auto_commit or Confirm.ask("Do you want to commit this message?", default=True):
            repo = git_handler.get_repo()

            if not git_handler.has_staged_changes():
                console.print("[red]No staged changes found.[/red]")
                raise typer.Exit(1)

            repo.index.commit(message_to_use)
            console.print("[green]Committed successfully![/green]")
        else:
            console.print("\n[dim]Copy this message to commit manually:[/dim]")
            console.print(Panel(message_to_use, border_style="dim"))

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command(help="List available LLM providers and their configuration status")
def providers():
    console.print("[bold blue]Available LLM Providers:[/bold blue]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan")
    table.add_column("Default Model", style="green")
    table.add_column("API Key Required", style="yellow")
    table.add_column("API Key Set", style="dim")

    for provider in Provider:
        info = get_provider_info(provider)
        api_key_required = "Yes" if info["requires_api_key"] else "No"
        api_key_set = "✓" if check_api_key(provider) else "✗"

        table.add_row(
            info["name"],
            info["default_model"],
            api_key_required,
            api_key_set
        )

    console.print(table)
    console.print("\n[dim]Usage: mint --provider <provider> --model <model>[/dim]")


@app.command(help="Initialize CommitMint with .env and config files")
def setup():
    console.print("[bold blue]CommitMint Setup[/bold blue]\n")

    # Create .env file
    env_path = Path.cwd() / ".env"
    env_created = False

    if env_path.exists():
        if not Confirm.ask(".env already exists. Overwrite?", default=False):
            console.print("[yellow].env setup skipped.[/yellow]")
        else:
            env_created = True
    else:
        env_created = True

    if env_created:
        env_content = """# CommitMint API Keys
# Uncomment and add your API key for the provider you want to use

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic Claude
# ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Google Gemini
# GOOGLE_API_KEY=your-google-api-key-here
"""
        with open(env_path, 'w') as f:
            f.write(env_content)

        console.print(f"[green]✓[/green] Created .env file")
        console.print(f"[dim]   {env_path.absolute()}[/dim]")

    # Create config file
    config_path = get_config_path()
    config_created = False

    if config_path.exists():
        if not Confirm.ask(f"\n~/.mintrc already exists. Overwrite?", default=False):
            console.print("[yellow]Config setup skipped.[/yellow]")
        else:
            config_created = True
    else:
        config_created = True

    if config_created:
        config_path = create_default_config()
        console.print(f"[green]✓[/green] Created config file")
        console.print(f"[dim]   {config_path}[/dim]")

    # Final instructions
    console.print(f"\n[bold green]Setup complete![/bold green]")
    console.print(f"\n[yellow]Next steps:[/yellow]")
    console.print(f"  1. Edit .env and add your API key")
    console.print(f"  2. Read the README")

@app.command(help="Manage CommitMint configuration (~/.mintrc)")
def config(
        init: bool = typer.Option(False, "--init", help="Create a default config file"),
        show: bool = typer.Option(False, "--show", help="Show current configuration"),
        edit: bool = typer.Option(False, "--edit", help="Open config file in editor"),
        set_provider: str = typer.Option(None, "--set-provider", help="Set default provider"),
        set_model: str = typer.Option(None, "--set-model", help="Set default model"),
        set_temperature: float = typer.Option(None, "--set-temp", help="Set default temperature")
):
    # Configure CommitMint settings

    if init:
        config_path = create_default_config()
        console.print(f"[green]✓[/green] Created config file at: {config_path}")
        console.print("[dim]Edit it to customize your settings[/dim]")
        return

    if edit:
        config_path = get_config_path()
        if not config_path.exists():
            console.print("[yellow]No config file found. Creating default...[/yellow]")
            config_path = create_default_config()

        typer.edit(filename=str(config_path))
        console.print(f"[green]✓[/green] Config file: {config_path}")
        return

    if show:
        current_config = load_config()
        config_path = get_config_path()

        console.print(f"[bold blue]Current Configuration[/bold blue] ({config_path})\n")

        config_dict = current_config.model_dump()
        config_dict['provider'] = config_dict['provider'].value
        config_dict['model'] = config_dict['model'] or f"{DEFAULT_MODELS[current_config.provider]} (default)"

        table = Table(show_header=False, box=None)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for key, value in config_dict.items():
            table.add_row(key, str(value))

        console.print(table)
        return

    if any([set_provider, set_model, set_temperature]):
        current_config = load_config()

        if set_provider:
            try:
                current_config.provider = Provider(set_provider)
                console.print(f"[green]✓[/green] Set provider to: {set_provider}")
            except ValueError:
                console.print(f"[red]Invalid provider: {set_provider}[/red]")
                console.print(f"Valid options: {', '.join(p.value for p in Provider)}")
                raise typer.Exit(1)

        if set_model:
            current_config.model = set_model
            console.print(f"[green]✓[/green] Set model to: {set_model}")

        if set_temperature is not None:
            current_config.temperature = set_temperature
            console.print(f"[green]✓[/green] Set temperature to: {set_temperature}")

        config_path = save_config(current_config)
        console.print(f"\n[dim]Saved to: {config_path}[/dim]")
        return

    console.print("[bold blue]CommitMint Configuration[/bold blue]\n")
    console.print("Usage:")
    console.print("  mint config --init          Create default config")
    console.print("  mint config --show          Show current config")
    console.print("  mint config --edit          Edit config file")
    console.print("  mint config --set-provider openai")
    console.print("  mint config --set-model gpt-5")
    console.print("  mint config --set-temp 0.3")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()