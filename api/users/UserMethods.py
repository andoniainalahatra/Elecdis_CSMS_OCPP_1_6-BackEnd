
import bcrypt
from fastapi import Depends

from core.database import get_session
from models.elecdis_model import User, Tag
from sqlmodel import Session, create_engine, select
from api.exeptions.EmailException import EmailException


def get_all_clients(session: Session = Depends(get_session)):
    clients = session.exec(select(User)).all()
    return clients

def get_all_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users