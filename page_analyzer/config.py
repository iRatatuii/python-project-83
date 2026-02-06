import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL не установлена")

SECRET_KEY = os.getenv("SECRET_KEY")

FLASK_ENV = os.getenv("FLASK_ENV")
