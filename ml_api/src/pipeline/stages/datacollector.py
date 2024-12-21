import psycopg2
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

    def run(self, input: StageOut | None = None) -> StageOut:
        print("Here")
        try:
            conn = psycopg2.connect(database="cinema",
                                    user="debug",
                                    password="pswd",
                                    host="postgres",
                                    port="5432")

            cur = conn.cursor()
            print("Cur")

            cur.execute("SELECT id AS user_id, name, surname, EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date)) AS age, sex, email FROM profile")
            users_cols = [desc[0] for desc in cur.description]
            users = cur.fetchall()

            print("Users")

            cur.execute("SELECT profile_id AS user_id, film_id AS item_id, last_interaction AS last_watched_dt, count_interaction, watchtime AS total_dur FROM interaction")
            inter_cols = [desc[0] for desc in cur.description]
            interactions = cur.fetchall()

            print("Interact")

            cur.execute("SELECT id AS item_id, name AS title, description, directors, actors, genres, year AS release_year, countries, rating_kp, age_rating FROM film")
            films_cols = [desc[0] for desc in cur.description]
            films = cur.fetchall()

            cur.close()
            conn.close()
            print("Data selected")
        except psycopg2.OperationalError as e:
            print(e)
        # тут подключение к БД и получение данных
        return StageOut((pd.DataFrame(users, columns=users_cols), pd.DataFrame(films, columns=films_cols), pd.DataFrame(interactions, columns=inter_cols))) # Tuple(raw_users_df, raw_items_df, raw_interactions_df)
