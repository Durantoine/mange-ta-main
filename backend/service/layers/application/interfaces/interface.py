from abc import ABC, abstractmethod

import pandas as pd

from service.layers.infrastructure.types import DataType


class IDataAdapter(ABC):

    @abstractmethod
    def load(self, data_type: DataType, raw: bool = False) -> pd.DataFrame:
        pass

    @abstractmethod
    def save(self, df: pd.DataFrame, data_type: DataType) -> None:
        pass