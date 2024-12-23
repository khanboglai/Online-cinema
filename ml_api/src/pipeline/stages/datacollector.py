import asyncpg
import logging
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

            query = """
            SELECT 
                id AS user_id,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date)) AS age,
                sex
            FROM profile
            """
            users = await conn.fetch()

            query = """
            SELECT profile_id AS user_id,
                film_id AS item_id,
                last_interaction AS last_watched_dt,
                watchtime AS total_dur
            FROM interaction
            """
            interactions = await conn.fetch()

            print("Interact")

            query = """
            SELECT 
                id AS item_id,
                name AS title,
                genres,
                year AS release_year,
                rating_kp, 
                age_rating
            FROM film"""
            films = await conn.fetch()

            await conn.close()
        except asyncpg.PostgresError as e:
            print(e)
            raise

        return StageOut((
            pd.DataFrame(users),
            pd.DataFrame(films),
            pd.DataFrame(interactions)
            )) # Tuple(raw_users_df, raw_items_df, raw_interactions_df)
