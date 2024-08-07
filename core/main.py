# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the API"}


from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from typing import List
from models.hero import Hero
import models.elecdis_model
from core.database import init_db, get_session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

# @app.get("/heroes/", response_model=List[Hero])
# def read_heroes(session: Session = Depends(get_session)):
#     heroes = session.exec(select(Hero)).all()
#     return heroes

# @app.post("/heroes/", response_model=Hero)
# def create_hero(hero: Hero, session: Session = Depends(get_session)):
#     session.add(hero)
#     session.commit()
#     session.refresh(hero)
#     return hero

@app.get("/users/", response_model=List[models.elecdis_model.User])
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(models.elecdis_model.User)).all()
    return users