from typing import Optional
from pydantic import BaseModel, Field


class VisualizationPlan(BaseModel):

    chart_type: str = Field(
        description=(
            "One of: bar, line, pie, scatter"
        )
    )

    x_column: str = Field(
        description="Column to use on x-axis"
    )

    y_columns: list[str] = Field(
        description="Columns to use as values"
    )

    title: str = Field(
        description="Clear chart title"
    )


class VisualizationAgent:

    def __init__(self,llm):

        self.llm = llm.with_structured_output(VisualizationPlan)

    def create_visualization_plan(
        self,
        state
    ):

        result_data = state.get(
            "query_result"
        )

        if result_data is None:

            return {
                **state,
                "visualization_plan": None
            }

        dataframe_json = result_data.to_json(
            orient="records"
        )

        columns = list(
            result_data.columns
        )

        prompt = f"""
You are a data visualization planner.

The user asked:

{state["question"]}

The analysis result is:

{dataframe_json}

Available columns:

{columns}

A visualization has already been determined
to be necessary.

Your task is ONLY to select the most suitable
chart configuration.

Rules:

1. Use line charts for trends over time.
2. Use bar charts for comparisons.
3. Use pie charts only for small part-to-whole
   datasets.
4. Use scatter charts for relationships between
   numeric variables.
5. Use ONLY existing columns.
6. Do not invent columns.
"""

        result = self.llm.invoke(
            prompt
        )

        return {
            **state,

            "visualization_plan":
                result.model_dump()
        }