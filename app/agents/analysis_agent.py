from typing import Literal,  Optional
from pydantic import BaseModel, Field


class AnalysisPlan(BaseModel):
    analysis_type: Literal["total","average","filter","comparison","trend","general"]= Field(description="The type of analysis required for the user's question.")
    requires_calculation: bool = Field(description=("True if mathematical calculation, aggregation,or computation is required."))
    sql: str = Field(description=("A valid DuckDB SQL query using only the provided table names and column names."))
    error: Optional[str] = Field(default=None,description=("Reason why analysis cannot be performed. Return null when SQL generation is successful."))
    visualization_required: bool = Field(description=("Whether the user explicitly requested a chart/visualization or the question requires comparison or trend analysis"))
    visualization_reason: str = Field(description=("Short reason explaining why visualization is or is not required"))
class AnalysisAgent:
    def __init__(self, llm):
        self.structured_llm = llm.with_structured_output(AnalysisPlan)
    def analyze(self, state):
        question = state["question"]
        selected_files = state["selected_files"]
        prompt = f"""
You are a data analysis planning agent.

User question:

{question}

Relevant datasets:

{selected_files}

Your responsibilities:

1. Understand the user's analytical request.
2. Identify the analysis type.
3. Generate valid DuckDB SQL.
4. Decide whether visualization is required.

ANALYSIS TYPES:

- total
- average
- filter
- comparison
- trend
- distribution
- general

VISUALIZATION RULES:

Set visualization_required = true ONLY when:

1. The user explicitly asks for:
   - chart
   - graph
   - plot
   - visualize
   - visualization

OR

2. The question requires comparing multiple
   categories, entities, groups, or values.

OR

3. The question asks for a trend or change
   over time.

OR

4. The question asks for a distribution or
   relationship between variables.

Set visualization_required = false for:

- a single total
- a single average
- a single scalar result
- simple lookup
- filtering/listing records
- questions where the user only asks for
  the answer or data

IMPORTANT:

Do not generate a visualization just because
the SQL result contains multiple rows.

The user's intent determines whether a chart
should be generated.

SQL RULES:
1. Use ONLY provided table names.
2. Use ONLY existing columns.
3. Generate SELECT queries only.
4. Never generate INSERT, UPDATE, DELETE,
   DROP, ALTER, CREATE, ATTACH, or DETACH.
"""
        response = self.structured_llm.invoke(prompt)
        

        return {
            **state,
            "analysis_type":response.analysis_type,
            "requires_calculation":response.requires_calculation,
            "generated_sql":response.sql,
            "visualization_required":response.visualization_required,
            "visualization_reason":response.visualization_reason}