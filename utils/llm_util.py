import re
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
REGEX_STRING = r"json\s*(\{.*?\})\s*"

def parse_json_possibly_markdown(string: str) -> Dict[str, Any]:

    match = re.search(REGEX_STRING, string, re.DOTALL)
    if match:
        json_string = match.group(1)
        logger.debug(f"Extracted JSON string:\n{json_string}")
        return json.loads(json_string)
    else:
        logger.debug("No markdown detected, attempting to parse as JSON.")
        return json.loads(string)


if __name__ == "__main__":
    markdown_string = """```json
    {
      "relevance": 85,
      "detailed_summary": "The paper introduces TEXTQUESTS, a benchmark designed to evaluate the intrinsic long-context reasoning and planning capabilities of LLM agents through interactive fiction games. This work is highly relevant to the user's research interests in multi-agent systems, LLM planning and reasoning, memory in LLM agents, and long-context memory and planning in language model agents. The benchmark emphasizes self-contained problem-solving without external tools, focusing on trial-and-error learning and sustained problem-solving within a single interactive session. Key findings include the identification of common failure modes in long-context reasoning and dynamic thinking efficiency, which are critical for understanding the limitations and potential improvements in LLM-based agents. The paper also discusses the implications of these findings for the development of more robust agent frameworks and conversational AI systems.",
      "search_terms": [
        "long-context reasoning in LLM agents",
        "evaluation of LLM planning capabilities",
        "interactive fiction games as AI benchmarks",
        "memory and planning in language model agents",
        "tool-free LLM agent performance"
      ]
    }
    ```"""

    non_markdown_string = """
    {
      "relevance": 85,
      "detailed_summary": "The paper introduces TEXTQUESTS, a benchmark designed to evaluate the intrinsic long-context reasoning and planning capabilities of LLM agents through interactive fiction games. This work is highly relevant to the user's research interests in multi-agent systems, LLM planning and reasoning, memory in LLM agents, and long-context memory and planning in language model agents. The benchmark emphasizes self-contained problem-solving without external tools, focusing on trial-and-error learning and sustained problem-solving within a single interactive session. Key findings include the identification of common failure modes in long-context reasoning and dynamic thinking efficiency, which are critical for understanding the limitations and potential improvements in LLM-based agents. The paper also discusses the implications of these findings for the development of more robust agent frameworks and conversational AI systems.",
      "search_terms": [
        "long-context reasoning in LLM agents",
        "evaluation of LLM planning capabilities",
        "interactive fiction games as AI benchmarks",
        "memory and planning in language model agents",
        "tool-free LLM agent performance"
      ]
    }
    """

    for string in [markdown_string, non_markdown_string]:
        result = parse_json_possibly_markdown(string)
        print(f"Result for {string}: {result}")