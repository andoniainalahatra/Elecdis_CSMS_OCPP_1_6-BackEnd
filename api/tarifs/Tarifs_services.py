# def upload_tarifs_from_csv(file: UploadFile):
from datetime import time, datetime
from typing import Optional

from sqlmodel import Session, select, text,desc,func

from api.transaction.Transaction_models import MeterValueData
from core.database import get_session
from models.Pagination import Pagination
from models.elecdis_model import Tariff, TariffSnapshot, TariffGroup
from api.tarifs.Tarifs_models import Tariff_create, Tariff_update, TariffGroup_create, TariffGroup_update


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
    ts=None
    if last_ts is None:
        ts=create_new_tarif_snapshot(meterValuesDatas.transactionId,meterValuesDatas.dateMeter,meterValuesDatas.metervalue,session_db,None)
    else :
        current_tarif= get_one_tarif_from_trans_end(meterValuesDatas.dateMeter,session_db)
        tarif= get_tarif_by_id(last_ts.tariff_id,session_db)
        if tarif.id!=current_tarif.id:
            update_tarif_snapshot(last_ts,meterValuesDatas.metervalue,session_db)
            ts=create_new_tarif_snapshot(meterValuesDatas.transactionId,meterValuesDatas.dateMeter,meterValuesDatas.metervalue,session_db,None)

    return ts

def get_tariff_snapshot_by_session_id(session_id:int, session_db:Session):
    try:
        return session_db.exec(select(TariffSnapshot).where(TariffSnapshot.session_id==session_id)).all()
    except Exception as  e:
        raise e

def get_tarif_data(tarif:Tariff):
    return {
        "id": tarif.id,
        "start_hour": tarif.start_hour,
        "end_hour": tarif.end_hour,
        "price": tarif.price,
        "currency": tarif.currency,
        "description": tarif.description,
        "name": tarif.name,
        "facteur_majoration": tarif.multiplier,
        "energy_unit": tarif.energy_unit,
        "backgroundColor":tarif.backgroundColor,
        "textColor":tarif.textColor,
        "category": tarif.tariff_group.name
    }
def get_tarif_datas(tarifs):
    return [get_tarif_data(tarif) for tarif in tarifs]
def get_all_tariff(session :Session, page:int=1, number_items:int=50):
    try:
        pagination = Pagination(page=page, limit=number_items)
        pagination.total_items= session.exec(select(func.count(Tariff.id))).first()
        return {"data":get_tarif_datas(session.exec(select(Tariff).offset(pagination.offset).limit(pagination.limit)).all()),"pagination":pagination.dict()}
    except Exception as e:
        raise e

def get_tarif_group_by_id(id:int, session:Session):
    try:
        return session.exec(select(TariffGroup).where(TariffGroup.id==id)).first()
    except Exception as e:
        raise e

def create_tariff(create_data:Tariff_create, session):

    tariff_group=get_tarif_group_by_id(create_data.category, session)
    if tariff_group is None:
        raise Exception("Tariff group not found")
    try:
        tariff = Tariff(
            start_hour=create_data.start_hour,
            end_hour=create_data.end_hour,
            price=create_data.price,
            currency=create_data.currency,
            name = create_data.name_tarif,
            description = create_data.description,
            multiplier = create_data.facteur_majoration,
            energy_unit = create_data.energy_unit,
            tariff_group_id = tariff_group.id,
            backgroundColor = create_data.backgroundColor,
            textColor = create_data.textColor

        )
        print(f"====> {tariff}")
        session.add(tariff)
        session.flush()
        session.commit()
        session.close()
        return tariff
    except Exception as e:
        raise e

def update_tariff(id: int, create_data: Tariff_update, session: Session):
    try:
        # Retrieve the existing tariff by its ID
        existing_tariff = get_tarif_by_id(id, session)
        if existing_tariff==None:
            raise Exception("Tariff not found")

        # Update the tariff's attributes with the new data if they are not None
        if create_data.start_hour is not None:
            existing_tariff.start_hour = create_data.start_hour
        if create_data.end_hour is not None:
            existing_tariff.end_hour = create_data.end_hour
        if create_data.price is not None:
            existing_tariff.price = create_data.price
        if create_data.currency is not None:
            existing_tariff.currency = create_data.currency
        if create_data.name_tarif is not None:
            existing_tariff.name = create_data.name_tarif
        if create_data.description is not None:
            existing_tariff.description = create_data.description
        if create_data.backgroundColor is not None:
            existing_tariff.backgroundColor = create_data.backgroundColor
        if create_data.textColor is not None:
            existing_tariff.textColor = create_data.textColor
        if create_data.facteur_majoration is not None:
            existing_tariff.multiplier = create_data.facteur_majoration
        if create_data.energy_unit is not None:
            existing_tariff.energy_unit = create_data.energy_unit
        if create_data.category is not None:
            tarif = get_tarif_group_by_id(create_data.category, session)
            if tarif is None:
                raise Exception("Tariff group not found")
            existing_tariff.tariff_group_id = create_data.category

        # Save the changes to the database
        session.add(existing_tariff)
        session.flush()
        session.commit()
        session.close()
        return existing_tariff
    except Exception as e:
        raise e

def delete_tariff(id, session):
    session.delete(get_tarif_by_id(id, session))
    session.commit()
    session.close()
    return "ok"

def create_tariff_group(create_data: TariffGroup_create, session: Session):
    try:
        tariff_group = TariffGroup(
            name=create_data.name,
        )
        session.add(tariff_group)
        session.flush()
        session.commit()
        return tariff_group
    except Exception as e:
        raise e

def get_tariff_group_by_id(id: int, session: Session):
    try:
        return session.exec(select(TariffGroup).where(TariffGroup.id == id)).first()
    except Exception as e:
        raise e

def get_all_tariff_groups(session: Session, page: int = 1, number_items: int = 50):
    try:
        pagination = Pagination(page=page, limit=number_items)
        pagination.total_items = session.exec(select(func.count(TariffGroup.id))).first()
        return {
            "data": get_list_tarif_group_data(session.exec(select(TariffGroup).offset(pagination.offset).limit(pagination.limit)).all()),
            "pagination": pagination.dict()
        }
    except Exception as e:
        raise e
def get_tarif_group_data (tarif_group:TariffGroup):
    return {
        "id":tarif_group.id,
        "name":tarif_group.name,
    }
def get_list_tarif_group_data(tarif_groups):
    return [get_tarif_group_data(tarif_group) for tarif_group in tarif_groups]

def update_tariff_group(id: int, update_data: TariffGroup_update, session: Session):
    try:
        existing_tariff_group = get_tariff_group_by_id(id, session)
        if not existing_tariff_group:
            raise Exception("Tariff group not found")

        if update_data.name is not None:
            existing_tariff_group.name = update_data.name

        session.add(existing_tariff_group)
        session.flush()
        session.commit()
        return existing_tariff_group
    except Exception as e:
        raise e

def delete_tariff_group(id: int, session: Session):
    try:
        tariff_group = get_tariff_group_by_id(id, session)
        if not tariff_group:
            raise Exception("Tariff group not found")

        session.delete(tariff_group)
        session.commit()
        return "ok"
    except Exception as e:
        raise e