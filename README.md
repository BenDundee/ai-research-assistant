# AI Research Assistant

An intelligent research paper discovery and summarization system that helps researchers stay up-to-date with the latest publications in their areas of interest. The system automatically fetches, filters, and summarizes research papers using AI, and exposes this functionality through a Model Context Protocol (MCP) server for integration with ChatGPT desktop and other AI assistants.

## Features

### 🔍 **Intelligent Paper Discovery**
- Automatically fetches recent papers from ArXiv
- Filters papers based on configurable research interests
- Uses AI to score relevance and generate focused summaries
- Tracks processing state to avoid duplicate work

### 🤖 **AI-Powered Analysis**
- Leverages OpenRouter API for paper summarization and relevance scoring
- Configurable prompts for customized analysis
- Parallel processing for efficient batch operations
- Relevance scoring from 0-100 based on your research interests

### 🌐 **MCP Server Integration**
- Exposes functionality through Model Context Protocol (MCP)
- Direct integration with ChatGPT desktop client
- Two main tools: `search` and `fetch`
- RESTful API for programmatic access

### ⚙️ **Modular Architecture**
- Extensible processor system for different paper sources
- Configuration-driven operation
- Thread-safe parallel processing
- Comprehensive error handling and logging

## Quick Start

### Prerequisites
- Python 3.13+
- OpenRouter API key
- Firecrawl API key (for web scraping)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-research-assistant
```


2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your settings:
```bash
cp config/secrets.yaml.example config/secrets.yaml
```

5. Edit `config/secrets.yaml` with your API keys:
```yaml
openrouter_api_key: "your-openrouter-key"
openrouter_model: "qwen/qwen3-235b-a22b-thinking-2507"
openai_api_key: "your-openai-key"
kaggle_username: "your-kaggle-username"
kaggle_key: "your-kaggle-key"
```

6. Customize `config/user_config.yaml` with your research interests:
```yaml
research_interests:
  - multi-agent systems
  - chatbot orchestration
  - llm tool use
  - llm planning and reasoning
  - agent frameworks
  - conversational ai
  - llm collaboration
  - tool-augmented language models
  - llm evaluation methods
  - memory in llm agents
```

### Usage

#### MCP Server (Recommended)
Start the MCP server for ChatGPT integration:
```bash
python server.py
```

The server exposes two tools:
- **Search Tool**: Find papers matching configured research interests
- **Deep Dive Tool**: Perform comprehensive analysis of a specific paper

#### Direct Controller Usage
```python
from controller import Controller

# Initialize controller
controller = Controller()

# Search for relevant papers
results = controller.search()
for paper in results:
    print(paper)

# Perform deep dive on specific ArXiv paper
deep_dive_result = controller.deep_dive_arXiv("2507.23701")
print(deep_dive_result)
```

#### Vector Database Setup

#### Direct Paper Processing
```python
from processors.arxiv_processor import ArXivProcessor

# Initialize processor
config = {"url": "https://arxiv.org/list/cs/recent"}
state = {"last_run": "2025-07-25"}
processor = ArXivProcessor(config=config, state=state)

# Fetch and process papers
raw_data = processor.fetch()
papers = processor.parse(raw_data)
new_papers = [p for p in papers if processor.paper_is_new(p)]
results = processor.summarize_and_score_all(new_papers)

# Display results
for paper in results:
    print(f"Title: {paper.title}")
    print(f"Relevance: {paper.relevance}/100")
    print(f"Summary: {paper.summary}")
```


#### MCP Server
Start the MCP server for ChatGPT integration:
```shell script
python server.py
```


The server exposes two tools:

**Search Tool**: Find papers matching the interests configured in `user_config.yaml`

**Fetch Tool**: Get detailed analysis of a specific paper

## Project Structure

```
ai-research-assistant/
├── config/                    # Configuration files
│   ├── prompts.yaml          # AI prompts for summarization
│   ├── secrets.yaml          # API keys (gitignored)
│   ├── user_config.yaml      # Research interests
│   └── state.yaml            # Processing state tracking
├── processors/               # Paper source processors
│   ├── base_processor.py     # Abstract base class
│   └── arxiv_processor.py    # ArXiv-specific implementation
├── schema/                   # Data models
│   └── paper.py             # Paper data structure
├── summarizer/              # AI summarization logic
│   └── summarizer.py        # OpenRouter integration
├── utils/                   # Utility functions
├── server.py               # MCP server implementation
└── README.md               # This file
```


## Configuration

### Research Interests (`config/user_config.yaml`)
Define your research areas to get more relevant results:
```yaml
research_interests:
  - "large language models"
  - "multi-agent systems"
  - "reinforcement learning"
```


### AI Prompts (`config/prompts.yaml`)
Customize how papers are analyzed:
```yaml
summarization_prompt: |
  You are an AI research assistant analyzing papers for relevance.
  User interests: {topics}
  
  Paper: {title}
  Abstract: {abstract}
  
  Provide a relevance score (0-100) and summary focused on user interests.
```


### API Configuration (`config/secrets.yaml`)
```yaml
openrouter_api_key: "your-key-here"
openrouter_model: "gpt-4"
firecrawl_api_key: "your-key-here"
```


## Example Output

```
# Gaussian Variation Field Diffusion for High-fidelity Video-to-4D Synthesis

Publication date: 2025-07-31

**Authors:**
* Bowen Zhang
* Sicheng Xu
* Chuxin Wang

Relevance score: 15/100

This paper focuses on video-to-4D synthesis using Gaussian Splatting and diffusion 
models for generating dynamic 3D content. While not directly related to LLM research, 
the diffusion model techniques could potentially inform future multimodal AI systems.
```


## Development

### Adding New Paper Sources
1. Create a new processor class inheriting from `Processor`
2. Implement `fetch()`, `parse()`, and `_async_summarize_and_score()` methods
3. Register the processor in the factory function