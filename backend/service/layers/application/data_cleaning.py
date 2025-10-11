from enum import StrEnum
from service.layers.application.interfaces.data_loader import IDataLoader
import pandas as pd
import ast

class RawDataTypes(StrEnum):
    RECIPES = "recipes"
    INTERACTIONS = "interactions"


def clean_data(loader: IDataLoader, raw_data_type: RawDataTypes) -> pd.DataFrame:
    match raw_data_type:
        case RawDataTypes.INTERACTIONS:
            df = loader.load_interactions()
        case RawDataTypes.RECIPES:
            df = loader.load_recipes()
        case _:
            raise ValueError(f"Unknown data type: {raw_data_type}")

    for col in df.columns:
        sample_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        if isinstance(sample_val, str) and sample_val.startswith('[') and sample_val.endswith(']'):
            df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    return df


