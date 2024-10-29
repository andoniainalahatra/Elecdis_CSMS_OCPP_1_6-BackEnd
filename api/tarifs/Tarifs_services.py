# def upload_tarifs_from_csv(file: UploadFile):
from datetime import time, datetime
from typing import Optional

from sqlmodel import Session, select, text,desc

from api.transaction.Transaction_models import MeterValueData
from core.database import get_session
from models.elecdis_model import Tariff, TariffSnapshot


def get_one_tarif_from_trans_end(end_trans : datetime, session : Session ):
    time_end = end_trans.time()
    query = select(Tariff).where(Tariff.start_hour <= time_end,Tariff.end_hour >= time_end)
    return session.exec(query).first()

def create_new_tarif_snapshot(session_id:int, date_start:datetime, meter_start:float, session:Session, tarif:Optional[Tariff]=None):
    try:
        if tarif==None:
            tarif = get_one_tarif_from_trans_end(date_start,session)
            print(f"{tarif}")
        tarifStapshot = TariffSnapshot(tariff_id = tarif.id, effective_date=date_start, session_id=session_id, meter_start=meter_start)
        session.add(tarifStapshot)
        session.flush()
        return tarifStapshot
    except Exception as e:
        raise e


def compare_tarifs(tarif1:Tariff, tarif2:Tariff):
    if tarif1 is None or tarif2 is None:
        return False
    return tarif1.id==tarif2.id

def update_tarif_snapshot(tarifSnapshot:TariffSnapshot, meterStop:float, session:Session):
    tarifSnapshot.meter_stop=meterStop
    session.add(tarifSnapshot)
    session.flush()
    return tarifSnapshot
def get_tarif_by_id(id_tarif:int,session:Session):
    try:
        return session.exec(select(Tariff).where(Tariff.id==id_tarif)).first()
    except:
        raise Exception("get_tarif_by_id problem")
def get_last_tarifSnapshot_by_session(session_id:int, session_db:Session):
    try:
        ts = session_db.exec(select(TariffSnapshot).where(TariffSnapshot.session_id==session_id).order_by(desc(TariffSnapshot.created_at))).first()
        return ts
    except:
        raise Exception ("get_last_tarifSnapshot_by_session problem")

def manage_tarif_snapshots_on_meter_values(meterValuesDatas:MeterValueData,session_db:Session,loggin):
    last_ts= get_last_tarifSnapshot_by_session(meterValuesDatas.transactionId,session_db)
    loggin.info(f"last_ts => {last_ts}")
    ts=None
    if last_ts is None:
        loggin.info("last_ts is None")
        ts=create_new_tarif_snapshot(meterValuesDatas.transactionId,meterValuesDatas.dateMeter,meterValuesDatas.metervalue,session_db,None)
    else :
        current_tarif= get_one_tarif_from_trans_end(meterValuesDatas.dateMeter,session_db)
        loggin.info(f"current_tarif => {current_tarif}")
        tarif= get_tarif_by_id(last_ts.tariff_id,session_db)
        loggin.info(f"tarif => {tarif}")
        if tarif.id!=current_tarif.id:
            loggin.info("tarif.id!=current_tarif.id")
            ts=update_tarif_snapshot(last_ts,meterValuesDatas.metervalue,session_db)
            ts=create_new_tarif_snapshot(meterValuesDatas.transactionId,meterValuesDatas.dateMeter,meterValuesDatas.metervalue,session_db,None)

    return ts

def get_tariff_snapshot_by_session_id(session_id:int, session_db:Session):
    try:
        return session_db.exec(select(TariffSnapshot).where(TariffSnapshot.session_id==session_id)).all()
    except Exception as  e:
        raise e

