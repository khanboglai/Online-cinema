import json
import pandas as pd
from typing import Dict, Any
from abc import ABC, abstractmethod

class RecommenderABC(ABC):
    @abstractmethod
    def fit(self) -> None:
        """
        Fit the recommender by the specified dataframes
        """
        ...

    @abstractmethod
    def recommend_all(self) -> pd.DataFrame:
        """
        Recommend items for all users
        """
        ...