from datetime import datetime
from typing import List

from sqlmodel import Session as Session_db, select,func

from core.database import get_session
from models.Pagination import Pagination
from models.elecdis_model import User, Session as SessionModel, Historique_metter_value, Transaction
from api.transaction.Transaction_models import Session_create, Session_update, Session_list_model
from api.RFID.RFID_Services import get_user_by_tag
from api.Connector.Connector_services import get_connector_by_id
from api.Connector.Connector_services import somme_metervalues,update_connector_valeur
from api.Connector.Connector_models import Connector_update
from api.CP.CP_services import update_cp,somme_metervalue_connector
from api.CP.CP_models import Cp_update
from api.tarifs.Tarifs_services import *
from models.elecdis_model import StatusEnum
import logging

logging.basicConfig(level=logging.INFO)


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
    session_model = SessionModel(
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
    session_model: SessionModel = session.exec(select(SessionModel).where(SessionModel.id == session_data.transaction_id)).first()
    if session_model is None:
        raise {"message": f"Session with id {session_data.transaction_id} not found."}
    session_model.end_time = session_data.end_time
    session_model.metter_stop = session_data.metter_stop
    session_model.updated_at=datetime.now()
    session.add(session_model)
    session.flush()
    # save historic mettervalue
    create_mettervalue_history(session=session, session_data=session_model, can_commit=False)
    session.flush()
    somme=somme_metervalues(session_model.connector_id,session)
    conne=Connector_update(valeur=somme,status=StatusEnum.available,time=datetime.now())
    logging.info(f"connector_id:{somme}+{session_model.connector_id}")
    update_connector_valeur(session_model.connector_id,conne,session,can_commit=False)
    # add transactions with its price
    create_transaction_by_session(sessionModel=session_model, session_db=session, can_commit=False)
    session.commit()
    session.refresh(session_model)
    return session_model


def create_mettervalue_history(session:Session_db, session_data:SessionModel, can_commit:bool=True):
    history : Historique_metter_value = Historique_metter_value(
        real_connector_id=session_data.connector_id,
        valeur=session_data.metter_stop-session_data.metter_start,
        )
    session.add(history)
    if can_commit:
        session.commit()


def get_current_sessions(session:Session_db, pagination:Pagination):
    pagination.total_items=count_current_session(session)
    sessions = session.exec( select(SessionModel).
        where(SessionModel.end_time == None).
        order_by(SessionModel.id).
        offset(pagination.offset).
        limit(pagination.limit)).all()
    return {"data":get_list_session_data(sessions), "pagination":pagination.dict()}

def get_session_by_id(session:Session_db, id:int):
    session_model: SessionModel = session.exec(select(SessionModel).where(SessionModel.id == id)).first()
    return session_model

def count_current_session(session:Session_db):
    count = session.exec(select(func.count(SessionModel.id)).where(SessionModel.end_time == None)).one()
    return count

def total_session_de_charges(session:Session_db):
    total = session.exec(select(func.count(SessionModel.id))).one()
    return total

def get_all_session(session:Session_db, pagination:Pagination):
    pagination.total_items=total_session_de_charges(session)
    pagination.total_items = session.exec(select(func.count(SessionModel.id))).one()
    sessions= session.exec(
        select(SessionModel).
        order_by(SessionModel.id).
        offset(pagination.offset).
        limit(pagination.limit)).all()
    return {"data":get_list_session_data(sessions),"pagination":pagination.dict()}

def get_session_data(session:SessionModel):
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
        ,
        charge_point_id=session.connector.charge_point_id
    )
    return data

def get_list_session_data (sessions:List[SessionModel]):
    return [get_session_data(session) for session in sessions]

def create_transaction_by_session(sessionModel:SessionModel, session_db:Session_db, can_commit:bool=True):
    tarif = get_one_tarif_from_trans_end(sessionModel.end_time, session_db)
    if tarif is None:
        raise Exception (f"message : No tarif found for session id {sessionModel.id}")
    consumed_energy = sessionModel.metter_stop - sessionModel.metter_start
    # need to be changed if the unit in the tariff is not the same as the unit in the session
    total_price = consumed_energy * tarif.price
    transaction = Transaction(
        session_id=sessionModel.id,
        currency=tarif.currency,
        unit_price=tarif.price,
        total_price=total_price,
        consumed_energy=consumed_energy,
        # this one also need to be changed based on what we get from the ocpp messages okay ?
        unit=tarif.unit
    )
    session_db.add(transaction)
    if can_commit:
        session_db.commit()
    return transaction,sessionModel