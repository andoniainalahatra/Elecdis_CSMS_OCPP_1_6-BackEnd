# def upload_tarifs_from_csv(file: UploadFile):
from datetime import time, datetime
from typing import Optional

from sqlmodel import Session, select, text

from models.elecdis_model import Tariff, TariffSnapshot


def get_one_tarif_from_trans_end(end_trans : datetime, session : Session ):
    time_end = end_trans.time()
    query = select(Tariff).where(Tariff.start_hour <= time_end,Tariff.end_hour >= time_end)
    return session.exec(query).first()

def create_new_tarif_snapshot(session_id:int, date_start:datetime, meter_start:float, session:Session, tarif:Optional[Tariff]=None):
    try:
        if tarif==None:
            tarif = get_one_tarif_from_trans_end(date_start,session)
        tarifStapshot = TariffSnapshot(tariff_if = tarif.id, effective_date=date_start, session_id=session_id, meter_start=meter_start)
        session.add(tarifStapshot)
    except:
        raise Exception("something about creaing tarifsnapshot went wrong")


def compare_tarifs(tarif1:Tariff, tarif2:Tariff):
    return tarif1.id==tarif2.id

def update_tarif_snapshot(tarifSnapshot:TariffSnapshot, meterStop:float, session:Session):
    tarifSnapshot.meter_stop=meterStop
    session.add(tarifSnapshot)

def get_last_tarifSnapshot_by_session(session_id:int, session_db:Session):
    try:
        ts= session_db.exec(select(TariffSnapshot).where(TariffSnapshot.meter_stop==None,TariffSnapshot.session_id==session_id))
        return ts
    except:
        raise Exception ("get_last_tarifSnapshot_by_session problem")

