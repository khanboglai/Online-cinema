""" Scheduler """

import logging
from fastapi import FastAPI
import uvicorn
import aio_pika
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import pytz
from contextlib import asynccontextmanager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def rabbitmq_send_msg(message: str):
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
    async with connection:
        channel = await connection.channel()
        queue =  await channel.declare_queue("ml_queue", durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode('utf-8')),
            routing_key=queue.name,
        )

        logger.info("Successfully sended to rabbitmq")


async def scheduler_task():
    """ Будем отправлять сообщения в очередь """
    message = "ml"
    await rabbitmq_send_msg(message)


@asynccontextmanager
async def lifespan(_: FastAPI):
    moscow_tz = pytz.timezone("Europe/Moscow") # настройка временной зоны
    scheduler.add_job(scheduler_task, CronTrigger(hour=18, minute=34, timezone=moscow_tz)) # start job in 00:00 every day
    scheduler.start()
    logger.info("Scheduler started and job added")

    yield

    scheduler.shutdown()
    logger.info("Scheduler shut down")


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return {"message": "Live"}


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8085)
