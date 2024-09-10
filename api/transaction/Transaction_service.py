from datetime import datetime
from typing import List

from sqlmodel import Session as Session_db, select,func

from core.database import get_session
from models.Pagination import Pagination
from models.elecdis_model import User, Session, Historique_metter_value
from api.transaction.Transaction_models import Session_create, Session_update, Session_list_model
from api.RFID.RFID_Services import get_user_by_tag
from api.Connector.Connector_services import get_connector_by_id


def create_session_service(session: Session_db, session_data: Session_create):
    # get user BY TAG
    user = get_user_by_tag(tag=session_data.user_tag, session=session)
    if user is None:
        raise {"message": f"User with tag {session_data.user_tag} not found."}
    # check connector
    connector = get_connector_by_id(id_connector=session_data.connector_id, session=session)
    if connector is None:
        raise {"message": f"Connector with id {session_data.connector_id} not found."}
    # create session
    session_model = Session(
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        connector_id=session_data.connector_id,
        user_id=user.id,
        metter_start=session_data.metter_start,
        metter_stop=session_data.metter_stop,
        tag=session_data.user_tag
    )
    session.add(session_model)
    session.commit()
    session.refresh(session_model)
    return session_model


def update_session_service_on_stopTransaction(session: Session_db, session_data: Session_update):
    session_model: Session = session.exec(select(Session).where(Session.id == session_data.transaction_id)).first()
    if session_model is None:
        raise {"message": f"Session with id {session_data.transaction_id} not found."}
    session_model.end_time = session_data.end_time
    session_model.metter_stop = session_data.metter_stop
    session_model.updated_at=datetime.now()
    session.add(session_model)
    session.flush()
    # save historic mettervalue
    create_mettervalue_history(session=session, session_data=session_model, can_commit=False)
    session.commit()
    session.refresh(session_model)
    return session_model


def create_mettervalue_history(session:Session_db, session_data:Session, can_commit:bool=True):
    history : Historique_metter_value = Historique_metter_value(
        real_connector_id=session_data.connector_id,
        valeur=session_data.metter_stop-session_data.metter_start,
        )
    session.add(history)
    if can_commit:
        session.commit()


def get_current_sessions(session:Session_db, pagination:Pagination):
    sessions: List[Session] = session.exec(
        select(Session).
        where(Session.end_time == None).
        order_by(Session.id).
        offset(pagination.offset).
        limit(pagination.limit)).all()
    return get_list_session_data(sessions)

def get_session_by_id(session:Session_db, id:int):
    session_model: Session = session.exec(select(Session).where(Session.id == id)).first()
    return session_model

def count_current_session(session:Session_db):
    count = session.exec(select(func.count(Session.id)).where(Session.end_time == None)).one()
    return count

def total_session_de_charges(session:Session_db):
    total = session.exec(select(func.count(Session.id))).one()
    return total

def get_all_session(session:Session_db, pagination:Pagination):
    sessions: List[Session] = session.exec(
        select(Session).
        order_by(Session.id).
        offset(pagination.offset).
        limit(pagination.limit)).all()
    return get_list_session_data(sessions)

def get_session_data(session:Session):
    data=Session_list_model(
        id=session.id,
        start_time=session.start_time,
        end_time=session.end_time,
        connector_id=session.connector_id,
        user_id=session.user_id,
        user_name=session.user.first_name + " "+session.user.last_name,
        metter_start=session.metter_start,
        metter_stop=session.metter_stop,
        tag=session.tag
    )
    return data

def get_list_session_data (sessions:List[Session]):
    return [get_session_data(session) for session in sessions]