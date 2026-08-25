import duckdb
from pathlib import Path
from typing import Any


class DuckDBManager:

    def __init__(self, db_path: str = "data/analytics.duckdb"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path

        self._initialize_database()

    def get_connection(self):
        return duckdb.connect(self.db_path)

    def _initialize_database(self):

        conn = self.get_connection()

        conn.execute("""
        CREATE TABLE IF NOT EXISTS file_metadata (
            file_id VARCHAR PRIMARY KEY,
            file_name VARCHAR,
            table_name VARCHAR,
            row_count BIGINT,
            column_count INTEGER,
            summary_json JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS column_metadata (
            file_id VARCHAR,
            column_name VARCHAR,
            data_type VARCHAR,
            unique_count BIGINT,
            null_count BIGINT,
            min_value VARCHAR,
            max_value VARCHAR,
            sample_values JSON,
            description VARCHAR,
            PRIMARY KEY (file_id, column_name)
        )
        """)

        conn.close()

    def save_dataframe(
        self,
        dataframe,
        table_name: str
    ):

        conn = self.get_connection()

        conn.register("temp_dataframe", dataframe)

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE "{table_name}" AS
            SELECT *
            FROM temp_dataframe
            """
        )

        conn.unregister("temp_dataframe")

        conn.close()

    def save_file_metadata(
        self,
        file_id: str,
        file_name: str,
        table_name: str,
        row_count: int,
        column_count: int,
        summary_json: str
    ):

        conn = self.get_connection()

        conn.execute(
            """
            INSERT OR REPLACE INTO file_metadata
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            [
                file_id,
                file_name,
                table_name,
                row_count,
                column_count,
                summary_json
            ]
        )

        conn.close()

    def save_column_metadata(
        self,
        column_records: list[dict[str, Any]]
    ):

        conn = self.get_connection()

        for record in column_records:

            conn.execute(
                """
                INSERT OR REPLACE INTO column_metadata
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    record["file_id"],
                    record["column_name"],
                    record["data_type"],
                    record["unique_count"],
                    record["null_count"],
                    record["min_value"],
                    record["max_value"],
                    record["sample_values"],
                    record["description"]
                ]
            )

        conn.close()

    def get_file_metadata(
        self,
        file_ids: list[str] | None = None
    ):

        conn = self.get_connection()

        if file_ids:

            placeholders = ",".join(["?"] * len(file_ids))

            result = conn.execute(
                f"""
                SELECT *
                FROM file_metadata
                WHERE file_id IN ({placeholders})
                """,
                file_ids
            ).fetchdf()

        else:

            result = conn.execute(
                """
                SELECT *
                FROM file_metadata
                """
            ).fetchdf()

        conn.close()

        return result

    def get_column_metadata(
        self,
        file_ids: list[str] | None = None
    ):

        conn = self.get_connection()

        if file_ids:

            placeholders = ",".join(["?"] * len(file_ids))

            result = conn.execute(
                f"""
                SELECT *
                FROM column_metadata
                WHERE file_id IN ({placeholders})
                """,
                file_ids
            ).fetchdf()

        else:

            result = conn.execute(
                """
                SELECT *
                FROM column_metadata
                """
            ).fetchdf()

        conn.close()

        return result

    def execute_query(self, query: str):

        conn = self.get_connection()

        try:

            result = conn.execute(query).fetchdf()

            return {
                "success": True,
                "data": result,
                "error": None
            }

        except Exception as e:

            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

        finally:

            conn.close()