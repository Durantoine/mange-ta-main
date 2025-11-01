from pathlib import Path

import pandas as pd

from service.layers.application.interfaces.interface import IDataAdapter
from service.layers.infrastructure.types import DataType
from service.layers.logger import struct_logger

# class CSVAdapter(IDataAdapter):

#     FILE_MAP = {
#         DataType.INTERACTIONS: "interactions.csv",
#         DataType.RECIPES: "recipes.csv",
#     }
#     RAW_FILE_MAP = {
#         DataType.INTERACTIONS: "RAW_interactions.csv",
#         DataType.RECIPES: "RAW_recipes.csv",
#     }

#     def __init__(self, data_dir: Path | None = None):
#         self.data_dir = data_dir or (Path(__file__).parent / "data")
#         self.data_dir.mkdir(exist_ok=True, parents=True)

#     def load(self, data_type: DataType, raw: bool = False) -> pd.DataFrame:
#         file_map = self.RAW_FILE_MAP if raw else self.FILE_MAP
#         path = self.data_dir / file_map[data_type]
#         try:
#             df = pd.read_csv(path)
#             df = df.astype(object).where(pd.notna(df), None)
#             return df

#         except FileNotFoundError:
#             struct_logger.info(f"[WARN] File {path} does not exist yet.")
#             return pd.DataFrame()

#     def save(self, df: pd.DataFrame, data_type: DataType) -> Path:
#         path = self.data_dir / self.FILE_MAP[data_type]
#         df.to_csv(path, index=False)
#         return path


class CSVAdapter(IDataAdapter):
    FILE_MAP = {
        DataType.INTERACTIONS: "interactions.csv",
        DataType.RECIPES: "recipes.csv",
    }
    RAW_FILE_MAP = {
        DataType.INTERACTIONS: "RAW_interactions.csv",
        DataType.RECIPES: "RAW_recipes.csv",
    }

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or (Path(__file__).parent / "data")
        self.data_dir.mkdir(exist_ok=True, parents=True)
        self._cache = {}

    def load(self, data_type: DataType, raw: bool = False) -> pd.DataFrame:
        cache_key = (data_type, raw)

        if cache_key in self._cache:
            return self._cache[cache_key]

        file_map = self.RAW_FILE_MAP if raw else self.FILE_MAP
        path = self.data_dir / file_map[data_type]

        try:
            df = pd.read_csv(path)
            df = df.astype(object).where(pd.notna(df), None)

            if not raw:
                df = self._optimize_memory(df)

            self._cache[cache_key] = df
            return df

        except FileNotFoundError:
            struct_logger.info(f"[WARN] File {path} does not exist yet.")
            return pd.DataFrame()

    def save(self, df: pd.DataFrame, data_type: DataType) -> Path:
        path = self.data_dir / self.FILE_MAP[data_type]
        df.to_csv(path, index=False)

        cache_key = (data_type, False)
        if cache_key in self._cache:
            del self._cache[cache_key]

        return path

    @staticmethod
    def _optimize_memory(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        initial_memory = df.memory_usage(deep=True).sum() / 1024**2

        numeric_cols = {'rating', 'minutes', 'n_steps', 'n_ingredients'}

        for col in df.columns:
            col_type = df[col].dtype

            if col_type == 'object':
                if col.lower() in numeric_cols:
                    continue

                num_unique = df[col].nunique()
                num_total = len(df[col])

                if num_unique / num_total < 0.5:
                    df[col] = df[col].astype('category')

            elif col_type in ['int64', 'int32']:
                df[col] = pd.to_numeric(df[col], downcast='integer')

            elif col_type in ['float64', 'float32']:
                df[col] = pd.to_numeric(df[col], downcast='float')

        final_memory = df.memory_usage(deep=True).sum() / 1024**2
        reduction = (1 - final_memory / initial_memory) * 100

        struct_logger.info(
            "memory_optimization",
            initial_mb=round(initial_memory, 2),
            final_mb=round(final_memory, 2),
            reduction_pct=round(reduction, 1),
        )

        return df
