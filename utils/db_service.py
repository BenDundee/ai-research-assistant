import logging
from pathlib import Path
import requests
from typing import List

import numpy as np
from pandas import read_csv
from pymilvus import MilvusClient, MilvusException

from utils import load_config

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
COLLECTION_LOCATION = VECTOR_DB_DIR / ".papers.db"

METADATA_CSV = VECTOR_DB_DIR / "papers.csv"
VECTORS_DAT = VECTOR_DB_DIR / "vectors.dat"
COLLECTION_NAME = "papers"


class OpenAIEmbeddingService:
    """
    Service to fetch embeddings from OpenAI's text embedding model.
    Uses `text-embedding-3-large`.
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


class MilvusDBService:
    """
    Simplified wrapper for Milvus using MilvusClient for an embedded server.
    Provides minimal functionality for bulk insertion and query.
    """

    def __init__(self, collection_name: str = COLLECTION_NAME, recreate_collection: bool = False):
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddingService()

        # Start embedded Milvus server using MilvusClient
        self.client = MilvusClient(COLLECTION_LOCATION.as_posix())
        logger.info("Embedded Milvus server started.")

        # Initialize or recreate the collection
        if recreate_collection and self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)
            logger.info(f"Dropped existing collection: {self.collection_name}")
        self._setup_collection()

    def _setup_collection(self) -> None:
        """Create or get the collection using MilvusClient."""
        if self.client.has_collection(self.collection_name):
            logger.info(f"Using existing collection: {self.collection_name}")
        else:
            # Create collection using MilvusClient
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=3072,
                primary_field_name="id",
                id_type="string",
                vector_field_name="vector",
                metric_type="COSINE",
                auto_id=False,
                max_length=25
            )
            logger.info(f"Created new collection: {self.collection_name}")

    def load_arXiv_data(self):
        self.bulk_insert(metadata_csv=METADATA_CSV, vectors_dat=VECTORS_DAT)

    def bulk_insert(self, metadata_csv: Path, vectors_dat: Path, chunk_size: int = 1000) -> None:
        """
        Insert data into the collection in chunks.
        :param metadata_csv: Path to metadata CSV file.
        :param vectors_dat: Path to precomputed vectors file.
        :param chunk_size: Number of records to process in each chunk (reduced from 100,000 to 1,000).
        """
        logger.info(f"Starting bulk insert for {metadata_csv} and {vectors_dat}")

        # Initialize vector memory map
        vectors = np.memmap(vectors_dat, dtype=np.float32, mode="r").reshape((-1, 3072))
        num_rows = vectors.shape[0]

        logger.info(f"Total records to process: {num_rows}")
        logger.info(f"Processing in chunks of {chunk_size} records")

        # Process the dataset in chunks
        for chunk_idx in range(0, num_rows, chunk_size):
            chunk_end = min(chunk_idx + chunk_size, num_rows)
            chunk_vectors = vectors[chunk_idx:chunk_end]
            chunk_metadata = read_csv(
                metadata_csv,
                skiprows=chunk_idx + 1,
                nrows=len(chunk_vectors),
                names=['index', 'id', 'journal'],
                dtype={'index': int, 'id': str, 'journal': str}
            )

            # Prepare data for MilvusClient
            batch_data = []
            for i, (vector, _, metadata) in enumerate(zip(chunk_vectors, range(len(chunk_vectors)), chunk_metadata.itertuples())):
                batch_data.append({
                    "id": str(metadata.id),
                    "vector": vector.tolist(),
                    "journal_name": metadata.journal
                })

            try:
                # Insert batch using MilvusClient
                logger.info(f"Inserting chunk {chunk_idx//chunk_size + 1}/{(num_rows + chunk_size - 1)//chunk_size}: records {chunk_idx}-{chunk_end-1} ({len(chunk_vectors)} records)")
                self.client.insert(collection_name=self.collection_name, data=batch_data)
                logger.info(f"Successfully inserted chunk {chunk_idx//chunk_size + 1}")
            except MilvusException as e:
                logger.error(f"Failed to insert chunk {chunk_idx}-{chunk_end}: {e}")
                raise

        logger.info("Data insertion completed successfully")

    def query_arXiv(self, query: str, top_k: int = 10) -> List[str]:
        """
        Perform a similarity query on the arXiv collection.
        :param query: The query text to search for.
        :param top_k: Number of top results to return.
        :return: List of query results with distances.
        """
        query_embedding = self.embeddings.get_embedding(query)

        # Perform the search using MilvusClient
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            limit=top_k,
            output_fields=["id", "journal_name"]
        )
        ids = results[0].ids
        return ids


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Initialize MilvusDBService
    # db_service = MilvusDBService(recreate_collection=True)
    db_service = MilvusDBService(recreate_collection=False)

    # Bulk insert data
    # db_service.load_arXiv_data()

    # Example query: https://arxivxplorer.com/?q=reinforcement+learning+from+human+feedback
    query_term = "reinforcement learning from human feedback"
    results = db_service.query_arXiv(query_term, top_k=5)

    print("Top search results:")
    for result_set in results:
        for result in result_set:
            print(f"ID: {result['id']}, Distance: {result['distance']}, Journal: {result.get('journal_name', '')}")

    results = (""" Top search results :
        ID: 2504.12501, Distance: 0.6638619899749756, Journal: arxiv (https://arxiv.org/abs/2504.12501)
        ID: 2312.14925, Distance: 0.66007399559021, Journal: arxiv (https://arxiv.org/abs/2312.14925)
        ID: 2504.14732, Distance: 0.6364675164222717, Journal: arxiv (https://arxiv.org/abs/2504.14732)
        ID: 1902.04257, Distance: 0.6266356706619263, Journal: arxiv (https://arxiv.org/abs/1902.04257)
        ID: 2211.11602, Distance: 0.6254575848579407, Journal: arxiv (https://arxiv.org/abs/2211.11602)
    """)