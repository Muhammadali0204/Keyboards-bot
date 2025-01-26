from pathlib import Path

from decouple import Config, Csv


config = Config(repository='.env')

ADMINS = config('ADMINS', cast=Csv(int))
BOT_TOKEN = config("BOT_TOKEN", cast=str)
BOT_USERNAME = config("BOT_USERNAME", cast=str)
DB_URL = config("DB_URL", cast=str)
REDIS_URL = config("REDIS_URL", cast=str)
RATE_LIMIT = config('RATE_LIMIT', cast=int)
WEBHOOK_HOST = config("WEBHOOK_HOST", cast=str)
MAX_CHANNELS_COUNT = config('MAX_CHANNELS_COUNT', cast=int)

WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URI = WEBHOOK_HOST + WEBHOOK_PATH

BASE_DIR = Path(__file__).resolve().parent.parent
PHOTO_PATH = BASE_DIR / 'static' / 'media' / 'photos'
