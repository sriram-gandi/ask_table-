# AskTable AI

> **Ask questions about CSV and Excel data in plain English — no SQL required.**

AskTable AI is an agentic data-analysis application that turns natural-language questions into validated DuckDB queries, executes them across uploaded datasets, explains the results, and generates a visualization when one adds value.

## Why this project?

Traditional analytics tools require users to know SQL, understand schemas, and manually build charts. AskTable AI puts an agentic layer over tabular data so users can start with the question instead of the query language.

## Core capabilities

- 📁 Upload multiple CSV and Excel files
- 🔎 Select the datasets relevant to a question
- 🤖 Use specialized agents for analysis, response generation, and visualization
- 🧠 Generate SQL from natural-language questions
- 🛡️ Preprocess and validate generated SQL before execution
- ⚡ Execute analytical queries locally with DuckDB
- 📊 Generate Plotly visualizations conditionally
- 💬 Return both a human-readable answer and query results
- 🔌 Expose the same service layer through Streamlit and FastAPI

## Architecture

```text
                         ┌─────────────────────┐
                         │       User          │
                         │  Files + Question   │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │ Streamlit / FastAPI │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │   Analysis Service  │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │      LangGraph Orchestrator   │
                    └───────────────┬───────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
 ┌────────▼────────┐      ┌────────▼────────┐      ┌────────▼────────┐
 │ File Selector    │      │ Analysis Agent  │      │ Response Agent  │
 │ Agent            │      │                 │      │                 │
 └─────────────────┘      └────────┬────────┘      └─────────────────┘
                                   │
                          ┌────────▼────────┐
                          │ SQL Processing  │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │ DuckDB Executor │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │ Query Result    │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │ Visualization   │
                          │ Agent (optional)│
                          └─────────────────┘
```

### Agent responsibilities

| Component | Responsibility |
|---|---|
| File Selector Agent | Determines which uploaded datasets are relevant |
| Analysis Agent | Plans the analysis and generates SQL |
| SQL processing | Cleans and validates generated SQL before execution |
| Query Executor | Runs SQL against DuckDB |
| Response Agent | Converts query results into a useful explanation |
| Visualization Agent | Decides whether a chart is useful and creates its specification |

## Tech stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini 2.5 Flash |
| Agent orchestration | LangGraph |
| LLM integration | LangChain Google GenAI |
| Analytical database | DuckDB |
| Data processing | Pandas |
| Visualization | Plotly |
| Web UI | Streamlit |
| API | FastAPI + Uvicorn |
| Validation | Pydantic |
| Configuration | python-dotenv |

## Project structure

```text
.
├── app/
│   ├── agents/
│   │   ├── analysis_agent.py
│   │   ├── file_selector.py
│   │   ├── orchestrator.py
│   │   ├── response_agent.py
│   │   ├── state.py
│   │   └── visualization_agent.py
│   ├── core/
│   │   └── dependencies.py
│   ├── database/
│   │   └── duckdb_manager.py
│   ├── ingestion/
│   ├── services/
│   │   ├── analysis_service.py
│   │   ├── chart_service.py
│   │   └── ingestion_service.py
│   └── utils/
├── ui/
│   └── streamlit.py
├── api_bridge.py
├── main.py
├── requirements.txt
└── .env.example
```

## Getting started

### Prerequisites

- Python 3.10+
- A Google Gemini API key

### 1. Clone

```bash
git clone https://github.com/sriram-gandi/ask_table-.git
cd ask_table-
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the API key

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Set your key in `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

**Never commit `.env` or API keys.**

### 5. Run the application

```bash
streamlit run ui/streamlit.py
```

The Streamlit application will be available at `http://localhost:8501`.

### Optional: run the CLI example

```bash
python main.py
```

The CLI example demonstrates the complete ingestion → agent orchestration → SQL → result → visualization flow.

## API

The project also includes a FastAPI bridge for integrating the analysis pipeline with another frontend or service.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/ingest` | Upload datasets |
| `POST` | `/analyze` | Ask a question about selected datasets |
| `POST` | `/chart` | Generate a chart from an analysis result |

## Design decisions

### Why DuckDB?

DuckDB provides an embedded analytical SQL engine without requiring a separate database server. This keeps the application lightweight while making relational analysis over uploaded files fast and reproducible.

### Why LangGraph?

The analysis workflow has explicit stages and conditional execution. LangGraph makes those state transitions visible and gives each specialized agent a well-defined responsibility rather than relying on a single unconstrained prompt.

### Why conditional visualization?

Not every analytical question benefits from a chart. AskTable AI separates visualization planning from answer generation so a visualization is produced only when the result supports a useful visual representation.

## Security and data handling

- API credentials are loaded from environment variables.
- Local uploaded datasets and DuckDB files are excluded from Git.
- No secrets should be committed to the repository.
- Uploaded data is processed locally by the application unless the configured LLM provider receives the information as part of an LLM request.

## Development

Before opening a pull request, run:

```bash
python -m compileall app ui api_bridge.py main.py
```

For linting and tests in development environments:

```bash
pip install ruff pytest
ruff check .
pytest
```

## Roadmap

- [ ] Add automated unit and integration tests
- [ ] Add SQL safety and query-cost guardrails
- [ ] Add structured observability/tracing for agent runs
- [ ] Add authentication and request-level isolation to the API
- [ ] Add deployment configuration
- [ ] Add evaluation datasets for SQL-generation accuracy

## Status

This project is an actively developed portfolio/reference implementation of an agentic analytics workflow. Interfaces and architecture may evolve as evaluation, testing, and production hardening are added.

## License

Add a license before treating this repository as a reusable open-source project.
