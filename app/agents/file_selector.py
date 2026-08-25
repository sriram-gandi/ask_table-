import json
from pydantic import BaseModel, Field
class FileSelectionPlan(BaseModel):
    selected_file_ids: list[str] = Field(description="List of file IDs selected for analysis.")
    reason: str = Field(description="Reason for selecting the files.")

class FileSelectorAgent:

    def __init__(self, llm):

        self.structured_llm = llm.with_structured_output(FileSelectionPlan)

    def select_files(self, state):

        question = state["question"]

        available_files = state[
            "available_files"
        ]

        prompt = f"""
You are a dataset selection agent.

User question:

{question}

Available datasets:

{json.dumps(
    available_files,
    indent=2,
    default=str
)}

Your task:

1. Identify which datasets are required.
2. Determine whether one or multiple datasets are needed.
3. Return ONLY valid JSON.

Format:

{{
    "selected_file_ids": [],
    "reason": ""
}}
"""

        response = self.structured_llm.invoke(prompt)

        selected_file_ids = response.selected_file_ids
        selected_files = [file for file in available_files if file["file_id"] in selected_file_ids]

        return {
            **state,
            "selected_files": selected_files
        }