from starlette.config import Config
from starlette.datastructures import Secret

try:
    config=Config(".env")
except:
    config=Config()

db_url=config("Database_url",cast=Secret)
