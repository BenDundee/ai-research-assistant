import requests
import logging
from pathlib import Path
import yaml
from openai import OpenAI


base_dir = Path(__file__).parent.parent.resolve()
config_dir = base_dir / "config"


def fetch_openrouter_api_key_and_model() -> (str, str):
    """
    Load the OpenRouter API key and model name from `config/secrets.yaml`.

    Returns:
        tuple: (API key, model name)
    """
    try:
        with open(config_dir / "secrets.yaml", "r") as file:
            secrets = yaml.safe_load(file)
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
        with open(config_dir / "prompts.yaml", "r") as file:
            prompts = yaml.safe_load(file)
            return prompts.get("summarization_prompt", "")
    except Exception as e:
        logging.error(f"Failed to load summarization prompt from prompts.yaml: {e}")
        return ""


def get_summary_and_relevance(prompt_input: dict) -> dict:
    """
    Call OpenRouter API to summarize and assign a relevance score.

    Args:
        prompt_input (dict): Input fields for the LLM prompt.

    Returns:
        dict: A dictionary containing "relevance" and "summary" fields.
    """
    api_key, model = fetch_openrouter_api_key_and_model()
    if not api_key:
        raise ValueError("OpenRouter API key not found in `secrets.yaml`.")

    prompt_template = load_summarization_prompt()
    if not prompt_template:
        raise ValueError("Summarization prompt not found in `prompts.yaml`.")

    # Fill the prompt template with the input data
    prompt = prompt_template.format(
        topics=prompt_input["topics"],
        title=prompt_input["title"],
        abstract=prompt_input["abstract"],
        link=prompt_input["link"],
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
        return {
            "summary": result.get("summary", ""),
            "relevance": result.get("relevance", 0),
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"OpenRouter request failed: {e}")
        raise RuntimeError("Failed to communicate with OpenRouter API.")
    except Exception as e:
        logging.error(f"Error processing OpenRouter response: {e}")
        return {"summary": "", "relevance": 0}


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    # Mock input
    prompt_input = {
        "topics": "chatbot, large language models",
        "title": "Advancements in Chatbot Development",
        "abstract": "This paper explores recent advancements in chatbot technologies, particularly focusing on LLM architectures.",
        "link": "https://arxiv.org/abs/1234.56789",
    }

    try:
        result = get_summary_and_relevance(prompt_input)
        print(f"Summary: {result['summary']}")
        print(f"Relevance: {result['relevance']}")
    except Exception as e:
        print(f"Error: {e}")