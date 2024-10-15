import re
from datetime import datetime
from typing import List, Optional

import bcrypt
from fastapi import Depends

from api.transaction.Transaction_models import Session_data_affichage, Transaction_details
# from api.transaction.Transaction_service import get_list_session_data_2
# from api.auth.UserAuthentification import validate_user, get_password_hash
from core.database import get_session
from core.utils import *
from models.Pagination import Pagination
from models.elecdis_model import User, Tag, Transaction, UserGroup, Session as SessionModel, Subscription, Partner
from sqlmodel import Session, select, text, func, cast, String
from api.exeptions.EmailException import EmailException
from pydantic import BaseModel
from passlib.context import CryptContext


class UserData(BaseModel):
    id: int
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: str
    role: str
    phone: Optional[str] = ""
    subscription: Optional[str]
    partner: Optional[str]


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    id_user_group: Optional[int] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    id_subscription: Optional[int] = None
    id_partner: Optional[int] = None


class UserUpdateData(BaseModel):
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    id_user_group: Optional[int] = None
    phone: Optional[str] = None
    id_subscription: Optional[int] = None
    id_partner: Optional[int] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_email_structure(email: str):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        raise EmailException(f"Email {email} is not valid")


def set_update_user_data(user: User):
    return UserUpdateData(id=user.id,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          email=user.email,
                          id_user_group=user.id_user_group,
                          phone=user.phone,
                          id_subscription=user.id_subscription,
                          id_partner=user.id_partner
                          )


def get_all_Admins(session: Session = Depends(get_session), page: Optional[int] = 1, item_numbers: Optional[int] = 50,
                   need_all_datas_user: bool = False):
    pagination = Pagination(page=page, limit=item_numbers)
    total_items_query = select(func.count(User.id)).join(UserGroup).where(
        UserGroup.name == ADMIN_NAME, User.state != DELETED_STATE)
    total_items = session.exec(total_items_query).one()
    pagination.total_items = total_items
    query = (select(User).join(UserGroup).where(
        UserGroup.name == ADMIN_NAME, User.state != DELETED_STATE)
             .offset(pagination.offset).limit(pagination.limit))
    clients = session.exec(query).all()
    if need_all_datas_user:
        return clients
    return {"data": get_list_user_data(clients), "pagination": pagination.dict()}


def create_default_admin_usergroup(session: Session):
    # Check if the "Admin" user group exists
    admin_group = session.exec(select(UserGroup).where(UserGroup.name == ADMIN_NAME)).first()

    # If it does not exist, create it
    if not admin_group:
        admin_group = UserGroup(name=ADMIN_NAME)
        session.add(admin_group)
        session.commit()


def get_all_clients(session: Session = Depends(get_session), page: int = 1, number_items: int = 50):
    pagination = Pagination(page=page, limit=number_items)
    # Query to count total items
    total_items_query = select(func.count(User.id)).join(UserGroup).where(
        UserGroup.name != ADMIN_NAME, User.state != DELETED_STATE)
    total_items = session.exec(total_items_query).one()
    pagination.total_items = total_items

    query = (select(User).join(UserGroup).
             where(UserGroup.name != ADMIN_NAME, User.state != DELETED_STATE))
    query = query.offset(pagination.offset).limit(pagination.limit)
    clients = session.exec(query).all()
    return {"data": get_list_user_data(clients), "pagination": pagination.dict()}


def get_new_clients_lists(session: Session = Depends(get_session), mois: Optional[int] = None,
                          annee: int = datetime.utcnow().year, page=1, number_items=50
                          ):
    query = select(User).join(UserGroup).where(
        UserGroup.name != ADMIN_NAME,
        User.state != DELETED_STATE,
    )
    pagination = Pagination(page=page, limit=number_items)
    total_items_query = select(func.count(User.id)).join(UserGroup).where(
        UserGroup.name != ADMIN_NAME,
        User.state != DELETED_STATE,
    )
    if mois != None:
        query = query.where(text(f"EXTRACT(MONTH FROM user_table.created_at) = {mois}"))
        total_items_query = total_items_query.where(text(f"EXTRACT(MONTH FROM user_table.created_at) = {mois}"))
    if annee != None:
        query = query.where(text(f"EXTRACT(YEAR FROM user_table.created_at) = {annee}"))
        total_items_query = total_items_query.where(text(f"EXTRACT(YEAR FROM user_table.created_at) = {annee}"))
    else:
        query = query.where(text(f"EXTRACT(YEAR FROM user_table.created_at) = {datetime.utcnow().year}"))
        total_items_query = total_items_query.where(
            text(f"EXTRACT(YEAR FROM user_table.created_at) = {datetime.utcnow().year}"))
    total_items = session.exec(total_items_query).one()
    pagination.total_items = total_items

    clients = session.exec(query).all()
    return {"data": get_list_user_data(clients), "pagination": pagination.dict()}


def count_new_clients(session: Session = Depends(get_session), mois: Optional[int] = None,
                      annee: int = datetime.utcnow().year):
    length = len(get_new_clients_lists(session, mois, annee).get("data"))
    return length


def get_all_users(session: Session = Depends(get_session), page=1, number_items=50):
    pagination = Pagination(page=page, limit=number_items)
    total_items = session.exec(select(func.count(User.id)).where(User.state != DELETED_STATE)).one()
    pagination.total_items = total_items
    users = session.exec(select(User).where(User.state != DELETED_STATE)).all()
    return {"data": get_list_user_data(users), "pagination": pagination.dict()}


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


def get_user_sessions_list(user, session: Session, page: int = 1, number_items: int = 50):
    pagination = Pagination(page=page, limit=number_items)
    total_items = session.exec(select(func.count(SessionModel.id)).where(SessionModel.user_id == user.id)).one()
    pagination.total_items = total_items
    sessionLists: List[SessionModel] = session.exec(select(SessionModel).where(SessionModel.user_id == user.id)).all()
    try:
        datas = get_list_session_data(sessionLists, session)
    except Exception as e:
        print(e)
        datas = []
    return {"data": datas, "pagination": pagination.dict()}


def get_sums_transactions(session: Session, session_id: int):
    sum = session.exec(
        select(
            func.sum(Transaction.total_price),
            Transaction.currency,
            Transaction.energy_unit
        ).where(
            Transaction.session_id == session_id
        ).group_by(
            Transaction.currency,
            Transaction.energy_unit
        )
    ).one()
    result_dict = Transaction_details(
        total_price=sum[0],
        currency=sum[1],
        energy_unit=sum[2])

    return result_dict


def get_session_data(session: SessionModel, session_db: Session):
    try:
        transaction_datas = get_sums_transactions(session_db, session.id)
    except Exception as e:
        print("eto", e)
        transaction_datas = Transaction_details()
    data = Session_data_affichage(
        id=session.id,
        start_time=session.start_time,
        end_time=session.end_time,
        connector_id=session.connector_id,
        user_id=session.user_id,
        user_name=session.user.first_name + " " + session.user.last_name,
        consumed_energy=f'{session.metter_stop - session.metter_start} {transaction_datas.energy_unit}',
        rfid=session.tag,
        charge_point_id=session.connector.charge_point_id,
        total_cost=f'{transaction_datas.total_price} {transaction_datas.currency}',
    )
    return data


def get_list_session_data(sessions: List[SessionModel], session_db: Session):
    if len(sessions) == 0:
        return []
    return [get_session_data(session, session_db) for session in sessions]


def get_user_transactions_list(user, session, page: int = 1, number_items: int = 50):
    pagination = Pagination(page=page, limit=number_items)
    sessions_id = [session_user.id for session_user in get_user_sessions_list(user, session)]
    total_items = session.exec(
        select(Transaction.id).where(Transaction.session_id.in_(sessions_id))).one()
    pagination.total_items = total_items
    transactions: List[Transaction] = session.exec(
        select(Transaction).where(Transaction.session_id.in_(sessions_id))).all()
    return {"data": transactions, "pagination": pagination.dict()}


def get_user_tags_list(user, session, page, number_items):
    pagination = Pagination(page=page, limit=number_items)
    total_items = session.exec(select(func.count(Tag.id)).where(
        Tag.user_id == user.id,
        Tag.state != DELETED_STATE)).one()
    pagination.total_items = total_items
    tags: List[Tag] = session.exec(select(Tag).where(
        Tag.user_id == user.id,
        Tag.state != DELETED_STATE
    )).all()
    return {"data": tags, pagination: pagination.dict()}


def get_user_from_email(email: str, session: Session):
    user = session.exec(select(User).where(User.email == email, User.state != DELETED_STATE)).first()
    return user


def get_user_by_id(id: int, session: Session):
    user = session.exec(select(User).where(User.id == id, User.state != DELETED_STATE)).first()
    return user


def delete_user(id: int, session: Session):
    user = get_user_by_id(id, session)
    if user is None:
        raise Exception(f"User with id {id} does not exist.")
    user.state = DELETED_STATE
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    return {"message": "User deleted successfully"}


async def upload_user_from_csv(file: UploadFile, session: Session):
    logs = []
    try:
        with session.begin():
            datas = await get_datas_from_csv(file)
            line = 1
            for data in datas:
                try:
                    verify_email_structure(data["email"].strip())
                except Exception as e:
                    logs.append({"message": str(e), "line": line})
                    line += 1
                    continue
                #     check if user already exists
                user = get_user_from_email(data["email"], session)
                if user is not None:
                    logs.append({"message": f"User with email {data['email']} already exists.", "line": line})
                    line += 1
                    continue
                else:
                    # check user group
                    user_group = session.exec(
                        select(UserGroup).where(UserGroup.name == data["user_group"].strip().lower())).first()
                    if user_group is None:
                        user_group = UserGroup(name=data["user_group"].strip().lower())
                        session.add(user_group)
                        session.flush()

                    # check subscription
                    subscription = session.exec(select(Subscription).where(
                        Subscription.type_subscription == data["subscription"].strip().lower())).first()
                    if subscription is None:
                        subscription = Subscription(type_subscription=data["subscription"].strip().lower())
                        session.add(subscription)
                        session.flush()
                    # check partner
                    partner: Optional[Partner] = None
                    if "partner" in data:
                        try:
                            partner = session.exec(
                                select(Partner).where(Partner.name == data["partner"].strip().lower())).first()
                            if partner is None and data["partner"].strip() != "":
                                partner = Partner(name=data["partner"].strip().lower())

                                session.add(partner)
                                session.flush()
                        except Exception as e:
                            print({"message": f"Partner {data['partner']} does not exist.", "line": line})
                    pid, sid, uid = partner.id if partner else None, subscription.id if subscription else None, user_group.id if user_group else None
                    user = User(
                        first_name=data["first_name"],
                        last_name=data["last_name"],
                        email=data["email"],
                        phone=data["phone"],
                        password=pwd_context.hash(data["password"]),
                        id_user_group=uid,
                        id_subscription=sid,
                        id_partner=pid
                    )
                    print(user)
                    session.add(user)
                    line += 1
            if len(logs) > 0:
                session.rollback()
                return {"messages": "Some errors occured during the upload.", "logs": logs}
            session.commit()
            return {"message": "Users imported successfully"}

    except Exception as e:
        session.rollback()
        return {"message": f"Error: {str(e)}"}


def search_queries_users(queries: str, session: Session, page, number_items):
    try:
        pagination = Pagination(page=page, limit=number_items)
        count_q = (select(func.count(User.id)).join(Subscription, User.id_subscription == Subscription.id).
        join(UserGroup, User.id_user_group == UserGroup.id).
        outerjoin(Partner, User.id_partner == Partner.id).
        where(
            func.concat(
                cast(User.last_name, String), ' ',
                cast(User.first_name, String), ' ',
                cast(User.email, String), ' ',
                cast(User.phone, String), ' ',
                cast(UserGroup.name, String), ' ',
                cast(Subscription.type_subscription, String)
            ).like(f"%{queries}%")
        ))
        count = session.exec(count_q).one()
        pagination.total_items = count
        query = (select(User).join(Subscription, User.id_subscription == Subscription.id).
        join(UserGroup, User.id_user_group == UserGroup.id).
        outerjoin(Partner, User.id_partner == Partner.id).
        where(
            func.concat(
                cast(User.last_name, String), ' ',
                cast(User.first_name, String), ' ',
                cast(User.email, String), ' ',
                cast(User.phone, String), ' ',
                cast(UserGroup.name, String), ' ',
                cast(Subscription.type_subscription, String)
            ).like(f"%{queries}%")
        ))

        users = session.exec(query).all()
        return {"data": get_list_user_data(users), "pagination": pagination.dict()}
    except Exception as e:
        print(e)


# EXEMPLE PAGINATION

# session = next(get_session())
# pagination = Pagination(page=2, limit=2)
# users = session.exec(select(User).order_by(User.id).offset(pagination.offset).limit(pagination.limit)).all()
# has_next = len(users) > pagination.limit

# print(f"pagination {has_next}")
# for i in users:
#     print(i.id)




