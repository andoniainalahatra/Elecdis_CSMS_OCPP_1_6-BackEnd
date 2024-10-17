from api.CP.CP_models import Cp_create,Cp_update,Cp_form
from models.elecdis_model import ChargePoint,StatusEnum,Connector,Historique_metter_value
from sqlmodel import Session, select,func,extract,case
from models.Pagination import Pagination
from fastapi import UploadFile
from core.utils import *
from sqlalchemy import or_
from datetime import date, datetime,timedelta
import aio_pika
from aio_pika import ExchangeType, Message as AioPikaMessage,IncomingMessage
import json
from core.config import *
from ocpp_scenario.RemoteStopTransaction import RemoteStopTransaction
from ocpp_scenario.RemoteStartTransaction import RemoteStartTransaction
from ocpp_scenario.GetDiagnostic import GetDiagnostic



import logging
from fastapi import HTTPException
logging.basicConfig(level=logging.INFO)

DELETED_STATE=DELETED_STATE
ACTIVE_STATE=DEFAULT_STATE

def create_cp(cp: Cp_create, session : Session):
    try:
        
        charge : ChargePoint = ChargePoint(id=cp.id,serial_number=cp.serial_number, charge_point_model=cp.charge_point_model,charge_point_vendors=cp.charge_point_vendors,status=cp.status,adresse=cp.adresse,longitude=cp.longitude,latitude=cp.latitude,state=ACTIVE_STATE)
        session.add(charge)
        session.commit()
        session.refresh(charge)
        return "insertion réussie"
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}

def update_cp(id_cp:str,cp:Cp_update,session : Session):
    
    charge=session.exec(select(ChargePoint).where(ChargePoint.id == id_cp)).first()
    if charge is None:
        raise Exception(f"CP  with id {id_cp} does not exist.")
    
    charge.status=cp.status
    charge.charge_point_model=cp.charge_point_model
    charge.charge_point_vendors=cp.charge_point_vendors
    charge.updated_at=datetime.now()
    charge.serial_number=cp.serial_number
    charge.adresse=cp.adresse
    charge.longitude=cp.longitude
    charge.latitude=cp.latitude
    charge.firmware_version=cp.firmware_version
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return "Modification réussie"

def update_cp_boot(id_cp:str,cp:Cp_update,session : Session):
    
    charge=session.exec(select(ChargePoint).where(ChargePoint.id == id_cp)).first()
    if charge is None:
        raise Exception(f"CP  with id {id_cp} does not exist.")
    
    charge.status=cp.status
    charge.charge_point_model=cp.charge_point_model
    charge.charge_point_vendors=cp.charge_point_vendors
    charge.updated_at=cp.time+timedelta(hours=3)
    charge.firmware_version=cp.firmware_version
    
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return "Modification réussie"

def update_cp_status(id_cp:str,cp:Cp_update,session : Session):
    
    charge=session.exec(select(ChargePoint).where(ChargePoint.id == id_cp)).first()
    if charge is None:
        raise Exception(f"CP  with id {id_cp} does not exist.")
    
    charge.status=cp.status
    charge.updated_at=cp.time+ timedelta(hours=3)
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return "Modification réussie"

def delete_cp(id_cp:str,session : Session):
    
    charge=session.exec(select(ChargePoint).where(ChargePoint.id == id_cp)).first()
    if charge is None:
        raise Exception(f"CP  with id {id_cp} does not exist.")
    charge.state=DELETED_STATE
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return "delete réussie"
    
def read_charge_point_connector(session:Session, page: int = 1, number_items: int = 50):
    try:
        pagination = Pagination(page=page, limit=number_items)
        chargepoints = session.exec(
            select(
                ChargePoint.id.label("id_charge_point"),
                ChargePoint.serial_number.label("serial_number"),
                ChargePoint.charge_point_model.label("charge_point_model"),
                ChargePoint.adresse.label("adresse"),
                func.sum(Connector.valeur).label("energie_consomme"),
                ChargePoint.status.label("status_charge_point"),
                func.array_agg(func.json_build_object("id", Connector.id, "status", Connector.status)).label("status_connectors") 
            )
            .join(Connector, ChargePoint.id == Connector.charge_point_id)
            .where(ChargePoint.state==ACTIVE_STATE)
            .group_by(ChargePoint.id)
            .offset(pagination.offset)  
            .limit(pagination.limit)
        ).all()

       
        count = session.exec(
            select(func.count(ChargePoint.id))
            .join(Connector, ChargePoint.id == Connector.charge_point_id)
            .where(ChargePoint.state == ACTIVE_STATE)
            .group_by(ChargePoint.id)
        ).all()

        
        formatted_result = [
            {
                "id_charge_point": cp.id_charge_point,
                "nom": cp.serial_number,
                "adresse": cp.adresse,
                "connecteurs": [
                    {"id": connector["id"], "status": connector["status"]} for connector in cp.status_connectors or []
                ],
                "energie_consomme": cp.energie_consomme,
                "status_charge_point": cp.status_charge_point,
            }
            for cp in chargepoints
        ]

        pagination.total_items = len(count)
        return {"data": formatted_result, "pagination":pagination.dict()}
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    
def read_detail_cp(id_cp:str,session:Session):
    result = session.exec(
        select(
            ChargePoint.id.label("id_charge_point"),
            ChargePoint.charge_point_model.label("charge_point_model"),
            ChargePoint.charge_point_vendors.label("charge_point_vendors"),
            ChargePoint.adresse.label("adresse"),
            Connector.id.label("id_connecteur"),
            ChargePoint.status.label("status_charge_point"),
            Connector.status.label("status_connector"),
            Connector.valeur.label("energie_delivre")
        )
        .join(Connector, ChargePoint.id == Connector.charge_point_id)
        .where(Connector.charge_point_id==id_cp)
        .where(Connector.id.not_like('0%'))
    ).all()
    if result is None:
        raise Exception(f"CP  with id {id_cp} does not exist.")
    formatted_result = [
        {
            "id_charge_point": row.id_charge_point,
            "id_connecteur": row.id_connecteur,
            "energie_delivre":row.energie_delivre,
            "status_charge_point": row.status_charge_point,
            "status_connector": row.status_connector,
            "charge_point_model":row.charge_point_model,
            "charge_point_vendors":row.charge_point_vendors,
            "adresse":row.adresse
        }
        for row in result
    ]

    return formatted_result
def read_detail_cp_update(id_cp:str,session:Session):
    result = session.exec(
        select(
            ChargePoint.id.label("id_charge_point"),
            ChargePoint.charge_point_model.label("charge_point_model"),
            ChargePoint.charge_point_vendors.label("charge_point_vendors"),
            ChargePoint.adresse.label("adresse"),
            Connector.id.label("id_connecteur"),
            ChargePoint.status.label("status_charge_point"),
            Connector.status.label("status_connector")
        )
        .join(Connector, ChargePoint.id == Connector.charge_point_id)
        .where(Connector.charge_point_id==id_cp)
    ).all()
    if result is None:
        raise Exception(f"CP  with id {id_cp} does not exist.")
    formatted_result = [
        {
            "id_charge_point": row.id_charge_point,
            "id_connecteur": row.id_connecteur,
            "status_charge_point": row.status_charge_point,
            "status_connector": row.status_connector,
            "charge_point_model":row.charge_point_model,
            "charge_point_vendors":row.charge_point_vendors,
            "adresse":row.adresse
        }
        for row in result
    ]

    return formatted_result


def read_cp(session:Session, page: int = 1, number_items: int = 50):
    try:
        pagination = Pagination(page=page, limit=number_items)
        charge = session.exec(
            select(
                ChargePoint,
                func.coalesce(func.sum(Connector.valeur), 0).label("energie_consomme")  
            )
            .select_from(ChargePoint) 
            .join(Connector, ChargePoint.id == Connector.charge_point_id, isouter=True)  
            .where(ChargePoint.state == ACTIVE_STATE)
            .group_by(ChargePoint.id)
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        count=session.exec(
            select(
                func.count(ChargePoint.id).label("nombre")
                 
            ).select_from(ChargePoint)).one()
        charge_data = []
        for cp, energy in charge:
            val=Cp_form(id=cp.id,serial_number=cp.serial_number,charge_point_model=cp.charge_point_model,charge_point_vendors=cp.charge_point_vendors,status=cp.status,adresse=cp.adresse,latitude=cp.latitude,longitude=cp.longitude,energie_consomme=energy)
            charge_data.append(dict(val))
        pagination.total_items = count
        return {"data": charge_data, "pagination": pagination.dict()}
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    
def escape_like_pattern(pattern: str) -> str:
    escape_chars = ["%", "_"]
    for char in escape_chars:
        pattern = pattern.replace(char, "\\" + char)
    return pattern
def recherche_cp(session: Session, recherche: str, page: int = 1, number_items: int = 50):
    try:
        pagination = Pagination(page=page, limit=number_items)
        recherche_pattern = f"%{escape_like_pattern(recherche)}%"
        
        charge_query = (
            select(ChargePoint)
            .filter(
                ChargePoint.state == ACTIVE_STATE,
                or_(
                    ChargePoint.id.ilike(recherche_pattern),
                    ChargePoint.charge_point_model.ilike(recherche_pattern),
                    ChargePoint.charge_point_vendors.ilike(recherche_pattern),
                    ChargePoint.adresse.ilike(recherche_pattern),
                    ChargePoint.status.ilike(recherche_pattern)
                )
            )
        )
        print("Requête après filtrage :", charge_query,recherche)
        if recherche.lower() == "available":
            charge_query = (
            select(ChargePoint)
            .filter(
                ChargePoint.state == ACTIVE_STATE,
                or_(
                    ChargePoint.id.ilike(recherche_pattern),
                    ChargePoint.charge_point_model.ilike(recherche_pattern),
                    ChargePoint.charge_point_vendors.ilike(recherche_pattern),
                    ChargePoint.adresse.ilike(recherche_pattern),
                    ChargePoint.status.ilike(recherche)
                )
            )
        )
        
        charge = session.exec(
            charge_query.offset(pagination.offset).limit(pagination.limit)
        ).all()
        has_next = len(charge)
        pagination.total_items = has_next
        return {"data": charge, "pagination": pagination.dict()}
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}


def somme_metervalue_connector(id_cp:str,session:Session):
    try:
        meter_values = session.exec(
            select(Connector).where(Connector.charge_point_id== id_cp)
        ).all()
        total_value = sum(meter_value.valeur for meter_value in meter_values)  
        return total_value 
    except Exception as e:
        return {"messageError": f" {str(e)}"}
    
def count_status_cp(status:str,session:Session):
    try:
        
        chargepoints = session.exec(
            select(
                func.count(ChargePoint.id).label("nombre")
            )
            .where(ChargePoint.state==ACTIVE_STATE,ChargePoint.status==status)
            
            
        ).first()
        formatted_result = [
            {
                "nombre": chargepoints,  
            }
        ]
        return formatted_result
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}

def detail_status_cp(status:str,session:Session):
    try:
        
        chargepoints = session.exec(
            select(
                ChargePoint.id.label("id_charge_point"),
                ChargePoint.charge_point_model.label("charge_point_model"),
                ChargePoint.charge_point_vendors.label("charge_point_vendors"),
                ChargePoint.adresse.label("adresse")
            )
            .where(ChargePoint.state==ACTIVE_STATE,ChargePoint.status==status)
            
            
        ).all()
        formatted_result = [
            {
                "id_charge_point": row.id_charge_point,
                "charge_point_model":row.charge_point_model,
                "charge_point_vendors":row.charge_point_vendors,
                "adresse":row.adresse  
            
            }
            for row in chargepoints
        ]
        return formatted_result
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    

async def upload_charge_points_from_csv(file: UploadFile, session: Session):
    logs = []
    try:
        # Commencer une transaction
        with session.begin():
            # Lire le fichier CSV
            datas = await get_datas_from_csv(file)
            line = 1
            for data in datas:
                # Vérifier les champs obligatoires
                if not data.get("serial_number"):
                    logs.append({"message": f"Serial number is missing.", "line": line})
                    line += 1
                    continue
                if not data.get("charge_point_model"):
                    logs.append({"message": f"charge_point_model is missing.", "line": line})
                    line += 1
                    continue
                if not data.get("charge_point_vendors"):
                    logs.append({"message": f"charge_point_vendors is missing.", "line": line})
                    line += 1
                    continue
                if not data.get("longitude"):
                    logs.append({"message": f"longitude is missing.", "line": line})
                    line += 1
                    continue
                if not data.get("latitude"):
                    logs.append({"message": f"latitude is missing.", "line": line})
                    line += 1
                    continue

                if not data.get("adresse"):
                    logs.append({"message": f"Address is missing.", "line": line})
                    line += 1
                    continue

                # Vérifier si le charge point existe déjà
                existing_charge_point = session.exec(select(ChargePoint).where(ChargePoint.id == data["serial_number"])).first()
                if existing_charge_point is not None:
                    logs.append({"message": f"Charge point with serial number {data['serial_number']} already exists.", "line": line})
                    line += 1
                    continue

                # Ajouter le nouveau charge point
                new_charge_point = ChargePoint(
                    id=data["serial_number"],
                    adresse=data["adresse"],
                    charge_point_model=data.get("charge_point_model"),
                    charge_point_vendors=data.get("charge_point_vendors"),
                    status=StatusEnum.unavailable,
                    serial_number=data["serial_number"],
                    longitude=data.get("longitude"),
                    latitude=data.get("latitude"),
                    state=ACTIVE_STATE
                      
                )
                session.add(new_charge_point)
                line += 1

            if len(logs) > 0:
                # Annuler la transaction s'il y a des erreurs
                session.rollback()
                return {"message": "Charge points imported with errors", "logs": logs}
            session.commit()
            return {"message": "Charge point  imported successfully"}
    except Exception as e:
        session.rollback()
        return {"message": f"Error: {str(e)}"}
    

async def send_remoteStopTransaction(charge_point_id: str, transaction_id: int):
    remote=RemoteStopTransaction()
    message = remote.on_remoteStop(transaction_id)
    response_json = {
        "charge_point_id": charge_point_id,
        "payload": message
    }
        
    try:
        connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.get_exchange("micro_ocpp") 
            await exchange.publish(
                AioPikaMessage(body=json.dumps(response_json).encode()),
                routing_key="02"
            )


        return {"status": "Message sent", "response": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")
async def send_remoteStartTransaction(charge_point_id: str, idTag:str,connectorId:str):
    remote=RemoteStartTransaction()
    message = remote.on_remoteStart(idTag,connectorId)
    response_json = {
        "charge_point_id": charge_point_id,
        "payload": message
    }
        
    try:
        connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.get_exchange("micro_ocpp") 
            await exchange.publish(
                AioPikaMessage(body=json.dumps(response_json).encode()),
                routing_key="02"
            )


        return {"status": "Message sent", "response": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")

async def send_getdiagnostic(charge_point_id: str, startTime:datetime,stopTime:datetime,path:str):
    get=GetDiagnostic()
    startTime_str = startTime.isoformat()
    stopTime_str = stopTime.isoformat()
    message = get.on_getdiagnostic(startTime=startTime_str,stopTime=stopTime_str,path=path)
    response_json = {
        "charge_point_id": charge_point_id,
        "payload": message
    }
      
    try:
        connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.get_exchange("micro_ocpp") 
            await exchange.publish(
                AioPikaMessage(body=json.dumps(response_json).encode()),
                routing_key="02"
            )


        return {"status": "Message sent", "response": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")

def graph_conso_energie_cp(id_cp:str,session:Session,CurrentYear: int = None):
    if CurrentYear is None:
        CurrentYear=datetime.now().year
    previous_year=CurrentYear-1
    current_year_data = session.exec(
        select(
            extract('month', Historique_metter_value.created_at).label("month"),
            func.sum(Historique_metter_value.valeur).label("total_value")
        )
        .join(Connector, Historique_metter_value.real_connector_id == Connector.id)
        .join(ChargePoint, Connector.charge_point_id == ChargePoint.id)
        .where(ChargePoint.id == id_cp)
        .where(extract('year', Historique_metter_value.created_at) == CurrentYear)
        .group_by("month")
    ).all()

    previous_year_data = session.exec(
        select(
            extract('month', Historique_metter_value.created_at).label("month"),
            func.sum(Historique_metter_value.valeur).label("total_value")
        )
        .join(Connector, Historique_metter_value.real_connector_id == Connector.id)
        .join(ChargePoint, Connector.charge_point_id == ChargePoint.id)
        .where(ChargePoint.id == id_cp)
        .where(extract('year', Historique_metter_value.created_at) == previous_year)
        .group_by("month")
    ).all()
    months_data = {month: {"label": month_name, "currentValue": 0, "oldValue": 0}
                   for month, month_name in enumerate(
                       ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"], 1)}

    for month, total_value in current_year_data:
        months_data[month]["currentValue"] = total_value

    for month, total_value in previous_year_data:
        months_data[month]["oldValue"] = total_value
    return list(months_data.values())

def graph_trimestriel_conso_energie_cp(id_cp:str,session:Session,CurrentYear: int = None):
    if CurrentYear is None:
        CurrentYear=datetime.now().year
    
    current_year_data = session.exec(
        select(
            extract('quarter', Historique_metter_value.created_at).label("quarter"),
            func.sum(Historique_metter_value.valeur).label("total_value")
        )
        .join(Connector, Historique_metter_value.real_connector_id == Connector.id)
        .join(ChargePoint, Connector.charge_point_id == ChargePoint.id)
        .where(ChargePoint.id == id_cp)
        .where(extract('year', Historique_metter_value.created_at) == CurrentYear)
        .group_by("quarter")
    ).all()

    
    trimestre_data = {trimestre: {"label": trimestre_name, "currentValue": 0}
                   for trimestre, trimestre_name in enumerate(
                       ["1er trimestre", "2eme trimestre", "3eme trimestre", "4eme trimestre"], 1)}

    for trimestre, total_value in current_year_data:
        trimestre_data[trimestre]["currentValue"] = total_value

    return list(trimestre_data.values())


def graph_semestriel_conso_energie_cp(id_cp:str,session:Session,CurrentYear: int = None):
    if CurrentYear is None:
        CurrentYear=datetime.now().year
    
    current_year_data = session.exec(
        select(
            case(
                (func.extract('month', Historique_metter_value.created_at).between(1, 6), 1),  
                (func.extract('month', Historique_metter_value.created_at).between(7, 12), 2)  
            ).label("semester"),
            func.sum(Historique_metter_value.valeur).label("total_value")
        )
        .join(Connector, Historique_metter_value.real_connector_id == Connector.id)
        .join(ChargePoint, Connector.charge_point_id == ChargePoint.id)
        .where(ChargePoint.id == id_cp)
        .where(extract('year', Historique_metter_value.created_at) == CurrentYear)
        .group_by("semester")
    ).all()

    
    semestre_data = {semestre: {"label": semestre_name, "currentValue": 0}
                   for semestre, semestre_name in enumerate(
                       ["1er semestre", "2eme semestre"], 1)}

    for semestre, total_value in current_year_data:
        semestre_data[semestre]["currentValue"] = total_value

    return list(semestre_data.values())



def graph_conso_energie(session:Session,CurrentYear: int = None):
    if CurrentYear is None:
        CurrentYear=datetime.now().year
    previous_year=CurrentYear-1
    current_year_data = session.exec(
        select(
            extract('month', Historique_metter_value.created_at).label("month"),
            func.sum(Historique_metter_value.valeur).label("total_value")
        )
        .join(Connector, Historique_metter_value.real_connector_id == Connector.id)
        .join(ChargePoint, Connector.charge_point_id == ChargePoint.id)
        .where(extract('year', Historique_metter_value.created_at) == CurrentYear)
        .group_by("month")
    ).all()

    previous_year_data = session.exec(
        select(
            extract('month', Historique_metter_value.created_at).label("month"),
            func.sum(Historique_metter_value.valeur).label("total_value")
        )
        .join(Connector, Historique_metter_value.real_connector_id == Connector.id)
        .join(ChargePoint, Connector.charge_point_id == ChargePoint.id)
        .where(extract('year', Historique_metter_value.created_at) == previous_year)
        .group_by("month")
    ).all()
    months_data = {month: {"label": month_name, "currentValue": 0, "oldValue": 0}
                   for month, month_name in enumerate(
                       ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"], 1)}

    for month, total_value in current_year_data:
        months_data[month]["currentValue"] = total_value

    for month, total_value in previous_year_data:
        months_data[month]["oldValue"] = total_value
    return list(months_data.values())

def graph_trimestriel_conso_energie(session:Session,CurrentYear: int = None):
    if CurrentYear is None:
        CurrentYear=datetime.now().year
    
    current_year_data = session.exec(
        select(
            extract('quarter', Historique_metter_value.created_at).label("quarter"),
            func.sum(Historique_metter_value.valeur).label("total_value")
        )
        .join(Connector, Historique_metter_value.real_connector_id == Connector.id)
        .join(ChargePoint, Connector.charge_point_id == ChargePoint.id)
        .where(extract('year', Historique_metter_value.created_at) == CurrentYear)
        .group_by("quarter")
    ).all()

    
    trimestre_data = {trimestre: {"label": trimestre_name, "currentValue": 0}
                   for trimestre, trimestre_name in enumerate(
                       ["1er trimestre", "2eme trimestre", "3eme trimestre", "4eme trimestre"], 1)}

    for trimestre, total_value in current_year_data:
        trimestre_data[trimestre]["currentValue"] = total_value

    return list(trimestre_data.values())


def graph_semestriel_conso_energie(session:Session,CurrentYear: int = None):
    if CurrentYear is None:
        CurrentYear=datetime.now().year
    
    current_year_data = session.exec(
        select(
            case(
                (func.extract('month', Historique_metter_value.created_at).between(1, 6), 1),  
                (func.extract('month', Historique_metter_value.created_at).between(7, 12), 2)  
            ).label("semester"),
            func.sum(Historique_metter_value.valeur).label("total_value")
        )
        .join(Connector, Historique_metter_value.real_connector_id == Connector.id)
        .join(ChargePoint, Connector.charge_point_id == ChargePoint.id)
        .where(extract('year', Historique_metter_value.created_at) == CurrentYear)
        .group_by("semester")
    ).all()

    
    semestre_data = {semestre: {"label": semestre_name, "currentValue": 0}
                   for semestre, semestre_name in enumerate(
                       ["1er semestre", "2eme semestre"], 1)}

    for semestre, total_value in current_year_data:
        semestre_data[semestre]["currentValue"] = total_value

    return list(semestre_data.values())

def map_cp(session:Session):
    result = session.exec(
        select(
            ChargePoint.id.label("id_charge_point"),
            ChargePoint.adresse.label("adresse"),
            ChargePoint.status.label("status_charge_point"),
            ChargePoint.longitude.label("longitude"),
            ChargePoint.latitude.label("latitude")
           
        )
        .where(ChargePoint.state==ACTIVE_STATE)
    ).all()
    formatted_result = [
        {
            "id": row.id_charge_point,
            "name": row.adresse,
            "position":[row.latitude,row.longitude],
            "status":row.status_charge_point
        }
        for row in result
    ]

    return formatted_result

    



        

        
        


    







    
    
