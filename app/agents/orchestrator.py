from pydantic import networks
from langgraph.graph import (
    StateGraph,
    END
)

from app.agents.state import AnalysisState
from app.utils.sql_utils import preprocess_sql
from app.agents.visualization_agent import VisualizationAgent
from app.agents.response_agent import ResponseAgent


class AnalysisOrchestrator:

    def __init__(
        self,
        file_selector_agent,
        analysis_agent,
        visualize_agent,
        response_agent,
        db_manager
    ):

        self.file_selector_agent = (file_selector_agent)
        self.analysis_agent = (analysis_agent)
        self.visualize_agent = (visualize_agent)
        self.response_agent = (response_agent)
        self.db_manager = (db_manager)

        self.graph = self._build_graph()

    def _build_graph(self):

        workflow = StateGraph(AnalysisState)
        workflow.add_node("select_files",self.file_selector_agent.select_files)
        workflow.add_node("analyze_question",self.analysis_agent.analyze)
        workflow.add_node("preprocess_sql",self._preprocess_sql)
        workflow.add_node("execute_query",self._execute_query)
        workflow.add_node("visualize",self.visualize_agent.create_visualization_plan)
        workflow.add_node("generate_response",self.response_agent.generate_response)
        workflow.set_entry_point("select_files")
        workflow.add_edge("select_files","analyze_question")
        workflow.add_edge("analyze_question","preprocess_sql")
        workflow.add_edge("preprocess_sql","execute_query")
        workflow.add_edge("execute_query","generate_response")
        workflow.add_conditional_edges("generate_response",self._should_visualize,{"visualize": "visualize","end": END})
        workflow.add_edge("visualize",END)
        workflow.add_edge("execute_query",END)
        return workflow.compile()
    def _preprocess_sql(self,state):
        try:
            processed_sql = (preprocess_sql(state["generated_sql"]))
            return {
                **state,
                "processed_sql":
                    processed_sql,
                "error": None
            }

        except Exception as e:

            return {
                **state,
                "processed_sql": None,
                "error": str(e)
            }

    def _execute_query(
        self,
        state
    ):

        if state.get("error"):

            return state

        result = self.db_manager.execute_query(
            state[
                "processed_sql"
            ]
        )

        if result["success"]:

            return {
                **state,
                "query_result":
                    result["data"],
                "error": None
            }

        return {
            **state,
            "query_result": None,
            "error":
                result["error"]
        }
    def _should_visualize(self, state):

        if state.get("error"):
            return "end"

        if state.get("visualization_required"):
            return "visualize"

        return "end"

    def run(self,question: str,selected_file_ids: list[str],available_files: list[dict]):
        initial_state = {

    "question": question,

    "selected_file_ids":selected_file_ids,

    "available_files":available_files,

    "selected_files": available_files,

    "analysis_type": None,

    "requires_calculation": False,

    "visualization_required": False,

    "visualization_reason": None,

    "generated_sql": None,

    "processed_sql": None,

    "query_result": None,

    "visualization_plan": None,

    "final_answer": None,

    "error": None
}

        return self.graph.invoke(
            initial_state
        )