import os
import logging
from multiprocessing import Process

import uvicorn
from fastapi import FastAPI

from apscheduler.schedulers.background import BackgroundScheduler

from routers import router
from pipeline.pipeline import *
from pipeline.stages.datacollector import DataCollector
from pipeline.stages.datapreparer import DataPreparer
from pipeline.stages.recsys_inference import RecSysInference
from pipeline.stages.recs_writer import RecsWriter

DB_CONFIG = {
    "DATABASE_URL": "postgresql://debug:pswd@db:5432/cinema"
}

logger = logging.getLogger(__name__)
app = FastAPI()
scheduler = BackgroundScheduler()
pipeline = Pipeline([
    DataCollector(DB_CONFIG),
    DataPreparer(),
    RecSysInference(),
    RecsWriter(DB_CONFIG)
], logger=logger)

def background_task() -> None:
    def run_pipeline(pipeline: Pipeline) -> Tuple[bool, int]:
        r, i = pipeline.run_all()
        if r:
            logger.info("Background task finished successfully.")
        else:
            logger.error(f"Background task failed. {i}")
        return (r, i)

    logger.info("Starting background process...")
    p = Process(target=run_pipeline, args=(pipeline,))
    p.start()
    p.join()
    logger.info("Background process joined.")

if __name__ == "__main__":
    scheduler.add_job(background_task, "interval", seconds=20, id="recsys_offline_pipeline")
    scheduler.start()
    uvicorn.run(app=app, host="0.0.0.0", port=8080)
