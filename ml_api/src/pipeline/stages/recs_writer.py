import psycopg2
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

        recs = recs[["user_id", "item_id"]]

        df = pd.DataFrame(recs)

        recs_grouped = df.groupby('user_id')['item_id'].agg(list).reset_index()

        recs_grouped = [tuple(row) for row in recs_grouped.values]
        
        try:
            conn = psycopg2.connect(database="cinema",
                                    user="debug",
                                    password="pswd",
                                    host="postgres",
                                    port="5432")
            cur  = conn.cursor()

            cur.execute("DELETE FROM recommend")
            print(recs_grouped)

            cur.executemany("INSERT INTO recommend (profile_id, film_ids) VALUES (%s, %s) RETURNING profile_id", recs_grouped)

            # ids = await conn.executemany(query2, recs_grouped)

            conn.commit()
            
            cur.close()
            conn.close()
            print("Inserted successfully")
        except psycopg2.errors.ConnectionException as e:
            print(f"Recs_writer: {e}")
        # тут запись рекомендаций в БД

