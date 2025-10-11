
from service.layers.application.interfaces.interface import IDataAdapter
from service.layers.infrastructure.csv_adapter import DataType
import pandas as pd


def load_data(csv_adapter: IDataAdapter, data_type: DataType) -> pd.DataFrame:
    match data_type:
        case DataType.RECIPES:
            df = csv_adapter.load(DataType.RECIPES)
        case DataType.INTERACTIONS:
            df = csv_adapter.load(DataType.INTERACTIONS)
        case _:
            raise ValueError(f"Unknown data type: {data_type}")
        
    return df