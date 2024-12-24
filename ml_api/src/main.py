import os
import logging

import aio_pika
import uvicorn
from fastapi import FastAPI

from apscheduler.schedulers.background import BackgroundScheduler
from aio_pika import Message
from routers import router
from pipeline.pipeline import *
from pipeline.stages.datacollector import DataCollector
from pipeline.stages.datapreparer import DataPreparer
from pipeline.stages.recsys_inference import RecSysInference
from pipeline.stages.recs_writer import RecsWriter
from contextlib import asynccontextmanager

# TODO: конфиг нужно через .env сюда притянуть
DB_CONFIG = {
    "database": "cinema",
    "user": "debug",
    "password": "pswd",
    "host": "postgres",
    "port": "5432"
}

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    r, i = await pipeline.run_all()
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
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
        channel = await connection.channel()  # Создаем канал

        await channel.set_qos(prefetch_count=1)  # Устанавливаем QoS

        queue = await channel.declare_queue("ml_queue", durable=True)  # Объявляем очередь

        await queue.consume(on_message)  # Подписываемся на очередь

        logger.info("Waiting for messages. To exit press CTRL+C")
        return connection  # Возвращаем соединение для дальнейшего использования
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise


@asynccontextmanager
async def lifespan(_: FastAPI):
    app.state.rabbit_connection = await start_rabbitmq_listener()
    logger.info("Successfully connected to rabbitmq")

    yield

    await app.state.rabbit_connection.close()
    logger.info("Closed connection with rabbitmq")


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8080)
