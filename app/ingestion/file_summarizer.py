import json
import pandas as pd
from typing import Any


class FileSummarizer:

    def summarize_dataframe(
        self,
        dataframe: pd.DataFrame,
        file_name: str
    ) -> dict[str, Any]:

        columns = []

        for column in dataframe.columns:

            column_summary = self._summarize_column(
                dataframe,
                column
            )

            columns.append(column_summary)

        summary = {
            "file_name": file_name,
            "row_count": int(len(dataframe)),
            "column_count": int(len(dataframe.columns)),
            "columns": columns
        }

        return summary

    def _summarize_column(
        self,
        dataframe: pd.DataFrame,
        column: str
    ) -> dict[str, Any]:

        series = dataframe[column]

        dtype = str(series.dtype)

        null_count = int(series.isna().sum())

        unique_count = int(
            series.nunique(dropna=True)
        )

        sample_values = (
            series
            .dropna()
            .astype(str)
            .unique()
            [:5]
            .tolist()
        )

        min_value = None
        max_value = None

        if pd.api.types.is_numeric_dtype(series):

            min_value = self._safe_value(
                series.min()
            )

            max_value = self._safe_value(
                series.max()
            )

        elif pd.api.types.is_datetime64_any_dtype(series):

            min_value = self._safe_value(
                series.min()
            )

            max_value = self._safe_value(
                series.max()
            )

        description = self._generate_description(
            column_name=column,
            dtype=dtype,
            unique_count=unique_count,
            sample_values=sample_values
        )

        return {
            "column_name": column,
            "data_type": dtype,
            "unique_count": unique_count,
            "null_count": null_count,
            "min_value": min_value,
            "max_value": max_value,
            "sample_values": sample_values,
            "description": description
        }

    @staticmethod
    def _safe_value(value):

        if pd.isna(value):

            return None

        return str(value)

    @staticmethod
    def _generate_description(
        column_name: str,
        dtype: str,
        unique_count: int,
        sample_values: list
    ) -> str:

        return (
            f"Column '{column_name}' has data type "
            f"'{dtype}', approximately {unique_count} "
            f"unique values. Example values: {sample_values}"
        )

    @staticmethod
    def to_json(summary: dict) -> str:

        return json.dumps(
            summary,
            default=str
        )