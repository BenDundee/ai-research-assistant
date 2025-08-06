import logging
from typing import List

from agents import deep_diver, summarize_and_score_all
from processors import load_processors, ArXivProcessor
from schema import DeepDive
from utils import load_config, update_last_run, MilvusDBService, parse_json_possibly_markdown


logger = logging.getLogger(__name__)

RELEVANCE_CUTOFF = 75  # TODO: move to some config or something
db_service = MilvusDBService()

class Controller:

    def __init__(self):
        self.state = load_config("state.yaml")
        self.processor_config = load_config("processor.yaml")
        self.processors = load_processors(self.state, self.processor_config)

    def search(self) -> List[str]:
        relevant_papers = []
        for name, proc in self.processors.items():
            logger.info(f"Fetching data from {name}...")
            raw_data = proc.fetch()
            if raw_data:
                papers = proc.parse(raw_data)
                logger.info(f"Found {len(papers)} papers from {name}, summarizing and scoring...")
                papers = summarize_and_score_all(papers)
                relevant_papers = list(filter(lambda x: x.relevance >= RELEVANCE_CUTOFF, papers))
                relevant_papers.sort(key=lambda x: x.relevance, reverse=True)
                logger.info(f"Isolated {len(relevant_papers)} relevant papers from {name}.")
            else:
                logger.warning(f"************************ Failed to fetch data from {name}.")
        self.state = update_last_run()
        return [p.pretty_print() for p in relevant_papers]

    def deep_dive(self, paper_url: str, top_k: int = 5) -> str:
        """ Perform a deep dive on a specific paper, assume paper is from arXiv

        :param paper_url:
        :param top_k:
        :return:
        """
        deep_dive = DeepDive()
        if "arxiv" in paper_url:
            deep_dive = self._deep_dive_arXiv(paper_url, top_k)
        else:
            raise NotImplementedError("Only arXiv papers are supported for now")

        # Deep dive will always be against arXiv database
        doc_ids = []
        for st in deep_dive.search_terms:
            doc_ids.extend(db_service.query_arXiv(st, top_k))
        doc_ids = list(set(doc_ids))
        processor = ArXivProcessor(self.state, self.processor_config["arxiv"])
        raw_papers = processor.get_several_papers_by_id(doc_ids)
        papers = processor.parse(raw_papers)
        papers = summarize_and_score_all(papers)
        papers.sort(key=lambda x: x.relevance, reverse=True)
        return deep_dive.generate_deep_dive_report(papers)

    def _deep_dive_arXiv(self, paper_url: str, top_k: int = 5) -> DeepDive:
        paper_id = paper_url.split("/")[-1]
        arXiv_processor = ArXivProcessor(self.state, self.processor_config["arxiv"])
        raw_data = arXiv_processor.get_several_papers_by_id([paper_id])
        research_paper = arXiv_processor.parse(raw_data)[0]

        logger.info(f"Starting deep dive on {research_paper.title}...")
        return deep_diver(research_paper, n_terms=5)

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Will take a while ~15 min to spin up DB
    controller = Controller()
    if False:
        results = controller.search()
        with open("results.txt", "w") as f:
            f.write("\n".join(results))
            f.write("\n\n\n\n")

    if True: # 15 minutes for DB to spin up...
        deep_dive = controller.deep_dive("https://arxiv.org/pdf/2507.23701")
        with open("deep_dive.txt", "w") as f:
            f.write(deep_dive)
