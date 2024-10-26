from datetime import timedelta

from api.Historique_session.Historique_session_models import historique_session_data
from models.elecdis_model import Historique_session, Session as Session_model
from sqlmodel import Session as Session_db, desc
from api.RFID.RFID_Services import *
def get_historique_session_data(historiqueSession : Historique_session, session_db : Session_db):
    tag = get_rdif_by_id(session=session_db,id=historiqueSession.idtag)
    return historique_session_data(
        id=historiqueSession.id,
        rfid=tag.rfid,
        user_name=tag.user_name,
        start_time=historiqueSession.start_time,
        end_time=historiqueSession.end_time
    )
def get_lists_historique_datas(historique:List[Historique_session], session_db:Session_db):
    return [get_historique_session_data(ses,session_db) for ses in historique]

def get_last_historique_by_idtag(idtag:int, session_db:Session_db):
    historique = session_db.exec(select (Historique_session).where(Historique_session.idtag==idtag).order_by(desc(Historique_session.start_time))).first()
    return historique

def check_if_history_passed_expiration_date(historique:Historique_session):
    return historique.expiry_date < datetime.now()

def get_history_by_id(id:int, session_db:Session_db):
    return session_db.exec(select(Historique_session).where(Historique_session.id==id)).first()
def get_last_session_in_history(id_history:int, session_db:Session_db):
    return session_db.exec(select(Session_model).where(Session_model.id_historique_session==id_history).order_by(desc(Session_model.start_time))).first()
def check_if_last_session_in_history_ended_normaly(id_history:int, session_db:Session_db):
    last_session = get_last_session_in_history(id_history,session_db)
    ending=["Local","Remote","EVDisconnected"]
    if last_session.reason in ending:
        return True
    return False




# *************** TESTS ***************

ses= next(get_session())
hs = Historique_session(
    id=1,
    expiry_date=datetime.now()+timedelta(hours=1),
    start_time=datetime.now(),
    end_time=datetime.now(),
    state=0,
    idtag=23
)
print(check_if_last_session_in_history_ended_normaly(hs.id,ses))