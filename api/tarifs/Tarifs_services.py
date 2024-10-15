# def upload_tarifs_from_csv(file: UploadFile):
from datetime import time, datetime
from sqlmodel import Session, select, text

from models.elecdis_model import Tariff


def get_one_tarif_from_trans_end(end_trans : datetime, session : Session ):
    time_end = end_trans.time()
    query = select(Tariff).where(Tariff.start_hour <= time_end,Tariff.end_hour >= time_end)
    return session.exec(query).first()