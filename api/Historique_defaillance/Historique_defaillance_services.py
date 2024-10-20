from api.Historique_defaillance.Historique_defaillance_models import Historique_defaillance_create,Historique_defaillance_update
from models.elecdis_model import Historique_defailllance,StatusEnum,ChargePoint
from models.Pagination import Pagination
from sqlmodel import Session, select,func,extract,case
from core.utils import *
from sqlalchemy import or_
from datetime import date, datetime,timedelta

import logging
from fastapi import HTTPException
logging.basicConfig(level=logging.INFO)


def create_historique_defaillance(histo: Historique_defaillance_create, session : Session):
    try:
        
        historique : Historique_defailllance = Historique_defailllance(charge_point_id=histo.charge_point_id,time=histo.time,Error_code=histo.Error_code,Description=histo.Description,etat=StatusEnum.no_resolve)
        session.add(historique)
        session.commit()
        session.refresh(historique)
        return "insertion réussie"
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}
    

def update_historique_defaillance(histo_id:str,histo:Historique_defaillance_update,session : Session):
    
    historique=session.exec(select(Historique_defailllance).where(Historique_defailllance.id == histo_id)).first()
    if historique is None:
        raise Exception(f"historique  with id {historique} does not exist.")
    histo.etat=StatusEnum.resolve
    historique.etat=histo.etat
    session.add(historique)
    session.commit()
    session.refresh(historique)
    return "Modification réussie"


def read_historique_defaillance(session : Session, page: int = 1, number_items: int = 50):
    try:
        pagination = Pagination(page=page, limit=number_items)
        histo = session.exec(
            select(Historique_defailllance,ChargePoint.id,ChargePoint.charge_point_model,ChargePoint.charge_point_vendors,ChargePoint.adresse)
            .join(ChargePoint, ChargePoint.id == Historique_defailllance.charge_point_id)
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        historique_data = [
            {

                "historique_id": record[0].id,  
                "historique_erreur":record[0].Error_code,
                "historique_description":record[0].Description,
                "heure_erreur":record[0].time,
                "charge_point_id": record[1],
                "charge_point_model": record[2],
                "charge_point_vendors": record[3],
                "adresse": record[4],
            }
            for record in histo
        ]
        count=session.exec(
            select(
                func.count(Historique_defailllance.id).label("nombre")
                 
            ).select_from(Historique_defailllance)).one()
        pagination.total_items = count
        return {"data": historique_data, "pagination": pagination.dict()}
    except Exception as e:
        return {"messageError": f"Error: {str(e)}"}