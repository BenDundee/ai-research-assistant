from pydantic import BaseModel, Field
from typing import Optional


class Paper(BaseModel):
    """Model for a paper"""
    title: Optional[str] = Field(None, description="Title of the paper")
    authors: Optional[list[str]] = Field(list, description="List of authors")
    link: Optional[str] = Field(..., description="Link to the paper")
    abstract: Optional[str] = Field(..., description="Abstract of the paper")