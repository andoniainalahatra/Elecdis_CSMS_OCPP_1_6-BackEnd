from api.Connector.Connector_models import Connector_create,Connector_update,Historique_metervalues_create,Historique_status_create
from models.elecdis_model import ChargePoint,Connector,StatusEnum,Historique_status,Historique_metter_value
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import date, datetime
import logging
logging.basicConfig(level=logging.INFO)

def create_connector(connector: Connector_create, session : Session):
    if connector.status=="string" or None:
            connector.status=StatusEnum.unavailable
    charge=session.exec(select(ChargePoint).where(ChargePoint.id == connector.charge_point_id)).first()
    if charge is None:
        raise Exception(f"ChargePoint with id {connector.charge_point_id} does not exist.")
            
    conne : Connector = Connector(id=connector.id,connector_type=connector.connector_type, connector_id=connector.connector_id,charge_point_id=connector.charge_point_id,status=connector.status,valeur=0)
    session.add(conne)
    session.commit()
    session.refresh(conne)
    return "insertion réussie"
    

def update_connector(id_connector:str,connector:Connector_update,session : Session):
    try:
        conne=session.exec(select(Connector).where(Connector.id == id_connector)).first()
        valeur=0
        if connector.valeur !=None:
            valeur=connector.valeur
        if connector.status == "string":
            connector.status=conne.status
        if conne is None:
            raise Exception(f"CP  with id {id_connector} does not exist.")
        
        if conne.updated_at is None:
            raise Exception("Connector 'updated_at' timestamp is missing and is required.")
        
        histo = Historique_status_create(real_connector_id=id_connector, status=conne.status,time_last_status=conne.updated_at)
        create_historique_status(histo, session)  
        session.commit()  
        logging.info(f"Historique inséré pour le connecteur ID: {id_connector} avec le statut: {conne.status}")

        #charge=session.exec(select(ChargePoint).where(ChargePoint.id == connector.charge_point_id)).first()
        #if charge is None:
            #raise Exception(f"CP  with id {connector.charge_point_id} does not exist.")
        conne.status=connector.status
        conne.valeur=valeur
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
    