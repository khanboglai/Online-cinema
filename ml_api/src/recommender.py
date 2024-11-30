import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix

from typing import List
import implicit
from rectools import Columns
from rectools.models import ImplicitALSWrapperModel
from rectools.dataset import Dataset
from implicit.als import AlternatingLeastSquares

class RecommenderConfig:
    load_path: str = "./artefacts/model.npz"
    save_path: str = "./artefacts/model_old.npz"
    data_dir: str = "./data"


class Recommender():
    def __init__(self, config: RecommenderConfig = RecommenderConfig()):
        self.config = config
        
        self.interactions_df = pd.read_csv(
            self.config.data_dir + "/interactions.csv",
            header=None,
            index_col=False,
            names=[Columns.User, Columns.Item, Columns.Datetime, "total_dur", "watched_pcs", Columns.Weight]
        )
        self.interactions_df["datetime"] = pd.to_datetime(self.interactions_df["datetime"])
        
        self.dataset = Dataset.construct(
            interactions_df=self.interactions_df,
        )

        self.user_item_matrix = csr_matrix(
            (self.interactions_df[Columns.Weight], 
            (self.interactions_df[Columns.User], self.interactions_df[Columns.Item])
            )
        )
        self.m = AlternatingLeastSquares(
            factors=12,
            regularization=0.05,
            iterations=7
        )

        self.m = implicit.cpu.als.AlternatingLeastSquares.load(self.config.load_path)
        self.m.is_fitted = True

    async def recommend(self, user_id: int) -> List[int]:
        ids, _ = self.m.recommend(
            user_id,
            user_items=self.user_item_matrix[user_id],
            N=10,
            filter_already_liked_items=True,
        )
        return list(ids)

    def load(self):
        self.m = AlternatingLeastSquares.load(self.config.load_path)

    def save(self):
        self.m.save(self.config.save_path)