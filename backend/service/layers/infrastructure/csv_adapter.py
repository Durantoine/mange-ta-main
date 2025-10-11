from enum import StrEnum
from pathlib import Path

import pandas as pd

from service.layers.logger import struct_logger


class DataType(StrEnum):
    INTERACTIONS = "interactions"
    RECIPES = "recipes"


class CSVAdapter:

    FILE_MAP = {
        DataType.INTERACTIONS: "interactions.csv",
        DataType.RECIPES: "recipes.csv",
    }
    RAW_FILE_MAP = {
        DataType.INTERACTIONS: "RAW_interactions.csv",
        DataType.RECIPES: "RAW_recipes.csv",
    }

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or (Path(__file__).parent / "data")
        self.data_dir.mkdir(exist_ok=True, parents=True)

    def load(self, data_type: DataType, raw: bool = False) -> pd.DataFrame:
        file_map = self.RAW_FILE_MAP if raw else self.FILE_MAP
        path = self.data_dir / file_map[data_type]
        try:
            df = pd.read_csv(path)
            df = df.astype(object).where(pd.notna(df), None)
            return df

        except FileNotFoundError:
            struct_logger.info(f"[WARN] File {path} does not exist yet.")
            return pd.DataFrame()

    def save(self, df: pd.DataFrame, data_type: DataType) -> Path:
        path = self.data_dir / self.FILE_MAP[data_type]
        df.to_csv(path, index=False)
        return path
