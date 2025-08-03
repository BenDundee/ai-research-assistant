import requests
import logging
from typing import List

from .config import load_config

logger = logging.getLogger(__name__)

class OpenAIEmbeddingService:
    """
    Service to fetch embeddings from OpenAI's text embedding model.
    Uses `text-embedding-ada-002`.
    """

    def __init__(self) -> None:
        self.model = "text-embedding-3-large"
        self.api_url = "https://api.openai.com/v1/embeddings"
        self.api_key = load_config("secrets.yaml").get("openai_api_key")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in `secrets.yaml`.")

    def get_embedding(self, input_text: str) -> List[float]:
        """
        Fetch embedding for a single input text.
        :param input_text: The text to embed.
        :return: Embedding vector as a list of floats
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            data = {"input": input_text, "model": self.model }

            response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()

            embedding = response.json()["data"][0]["embedding"]
            return embedding

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching embedding from OpenAI: {e}")
            raise

    def get_batch_embeddings(self, input_texts: List[str]) -> List[List[float]]:
        """
        Fetch embeddings for a batch of input texts.
        :param input_texts: A list of texts to embed.
        :return: List of embeddings, each as a list of floats.
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            data = {"input": input_texts, "model": self.model}

            response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()

            embeddings = [item["embedding"] for item in response.json()["data"]]
            return embeddings

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching batch embeddings from OpenAI: {e}")
            raise


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    embedding_service = OpenAIEmbeddingService()

    # Query Examples
    text_to_embed = "What can AI assistants do?"
    embedding = embedding_service.get_embedding(text_to_embed)
    print(f"Embedding for '{text_to_embed}': {embedding[:5]}...")  # Display first 5 dimensions

    texts_to_embed = ["How does machine learning work?", "Explain neural networks."]
    batch_embeddings = embedding_service.get_batch_embeddings(texts_to_embed)
    print(f"Batch Embeddings: {[e[:5] for e in batch_embeddings]}")  # Display first 5 dimensions of each