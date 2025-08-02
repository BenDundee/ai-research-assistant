import requests
import logging
from pathlib import Path
import yaml
from openai import OpenAI
from utils import load_config
from typing import Dict, Any
from schema import Paper


base_dir = Path(__file__).parent.parent.resolve()
config_dir = base_dir / "config"


def fetch_openrouter_api_key_and_model() -> (str, str):
    """
    Load the OpenRouter API key and model name from `config/secrets.yaml`.

    Returns:
        tuple: (API key, model name)
    """
    try:
        secrets = load_config("secrets.yaml")
        api_key = secrets.get("openrouter_api_key", "")
        model = secrets.get("openrouter_model", "gpt-4")  # Default model
        return api_key, model
    except Exception as e:
        logging.error(f"Failed to load OpenRouter API key or model from secrets.yaml: {e}")
        return "", ""


def load_summarization_prompt() -> str:
    """
    Load the summarization prompt template from `config/prompts.yaml`.

    Returns:
        str: The summarization prompt.
    """
    try:
        prompts = load_config("prompts.yaml")
        return prompts.get("summarization_prompt", "")
    except Exception as e:
        logging.error(f"Failed to load summarization prompt from prompts.yaml: {e}")
        return ""


def load_user_config() -> Dict[str, Any]:
    user_config = load_config("user_config.yaml")
    return user_config


def get_summary_and_relevance(paper: Paper) -> Paper:
    """
    Call OpenRouter API to summarize and assign a relevance score.

    Args:
        paper (Paper): A dictionary containing paper metadata.

    Returns:
        Paper: The input paper with updated summary and relevance.
    """
    api_key, model = fetch_openrouter_api_key_and_model()
    if not api_key:
        raise ValueError("OpenRouter API key not found in `secrets.yaml`.")

    prompt_template = load_summarization_prompt()
    if not prompt_template:
        raise ValueError("Summarization prompt not found in `prompts.yaml`.")

    user_config = load_user_config()
    if not user_config:
        raise ValueError("User config not found in `user_config.yaml`.")

    # Fill the prompt template with the input data
    prompt = prompt_template.format(
        topics=user_config["research_interests"],
        title=paper.title,
        abstract=paper.abstract,
        full_text_link=paper.full_text_link,
    )

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        content = completion.choices[0].message.content
        result = yaml.safe_load(content)
        paper.summary = result.get("summary", "")
        paper.relevance = result.get("relevance", 0)
        return paper

    except requests.exceptions.RequestException as e:
        logging.error(f"OpenRouter request failed: {e}")
        raise RuntimeError("Failed to communicate with OpenRouter API.")
    except Exception as e:
        logging.error(f"Error processing OpenRouter response: {e}")
        paper.summary = ""
        paper.relevance = 0
        return paper


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    # Mock input
    paper = Paper(
        title ="Advancements in Chatbot Development",
        abstract="This paper explores recent advancements in chatbot technologies, particularly focusing on LLM architectures.",
        abstract_link="https://arxiv.org/abs/1234.56789",
        full_text_link="https://arxiv.org/pdf/1234.56789.pdf"
    )

    try:
        paper = get_summary_and_relevance(paper)
        print(f"Summary: {paper.summary}")
        print(f"Relevance: {paper.relevance}")
    except Exception as e:
        print(f"Error: {e}")