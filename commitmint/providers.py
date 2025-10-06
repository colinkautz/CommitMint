from enum import Enum
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


DEFAULT_MODELS = {
    Provider.OPENAI: "gpt-5",
    Provider.ANTHROPIC: "claude-sonnet-4-5",
    Provider.GOOGLE: "gemini-2.5-flash"
}

API_KEY_VARS = {
    Provider.OPENAI: "OPENAI_API_KEY",
    Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
    Provider.GOOGLE: "GOOGLE_API_KEY",
}

def get_llm(provider: Provider, model: Optional[str] = None, temperature: float = 0.25):
    if model is None:
        model = DEFAULT_MODELS[provider]

    if provider == Provider.OPENAI:
        return ChatOpenAI(model=model, temperature=temperature)

    elif provider == Provider.ANTHROPIC:
        return ChatAnthropic(model_name=model, temperature=temperature)

    elif provider == Provider.GOOGLE:
        return ChatGoogleGenerativeAI(model=model, temperature=temperature)

    else:
        raise ValueError(f"Unsupported provider: {provider}")

def check_api_key(provider: Provider) -> bool:
    import os

    key_var = API_KEY_VARS.get(provider)
    return bool(os.environ.get(key_var))

def get_provider_info(provider: Provider) -> dict:
    return {
        "name": provider.value,
        "default_model": DEFAULT_MODELS[provider],
        "api_key_var": API_KEY_VARS[provider],
        "requires_api_key": API_KEY_VARS[provider] is not None
    }
