import os

from langchain_google_genai import ChatGoogleGenerativeAI

from app.database.duckdb_manager import DuckDBManager

from app.services.ingestion_service import IngestionService
from app.services.analysis_service import AnalysisService

from app.agents.file_selector import FileSelectorAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.visualization_agent import VisualizationAgent
from app.agents.response_agent import ResponseAgent
from app.agents.orchestrator import AnalysisOrchestrator
from dotenv import load_dotenv

load_dotenv()

def create_db_manager():

    return DuckDBManager()


def create_ingestion_service(
    db_manager
):

    return IngestionService(
        db_manager
    )


def create_llm():

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv(
            "GOOGLE_API_KEY"
        ),
        temperature=0,
        max_retries=2
    )


def create_analysis_service(
    db_manager
):

    llm = create_llm()

    file_selector_agent = (
        FileSelectorAgent(llm)
    )

    visualization_agent = (
        VisualizationAgent(llm)
    )

    analysis_agent = (
        AnalysisAgent(llm)
    )

    response_agent = (
        ResponseAgent(llm)
    )

    orchestrator = AnalysisOrchestrator(

        file_selector_agent=
        file_selector_agent,

        analysis_agent=
        analysis_agent,

        visualize_agent=
        visualization_agent,

        response_agent=
        response_agent,

        db_manager=
        db_manager
    )

    return AnalysisService(

        db_manager=db_manager,

        orchestrator=orchestrator
    )