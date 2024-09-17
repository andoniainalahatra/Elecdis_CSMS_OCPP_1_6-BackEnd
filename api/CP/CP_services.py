from api.CP.CP_models import Cp_create,Cp_update
from models.elecdis_model import ChargePoint,StatusEnum,Connector
from sqlmodel import Session, select,func
from models.Pagination import Pagination
from fastapi import UploadFile
from core.utils import *
from datetime import date, datetime,timedelta



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
    charge.updated_at=cp.time+ timedelta(hours=3)
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return "Modification réussie"

def update_cp_status(id_cp:str,cp:Cp_update,session : Session):
    
    charge=session.exec(select(ChargePoint).where(ChargePoint.id == id_cp)).first()
    if charge is None:
        raise Exception(f"CP  with id {id_cp} does not exist.")
    
    charge.status=cp.status
    charge.updated_at=cp.time
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

        pagination.total_items = len(formatted_result)
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
        charge=session.exec(select(ChargePoint).where(ChargePoint.state==ACTIVE_STATE).offset(pagination.offset).limit(pagination.limit)).all()
        numer_itemQuery=session.exec(select(func.count(ChargePoint.id)).where(ChargePoint.state==ACTIVE_STATE)).one()
        pagination.total_items=numer_itemQuery
        has_next = len(charge) == pagination.limit

        return {"data": charge, "pagination":pagination.dict()}
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
    



        

        
        


    







    
    
