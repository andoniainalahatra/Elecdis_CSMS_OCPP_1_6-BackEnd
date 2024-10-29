from datetime import datetime, date
from typing import List

from sqlmodel import Session as Session_db, select,func,case

from api.Historique_session.Historique_session_services import get_history_for_a_session, \
    end_a_history_session_in_a_transaction
from api.userCredit.UserCredit_services import debit_credit_to_user_account_after_session, check_if_sold_out
from api.users.UserServices import get_user_by_id, get_user_by_id_trans
from core.database import get_session
from core.utils import UNIT_KWH, UNIT_WH
from models.Pagination import Pagination, Data_display
from models.elecdis_model import User, Session as SessionModel, Historique_metter_value, Transaction, Historique_session
from api.transaction.Transaction_models import Session_create, Session_update, Session_list_model, Transaction_details, \
    Session_data_affichage, MeterValueData
from api.RFID.RFID_Services import get_user_by_tag, get_by_tag
from api.Connector.Connector_services import get_connector_by_id
from api.Connector.Connector_services import somme_metervalues,update_connector_valeur
from api.Connector.Connector_models import Connector_update
from api.CP.CP_services import update_cp, somme_metervalue_connector, send_remoteStopTransaction
from api.CP.CP_models import Cp_update
from api.tarifs.Tarifs_services import *
from models.elecdis_model import StatusEnum
import logging

from ocpp_scenario.RemoteStopTransaction import RemoteStopTransaction

logging.basicConfig(level=logging.INFO)


def create_session_service(session: Session_db, session_data: Session_create):
    # get user BY TAG
    user = get_user_by_tag(tag=session_data.user_tag, session=session)
    if user is None:
        raise {"message": f"User with tag {session_data.user_tag} not found."}
    #  get tag
    tag = get_by_tag(session,session_data.user_tag)
    # check connector
    connector = get_connector_by_id(id_connector=session_data.connector_id, session=session)
    if connector is None:
        raise {"message": f"Connector with id {session_data.connector_id} not found."}

    # get historique session
    hs = get_history_for_a_session(tag.id,session)
    # create session
    print(f"user id {user.id}")
    print(f"tag id {hs.id}")
    session_model = SessionModel(
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        connector_id=session_data.connector_id,
        user_id=user.id,
        metter_start=session_data.metter_start,
        metter_stop=session_data.metter_stop,
        tag=session_data.user_tag,
        id_historique_session=hs.id
    )

    session.add(session_model)
    session.flush()
    ts=create_new_tarif_snapshot(session_model.id,session_model.start_time,session_model.metter_start/1000,session,None)

    session.commit()
    session.refresh(session_model)
    return session_model


def update_session_service_on_stopTransaction(session: Session_db, session_data: Session_update):
    session_model: SessionModel = session.exec(select(SessionModel).where(SessionModel.id == session_data.transaction_id)).first()
    if session_model is None:
        raise {"message": f"Session with id {session_data.transaction_id} not found."}
    session_model.end_time = session_data.end_time
    session_model.metter_stop = session_data.metter_stop
    if session_model.reason==None:
        session_model.reason = session_data.reason
    session_model.updated_at=datetime.now()
    session.add(session_model)
    session.flush()

    # save historic mettervalue
    create_mettervalue_history(session=session, session_data=session_model, can_commit=False)
    session.flush()
    somme=somme_metervalues(session_model.connector_id,session)
    conne=Connector_update(valeur=somme,status=StatusEnum.available,time=datetime.now())
    update_connector_valeur(session_model.connector_id,conne,session,can_commit=False)

    # update the last tariff snapshot
    last_ts = get_last_tarifSnapshot_by_session(session_model.id, session)
    met_stop= session_model.metter_stop/1000
    update_tarif_snapshot(last_ts, met_stop, session)
    # add transactions with its price

    create_and_save_detail_transaction_by_tarif_snapshot(session_model.id, session_db=session)
    # create_transaction_by_session(sessionModel=session_model, session_db=session, can_commit=False)
    tag=get_by_tag(session,session_model.tag)
    # debiter le compte user pour la consommation
    debit_credit_to_user_account_after_session(session, tag.id, session_model.id)

    # terminer la HS :
    end_a_history_session_in_a_transaction(session_model,session)
    session.commit()
    session.refresh(session_model)
    return session_model


def create_mettervalue_history(session:Session_db, session_data:SessionModel, can_commit:bool=True):
    history : Historique_metter_value = Historique_metter_value(
        real_connector_id=session_data.connector_id,
        valeur=(session_data.metter_stop-session_data.metter_start)/1000,
        )
    session.add(history)
    if can_commit:
        session.commit()


def get_current_sessions(session:Session_db, pagination:Pagination):
    pagination.total_items=count_current_session(session)
    sessions = session.exec( select(SessionModel).
        where(SessionModel.end_time == None).
        where(SessionModel.id!=-1).
        order_by(SessionModel.id).
        offset(pagination.offset).
        limit(pagination.limit)).all()
    return {"data":get_list_session_data_2(sessions=sessions,session_db=session), "pagination":pagination.dict()}
def get_done_sessions(session:Session_db, pagination:Pagination):
    pagination.total_items=count_done_sessions(session)
    sessions = session.exec( select(SessionModel).
        where(SessionModel.end_time != None).
        where(SessionModel.id!=-1).
        order_by(SessionModel.id).
        offset(pagination.offset).
        limit(pagination.limit)).all()
    return {"data":get_list_session_data_2(sessions=sessions,session_db=session), "pagination":pagination.dict()}

def get_session_by_id(session:Session_db, id:int):
    session_model: SessionModel = session.exec(select(SessionModel).where(SessionModel.id == id)).first()
    return session_model

def count_current_session(session:Session_db):
    count = session.exec(select(func.count(SessionModel.id)).where(SessionModel.end_time == None).where(SessionModel.id!=-1)).one()
    return count

def count_done_sessions(session : Session_db):
    count = session.exec(select(func.count(SessionModel.id)).where(SessionModel.end_time != None).where(SessionModel.id!=-1)).one()
    return count

def total_session_de_charges(session:Session_db):
    total = session.exec(select(func.count(SessionModel.id)).where(SessionModel.id!=-1)).one()
    return total

def get_all_session(session:Session_db, pagination:Pagination):
    pagination.total_items=total_session_de_charges(session)
    pagination.total_items = session.exec(select(func.count(SessionModel.id)).where(SessionModel.id!=-1)).one()
    sessions= session.exec(
        select(SessionModel).
        where(SessionModel.id!=-1).
        order_by(SessionModel.id).
        offset(pagination.offset).
        limit(pagination.limit)).all()
    return {"data":get_list_session_data_2(sessions, session_db=session),"pagination":pagination.dict()}

def get_session_data(session:SessionModel):
    data=Session_list_model(
        id=session.id,
        start_time=session.start_time,
        end_time=session.end_time,
        connector_id=session.connector_id,
        user_id=session.user_id,
        user_name=session.user.first_name + " "+session.user.last_name,
        consumed_energy=session.metter_stop-session.metter_start,
        rfid=session.tag,
        charge_point_id=session.connector.charge_point_id
    )
    return data

def get_list_session_data (sessions:List[SessionModel]):
    return [get_session_data(session) for session in sessions]

def get_status_session(session:Session_db, session_id:int):
    query = select(
        case(
            (SessionModel.end_time.is_(None), 'en cours'),
            else_='terminé'
        ).label("end_time_status")
    ).where(SessionModel.id == session_id)

    results = session.exec(query).first()
    return results

def get_session_data_2(session:SessionModel, session_db:Session_db):

    transaction_datas = get_sums_transactions(session_db, session.id)
    # user=get_user_by_tag(session_db,session.tag)
    user=get_user_by_id_trans(session.user_id,session_db)
    status=get_status_session(session_db,session.id)
    # print(session)
    # print(f'==> {user}')

    if session is not None and user is not None:
        data=Session_data_affichage(
            id=session.id,
            start_time=session.start_time,
            end_time=session.end_time,
            connector_id=session.connector_id,
            user_id=session.user_id,
            user_name=user.first_name + " "+user.last_name,
            consumed_energy=f'{transaction_datas.consumed_energy} {transaction_datas.energy_unit}',
            rfid=session.tag,
            charge_point_id=session.connector.charge_point_id,
            total_cost=f'{transaction_datas.total_price} {transaction_datas.currency}',
            statuts=status
        )
    else :
        data = Session_data_affichage()
    return data

def get_list_session_data_2 (sessions:List[SessionModel], session_db:Session_db):
    return [get_session_data_2(session,session_db) for session in sessions]

def get_sums_transactions(session:Session_db, session_id:int):
    sum = session.exec(
        select(
            func.sum(Transaction.total_price),
            Transaction.currency,
            Transaction.energy_unit,
            func.sum(Transaction.consumed_energy)
        ).where(
            Transaction.session_id == session_id
        ).group_by(
            Transaction.currency,
            Transaction.energy_unit
        )
    ).first()
    if sum is None:
        result_dict = Transaction_details(
            total_price=0,
            currency="",
            energy_unit="",
            consumed_energy=0
        )
    else :
        result_dict = Transaction_details(
            total_price= sum[0],
            currency=sum[1],
            energy_unit= sum[2],
            consumed_energy=sum[3]
        )

    return result_dict
def create_transaction_by_session(sessionModel:SessionModel, session_db:Session_db, can_commit:bool=True):
    tarif = get_one_tarif_from_trans_end(sessionModel.end_time, session_db)
    if tarif is None:
        raise Exception (f"message : No tarif found for session id {sessionModel.id}")
    consumed_energy = (sessionModel.metter_stop - sessionModel.metter_start)/1000
    # need to be changed if the unit in the tariff is not the same as the unit in the session
    total_price = consumed_energy * tarif.price
    transaction = Transaction(
        session_id=sessionModel.id,
        currency=tarif.currency,
        unit_price=tarif.price,
        total_price=total_price,
        consumed_energy=consumed_energy,
        # this one also need to be changed based on what we get from the ocpp messages okay ?
        energy_unit=tarif.energy_unit
    )
    session_db.add(transaction)
    if can_commit:
        session_db.commit()
    return transaction,sessionModel

def create_default_transaction(session:Session_db):
    session_default = session.exec(select (SessionModel).where(SessionModel.id==-1)).first()
    if(session_default is None):
        session_default = SessionModel(
            id=-1,
            start_time=datetime.now(),
            end_time=datetime.now(),
            metter_start=0,
            metter_stop=0,
            tag="default"
        )
        session.add(session_default)
        session.commit()

def get_transactions_details_by_session(session_db:Session_db, session_id:int, page:int, number_items:int):
    paginations = Pagination(page=page, limit=number_items)
    count = session_db.exec(select(func.count(Transaction.id)).where(Transaction.session_id == session_id).where(SessionModel.id!=-1)).one()
    transactions = session_db.exec(select(Transaction).where(Transaction.session_id == session_id).where(SessionModel.id!=-1).offset(paginations.offset).limit(paginations.limit)).all()
    paginations.total_items = count
    datas=Data_display(data=transactions, pagination=paginations)
    return datas

def get_transactions_by_user_id(user_id:int, session:Session_db, page:int, number_items:int):
    paginations = Pagination(page=page, limit=number_items)
    count = session.exec(select(func.count(SessionModel.id)).where(SessionModel.user_id == user_id)).one()
    transactions = session.exec(select(SessionModel).where(SessionModel.user_id == user_id).offset(paginations.offset).limit(paginations.limit)).all()
    paginations.total_items = count
    datas=Data_display(data=get_list_session_data_2(transactions,session_db=session), pagination=paginations)
    return datas

def get_transactions_by_user_tags(user_tag:str, session:Session_db, page:int, number_items:int):
    paginations = Pagination(page=page, limit=number_items)
    print("hoho")

    count = session.exec(select(func.count(SessionModel.id)).where(SessionModel.tag == user_tag)).one()
    print(session.exec(select(SessionModel).where(SessionModel.tag == user_tag)))
    print("hehe")
    transactions = session.exec(select(SessionModel).where(SessionModel.tag == user_tag).offset(paginations.offset).limit(paginations.limit)).all()
    paginations.total_items = count
    datas=Data_display(data=get_list_session_data_2(transactions,session_db=session), pagination=paginations)
    return datas

def moyenne_session_duration(session: Session):
    query = select(
        func.to_char(
            text("interval '1 second'") * func.avg(func.extract('epoch', SessionModel.end_time - SessionModel.start_time)),
            'HH24 h MI mn SS s'
        ).label('avg'),
        func.to_char(
            text("interval '1 second'") * func.min(func.extract('epoch', SessionModel.end_time - SessionModel.start_time)),
            'HH24 h MI mn SS s'
        ).label('min'),
        func.to_char(
            text("interval '1 second'") * func.max(func.extract('epoch', SessionModel.end_time - SessionModel.start_time)),
            'HH24 h MI mn SS s'
        ).label('max')
    ).where(
        SessionModel.id != -1,
        SessionModel.end_time.isnot(None)
    )
    result = session.exec(query).one()
    result_dict = {
        "avg": result.avg,
        "min": result.min,
        "max": result.max
    }
    return result_dict

def get_heures_de_pointes(session: Session):
    query = select(
        func.to_char(
            func.date_trunc('hour', SessionModel.start_time),
            'HH24:MI:SS'
        ).label('hour')
    ).group_by(
        func.to_char(func.date_trunc('hour', SessionModel.start_time), 'HH24:MI:SS')
    ).order_by(
        func.count().desc()
    ).where(
        SessionModel.id != -1
    )
    result = session.exec(query).first()
    print("==>",result)
    return result

def get_session_data_chart(session :Session_db, date_here:date):
    query = text(f"""
    select hour , max(user_count) as event_count, max(user_count) as user_count from (
    (select
         TO_CHAR(DATE_TRUNC('hour', start_time),'HH24:MI:SS') AS hour,
         COUNT(*) AS event_count,
         COUNT(DISTINCT user_id) as user_count
     from session
     where session.id != -1
     and session.start_time:: date= '{date_here}' :: date
     group by hour
     order by hour)
    union 
    (select
         TO_CHAR(generate_series::time, 'HH24:MI:SS') AS hour,
         0 AS event_count,
         0 as user_count
     from generate_series(
         '2023-01-01 00:00:00'::timestamp,
         '2023-01-01 23:00:00'::timestamp,
         '1 hour'::interval
     ))
    order by hour ) as t group by hour;
    """)

    with session:
        result = session.exec(query).all()
    result_dicts=[]
    for i in result:
        temp = { "label":i.hour,
        "nombreSession":i.event_count,
        "uniqueUsers":i.user_count
        }
        result_dicts.append(temp)
    return result_dicts

def search_transactions_by_date(session:Session_db, date_start:date, date_end:date, montant_fin, montant_debut, energy_fin, energy_debut,page, number_items):
    query = select(SessionModel).where(SessionModel.id != -1)
    query_count = select(func.count(SessionModel.id))

    # Handle montant filters
    if montant_debut is not None and montant_fin is not None:
        # Modify the query to include grouping and handle aggregates properly
        query = (
            query
            .join(Transaction, Transaction.session_id == SessionModel.id)
            .group_by(SessionModel.id, SessionModel.created_at, SessionModel.updated_at)
            .having(func.sum(Transaction.total_price) >= montant_debut, func.sum(Transaction.total_price) <= montant_fin)
        )

        # Subquery to count the sessions based on the total price range
        total_price_subquery = (
            select(
                SessionModel.id,
                func.sum(Transaction.total_price).label("total_price")
            )
            .join(Transaction, Transaction.session_id == SessionModel.id)
            .group_by(SessionModel.id)
            .subquery()
        )
        query_count = (
            select(func.count())
            .select_from(total_price_subquery)
            .where(total_price_subquery.c.total_price.between(montant_debut, montant_fin))
        )

    # Handle date filters
    if date_start is not None and date_end is not None:
        query = query.where(func.date(SessionModel.start_time).between(date_start, date_end))
        query_count = query_count.where(func.date(SessionModel.start_time).between(date_start, date_end))

    # Handle energy filters
    if energy_debut is not None and energy_fin is not None:
        query = query.where((SessionModel.metter_stop - SessionModel.metter_start) / 1000 >= energy_debut,
                            (SessionModel.metter_stop - SessionModel.metter_start) / 1000 <= energy_fin)
        query_count = query_count.where(SessionModel.metter_start >= energy_debut,
                                        SessionModel.metter_stop <= energy_fin)

    # Final query adjustments
    query_count = query_count.where(SessionModel.id != -1)

    # Pagination logic
    pagination = Pagination(page=page, limit=number_items)
    print(query_count)
    count = session.exec(query_count).one()
    print("hehe",count)
    pagination.total_items = count
    transactions = session.exec(query.offset(pagination.offset).limit(pagination.limit)).all()

    return {"data": get_list_session_data_2(transactions, session_db=session), "pagination": pagination.dict()}
def search_transactions_by_date2(session:Session_db, date_start:date, date_end:date, montant_fin, montant_debut, energy_fin, energy_debut,page, number_items):
    query = select(SessionModel).where(SessionModel.id != -1)
    query_count = select(func.count(SessionModel.id))

    # Handle montant filters
    if montant_debut is not None and montant_fin is not None:
        query = (
            query
            .join(Transaction, Transaction.session_id == SessionModel.id)
            .group_by(SessionModel.id, SessionModel.created_at, SessionModel.updated_at)
            .having(func.sum(Transaction.total_price) >= montant_debut, func.sum(Transaction.total_price) <= montant_fin)
        )

        # Adjust count query to count grouped rows properly
        query_count = (
            select(func.count(SessionModel.id))
            .join(Transaction, Transaction.session_id == SessionModel.id)
            .group_by(SessionModel.id, SessionModel.created_at, SessionModel.updated_at)
            .having(func.sum(Transaction.total_price) >= montant_debut, func.sum(Transaction.total_price) <= montant_fin)
        )

    # Handle date filters
    if date_start is not None and date_end is not None:
        query = query.where(func.date(SessionModel.start_time).between(date_start, date_end))
        query_count = query_count.where(func.date(SessionModel.start_time).between(date_start, date_end))

    # Handle energy filters
    if energy_debut is not None and energy_fin is not None:
        query = query.where((SessionModel.metter_stop - SessionModel.metter_start) / 1000 >= energy_debut,
                            (SessionModel.metter_stop - SessionModel.metter_start) / 1000 <= energy_fin)
        query_count = query_count.where(SessionModel.metter_start >= energy_debut,
                                        SessionModel.metter_stop <= energy_fin)

    # Final query adjustments
    query_count = query_count.where(SessionModel.id != -1)

    # Pagination logic
    pagination = Pagination(page=page, limit=number_items)

    # Use `.scalar()` to fetch the count
    count = len(session.exec(query).all())
    pagination.total_items = count if count is not None else 0

    # Fetch the transactions with pagination
    transactions = session.exec(query.offset(pagination.offset).limit(pagination.limit)).all()

    return {"data": get_list_session_data_2(transactions, session_db=session), "pagination": pagination.dict()}

def create_and_save_detail_transaction_by_tarif_snapshot(session_id:int, session_db:Session):
    list_ts= get_tariff_snapshot_by_session_id(session_id, session_db)
    transactions=[]
    for ts in list_ts:
        trans=Transaction(
            session_id=session_id,
            currency=ts.tariff.currency,
            unit_price=ts.tariff.price,
            total_price=(ts.meter_stop-ts.meter_start)*ts.tariff.price,
            consumed_energy=(ts.meter_stop-ts.meter_start),
            energy_unit=ts.tariff.energy_unit
        )
        trans.consumed_energy_added=trans.consumed_energy*ts.tariff.multiplier
        transactions.append(trans)
    session_db.add_all(transactions)
    return transactions

async def stop_transactions_on_sold_out(session: Session_db, idtag: int, session_id: int, metervalue: float, charge_point_id):
    list_sn = get_tariff_snapshot_by_session_id(session_id, session)
    total_energy=0
    for ts in list_sn:
        if ts.meter_stop is None:
            ts.meter_stop = metervalue
        total_energy+=(ts.meter_stop-ts.meter_start)*ts.tariff.multiplier
        print(check_if_sold_out(session, idtag, total_energy))
    if check_if_sold_out(session, idtag, total_energy):
        session_model = get_session_by_id(session, session_id)
        session_model.reason = "Credit de recharge insuffisante"
        await send_remoteStopTransaction(charge_point_id,session_id)


def create_metervalue_from_mvdata(mvdata:[],connectorId,transactionId, dateMeter:datetime):
    mv= MeterValueData(connectorId=connectorId,transactionId=transactionId,dateMeter=dateMeter)
    for i in mvdata:
        if i.get('measurand') == "Energy.Active.Import.Register":
            if i.get('unit') == "Wh":
                mv.metervalue=float(i.get('value'))/1000
                mv.meterunit=UNIT_KWH
            else:
                mv.metervalue=float(i.get('value'))
                mv.meterunit=get_unit(i.get('unit'))
    return mv

def get_unit(unit):
    if unit =="kwh" or unit=="KWh" or unit=="kWh" or unit=="KWH":
        return UNIT_KWH
    if unit =="Wh" or unit=="wh" or unit=="WH" or unit=="Wh":
        return UNIT_WH

