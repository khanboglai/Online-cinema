import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from pipeline.pipeline import *

class DataPreparer(StageABC):
    """
    Prepares raw data
    """

    def __init__(self):
        super().__init__("DataPreparer")

    async def run(self, input: StageOut | None = None) -> StageOut:
        raw_users_df, raw_items_df, raw_interactions_df = input.unpack()
        
        print("users")
        prepared_users = self._prepare_users(raw_users_df)
        print("items")
        prepared_items = self._prepare_items(raw_items_df)
        print("interactions")
        prepared_interactions = self._prepare_interactions(raw_interactions_df)

        return StageOut((prepared_users, prepared_items, prepared_interactions))

    def _prepare_users(self, users_df: pd.DataFrame) -> pd.DataFrame:
        prepared_users = users_df

        prepared_users["sex"] = prepared_users["sex"].fillna(prepared_users["sex"].mode()[0])
        prepared_users["age"] = prepared_users["age"].fillna(prepared_users["age"].mode()[0])

        prepared_users["sex"] = prepared_users["sex"].map({"male": 1, "female": 0}).astype(np.int8)
        prepared_users["user_id"] = prepared_users["user_id"].astype(np.int32)

        return prepared_users

    def _prepare_items(self, items_df: pd.DataFrame) -> pd.DataFrame:
        prepared_items = items_df[["item_id", "title", "release_year", "genres", "age_rating", "rating_kp"]]
        return prepared_items
    
    def _prepare_interactions(self, interactions_df: pd.DataFrame) -> pd.DataFrame:
        prepared_interactions = interactions_df
        
        prepared_interactions = prepared_interactions[~prepared_interactions["item_id"].isnull()]
        prepared_interactions = prepared_interactions[~prepared_interactions["user_id"].isnull()]
        prepared_interactions = prepared_interactions[~prepared_interactions["total_dur"].isnull()]

        prepared_interactions["total_dur"] = prepared_interactions["total_dur"].astype(np.int16)
        prepared_interactions["user_id"] = prepared_interactions["user_id"].astype(np.int32)
        prepared_interactions["item_id"] = prepared_interactions["item_id"].astype(np.int32)
        prepared_interactions["datetime"] = pd.to_datetime(prepared_interactions["last_watched_dt"])

        #prepared_interactions = prepared_interactions[prepared_interactions["total_dur"] > 100].reset_index(drop = True)
        #prepared_interactions["weight"] = np.where(prepared_interactions['total_dur'] > 10, np.int8(3), np.int8(1))

        return prepared_interactions

    def _check_raw_data(self):
        ...
