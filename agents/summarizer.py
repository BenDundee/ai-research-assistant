import requests
import logging
from pathlib import Path
import yaml
from utils import load_config, fetch_openrouter_api_key_and_model, parse_json_possibly_markdown
from typing import List
from schema import Paper
from concurrent.futures import ThreadPoolExecutor, as_completed

base_dir = Path(__file__).parent.parent.resolve()
config_dir = base_dir / "config"

logger = logging.getLogger(__name__)


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
        logger.error(f"Failed to load summarization prompt from prompts.yaml: {e}")
        return ""


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

    user_config = load_config("user_config.yaml")
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
        # Use requests instead of OpenAI client
        logger.debug(f"Calling OpenRouter model: {model} with prompt:\n{prompt}")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        response_data = response.json()
        
        content = response_data["choices"][0]["message"]["content"]
        #result = yaml.safe_load(content)
        result = parse_json_possibly_markdown(content)
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


def summarize_and_score_all(papers: List[Paper]) -> List[Paper]:
    """
    Process multiple papers concurrently using threads.

    Args:
        papers (List[Paper]): List of papers to process

    Returns:
        List[Paper]: List of processed papers with summaries and relevance scores
    """
    processed_papers = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_paper = {executor.submit(get_summary_and_relevance, paper): paper for paper in papers}
        for future in as_completed(future_to_paper):
            try:
                processed_paper = future.result()
                processed_papers.append(processed_paper)
            except Exception as e:
                logger.error(f"Paper processing failed: {e}")

    return sorted(processed_papers, key=lambda p: p.relevance, reverse=True)


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