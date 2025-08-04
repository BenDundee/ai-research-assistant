import logging
from fastmcp import MCPServer
from typing import List
from controller import Controller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define MCP server
controller = Controller()
server = MCPServer(name="AI-Research-Assistant", version="1.0")


@server.tool(name="search", description="Search for recent, relevant research papers.")
def search() -> List[str]:
    """
    Search for recent papers relevant to the given query.

    Args:
        query (str): A topic or keywords to filter papers.

    Returns:
        list: Titles of papers matching the query.
    """
    return controller.search()

@server.tool(name="deep_dive", description="Does a deep dive on a specific paper")
def deep_dive(url_location: str) -> str:
    """
    Does a deep analysis on a specific paper using its identifier.

    This function takes the url of a research paper (pdf), reads, and summarizes it.
    The user's research interests are considered when building the summary. It returns
    the links to several related research papers in case a larger study is needed.

    :param url_location: URL where pdf of the paper is located
    :type url_location: str
    :return: The result of the deep dive from the controller
    :rtype: str
    """
    return controller.deep_dive(url_location)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger.info("Starting MCP server...")
    server.run(host="127.0.0.1", port=8000)