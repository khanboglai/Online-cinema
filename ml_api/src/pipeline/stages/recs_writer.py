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

    async def run(self, input: StageOut | None = None) -> StageOut:
        recs = input.unpack()

        recs = recs[["user_id", "item_id"]]

        df = pd.DataFrame(recs)

        recs_grouped = df.groupby("user_id")["item_id"].agg(list).reset_index()
        recs_grouped = [tuple(row) for row in recs_grouped.values]
        
        try:
            conn = await asyncpg.connect(**self._db_config)

            await conn.execute("""DELETE FROM recommend""")

            query = """
            INSERT INTO recommend (profile_id, film_ids)
            VALUES ($1, $2) 
            RETURNING profile_id
            """
            await conn.executemany(query, recs_grouped)
            await conn.close()

        except asyncpg.PostgresError as e:
            print(f"Recs_writer: {e}")
            raise
