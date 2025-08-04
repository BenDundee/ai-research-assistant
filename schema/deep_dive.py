from pydantic import BaseModel, Field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from schema.paper import Paper

class DeepDive(BaseModel):
    paper: Paper = Field(..., description="Title of the paper")
    search_terms: List[str] = Field(..., description="Recommended search terms for further research")

    def generate_deep_dive_report(self, related_papers: List[Paper]) -> str:
        output = []
        output.append(f"# {self.paper.title}")
        output.append(f"  {len(self.paper.title)*'-'}")
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
