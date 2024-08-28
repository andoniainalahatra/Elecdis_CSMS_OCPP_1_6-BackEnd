import bcrypt
from fastapi import Depends

from core.database import get_session
from models.elecdis_model import User, Tag, UserGroup
from sqlmodel import Session, create_engine, select, text
from api.exeptions.EmailException import EmailException
from pydantic import BaseModel

class UserData(BaseModel):
    id: int
    first_name: str
    last_name: str
    email:str
    role:str


def get_all_Admins(session: Session = Depends(get_session)):
    query = select(User).join(UserGroup).where(UserGroup.name.in_(['admin', 'Admin', 'Administrator', 'administrator', 'ADMIN']))
    clients = session.exec(query).all()
    return get_list_user_data(clients)

def get_all_clients(session: Session = Depends(get_session)):
    query = select(User).join(UserGroup).where(UserGroup.name not in get_all_Admins(session))
    clients = session.exec(query).all()
    return get_list_user_data(clients)


def get_all_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return get_list_user_data(users)

def get_list_user_data(users : list[User]):
    return [UserData(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.user_group.name
    ) for user in users]


def get_user_data(user):
    return UserData(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.user_group.name
    )