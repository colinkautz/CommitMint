# CommitMint

**The freshest AI-powered git commit message generator**

CommitMint uses AI to analyze your git diffs and generate multiple high-quality, conventional commit message options. Never stare at `git commit -m ""` again.

## Features

- **AI-Powered**: Generates multiple commit message options using state-of-the-art LLMs
- **Conventional Commits**: Follows the [Conventional Commits](https://www.conventionalcommits.org/) specification
- **Beautiful CLI**: Rich, interactive terminal interface
- **Multiple Providers**: Support for OpenAI, Anthropic Claude, and Google Gemini
- **Configurable**: Save your preferences in `~/.mintrc`
- **Interactive**: Select, edit, and commit all in one flow
- **Smart Analysis**: Understands your code changes and generates relevant messages

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/commitmint.git
cd commitmint

# Install
pip install -e .
```

### Setup

1. Set your API key in `.env`:
```bash
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

2. Stage your changes:
```bash
git add .
```

3. Generate commit messages:
```bash
mint
```

That's it!

## Usage

### Basic Usage

```bash
# Generate commit messages for staged changes
mint

# Use unstaged changes
mint --unstaged

# Auto-commit without confirmation
mint --commit
```

### Advanced Usage

```bash
# Use a different provider
mint --provider anthropic

# Use a specific model
mint --model gpt-4o

# Adjust temperature (creativity)
mint --temperature 0.5
```

## Configuration

CommitMint can be configured via `~/.mintrc`:

```bash
# Create default config
mint config --init

# Edit config
mint config --edit

# Show current config
mint config --show

# Set specific values
mint config --set-provider anthropic
mint config --set-model claude-sonnet-4-20250514
mint config --set-temperature 0.3
```

### Configuration Options

```yaml
# LLM Provider (openai, anthropic, google)
provider: openai

# Model name (leave empty to use provider default)
model: null

# Temperature for generation (0.0 = deterministic, 1.0 = creative)
temperature: 0.25

# Auto-commit without confirmation prompt
auto_commit: false

# Number of commit message options to generate (1-10)
num_options: 5
```

## Supported Providers

| Provider  | Default Model            | API Key Required  |
|-----------|--------------------------|-------------------|
| OpenAI    | gpt-4o                   | OPENAI_API_KEY    |
| Anthropic | claude-sonnet-4-20250514 | ANTHROPIC_API_KEY |
| Google    | gemini-2.0-flash-exp     | GOOGLE_API_KEY    |

```bash
# List all providers
mint providers
```

### Setting up API Keys

Add your API keys to `.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Google
GOOGLE_API_KEY=your-google-api-key
```

## Examples

### Example Output

```bash
$ mint

mint - Generating commit messages...

Using openai with model: gpt-4o

Generated commit messages:

┌───┬─────────────────────────────────────────────────────┬────────────┐
│ # │ Message                                             │ Confidence │
├───┼─────────────────────────────────────────────────────┼────────────┤
│ 1 │ feat(cli): add interactive commit message selection │        95% │
│ 2 │ feat: implement AI-powered commit generator         │        92% │
│ 3 │ chore: add CommitMint CLI tool                      │        88% │
│ 4 │ feat(git): add diff analysis and message generation │        90% │
│ 5 │ docs: add README and configuration examples         │        85% │
└───┴─────────────────────────────────────────────────────┴────────────┘

Select an option: [1/2/3/4/5/quit] (1): 1

Selected commit message:
┌─────────────────────────────────────────────────────────┐
│ feat(cli): add interactive commit message selection     │
│                                                          │
│ Implement a rich CLI interface that allows users to     │
│ select from AI-generated commit message options with    │
│ confidence scores.                                       │
└─────────────────────────────────────────────────────────┘

Do you want to edit this message? [y/N]: n
Do you want to commit this message? [Y/n]: y
Committed successfully!
```

## Development

### Project Structure

```
commitmint/
├── commitmint/
│   ├── __init__.py
│   ├── cli.py           # CLI interface
│   ├── config.py        # Configuration management
│   ├── generator.py     # LLM message generation
│   ├── git_handler.py   # Git operations
│   ├── models.py        # Pydantic models
│   ├── providers.py     # LLM provider configs
│   └── prompts/
│       ├── system_prompt.txt
│       └── human_prompt.txt
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Use CommitMint to generate your commit message!
5. Push to your branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

GPL-3.0 License - see [LICENSE](LICENSE) for details

This ensures that any modifications or derivative works must also be open source under GPL-3.0.

## Acknowledgments

- Built with [LangChain](https://langchain.com)
- CLI powered by [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
- Inspired by the pain of writing commit messages at 2 AM

## Support

- Found a bug? [Open an issue](https://github.com/colinkautz/commitmint/issues)
- Have a feature idea? [Start a discussion](https://github.com/colinkautz/commitmint/discussions)
- Like CommitMint? Give us a star!

---

Made with care by [Colin K.](https://github.com/colinkautz)

**Keep your commits fresh!**