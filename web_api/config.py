"""Config"""
import os
import json
import logging
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from starlette.templating import Jinja2Templates
import boto3


# load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """ Settings """
    DB_HOST: str | None = os.getenv("DB_HOST")
    DB_PORT: str | None = os.getenv("DB_PORT")
    DB_NAME: str | None = os.getenv("DB_NAME")
    DB_USER: str | None = os.getenv("DB_USER")
    DB_PASSWORD: str | None = os.getenv("DB_PASSWORD")
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")
    ALGORITHM: str | None = os.getenv("ALGORITHM")
    


settings = Settings()

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
templates = Jinja2Templates(directory=templates_dir)

def get_db_url():
    """Getter of db URL"""
    return (f"postgresql+asyncpg://debug:pswd@"
            f"cinema_postgres_db:5432/cinema")


# S3 settings

s3_client = boto3.client(
    's3',
    endpoint_url='http://storage:9000', # ссылка на сайт
    aws_access_key_id='storage', # логин
    aws_secret_access_key='qwerty2024', # пароль
)

# название бакета
BUCKET_NAME = 'storage-cinema'

# # Настройка конфигурации для многочастной загрузки
# config = TransferConfig(
#     multipart_threshold=1024 * 25,  # Порог для многочастной загрузки (25 МБ)
#     max_concurrency=10,              # Максимальное количество параллельных загрузок
#     multipart_chunksize=1024 * 25,   # Размер частей (25 МБ)
#     use_threads=True                  # Использовать потоки
# )

