from sqlmodel import SQLModel, create_engine, Session
from core.config import DATABASE_URL
import psycopg2

engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
