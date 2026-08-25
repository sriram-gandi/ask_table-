import uuid
import json
from pathlib import Path
from app.database.duckdb_manager import DuckDBManager
from app.ingestion.file_loader import FileLoader
from app.ingestion.file_summarizer import FileSummarizer


class IngestionService:

    def __init__(self,db_manager: DuckDBManager):

        self.db_manager = db_manager
        self.file_loader = FileLoader()
        self.file_summarizer = FileSummarizer()

    def ingest_files(self,file_paths: list[str]):
        results = []
        for file_path in file_paths:
            result = self.ingest_file(file_path)
            results.append(result)
        return results

    def ingest_file(self,file_path: str):
        file_id = str(uuid.uuid4())
        file_name = Path(file_path).name
        table_name = ("dataset_"+ file_id.replace("-", "_"))
        dataframe = self.file_loader.load_file(file_path)
        summary = (self.file_summarizer.summarize_dataframe(dataframe,file_name))
        self.db_manager.save_dataframe(dataframe=dataframe,table_name=table_name)
        summary_json = json.dumps(summary,default=str)
        self.db_manager.save_file_metadata(
            file_id=file_id,
            file_name=file_name,
            table_name=table_name,
            row_count=len(dataframe),
            column_count=len(dataframe.columns),
            summary_json=summary_json
        )

        column_records = []

        for column in summary["columns"]:

            column_records.append(
                {
                    "file_id": file_id,
                    "column_name": column[
                        "column_name"
                    ],
                    "data_type": column[
                        "data_type"
                    ],
                    "unique_count": column[
                        "unique_count"
                    ],
                    "null_count": column[
                        "null_count"
                    ],
                    "min_value": column[
                        "min_value"
                    ],
                    "max_value": column[
                        "max_value"
                    ],
                    "sample_values": json.dumps(
                        column["sample_values"]
                    ),
                    "description": column[
                        "description"
                    ]
                }
            )
        self.db_manager.save_column_metadata(column_records)
        return {
            "file_id": file_id,
            "file_name": file_name,
            "table_name": table_name,
            "summary": summary
        }

    