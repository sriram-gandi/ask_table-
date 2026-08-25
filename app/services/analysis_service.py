class AnalysisService:

    def __init__(
        self,
        db_manager,
        orchestrator
    ):

        self.db_manager = db_manager

        self.orchestrator = orchestrator

    def analyze(
        self,
        question: str,
        selected_file_ids: list[str]
    ):

        available_files = []

        metadata_df = (self.db_manager.get_file_metadata(selected_file_ids))
        print(metadata_df)
        for _, row in metadata_df.iterrows():

            available_files.append(
                {
                    "file_id":
                        row["file_id"],

                    "file_name":
                        row["file_name"],

                    "table_name":
                        row["table_name"],

                    "summary":
                        row["summary_json"]
                }
            )

        result = self.orchestrator.run(
            question=question,
            selected_file_ids=
                selected_file_ids,

            available_files=
                available_files
        )

        return result