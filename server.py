import logging
from fastmcp import MCPServer
from typing import List
from controller import Controller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define MCP server
controller = Controller()
server = MCPServer(name="AIResearchAssistant", version="1.0")

# MCP tool: Search for papers
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
def deep_dive() -> str:
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger.info("Starting MCP server...")
    server.run(host="127.0.0.1", port=8000)