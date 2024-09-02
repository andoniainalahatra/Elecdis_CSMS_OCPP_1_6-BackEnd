from api.Connector.Connector_models import Connector_create,Connector_update,Historique_metervalues_create,Historique_status_create
from models.elecdis_model import ChargePoint,Connector,StatusEnum,Historique_status,Historique_metter_value
from sqlmodel import Session, select
from fastapi import HTTPException


def create_connector(connector: Connector_create, session : Session):
    
    charge=session.exec(select(ChargePoint).where(ChargePoint.id == connector.charge_point_id)).first()
    if charge is None:
        raise Exception(f"ChargePoint with id {connector.charge_point_id} does not exist.")
            
    conne : Connector = Connector(connector_type=connector.connector_type, connector_id=connector.connector_id,charge_point_id=connector.charge_point_id,status=StatusEnum.unavailable,valeur=0)
    session.add(conne)
    session.commit()
    session.refresh(conne)
    return "insertion réussie"
    

def update_connector(id_connector:int,connector:Connector_update,session : Session):
    try:
        conne=session.exec(select(Connector).where(Connector.id == id_connector)).first()
        valeur=0
        if connector.valeur !=None:
            valeur=connector.valeur
        if connector.status == None:
            connector.status=conne.status
        if conne is None:
            raise Exception(f"CP  with id {id_connector} does not exist.")
        charge=session.exec(select(ChargePoint).where(ChargePoint.id == connector.charge_point_id)).first()
        if charge is None:
            raise Exception(f"CP  with id {connector.charge_point_id} does not exist.")
        conne.status=connector.status
        conne.valeur=valeur
        session.add(conne)
        session.commit()
        session.refresh(conne)
        return "update réussie"
    except Exception as e:
        return {"messageError":f"{str(e)}"}
    

def create_historique_status(historique:Historique_status_create,session : Session):
    try:
        histo:Historique_status=Historique_status(real_connector_id=historique.real_connector_id,statut=historique.status)
        session.add(histo)
        session.commit()
        session.refresh(histo)
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
    


def check_status_connector(id_charge_point: int, session: Session):
    try:
        connectors = session.exec(
            select(Connector).where(Connector.charge_point_id == id_charge_point)
        ).all()       
        has_available = any(connector.status == StatusEnum.available for connector in connectors) 
        return has_available
    except Exception as e:
        return {"messageError": f"{str(e)}"}
    
def somme_metervalues(id_connector:int,session:Session):
    try:
        meter_values = session.exec(
            select(Historique_metter_value).where(Historique_metter_value.real_connector_id == id_connector)
        ).all()
        total_value = sum(meter_value.valeur for meter_value in meter_values)  # Remplacez 'value' par le nom du champ à additionner
        return total_value 
    except Exception as e:
        return {"messageError": f" {str(e)}"}
    