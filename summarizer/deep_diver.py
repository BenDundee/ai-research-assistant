import logging
import requests
import yaml

from schema import DeepDive
from utils import fetch_openrouter_api_key_and_model, load_config

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


def deep_diver(url_pdf: str, n_terms: int=5) -> DeepDive:
    """

    :param n_terms:
    :param url_pdf: url location of pdf
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
        # TODO: Move this to utils
        # Use requests instead of OpenAI client
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What are the main points in this document?"},
                    {"type": "file", "file": {"filename": "document.pdf", "file_data": url_pdf}}
                ]}
            ]}

        logger.debug(f"Calling OpenRouter model: {model} with prompt:\n{prompt}")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )

        response.raise_for_status()  # Raise an exception for bad status codes
        response_data = response.json()

        content = response_data["choices"][0]["message"]["content"]
        result = yaml.safe_load(content)
        output = DeepDive(**result)
        return output
    except requests.exceptions.RequestException as e:
        logging.error(f"OpenRouter request failed: {e}")
        raise RuntimeError("Failed to communicate with OpenRouter API.")
    except Exception as e:
        logging.error(f"Error processing OpenRouter response: {e}")
        return DeepDive()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    result = deep_diver("https://arxiv.org/abs/2507.23701")