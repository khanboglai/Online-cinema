import time
import uvicorn

from pydantic import BaseModel
from typing import List

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from recommender import Recommender
from data_collector import DataCollector

class RecSysResponse(BaseModel):
    user_id: int
    status: int
    recommendations: List[int]

app = FastAPI()
model = Recommender()
data_collector = DataCollector()
scheduler = BackgroundScheduler()

def update_model_task():
    print("Start model update...")
    time.sleep(30)
    print("End model update!")

@app.get("/recommend/{user_id}", response_model=RecSysResponse)
async def send_recommendations(user_id: int):
    item_ids = await model.recommend(user_id=user_id)
    return RecSysResponse(
        user_id=user_id,
        status=200,
        recommendations=item_ids
    )

if __name__ == "__main__":
    scheduler.add_job(update_model_task, "interval", minutes=5)
    scheduler.start()
    uvicorn.run(app=app, host="0.0.0.0", port=8080)