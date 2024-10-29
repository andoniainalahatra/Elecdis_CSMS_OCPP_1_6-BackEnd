from datetime import timedelta

from api.CP.CP_services import send_remoteStartTransaction
from api.Historique_session.Historique_session_models import historique_session_data
from models.elecdis_model import Historique_session, Session as Session_model
from sqlmodel import Session as Session_db, desc
from api.RFID.RFID_Services import *
# from api.transaction.Transaction_service import get_session_by_id


# formatage
def get_historique_session_data(historiqueSession : Historique_session, session_db : Session_db):
    tag = get_rdif_by_id(session=session_db,id=historiqueSession.idtag)
    return historique_session_data(
        id=historiqueSession.id,
        rfid=tag.rfid,
        user_name=tag.user_name,
        start_time=historiqueSession.start_time,
        end_time=historiqueSession.end_time,
        state="en cours" if historiqueSession.state==DEFAULT_STATE else "terminé"
    )
def get_lists_historique_datas(historique:List[Historique_session], session_db:Session_db):
    return [get_historique_session_data(ses,session_db) for ses in historique]
# ----------------------------
def get_last_historique_by_idtag(idtag:int, session_db:Session_db):
    historique = session_db.exec(select (Historique_session).where(Historique_session.idtag==idtag , Historique_session.state==HISTORIQUE_URGENCY).order_by(desc(Historique_session.start_time))).first()
    if historique is None:
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
    print(f" last session : {last_session}")
    if last_session.reason in ending:
        return True
    return False

def check_if_we_need_to_create_HS_or_not(last_history: Historique_session, session_db:Session_db):
    last_hs = last_history
    print(last_hs)
    if last_hs is None:
        return True
    if check_if_history_passed_expiration_date(last_hs):
        print("past expiration date")
        return True
    if check_if_last_session_in_history_ended_normaly(last_hs.id,session_db):
        print("ended normaly")
        return True
    return False

def get_history_for_a_session(id_tag:int, session_db:Session_db):
    last_history = get_last_historique_by_idtag(id_tag,session_db)
    if check_if_we_need_to_create_HS_or_not(last_history,session_db):
        print("need to recreate")
        hs = Historique_session(
            idtag=id_tag,
            expiry_date=datetime.now()+timedelta(hours=EXPIRATION_HOUR),
            start_time=datetime.now(),
            state=DEFAULT_STATE
        )
        session_db.add(hs)
        session_db.flush()
        return hs
    last_history.state=DEFAULT_STATE
    print("no need to recreate")
    session_db.add(last_history)
    session_db.flush()
    return last_history

def end_a_history_session(historique:Historique_session,end_time:datetime, session_db:Session_db):
    historique.end_time = end_time
    historique.state = DELETED_STATE
    session_db.add(historique)
    session_db.flush()
    return historique

def end_a_history_session_in_a_transaction(session_trans:Session_model, session_db:Session_db):
    historique = get_history_by_id(session_trans.id_historique_session, session_db)
    return end_a_history_session(historique,session_trans.end_time, session_db)

def get_all_history(session_db:Session_db, pagination:Pagination ):
    count_query= session_db.exec(select(func.count(Historique_session.id))).first()
    query = session_db.exec(select(Historique_session).order_by(Historique_session.id).offset(pagination.offset).limit(pagination.limit)).all()
    pagination.total_items=count_query
    return {"data":get_lists_historique_datas(query,session_db),"pagination":pagination.dict()}

def get_all_session_from_history(id_history:int, session_db:Session_db, pagination:Pagination):
    from api.transaction.Transaction_service import get_list_session_data_2
    query_count = session_db.exec(select(func.count(Session_model.id)).where(Session_model.id_historique_session==id_history)).first()
    query = session_db.exec(select(Session_model).where(Session_model.id_historique_session==id_history).order_by(Session_model.id).offset(pagination.offset).limit(pagination.limit)).all()
    pagination.total_items=query_count
    return {"data":get_list_session_data_2(query,session_db),"pagination":pagination.dict()}

def get_all_HS_by_user(id_user:int, session_db:Session_db, pagination:Pagination):
    query_count=len(session_db.exec(select(Historique_session)
                                .join(Session_model)
                                .where(Session_model.user_id == id_user)
                                .distinct() ).all())
    query = session_db.exec(
        select(Historique_session)
        .join(Session_model)
        .where(Session_model.user_id == id_user)
        .distinct(Historique_session.id)
        .limit(pagination.limit)
        .offset(pagination.offset)
    ).all()
    pagination.total_items=query_count
    return {"data":get_lists_historique_datas(query,session_db),"pagination":pagination.dict()}

async def reprendre_une_transaction(id_historique_session : int,id_tag:int,connector_id,charge_point_id, session_db:Session_db):
    historique = get_history_by_id(id_historique_session,session_db)
    if historique==None:
        raise ValueError("Historique session not found")
    historique.state = HISTORIQUE_URGENCY
    session_db.add(historique)
    session_db.flush()
    tag = get_rdif_by_id(session=session_db,id=id_tag)
    await send_remoteStartTransaction(charge_point_id,tag.rfid,connector_id)
    session_db.commit()
    return {"message":"transaction reprise"}
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
# sm = ses.exec(select(Session_model).where(Session_model.id == 174)).first()
# print(f" session : {sm}")
# print(end_a_history_session_in_a_transaction(sm,ses))
# ses.commit()