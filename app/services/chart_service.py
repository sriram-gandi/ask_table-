import plotly.express as px
import pandas as pd


class ChartService:

    SUPPORTED_CHARTS = {
        "bar",
        "line",
        "pie",
        "scatter"
    }

    @classmethod
    def create_chart(
        cls,
        dataframe: pd.DataFrame,
        visualization_plan: dict
    ):

        if dataframe is None or dataframe.empty:
            return None

        if not visualization_plan:
            return None

        chart_type = visualization_plan.get(
            "chart_type"
        )

        x_column = visualization_plan.get(
            "x_column"
        )

        y_columns = visualization_plan.get(
            "y_columns",
            []
        )

        title = visualization_plan.get(
            "title",
            "Data Visualization"
        )

        # Validate chart type
        if chart_type not in cls.SUPPORTED_CHARTS:

            raise ValueError(
                f"Unsupported chart type: {chart_type}"
            )

        # Validate x column
        if x_column not in dataframe.columns:

            raise ValueError(
                f"x_column '{x_column}' "
                f"does not exist in result"
            )

        # Validate y columns
        valid_y_columns = [
            column
            for column in y_columns
            if column in dataframe.columns
        ]

        if chart_type != "pie" and not valid_y_columns:

            raise ValueError(
                "No valid y_columns found "
                "in visualization result"
            )

        return cls._build_chart(
            dataframe=dataframe,
            chart_type=chart_type,
            x_column=x_column,
            y_columns=valid_y_columns,
            title=title
        )

    @staticmethod
    def _build_chart(
        dataframe: pd.DataFrame,
        chart_type: str,
        x_column: str,
        y_columns: list[str],
        title: str
    ):

        if chart_type == "bar":

            return px.bar(
                dataframe,
                x=x_column,
                y=y_columns,
                title=title,
                barmode="group"
            )

        if chart_type == "line":

            return px.line(
                dataframe,
                x=x_column,
                y=y_columns,
                title=title,
                markers=True
            )

        if chart_type == "pie":

            if not y_columns:

                raise ValueError(
                    "Pie chart requires "
                    "at least one y column"
                )

            return px.pie(
                dataframe,
                names=x_column,
                values=y_columns[0],
                title=title
            )

        if chart_type == "scatter":

            return px.scatter(
                dataframe,
                x=x_column,
                y=y_columns[0],
                title=title
            )

        return None