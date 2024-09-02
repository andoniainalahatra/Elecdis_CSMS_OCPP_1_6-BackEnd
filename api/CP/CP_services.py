from api.CP.CP_models import Cp_create,Cp_update
from models.elecdis_model import ChargePoint,StatusEnum,Connector
from sqlmodel import Session, select,func



def create_cp(cp: Cp_create, session : Session):
    try:
        charge : ChargePoint = ChargePoint(id=cp.id,serial_number=cp.serial_number, charge_point_model=cp.charge_point_model,charge_point_vendors=cp.charge_point_vendors,status=StatusEnum.unavailable,adresse=cp.adresse,longitude=cp.longitude,latitude=cp.latitude)
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
    session.add(charge)
    session.commit()
    session.refresh(charge)
    return "Modification réussie"
    
def read_charge_point(session:Session):
    try:
        chargepoints = session.exec(
            select(
                ChargePoint.id.label("id_charge_point"),
                ChargePoint.serial_number.label("serial_number"),
                ChargePoint.charge_point_model.label("charge_point_model"),
                ChargePoint.adresse.label("adresse"),
                func.sum(Connector.valeur).label("energie_consomme"),
                ChargePoint.status.label("status_charge_point"),
                func.array_agg(func.json_build_object("id", Connector.id, "status", Connector.status)).label("status_connectors")  # Aggregate both id and status in JSON format
            )
            .join(Connector, ChargePoint.id == Connector.charge_point_id)
            .group_by(ChargePoint.id)
        ).all()
        formatted_result = [
            {
                "id_charge_point": cp.id_charge_point,
                "nom": cp.serial_number,
                "adresse": cp.adresse,
                "connecteurs": [
                    {"id": connector["id"], "status": connector["status"]} for connector in cp.status_connectors
                ],
                "energie_consomme": cp.energie_consomme,
                "status_charge_point": cp.status_charge_point,
            }
            for cp in chargepoints
        ]

        return formatted_result
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    
def read_detail_cp(id_cp:int,session:Session):
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
    
    
