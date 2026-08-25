from pydantic import BaseModel, Field


class FinalAnswer(BaseModel):
    answer: str = Field(description=("A clear, concise answer to the user's question, based strictly on the query result."))

class ResponseAgent:
    def __init__(self, llm):

        self.llm = llm.with_structured_output(FinalAnswer)

    def generate_response(
        self,
        state
    ):

        query_result = state.get("query_result")

        # If query execution failed or returned nothing
        if query_result is None:
            return {
                **state,
                "final_answer": None
            }

        # Convert DataFrame into JSON so it can be passed
        # safely to the LLM.
        result_json = query_result.to_json(
            orient="records",
            date_format="iso"
        )

        prompt = f"""
You are a data analyst responsible for presenting
query results to the user.

User question:

{state["question"]}

Query result:

{result_json}

Instructions:

1. Answer the user's question directly.
2. Use ONLY the provided query result.
3. Do not invent, estimate, or assume any data.
4. Keep the answer concise.
5. Do not mention SQL, DuckDB, DataFrames, or internal
   implementation details.
6. Format numbers clearly when appropriate.
7. If the result contains multiple records, summarize
   the result without hiding important information.
"""

        result = self.llm.invoke(
            prompt
        )

        return {
            **state,

            "final_answer": {
                "answer": result.answer
            }
        }