import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from pipeline.pipeline import *
from recommender import Recommender

class RecSysInference(StageABC):
    """
    Fits recommender model and updates recommendations
    """

    def __init__(self):
        super().__init__("RecSysInference")

    def run(self, input: StageOut | None = None) -> StageOut:
        model = Recommender(
            candidates_selector_cfg={
                "n_estimators": 1000,
                "max_depth": 5,
                "learning_rate": 0.12,
                "thread_count": 16,
            },
            reranker_cfg={
                "K": 60,
                "K1": 0.6,
                "B": 0.8
            }
            )
        
        data = input.unpack()
        model.fit(*data)
        return StageOut(model.recommend_all())
