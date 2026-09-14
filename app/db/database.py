from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

class Base(DeclarativeBase):
    pass

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)  # echo=True prints the raw SQL queries to your console

# sessionmaker acts as a factory that fabricates brand new Session objects for us
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
