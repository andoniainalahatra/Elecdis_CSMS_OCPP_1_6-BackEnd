from typing import Optional

from sqlalchemy.orm import Session as Session_db
from sqlmodel import select,func,cast,Date
from datetime import date, datetime

from api.users.UserServices import count_new_clients
from core.utils import DELETED_STATE, ADMIN_NAME
from models.elecdis_model import User, Session as SessionModel, Transaction, Historique_metter_value, UserGroup


def get_dashboard_datas_by_date(session:Session_db, date_choosen:date):
    # get the number of charging sessions
    charging_sessions = count_session_charge_by_date(session, date_choosen)
    # get total energy consumed
    energy_consumed = total_energy_by_date(session, date_choosen)
    # get total revenue
    revenue = total_revenus_by_date(session, date_choosen)
    # get the number of users
    users = count_users_by_date(session, date_choosen)

    return {"revenus": revenue, "nombres_sessions": charging_sessions, "nombre_utilisateurs": users, "energy_kwh": energy_consumed}

def count_users_by_date(session: Session_db, date_here: date):
    query = select(func.count(User.id)).join(UserGroup, User.id_user_group == UserGroup.id).where(cast(User.created_at, Date) == date_here,User.state!=DELETED_STATE,UserGroup.name!=ADMIN_NAME)
    result = session.exec(query).one()
    return result

def count_all_users(session: Session_db):
    query = select(func.count(User.id)).select_from(User).join(UserGroup, User.id_user_group == UserGroup.id).where(User.state != DELETED_STATE, UserGroup.name != ADMIN_NAME)
    result = session.exec(query).one()
    return result

def count_users_by_month(session:Session_db, month:Optional[int], year:Optional[int]):
    return count_new_clients(session=session,mois=month,annee=year)
def count_session_charge_by_date(session: Session_db, date_here: date):
    query = select(func.count(SessionModel.id)).where(cast(SessionModel.start_time, Date) == date_here).where(SessionModel.id!=-1)
    result = session.exec(query).one()
    return result
def count_session_charge_by_month(session:Session_db, month:Optional[int], year:Optional[int]):
    query = select(func.count(SessionModel.id)).where(func.extract('year', SessionModel.start_time) == year)
    if month is not None:
        query = query.where(func.extract('month', SessionModel.start_time) == month)
    result = session.exec(query).one()
    return result

def total_session_charge(session:Session_db):
    query = select(func.count(SessionModel.id)).where(SessionModel.id!=-1)
    result = session.exec(query).one()
    return result

def total_revenus_by_date(session: Session_db, date_here: date):
    query = select(
        ((func.sum(Transaction.total_price)))
    ).select_from(
        SessionModel
    ).join(
        Transaction, SessionModel.id == Transaction.session_id
    ).where(
        cast(SessionModel.start_time, Date) == date_here
    ).where(
        SessionModel.id != -1
    )
    results = session.exec(query).one()
    return results
def total_revenus_by_month(session:Session_db, month:Optional[int], year:Optional[int]):
    query = (select (func.sum(Transaction.total_price))
             .select_from(SessionModel).
             join(Transaction, SessionModel.id == Transaction.session_id)
             .where(func.extract('year', SessionModel.start_time) == year))
    if month is not None:
        query = query.where(func.extract('month', SessionModel.start_time) == month)
    results = session.exec(query).one()
    return results

def get_total_revenus(session:Session_db):
    query = select(func.sum(Transaction.total_price))
    result = session.exec(query).one()
    return result
def get_currency(session:Session_db):
    query = select(Transaction.currency).distinct()
    result = session.exec(query).one()
    return result
def total_energy_by_date(session: Session_db, date_here: date):
    query = select(func.sum(Historique_metter_value.valeur)).where(cast(Historique_metter_value.created_at, Date) == date_here)
    results = session.exec(query).one()
    return results

def total_energy_by_year_month(session:Session_db, month:Optional[int], year:Optional[int]):
    query = select(func.sum(Historique_metter_value.valeur)).where(func.extract('year', Historique_metter_value.created_at) == year)
    if month is not None:
        query = query.where(func.extract('month', Historique_metter_value.created_at) == month)
    results = session.exec(query).one()
    return results
def get_energy_unit(session:Session_db):
    query = select(Transaction.energy_unit).distinct()
    result = session.exec(query).one()
    return result

def get_total_energy(session:Session_db):
    query = select(func.sum(Historique_metter_value.valeur))
    result = session.exec(query).one()
    return result