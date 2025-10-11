from abc import ABC, abstractmethod
import pandas as pd

class IDataLoader(ABC):

    @abstractmethod
    def load_interactions(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def load_recipes(self) -> pd.DataFrame:
        pass