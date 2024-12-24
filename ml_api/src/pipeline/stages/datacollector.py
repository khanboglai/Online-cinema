import asyncpg
from logs import logger
from typing import Dict, Any
from pipeline.pipeline import *
import pandas as pd

class DataCollector(StageABC):
    """
    Collects data from database and converts it to pd.DataFrame
    """

    def __init__(self, db_config: Dict[str, Any]):
        super().__init__("DataCollector")
        self._db_config = db_config

    async def run(self, input: StageOut | None = None) -> StageOut:
        try:
            conn = await asyncpg.connect(**self._db_config)

            logger.info("1/3 Get users info...")
            query = """
            SELECT 
                id AS user_id,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date)) AS age,
                sex
            FROM profile
            """
            users = await conn.fetch(query)
            
            logger.info("2/3 Get interactions info...")
            query = """
            SELECT profile_id AS user_id,
                film_id AS item_id,
                last_interaction AS last_watched_dt,
                watchtime AS total_dur
            FROM interaction
            """
            interactions = await conn.fetch(query)

            logger.info("3/3 Get items info...")
            query = """
            SELECT 
                id AS item_id,
                name AS title,
                genres,
                year AS release_year,
                rating_kp, 
                age_rating
            FROM film"""
            films = await conn.fetch(query)

            await conn.close()
        except asyncpg.PostgresError as e:
            logger.error(f"Database error: {e}")
            raise

        return StageOut((
            pd.DataFrame.from_records(users, columns=users[0].keys()),
            pd.DataFrame.from_records(films, columns=films[0].keys()),
            pd.DataFrame.from_records(interactions, columns=interactions[0].keys())
            )) # Tuple(raw_users_df, raw_items_df, raw_interactions_df)
