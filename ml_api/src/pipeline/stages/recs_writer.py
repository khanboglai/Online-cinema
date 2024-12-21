import asyncpg
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from pipeline.pipeline import *

class RecsWriter(StageABC):
    """
    Writes recommendations to the database
    """
    def __init__(self, db_config: Dict[str, Any]):
        super().__init__("RecsWriter")
        self._db_config = db_config

    def run(self, input: StageOut | None = None) -> StageOut:
        recs = input.unpack()
        ... 
        # тут запись рекомендаций в БД