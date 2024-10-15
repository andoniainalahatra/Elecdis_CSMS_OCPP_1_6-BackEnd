from api.Connector.Connector_models import Connector_create,Connector_update,Historique_metervalues_create,Historique_status_create
from models.elecdis_model import ChargePoint,Connector,StatusEnum,Historique_status,Historique_metter_value
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import timedelta
from sqlmodel import Session, select,func,extract
import logging
logging.basicConfig(level=logging.INFO)

def create_connector(connector: Connector_create, session : Session):
    charge=session.exec(select(ChargePoint).where(ChargePoint.id == connector.charge_point_id)).first()
    if charge is None:
        raise Exception(f"ChargePoint with id {connector.charge_point_id} does not exist.")
            
    conne : Connector = Connector(id=connector.id,connector_type=connector.connector_type, connector_id=connector.connector_id,charge_point_id=connector.charge_point_id,status=connector.status,valeur=0)
    session.add(conne)
    session.commit()
    session.refresh(conne)
    return "insertion réussie"


def update_connector(id_connector:str,connector:Connector_update,session : Session,can_commit=True):
    try:
        conne=session.exec(select(Connector).where(Connector.id == id_connector)).first()
        if conne is None:
            raise Exception(f"CP  with id {id_connector} does not exist.")
        
        if conne.updated_at is None:
            raise Exception("Connector 'updated_at' timestamp is missing and is required.")
        
        histo = Historique_status_create(real_connector_id=id_connector, status=conne.status,time_last_status=conne.updated_at)
        create_historique_status(histo, session)  
        if can_commit:
            session.commit()  
        logging.info(f"Historique inséré pour le connecteur ID: {id_connector} avec le statut: {conne.status}")

        #charge=session.exec(select(ChargePoint).where(ChargePoint.id == connector.charge_point_id)).first()
        #if charge is None:
            #raise Exception(f"CP  with id {connector.charge_point_id} does not exist.")
        conne.status=connector.status
        conne.updated_at=connector.time+ timedelta(hours=3)
        conne.valeur=connector.valeur
        session.add(conne)
        session.commit()
        session.refresh(conne) 
        return "update réussie"
    except Exception as e:
        return {"messageError":f"{str(e)}"}

def update_connector_status(id_connector:str,connector:Connector_update,session : Session,can_commit=True):
    try:
        conne=session.exec(select(Connector).where(Connector.id == id_connector)).first()
        if conne is None:
            raise Exception(f"CP  with id {id_connector} does not exist.")
        
        if conne.updated_at is None:
            raise Exception("Connector 'updated_at' timestamp is missing and is required.")
        
        histo = Historique_status_create(real_connector_id=id_connector, status=conne.status,time_last_status=conne.updated_at)
        create_historique_status(histo, session)  
        if can_commit:
            session.commit()  
        #logging.info(f"Historique inséré pour le connecteur ID: {id_connector} avec le statut: {conne.status}")

        #charge=session.exec(select(ChargePoint).where(ChargePoint.id == connector.charge_point_id)).first()
        #if charge is None:
            #raise Exception(f"CP  with id {connector.charge_point_id} does not exist.")
        conne.status=connector.status
        conne.updated_at=connector.time
        session.add(conne)
        session.commit()
        session.refresh(conne) 
        return "update réussie"
    except Exception as e:
        return {"messageError":f"{str(e)}"}
    

def update_connector_valeur(id_connector:str,connector:Connector_update,session : Session,can_commit=True):
    try:
        conne=session.exec(select(Connector).where(Connector.id == id_connector)).first()
        if conne is None:
            raise Exception(f"CP  with id {id_connector} does not exist.")
        
        if conne.updated_at is None:
            raise Exception("Connector 'updated_at' timestamp is missing and is required.")
         
        if can_commit:
            session.commit()  

        #charge=session.exec(select(ChargePoint).where(ChargePoint.id == connector.charge_point_id)).first()
        #if charge is None:
            #raise Exception(f"CP  with id {connector.charge_point_id} does not exist.")
        conne.valeur=connector.valeur
        conne.updated_at=connector.time
        session.add(conne)
        session.commit()
        session.refresh(conne) 
        return "update réussie"
    except Exception as e:
        return {"messageError":f"{str(e)}"}
    

def create_historique_status(historique:Historique_status_create,session : Session):
    try:
        histo:Historique_status=Historique_status(real_connector_id=historique.real_connector_id,statut=historique.status,time_last_statut=historique.time_last_status)
        session.add(histo)
        session.commit()
       
    except Exception as e:
        return {"messageError":f"{str(e)}"}
    
def create_historique_metervalues(historique:Historique_metervalues_create,session:Session):
    try:
        histo:Historique_metter_value=Historique_metter_value(real_connector_id=historique.real_connector_id,valeur=historique.valeur)
        session.add(histo)
        session.commit()
        session.refresh(histo)
    except Exception as e:
        return {"messageError":f"{str(e)}"}


def get_connector_by_id(id_connector:str,session:Session):
    try:
        connector = session.exec(select(Connector).where(Connector.id == id_connector)).first()
        if connector is None:
            raise HTTPException(status_code=404, detail=f"Connector with id {id_connector} not found")
        return connector
    except Exception as e:
        return {"messageError":f"{str(e)}"}
    



# def check_status_connector(id_charge_point: str, session: Session):
#     try:
#         connectors = session.exec(
#             select(Connector).where(Connector.charge_point_id == id_charge_point)
#         ).all()       
#         has_available = any(connector.status == StatusEnum.available for connector in connectors) 
#         return has_available
#     except Exception as e:
#         return {"messageError": f"{str(e)}"}
    
def somme_metervalues(id_connector:str,session:Session):
    try:
        meter_values = session.exec(
            select(Historique_metter_value).where(Historique_metter_value.real_connector_id == id_connector)
        ).all()
        total_value = sum(meter_value.valeur for meter_value in meter_values)  
        return total_value 
    except Exception as e:
        return {"messageError": f" {str(e)}"}
    
def graph_connector_status(session:Session):
    total_connector = session.exec(
        select(func.count(Connector.id))
        .where(Connector.id.not_like('0%'))).first()


    total_unavailable_connector = session.exec(
        select(func.count(Connector.id)).where(Connector.status == "Unavailable").where(Connector.id.not_like('0%'))
    ).first()
    total_charging_connector = session.exec(
        select(func.count(Connector.id.not_like('0%')))
        .where(Connector.status == "Charging")
        .where(Connector.id.not_like('0%'))
    ).first()
    total_available_connector=int(total_connector-(total_unavailable_connector+total_charging_connector))
    
    stats = [
        {
            "status": "charging",
            "value": total_charging_connector,
            "fill": "var(--color-charging)"
        },
        {
            "status": "available",
            "value": total_available_connector,
            "fill": "var(--color-available)"
        },
        {
            "status": "unavailable",
            "value": total_unavailable_connector,
            "fill": "var(--color-unavailable)"
        }
    ]
    
    return stats
    