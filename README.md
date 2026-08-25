
AskTable AI lets you upload CSV or Excel files and query them in plain English. No SQL knowledge required. You type something like *"Compare sales across regions"* and the app figures out what to query, runs it, and hands you back an answer � along with a chart if it makes sense to show one.

Under the hood it's a multi-agent pipeline powered by Google's Gemini model, stitched together with LangGraph, and backed by DuckDB for blazing-fast in-process SQL. The UI is built in Streamlit and there's also a thin FastAPI bridge if you want to wire it up to a custom frontend.


## What it can do

- Upload multiple CSV / Excel files in one go
- Ask natural-language questions across one or more of those datasets
- Get a written answer plus the raw data table
- Automatically decide when a chart is actually useful and render one (via Plotly)
- Expose the same logic through a REST API (`/ingest`, `/analyze`, `/chart`)

---

## How it works

The pipeline is a LangGraph state machine. Each step is a dedicated agent:

```
Upload files
     |
     V
[File Selector Agent]  -> picks which tables are relevant to the question
     |
     V
[Analysis Agent]       -> decides analysis type, generates DuckDB SQL,visualization_required or not and reason
     |
     V
[SQL Preprocessor]     -> cleans / validates the generated SQL
     |
     V
[Query Executor]       -> runs SQL against DuckDB, returns a DataFrame
     |
     V
[Response Agent]       -> writes a human-readable answer
     |
     V
[Visualization Agent]  -> (conditional) creates a Plotly chart spec


Every uploaded file lands in a local DuckDB database. Column-level metadata (types, unique counts, sample values) is stored alongside it so the agents have enough context to generate accurate SQL without hallucinating column names.

---

## Tech stack

| Layer | Tech |
|---|---|
| LLM | Google Gemini 2.5 Flash via `langchain-google-genai` |
| Agent orchestration | LangGraph |
| Database | DuckDB (in-process, no server needed) |
| UI | Streamlit |
| REST API | FastAPI |
| Charts | Plotly |
| Data handling | Pandas |
| Schema validation | Pydantic |
| Config | python-dotenv |



## Project layout


ask_table_v1/
+-- main.py                   # Script entrypoint (demo purpose only)
+-- api_bridge.py             # FastAPI REST bridge
+-- .env                      # API keys (not committed)
+-- requirements.txt
|
+-- app/
|   +-- agents/
|   |   +-- orchestrator.py   # LangGraph state machine
|   |   +-- analysis_agent.py # SQL generation + analysis planning
|   |   +-- file_selector.py  # Picks relevant datasets
|   |   +-- visualization_agent.py # generates chart spec
|   |   +-- response_agent.py # generates actual response
|   |   +-- state.py          # Shared state schema
|
|       +-- core/
|       +-- dependencies.py   # Factory functions (LLM, services)

   
|   +-- database/
|       +-- duckdb_manager.py # All DuckDB operations
|   
|   +-- services/
|       +-- ingestion_service.py
|       +-- analysis_service.py
|       +-- chart_service.py
|
+-- ui/
|   +-- streamlit.py          # Main Streamlit app
|
+-- data/                     # Drop your CSV / Excel files here


## Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd ask_table_v1
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

The `requirements.txt` is currently empty � install everything you need:

```bash
pip install streamlit langchain-google-genai langgraph duckdb pandas \
            plotly pydantic python-dotenv fastapi uvicorn openpyxl
```

> **Tip:** Pin these versions once things are stable and commit a proper `requirements.txt`.

### 4. Set your Google API key

Create a `.env` file in the project root (or edit the existing one):

```
GOOGLE_API_KEY=your_key_here
```

You can get a key from [Google AI Studio](https://aistudio.google.com/). The app uses **Gemini 2.5 Flash** � make sure your key has access to it.


### 5. Run the Streamlit app

```bash
streamlit run ui/streamlit.py
```

Open `http://localhost:8501` in your browser. Upload some CSVs, select datasets, type a question, hit **Analyze**.

### 6. (Optional) Run the CLI demo

If you want to test the pipeline without the UI:

```bash
python main.py
```

This ingests `data/customers.csv`, `data/orders.csv`, and `data/products.csv` and runs a hardcoded question. Drop your own files in the `data/` folder first.


The API exposes three endpoints:

| Method | Path | What it does |
|---|---|---|
| `POST` | `/ingest` | Upload files (multipart form) |
| `POST` | `/analyze` | Send a question + file IDs, get back a result |
| `POST` | `/chart` | Generate a Plotly chart from a result |



## Things worth knowing

- DuckDB stores its database at `data/analytics.duckdb`. Delete this file if you want a fresh start.
- The Streamlit app keeps services in `st.session_state`, so everything persists across rerenders within a session.
- The FastAPI bridge reuses the exact same service layer as the Streamlit app no duplicated business logic.
- The visualization agent only produces a chart when it genuinely makes sense (comparisons, trends, distributions). Single-value answers just get a text response.
