import logging
import requests

from schema import DeepDive, Paper
from utils import fetch_openrouter_api_key_and_model, load_config, parse_json_possibly_markdown


logger = logging.getLogger(__name__)


def load_deep_dive_prompt() -> str:
    """
    Load the summarization prompt template from `config/prompts.yaml`.

    Returns:
        str: The summarization prompt.
    """
    try:
        prompts = load_config("prompts.yaml")
        return prompts.get("deep_dive_prompt", "")
    except Exception as e:
        logger.error(f"Failed to load deep dive prompt from prompts.yaml: {e}")
        return ""


def deep_diver(paper: Paper, n_terms: int=5) -> DeepDive:
    """

    :param n_terms:
    :param paper: Paper to research
    :return:
    """
    api_key, model = fetch_openrouter_api_key_and_model()
    if not api_key:
        raise ValueError("OpenRouter API key not found in `secrets.yaml`.")

    prompt_template = load_deep_dive_prompt()
    if not prompt_template:
        raise ValueError("Deep dive prompt not found in `prompts.yaml`.")

    user_config = load_config("user_config.yaml")
    if not user_config:
        raise ValueError("User config not found in `user_config.yaml`.")

    # Fill the prompt template with the input data
    research_interests = f"  - {'\n  - '.join(user_config['research_interests'])}"

    prompt = prompt_template.format(
        topics=research_interests,
        n_terms=n_terms
    )

    try:
        # TODO: Move this to utils?
        # Use requests instead of OpenAI client
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        plugins = [{"id": "file-parser", "pdf": {"engine": "pdf-text"}}]
        payload = {
            "model": model,
            "plugins": plugins,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "file", "file": {"filename": "document.pdf", "file_data": paper.full_text_link}}
                ]}
            ]
        }

        logger.debug(f"Calling OpenRouter model: {model} with prompt:\n{prompt}")
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        result = parse_json_possibly_markdown(content)

        # Check fields -- maybe do some error handling in the future...
        detailed_summary = result.get("detailed_summary", "")
        relevance = result.get("relevance", None)
        search_terms = result.get("search_terms", [])
        paper.summary = detailed_summary
        paper.relevance = relevance
        deep_dive = DeepDive(paper=paper, search_terms=search_terms)
        return deep_dive

    except requests.exceptions.RequestException as e:
        logging.error(f"OpenRouter request failed: {e}")
        raise RuntimeError("Failed to communicate with OpenRouter API.")
    except Exception as e:
        logging.error(f"Error processing OpenRouter response: {e}")
        return DeepDive()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    _paper = Paper(full_text_link="https://arxiv.org/pdf/2507.23701.pdf")
    result = deep_diver(_paper)
    print("wait")