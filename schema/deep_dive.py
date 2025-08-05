from pydantic import BaseModel, Field
from typing import List, Optional

from schema.paper import Paper

class DeepDive(BaseModel):
    paper: Optional[Paper] = Field(Paper, description="Title of the paper")
    search_terms: Optional[List[str]] = Field(list, description="Recommended search terms for further research")

    def generate_deep_dive_report(self, related_papers: List[Paper]) -> str:
        output = [f"# {self.paper.title}", f"  {len(self.paper.title) * '-'}"]
        for author in self.paper.authors:
            output.append(f"  * {author}")
        output.append(f"\n# Abstract")
        output.append(f"\n{self.paper.abstract}")
        output.append(f"\n# Summary")
        output.append(f"\n{self.paper.summary}")
        output.append(f"\n# Related papers")
        for paper in related_papers:
            output.append(f"* {paper.title}")
        output.append(f"\n{80*'-'}")
        output.append(f"\n**Search terms:**")
        return "\n".join(output) + "\n"
