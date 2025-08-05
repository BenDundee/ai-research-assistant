from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Paper(BaseModel):
    """Model for a paper"""
    title: Optional[str] = Field(None, description="Title of the paper")
    authors: Optional[list[str]] = Field(list, description="List of authors")
    full_text_link: Optional[str] = Field(None, description="Link to the paper")
    abstract_link: Optional[str] = Field(None, description="Link to the abstract")
    abstract: Optional[str] = Field(None, description="Abstract of the paper")
    published: Optional[datetime] = Field(None, description="Date of publication")
    summary: Optional[str] = Field(None, description="Short summary of the paper, in relation to research interests")
    relevance: Optional[int] = Field(None, description="Relevance score, in relation to research interests")
    
    def pretty_print(self) -> str:
        output = ["\n", 80*'-']
        if self.title:
            output.append(f"# {self.title}")
        if self.authors:
            output.append("\n# Authors:")
            for author in self.authors:
                output.append(f"  * {author}")
        if self.relevance is not None:
            output.append(f"\n# Relevance score: {self.relevance}/100")
        if self.summary:
            output.append("\n# Summary")
            output.append(f"\n{self.summary}")
        else:
            output.append("\n# Abstract")
            output.append(f"\n{self.abstract}")
        return "\n".join(output)
