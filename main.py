"""CLI example for running the AskTable analysis pipeline."""

from app.agents.analysis_agent import AnalysisAgent
from app.agents.file_selector import FileSelectorAgent
from app.agents.orchestrator import AnalysisOrchestrator
from app.agents.response_agent import ResponseAgent
from app.agents.visualization_agent import VisualizationAgent
from app.core.dependencies import create_db_manager, create_llm
from app.services.analysis_service import AnalysisService
from app.services.chart_service import ChartService
from app.services.ingestion_service import IngestionService


def main() -> None:
    """Run a small end-to-end local analysis example."""
    db_manager = create_db_manager()
    ingestion_service = IngestionService(db_manager)

    file_paths = [
        "data/customers.csv",
        "data/products.csv",
        "data/orders.csv",
    ]

    ingestion_results = ingestion_service.ingest_files(file_paths)
    selected_file_ids = [result["file_id"] for result in ingestion_results]

    llm = create_llm()
    orchestrator = AnalysisOrchestrator(
        file_selector_agent=FileSelectorAgent(llm),
        analysis_agent=AnalysisAgent(llm),
        visualize_agent=VisualizationAgent(llm),
        response_agent=ResponseAgent(llm),
        db_manager=db_manager,
    )

    analysis_service = AnalysisService(
        db_manager=db_manager,
        orchestrator=orchestrator,
    )

    result = analysis_service.analyze(
        question="Compare sales across regions",
        selected_file_ids=selected_file_ids,
    )

    print("\n=== AskTable AI Analysis ===")
    print(f"Analysis type: {result.get('analysis_type')}")
    print(f"Answer: {result.get('response')}")
    print(f"Error: {result.get('error')}")

    if (
        result.get("visualization_required")
        and result.get("visualization_plan")
        and result.get("query_result") is not None
    ):
        chart = ChartService.create_chart(
            dataframe=result["query_result"],
            visualization_plan=result["visualization_plan"],
        )
        if chart is not None:
            chart.show()


if __name__ == "__main__":
    main()
