from sqlmodel import SQLModel, create_engine, Session
from core.config import DATABASE_URL, MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT, MONGO_AUTH_DATABASE
import psycopg2
from motor.motor_asyncio import AsyncIOMotorClient

engine = create_engine(DATABASE_URL)

MONGO_DETAILS = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource={MONGO_AUTH_DATABASE}"
#MONGO_DETAILS = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.metering_db 
meter_values_collection = database.get_collection("meter_values")