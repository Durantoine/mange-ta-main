from abc import ABC, abstractmethod
import pandas as pd
from enum import Enum

from service.layers.infrastructure.csv_adapter import DataType


class IDataAdapter(ABC):

    @abstractmethod
    def load(self, data_type: DataType) -> pd.DataFrame:
        pass

    @abstractmethod
    def save(self, df: pd.DataFrame, data_type: DataType) -> None:

        pass