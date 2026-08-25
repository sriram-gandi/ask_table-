import pandas as pd
from pathlib import Path


class FileLoader:

    SUPPORTED_EXTENSIONS = {
        ".csv",
        ".xlsx",
        ".xls"
    }

    @staticmethod
    def load_file(file_path: str) -> pd.DataFrame:

        path = Path(file_path)

        if not path.exists():

            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        extension = path.suffix.lower()

        if extension not in FileLoader.SUPPORTED_EXTENSIONS:

            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        if extension == ".csv":

            dataframe = pd.read_csv(file_path)

        elif extension in [".xlsx", ".xls"]:

            dataframe = pd.read_excel(file_path)

        else:

            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        dataframe.columns = (
            dataframe.columns
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        return dataframe