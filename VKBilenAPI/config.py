# config.py
import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    print(os.getenv("SECRET_KEY"))
    SECRET_KEY = os.getenv("SECRET_KEY")
    print(os.getenv("DATABASE_URL"))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
