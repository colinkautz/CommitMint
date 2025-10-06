from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field, ValidationError
from .providers import Provider, DEFAULT_MODELS


class MintConfig(BaseModel):
    provider: Provider = Field(default=Provider.OPENAI)
    model: Optional[str] = Field(default=None)
    temperature: float = Field(default=0.25, ge=0.0, le=1.0)
    auto_commit: bool = Field(default=False)
    num_options: int = Field(default=5, ge=1, le=10)

    def get_model(self) -> str:
        return self.model or DEFAULT_MODELS[self.provider]


def get_config_path() -> Path:
    return Path.home() / ".mintrc"


def load_config() -> MintConfig:
    #Load configuration from file, or return defaults
    config_path = get_config_path()

    if not config_path.exists():
        return MintConfig()

    try:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            if data is None:
                return MintConfig()
            return MintConfig(**data)
    except (yaml.YAMLError, IOError, OSError, ValidationError):
        return MintConfig()


def save_config(config: MintConfig) -> Path:
    config_path = get_config_path()

    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the config with comments
    config_content = f"""# CommitMint Configuration
# This file configures default behavior for mint

# LLM Provider (openai, anthropic, google)
provider: {config.provider.value}

# Model name (leave empty to use provider default)
model: {config.model if config.model else 'null'}

# Temperature for generation (0.0 = deterministic, 1.0 = creative)
temperature: {config.temperature}

# Auto-commit without confirmation prompt
auto_commit: {str(config.auto_commit).lower()}

# Number of commit message options to generate (1-10)
num_options: {config.num_options}
"""

    with open(config_path, 'w') as f:
        f.write(config_content)

    return config_path


def create_default_config() -> Path:
    # Create a default config file at ~/.mintrc
    config_path = get_config_path()

    config_path.parent.mkdir(parents=True, exist_ok=True)

    default_config = """# CommitMint Configuration
# This file configures default behavior for mint

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
"""

    with open(config_path, 'w') as f:
        f.write(default_config)

    return config_path