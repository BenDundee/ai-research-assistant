from pydantic import BaseModel, Field
from typing import List


class DeepDive(BaseModel):
    title: str = Field(..., description="Title of the paper")
    relevance: int = Field(..., description="Relevance score, in relation to research interests")
    detailed_summary: str = Field(..., description="Detailed summary of the paper")
    search_terms: List[str] = Field(..., description="Recommended search terms for further research")
