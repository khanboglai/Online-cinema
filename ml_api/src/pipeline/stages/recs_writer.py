import asyncpg
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from pipeline.pipeline import *
from logs import logger

class RecsWriter(StageABC):
    """
    Writes recommendations to the database
    """

    def __init__(self, db_config: Dict[str, Any]):
        super().__init__("RecsWriter")
        self._db_config = db_config

    async def run(self, input: StageOut | None = None) -> StageOut:
        recs = input.unpack()

        recs = recs[["user_id", "item_id", "rank"]]

        logger.info("1/3 - Processing data...")
        df = pd.DataFrame(recs)
        # recs_grouped = df.groupby("user_id")["item_id"].agg(list).reset_index()
        # recs_grouped = [tuple(row) for row in recs_grouped.values]
        
        try:
            conn = await asyncpg.connect(**self._db_config)

            async with conn.transaction():
                logger.info("2/3 - Deleting old data...")
                await conn.execute("""DELETE FROM recommend""")

                logger.info("3/3 - Inserting new recommendations...")
                query = """
                INSERT INTO recommend (profile_id, film_id, rank)
                VALUES ($1, $2, $3) 
                RETURNING profile_id
                """
                await conn.executemany(query, df.itertuples(index=False, name=None))
            await conn.close()
        except asyncpg.PostgresError as e:
            print(f"Database error: {e}")
            raise
