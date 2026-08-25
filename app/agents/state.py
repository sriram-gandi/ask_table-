from typing import TypedDict, Any
class AnalysisState(TypedDict):

    question: str

    selected_file_ids: list[str]

    available_files: list[dict[str, Any]]

    selected_files: list[dict[str, Any]]

    analysis_type: str | None

    requires_calculation: bool

    visualization_required: bool

    visualization_reason: str | None

    generated_sql: str | None

    processed_sql: str | None

    query_result: Any

    visualization_plan: dict | None

    final_answer: dict | None

    error: str | None
