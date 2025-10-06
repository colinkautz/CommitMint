from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from .models import DiffAnalysis, CommitOptions
from .providers import Provider, get_llm


def load_prompt(file: str) -> str:
    prompts_dir = Path(__file__).parent / "prompts"
    prompt_file = prompts_dir / file

    if not prompt_file.exists():
        raise FileNotFoundError(f"{file} not found")

    return prompt_file.read_text().strip()


def generate_messages(
    diff_text: str,
    analysis: DiffAnalysis,
    provider: Provider = None,
    model_name: str = None,
    temperature: float = None
) -> CommitOptions:
    from .config import load_config
    cfg = load_config()

    if provider is None:
        provider = cfg.provider
    if model_name is None:
        model_name = cfg.get_model()
    if temperature is None:
        temperature = cfg.temperature

    llm = get_llm(provider, model_name, temperature)
    parser = PydanticOutputParser(pydantic_object=CommitOptions)

    system_prompt = load_prompt("system_prompt.txt")
    human_prompt = load_prompt("human_prompt.txt")

    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])

    chain = prompt | llm | parser

    file_list = "\n".join(
        f"- {f.path}: +{f.additions} -{f.deletions}"
        for f in analysis.files_changed
    )

    max_length = 3500
    truncated_diff = diff_text[:max_length]
    if len(truncated_diff) > max_length:
        truncated_diff += "\n...(truncated)"

    result = chain.invoke({
        "format_instructions": parser.get_format_instructions(),
        "num_files": len(analysis.files_changed),
        "additions": analysis.total_additions,
        "deletions": analysis.total_deletions,
        "file_list": file_list or "No files parsed",
        "diff_content": truncated_diff
    })

    return result