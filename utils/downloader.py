from pathlib import Path

import kagglehub
from kagglehub.config import set_kaggle_credentials


data_dir = Path(__file__).parent.parent / "data" / "vector_db"
data_dir.mkdir(exist_ok=True, parents=True)

set_kaggle_credentials("bendundee", "key")
path = kagglehub.dataset_download("tomtum/openai-arxiv-embeddings")