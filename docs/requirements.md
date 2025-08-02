# AI Research Scraper — Requirements & Architecture

## Goal
Build a modular scraping and summarization system that:
- Pulls recent research papers/blog posts from multiple AI-related sources.
- Filters them by **topics of interest** (high-recall first pass).
- Uses an **LLM as a high-precision second pass** to score and summarize.
- Stores the **last run date** and only processes new papers since that date.
- Outputs a sorted digest (Markdown or JSON) ranked by **relevance**.
- **Exposes this functionality as an MCP (Model Context Protocol) server** so the ChatGPT desktop app can call it directly.

---

## Key Features

### 1. Multi-source support
- Sources are configured in **`config.yaml`**.
- Each source has:
  - `name` — friendly name.
  - `url` — where to scrape.
  - `type` — which **Processor** class to use.
- Example:
```yaml
sites:
  - name: arxiv_cs_recent
    url: https://arxiv.org/list/cs/recent
    type: arxiv
  - name: huggingface_blog
    url: https://huggingface.co/blog
    type: blog
````

---

### 2. Config-driven topics

* **Topics list** in `config.yaml` is the first-pass filter.
* Example:

```yaml
topics:
  - multi-agent
  - chatbot
  - llm orchestration
  - reasoning model
```

* This **high recall** step filters out obvious irrelevant content before hitting the LLM.

---

### 3. Prompt-driven summarization

* Summarization prompt lives in **`prompts.yaml`** (not in code).
* Supports placeholders:

  * `{topics}`
  * `{title}`
  * `{abstract}`
  * `{link}`
* Example:

```yaml
summarization_prompt: |
  You are an AI research assistant. 
  The user is interested in the following research topics: {topics}.

  You are given a paper with the following metadata:

  Title: {title}
  Abstract: {abstract}
  Link: {link}

  First, determine how relevant this paper is to the user's interests.
  Assign a **relevance score from 0 to 100**.

  Then, provide a short summary (3-5 sentences) that focuses on aspects of the paper relevant to the user's interests.

  Respond in JSON:
  {
      "relevance": <integer 0-100>,
      "summary": "<summary text>"
  }
```

---

### 4. Modular processor architecture

* Each **Processor**:

  * Knows how to fetch its source (`fetch()`).
  * Knows how to parse it into `{title, abstract, link, date}`.
  * Knows how to check if a paper is **new** since `last_run`.
  * Filters by topic (`topic_match()`).
  * Calls summarization & scoring (`summarize_and_score()`).
  * Returns a **list of normalized paper dicts**.
* Structure:

```
processors/
│
├── base_processor.py
├── arxiv_processor.py
├── blog_processor.py
├── publist_processor.py
└── __init__.py
```

---

### 5. Firecrawl API for fetching

* **API key** stored in `secrets.yaml`:

```yaml
firecrawl_api_key: "YOUR_KEY"
openai_api_key: "YOUR_KEY"
```

* `fetch_page(url)` sends request:

```python
payload = {"url": url, "formats": ["markdown"]}
```

* Returns **cleaned markdown** for parsing.

---

### 6. State tracking

* **`state.yaml`** stores:

```yaml
last_run: "2025-08-01"
```

* On each run:

  * Use `last_run` to decide if a paper is new.
  * Update `last_run` to today after successful scrape.

---

### 7. Output

* Supports **Markdown** or **JSON** (set in `config.yaml`).
* Markdown output includes:

  * Title
  * Link
  * Relevance score
  * Summary
* Sorted **descending by relevance**.

---

### 8. MCP Server Integration

* Expose scraper functionality as an **MCP server** so the ChatGPT desktop app can call it directly in agent mode.
* Implemented using **FastMCP**.
* Two main tools exposed:

  * **`search(query: str) -> list[str]`**

    * Runs scraper pipeline with `topics = [query]` or uses existing data store to filter.
    * Returns list of **record IDs** (e.g., arXiv IDs or unique paper titles) ordered by relevance.
  * **`fetch(id: str) -> dict`**

    * Returns `{title, abstract, link, relevance, summary, date}` for the specified paper ID.

**Tool usage flow:**

```
ChatGPT asks “Find me recent multi-agent chatbot research.”
 ↓
search("multi-agent chatbot")  → ["Paper A", "Paper B"]
 ↓
fetch("Paper A") → {metadata + summary}
 ↓
ChatGPT uses returned data to answer user query
```

**Benefits:**

* Allows ChatGPT desktop to dynamically query and fetch relevant papers.
* Avoids re-scraping for every request (can serve from cached store).
* Standardizes responses for better LLM tool use.

---

## Data Flow

```
config.yaml → [get_processor(site) for site in sites]
   ↓
Processor.fetch() → Firecrawl API
   ↓
Processor.parse() → [{title, abstract, link, date}, ...]
   ↓
Processor.paper_is_new(last_run) → keep only new papers
   ↓
Processor.topic_match(topics) → keep only relevant topics
   ↓
summarize_and_score() → relevance + summary
   ↓
Return normalized dicts
   ↓
Aggregate + sort by relevance
   ↓
Serve via MCP search/fetch tools
   ↓
Save output (Markdown/JSON)
   ↓
Update state.yaml with new last_run date
```

---

## Example — `ArxivProcessor.paper_is_new()`

For arXiv:

* Detect lines like `"Submitted on 1 Aug 2025"`.
* Parse date with:

```python
datetime.strptime(date_str, "%d %b %Y").date()
```

* Compare against `last_run_date`.

---

## Important Implementation Decisions

1. **Prompt externalization** — All LLM prompts live in `prompts.yaml`, allowing easy updates without code changes.
2. **High recall → high precision** — First pass is keyword match, second pass is LLM relevance + summary.
3. **Encapsulation** — Parsing, freshness filtering, summarization are in the **same Processor** class for each site.
4. **Extensible sources** — Adding a new site = add a new Processor subclass + register in `get_processor()`.
5. **Date awareness** — Processors can filter out old papers using `state.yaml`’s `last_run`.
6. **Firecrawl** — Unified way to fetch clean markdown from any URL, reducing parsing complexity.
7. **Sorted outputs** — Always sort by relevance before writing output.
8. **MCP API** — `search()` and `fetch()` tools allow ChatGPT desktop to dynamically retrieve relevant research.

---

## Proposed Project Structure

```
ai-research-scraper/
│
├── config
│   ├── config.yaml          # Sites + topics config
│   ├── prompts.yaml         # LLM prompt templates
│   ├── secrets.yaml         # API keys (gitignored)
│   ├── state.yaml           # Last run date (auto-updated by scraper)
│
├── scraper.py               # CLI entry point to run the scraper pipeline
├── server.py                # MCP server entry point (FastMCP)
│
├── processors/              # Site-specific processors
│   ├── base_processor.py    # Shared interface + common logic
│   ├── arxiv_processor.py   # Arxiv-specific parsing/freshness logic
│   ├── blog_processor.py    # Blog/news parsing/freshness logic
│   ├── publist_processor.py # Publication list parsing/freshness logic
│   └── __init__.py          # get_processor() factory
│
├── summarizer/              
│   ├── __init__.py
│   └── summarizer.py        # summarize_and_score() + OpenAI integration
│
├── utils/
│   ├── fetcher.py           # Firecrawl fetch_page()
│   ├── yaml_loader.py       # load_yaml() / save_yaml()
│   ├── output_writer.py     # Optional helper for JSON/Markdown output
│   └── __init__.py
│
├── mcp_tools/               # MCP tool implementations
│   ├── search_tool.py       # search(query) logic using scraper/data store
│   ├── fetch_tool.py        # fetch(id) logic returning paper metadata
│   └── __init__.py
│
├── data/                    # Optional storage for cached scrape results
│   └── papers.json
│
├── docs/
│   ├── requirements.md      # This requirements & architecture doc
│   └── mcp_integration.md   # MCP server-specific notes
│
├── requirements.txt         # Python dependencies
└── README.md                # Project overview

```

## Updates Based on Recent Decisions

### 1. Supported Sources
- Initially, support only **Arxiv** and **Hugging Face Blog**.
- Additional sources to be added later.

### 2. Output
- Start with a **simple ranked list** of relevant papers (titles, link, relevance, summary).
- Future iterations may include more advanced formatting (e.g., collapsible sections).

### 3. Error Handling
- Use Python's `logging` module for warning and error logging.
- Ignore failed source scrapes for now and skip to the next source.
- Any significant API failures are treated as definitive.

### 4. State Tracking
- If `state.yaml` is missing or empty:
  - Default `last_run` should be **one week prior to today**.
  - Log a warning indicating no `last_run` was specified.

### 5. MCP Server Tools
- Expose two tools:
  - **`search(query: str)`**:
    - Allows querying papers relevant to one or more topics.
  - **`fetch(id: str)`** or batch fetching:
    - Returns metadata, relevance, and summary for one or multiple paper IDs.
- No threading/async to simplify the design since latency isn't critical.

### 6. Authentication
- No authentication needed as the **MCP server runs locally**.

### 7. Processor Design
- Push **all processing operations** (`fetch()`, `parse()`, `is_new()`, `topic_match()`, `summarize_and_score()`) to subclasses.
- The `Processor` base class will serve as a simple interface definition or provide minimal shared logic.

### 8. Summarization Backend
- Replace OpenAI directly with **OpenRouter** for summarization.
- Configuration in `secrets.yaml`:
  ```yaml
  openrouter_api_key: "YOUR_KEY"
  openrouter_model: "MODEL_NAME"  # Model to use for summarization (e.g., gpt-4)
  ```

### 9. Handling Firecrawl Failures
- Treat any Firecrawl API failure as definitive for now (no fallback to parsing raw HTML).

### 10. Testing
- Unit tests for core functionality should:
  - Use **mock data** where APIs or external dependencies are involved.
  - Be declared in the `"__main__"` namespace for now.

### 11. Scaling and Async
- Avoid threading or async complexities for now. Scaling with simple iterative logic.

### 12. Data Storage
- Store processed paper metadata in `data/papers.json`.
- Fields to include:
  - Metadata (`title`, `author`, `link`, `abstract`, etc.).
  - `relevance` and `summary`.
  - Optionally, `date` and `topics`.

### 13. Dependencies
- Any Python dependency can be introduced, provided they are added to `requirements.txt`.

---

All other requirements and architecture notes remain valid and unchanged. 
