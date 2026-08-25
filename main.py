#testing purpose
from langchain_google_genai import ChatGoogleGenerativeAI
from app.database.duckdb_manager import DuckDBManager
from app.services.ingestion_service import IngestionService
from app.services.analysis_service import AnalysisService
from app.agents.file_selector import FileSelectorAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.orchestrator import AnalysisOrchestrator
from app.agents.visualization_agent import VisualizationAgent
from app.agents.response_agent import ResponseAgent
from app.services.chart_service import ChartService

def main():

    db_manager = DuckDBManager()

    ingestion_service = (IngestionService(db_manager))

    # STEP 1
    # Ingest multiple files

    file_paths = [

        "data/customers.csv",

        "data/products.csv",

        "data/orders.csv"
    ]

    ingestion_results = (
        ingestion_service.ingest_files(
            file_paths
        )
    )

    print("INGESTION RESULTS")

    for result in ingestion_results:

        print(
            result["file_name"]
        )

        print(
            result["file_id"]
        )

        print("-" * 50)

    # STEP 2    
    print("Initializing LLM...")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key="your_api_key_here",
        temperature=0,
        max_retries=2,
    )

    # STEP 3
    print("Initializing Agents...")

    file_selector_agent = (FileSelectorAgent(llm))
    visualize_agent = (VisualizationAgent(llm))
    analysis_agent = (AnalysisAgent(llm))
    response_agent = (ResponseAgent(llm))

    orchestrator = (AnalysisOrchestrator(
            file_selector_agent=file_selector_agent,
            analysis_agent=analysis_agent,
            visualize_agent=visualize_agent,
            response_agent=response_agent,
            db_manager=db_manager))

    analysis_service = (
        AnalysisService(
            db_manager=db_manager,
            orchestrator=orchestrator
        )
    )

    # STEP 4
    # User selected files

    selected_file_ids = [r["file_id"] for r in ingestion_results]

    # STEP 5
    # Ask question

    result = analysis_service.analyze(
        question="Compare sales across regions",
        selected_file_ids=selected_file_ids)

    print("\nFINAL RESULT")

    print(
        "Analysis Type:",
        result["analysis_type"]
    )

    print(
        "Generated SQL:",
        result["generated_sql"]
    )

    print(
        "Processed SQL:",
        result["processed_sql"]
    )

    print(
        "Result:",
        result["query_result"]
    )

    print(
        "Error:",
        result["error"]
    )
    if (result.get("visualization_required")and result.get("visualization_plan")and result.get("query_result") is not None):

        chart = ChartService.create_chart(
            dataframe=result["query_result"],
            visualization_plan=result["visualization_plan"]
        )

        if chart is not None:
            chart.show()

if __name__ == "__main__":

    main()