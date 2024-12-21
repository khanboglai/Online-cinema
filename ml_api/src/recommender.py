import pandas as pd
from catboost import CatBoostClassifier
from implicit.nearest_neighbours import BM25Recommender
from rectools import Columns
from rectools.dataset import Dataset
from rectools.models import ImplicitItemKNNWrapperModel, RandomModel, PopularModel
from sklearn.model_selection import train_test_split
from abstract.recommender import *

class Recommender(RecommenderABC):
    """
    RecSys recommender (BM25 Implicit ItemKNN + CatBoost)
    """

    def __init__(self, 
                 n_candidates: int = 200,
                 n_recs: int = 10,
                 candidates_selector_cfg: dict[str, Any] | None = None,
                 reranker_cfg: dict[str, Any] | None = None
                 ):

        # first-stage candidates number
        self._n_candidates = n_candidates

        # total peronalized recommendations size
        self._n_recs = n_recs

        # first-stage model
        self._candidate_selector = ImplicitItemKNNWrapperModel(BM25Recommender(**candidates_selector_cfg))
        # second-stage model
        self._reranker = CatBoostClassifier(**reranker_cfg)

        # dataframes
        self._items_df: pd.DataFrame | None = None
        self._users_df: pd.DataFrame | None = None
        self._interactions_df: pd.DataFrame | None = None

        # rectools interactions Dataset
        self._dataset: Dataset | None = None

        # list of "hot" users
        self._hot_users_id: set[int] | None = None
        # list of "warm" users
        self._warm_users_id: set[int] | None = None

        # model fit flag
        self._is_fitted: bool = False
    
    def fit(self,
            items_df: pd.DataFrame,
            users_df: pd.DataFrame,
            interactions_df: pd.DataFrame
            ) -> None:

        self._items_df = items_df
        self._users_df = users_df
        self._interactions_df = interactions_df
        self._dataset = Dataset.construct(self._interactions_df)

        # create "hot" and "warm" user_ids list
        self._hot_users_id = set(self._interactions_df["user_id"].unique().tolist())
        self._warm_users_id = set([u for u in set(self._users_df["user_id"].unique().tolist())\
            if u not in self._hot_users_id])

        if len(interactions_df) < 100:
            self._candidate_selector = RandomModel()
            self._reranker = None
            self._candidate_selector.fit(self._dataset)
            return
        elif len(interactions_df) < 10000:
            self._candidate_selector = PopularModel(popularity="n_interactions")
            self._reranker = None
            self._candidate_selector.fit(self._dataset)
            return

        # split the data on train and test sets
        split_dt = self._interactions_df["datetime"].quantile(q=0.75, interpolation="nearest")

        train_df = self._interactions_df[self._interactions_df["datetime"] < split_dt]
        test_df = self._interactions_df[self._interactions_df["datetime"] >= split_dt]

        train_dataset = Dataset.construct(train_df)

        # use candidates selector model on train set 
        self._candidate_selector.fit(train_dataset)
        train_candidates = self._candidate_selector.recommend(
            dataset=train_dataset,
            k=50,
            users=self._hot_users_id,
            filter_viewed=True
        )

        # create positive examples
        positives = train_candidates.merge(test_df, on=["user_id", "item_id"], how="inner")
        positives["target"] = 1

        # create negative examples
        negatives = train_candidates.set_index(["user_id", "item_id"])\
            .join(test_df.set_index(["user_id", "item_id"]))
        negatives = negatives[negatives["watched_pct"].isnull().reset_index()]
        negatives = negatives.sample(frac=0.07)
        negatives["target"] = 0

        # build CatBoost datasets
        train_users, val_users = train_test_split(test_df["user_id"].unique(), test_size=0.2)
        gb_train = pd.concat([
            positives[positives["user_id"].isin(train_users)],
            negatives[negatives["user_id"].isin(train_users)]
            ]).sample(frac=1).reset_index(drop=True)
        gb_val = pd.concat([
            positives[positives["user_id"].isin(val_users)],
            negatives[negatives["user_id"].isin(val_users)]
            ]).sample(frac=1).reset_index(drop=True)
        
        user_cols = ["user_id", "age", "sex", "kids_flg"]
        item_cols = ["item_id", "for_kids", "content_type", "age_rating", "rating_kp"]

        gb_train = gb_train.merge(
            users_df[user_cols], on=["user_id"], how="left"
            ).merge(items_df[item_cols], on=["item_id"], how="left")
        
        gb_val = gb_val.merge(
            users_df[user_cols], on=["user_id"], how="left"
            ).merge(items_df[item_cols], on=["item_id"], how="left")
        
        cols_to_drop = ["item_id", "user_id"]
        target_col = ["target"]
        cat_cols = ["age", "sex", "content_type"]

        X_train, y_train = gb_train.drop(cols_to_drop + target_col, axis=1), gb_train[target_col]
        X_val, y_val = gb_val.drop(cols_to_drop + target_col, axis=1), gb_val[target_col]

        # fit the reranker model
        self._reranker.fit(
            X_train,
            y_train,
            eval_set=(X_val, y_val),
            early_stopping_rounds=100,
            cat_features=cat_cols,
            verbose=False
        )

        # set the model as fitted
        self._is_fitted = True

    def recommend_all(self) -> pd.DataFrame:
        if not self._is_fitted:
            raise RuntimeError("Recommender is not fitted yet")
        
        if self._reranker is None:
            return self._candidate_selector.recommend(
                k=self._n_recs,
                users=self._hot_users_id | self._warm_users_id,
                dataset=self._dataset,
                filter_viewed=True
            )

        # make candidates for "hot" users
        candidates = self._candidate_selector.recommend(
            k=self._n_candidates,
            users=self._hot_users_id,
            dataset=self._dataset,
            filter_viewed=True
        )

        user_cols = ["user_id", "age", "sex", "kids_flg"]
        item_cols = ["item_id", "for_kids", "content_type", "age_rating", "rating_kp"]
        cols_to_drop = ["item_id", "user_id"]

        candidates = candidates.merge(
            self._users_df[user_cols], on=["user_id"], how="left"
            ).merge(self._items_df[item_cols], on=["item_id"], how="left")
        
        candidates.drop(cols_to_drop, axis=1)

        # predict probabilities with CatBoost 
        scores = self._reranker.predict_proba(candidates.drop(cols_to_drop, axis=1))
        candidates["reranker_score"] = scores[:, 1]

        # sort candidates by reranker rank
        candidates.sort_values(
            by=["user_id", "reranker_score"],
            ascending=(True, False)
        )

        # save new candidate ranking
        candidates.drop(["score", "reranker_score"], axis=1, inplace=True)
        candidates["rank"] = candidates.groupby("user_id").cumcount() + 1
        
        return candidates.reset_index(drop=True)
