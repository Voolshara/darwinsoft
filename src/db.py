from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

CONNECTION_STRING = "postgresql+psycopg2://{}:{}@{}/{}".format(
    getenv("POSTGRES_USER"),
    getenv("POSTGRES_PASSWORD"),
    getenv("POSTGRES_HOST"),
    getenv("POSTGRES_DB"),
)

engine = create_engine(CONNECTION_STRING)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

