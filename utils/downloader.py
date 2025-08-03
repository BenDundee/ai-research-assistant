import kagglehub
from kagglehub.config import set_kaggle_credentials
from pathlib import Path

data_dir = Path(__file__).parent.parent / "data" / "vector_db"
data_dir.mkdir(exist_ok=True, parents=True)

set_kaggle_credentials("bendundee", "key")
path = kagglehub.dataset_download("tomtum/openai-arxiv-embeddings")