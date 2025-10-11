import pandas as pd
from pathlib import Path

INTERACTIONS_FILE = "RAW_interactions.csv"
RECIPES_FILE = "RAW_recipes.csv"

class CSVDataLoader:

    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
     

    def load_interactions(self) -> pd.DataFrame:
        """
        Charge RAW_interactions.csv
        """
        path = self.data_dir / INTERACTIONS_FILE
        return pd.read_csv(path)

    def load_recipes(self) -> pd.DataFrame:
    
        path = self.data_dir / RECIPES_FILE
        return pd.read_csv(path)

    def load_all(self) -> dict[str, pd.DataFrame]:
       
        return {
            "interactions": self.load_interactions(),
            "recipes": self.load_recipes()
        }