import asyncpg
import logging
from typing import Dict, Any
from pipeline.pipeline import *

class DataCollector(StageABC):
    """
    Collects data from database and converts it to pd.DataFrame
    """

    def __init__(self, db_config: Dict[str, Any]):
        super().__init__("DataCollector")
        self._db_config = db_config

    def run(self, input: StageOut | None = None) -> StageOut:
        ...
        # тут подключение к БД и получение данных
        return StageOut(...) # Tuple(raw_users_df, raw_items_df, raw_interactions_df)