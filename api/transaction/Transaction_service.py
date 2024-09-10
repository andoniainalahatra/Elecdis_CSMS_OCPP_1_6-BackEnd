from datetime import datetime

from sqlmodel import Session as Session_db, select

from core.database import get_session
from models.elecdis_model import User, Session, Historique_metter_value
from api.transaction.Transaction_models import Session_create, Session_update
from api.RFID.RFID_Services import get_user_by_tag
from api.Connector.Connector_services import get_connector_by_id
from api.Connector.Connector_services import somme_metervalues,update_connector_valeur
from api.Connector.Connector_models import Connector_update
from api.CP.CP_services import update_cp,somme_metervalue_connector
from api.CP.CP_models import Cp_update
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
    session_model = Session(
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        connector_id=session_data.connector_id,
        user_id=user.id,
        metter_start=session_data.metter_start,
        metter_stop=session_data.metter_stop,
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
    session.flush()
    somme=somme_metervalues(session_model.connector_id,session)
    conne=Connector_update(valeur=somme,status=StatusEnum.available,time=datetime.now())
    logging.info(f"connector_id:{somme}+{session_model.connector_id}")
    update_connector_valeur(session_model.connector_id,conne,session,can_commit=False)
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
