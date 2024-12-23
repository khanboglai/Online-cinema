import os
import logging
from multiprocessing import Process

import aio_pika
import uvicorn
from fastapi import FastAPI

from apscheduler.schedulers.background import BackgroundScheduler
from aio_pika import connect, Message, ExchangeType
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


# def background_task() -> None:
    

#     logger.info("Starting background process...")
#     p = Process(target=run_pipeline, args=(pipeline,))
#     p.start()
#     p.join()
#     logger.info("Background process joined.")

async def run_pipeline(pipeline: Pipeline) -> Tuple[bool, int]:
    r, i = pipeline.run_all()
    if r:
        logger.info("Background task finished successfully.")
    else:
        logger.error(f"Background task failed. {i}")
    return (r, i)


async def on_message(message: Message):
    logger.info("Received a task from RabbitMQ.")
    message_body = message.body.decode()  # Декодируем тело сообщения
    routing_key = message.routing_key  # Получаем ключ маршрутизации
    if message_body == "ml" and routing_key == "ml_queue":
        await run_pipeline(pipeline)
        logger.info("Start ML")
    await message.ack()  # Подтверждаем получение сообщения


async def start_rabbitmq_listener():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()  # Создаем канал

    await channel.set_qos(prefetch_count=1)  # Устанавливаем QoS

    queue = await channel.declare_queue("ml_queue", durable=True)  # Объявляем очередь

    await queue.consume(on_message)  # Подписываемся на очередь

    logger.info("Waiting for messages. To exit press CTRL+C")
    return connection  # Возвращаем соединение для дальнейшего использования


@app.on_event("startup")
async def startup_event():
    app.state.rabbit_connection = await start_rabbitmq_listener()


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.rabbit_connection.close()


if __name__ == "__main__":
    # scheduler.add_job(background_task, "interval", seconds=20, id="recsys_offline_pipeline")
    # scheduler.start()
    uvicorn.run(app=app, host="0.0.0.0", port=8080)
