from datetime import datetime
from typing import List, Optional

import bcrypt
from fastapi import Depends

# from api.auth.UserAuthentification import validate_user, get_password_hash
from core.database import get_session
from core.utils import *
from models.Pagination import Pagination
from models.elecdis_model import User, Tag, Transaction, UserGroup, Session as SessionModel
from sqlmodel import Session, create_engine, select, text
from api.exeptions.EmailException import EmailException
from pydantic import BaseModel



class UserData(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    phone: str
    subscription: Optional[str]
    partner: Optional[str]


class UserUpdate(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    id_user_group: int
    phone: str
    password: str
    id_subscription: Optional[int]
    id_partner: Optional[int]


def get_all_Admins(session: Session = Depends(get_session), need_all_datas_user:bool=False):
    query = select(User).join(UserGroup).where(
        UserGroup.name==ADMIN_NAME, User.state!=DELETED_STATE)
    clients = session.exec(query).all()
    if need_all_datas_user:
        return clients
    return get_list_user_data(clients)


def create_default_admin_usergroup(session: Session):
    # Check if the "Admin" user group exists
    admin_group = session.exec(select(UserGroup).where(UserGroup.name == ADMIN_NAME)).first()

    # If it does not exist, create it
    if not admin_group:
        admin_group = UserGroup(name=ADMIN_NAME)
        session.add(admin_group)
        session.commit()
        print(f"Default {ADMIN_NAME} user group created.")
    else:
        print(f"{ADMIN_NAME} user group already exists.")

def get_all_clients(session: Session = Depends(get_session)):
    query = select(User).join(UserGroup).where(UserGroup.name != ADMIN_NAME, User.state!=DELETED_STATE)
    clients = session.exec(query).all()
    return get_list_user_data(clients)

def get_new_clients_lists(session: Session = Depends(get_session), mois : Optional[int] = None, annee : int = datetime.utcnow().year):
    query = select(User).join(UserGroup).where(
        UserGroup.name!=ADMIN_NAME,
        User.state != DELETED_STATE,

    )
    if mois != None:
        print("mois =>", mois)
        query = query.where(text(f"EXTRACT(MONTH FROM user_table.created_at) = {mois}"))
    if annee != None:
        print("annee", annee)
        query = query.where(text(f"EXTRACT(YEAR FROM user_table.created_at) = {annee}"))
    else:
        print("else")
        query = query.where(text(f"EXTRACT(YEAR FROM user_table.created_at) = {datetime.utcnow().year}"))
    print(query)
    clients = session.exec(query).all()
    return get_list_user_data(clients)

def count_new_clients(session: Session = Depends(get_session), mois : Optional[int] = None, annee : int = datetime.utcnow().year):
    length = len(get_new_clients_lists(session, mois, annee))
    return length



def get_all_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return get_list_user_data(users)


def get_list_user_data(users: list[User]):
    return [UserData(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.user_group.name,
        phone=user.phone,
        subscription=user.subscription.type_subscription if user.subscription else None,
        partner=user.partner.name if user.partner else None
    ) for user in users]


def get_user_data(user):
    return UserData(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.user_group.name,
        phone=user.phone,
        subscription=user.subscription.type_subscription if user.subscription else None,
        partner=user.partner.name if user.partner else None
    )


def get_user_sessions_list(user, session):
    sessionLists: List[SessionModel] = session.exec(select(SessionModel).where(SessionModel.user_id == user.id)).all()
    return sessionLists


def get_user_transactions_list(user, session):
    sessions_id = [session_user.id for session_user in get_user_sessions_list(user, session)]
    transactions: List[Transaction] = session.exec(
        select(Transaction).where(Transaction.session_id.in_(sessions_id))).all()
    return transactions


def get_user_profile(user: UserData, session: Session):
    # sessions = get_user_sessions_list(user, session)
    transactions = get_user_transactions_list(user, session)
    return transactions


def get_user_tags_list(user, session):
    tags: List[Tag] = session.exec(select(Tag).where(
        Tag.user_id == user.id,
        Tag.state != DELETED_STATE
    )).all()
    return tags

def get_user_from_email(email: str, session: Session):
    user = session.exec(select(User).where(User.email == email, User.state!=DELETED_STATE)).first()
    return user

def get_user_by_id(id: int, session: Session):
    user = session.exec(select(User).where(User.id == id, User.state!=DELETED_STATE)).first()
    return user

def delete_user(id: int, session: Session):
    user = get_user_by_id(id, session)
    if user is None:
        raise Exception(f"User with id {id} does not exist.")
    user.state = DELETED_STATE
    session.add(user)
    session.commit()
    return {"message": "User deleted successfully"}

# nouveaux clients


# EXEMPLE PAGINATION

# session = next(get_session())
# pagination = Pagination(page=2, limit=2)
# users = session.exec(select(User).order_by(User.id).offset(pagination.offset).limit(pagination.limit)).all()
# has_next = len(users) > pagination.limit

# print(f"pagination {has_next}")
# for i in users:
#     print(i.id)
