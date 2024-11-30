import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix

from rectools import Columns
from rectools.models import ImplicitALSWrapperModel
from rectools.dataset import Dataset
from implicit.als import AlternatingLeastSquares

DATASET_DIR = "./data"

if __name__ == "__main__":
    interactions_df = pd.read_csv(
        f"{DATASET_DIR}/interactions.csv",
        header=None,
        index_col=False,
        names=[Columns.User, Columns.Item, Columns.Datetime, "total_dur", "watched_pcs", Columns.Weight]
    )
    interactions_df["datetime"] = pd.to_datetime(interactions_df["datetime"])

    dataset = Dataset.construct(interactions_df)

    user_item_matrix = csr_matrix(
            (interactions_df[Columns.Weight], 
            (interactions_df[Columns.User], interactions_df[Columns.Item])
            )
        )
    model = AlternatingLeastSquares(
        factors=12,
        regularization=0.05,
        iterations=7
    )

    model.fit(user_items=user_item_matrix)

    model.save("./artefacts/model")

