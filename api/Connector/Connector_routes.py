from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.Connector.Connector_services import create_connector,update_connector
from api.Connector.Connector_models import Connector_create,Connector_update,Historique_metervalues_create,Historique_status_create
from fastapi import HTTPException

from core.database import get_session

router = APIRouter()

@router.post("/create")
def create_conne(create_data : Connector_create, session : Session=Depends(get_session)):
    try:
        return create_connector(create_data, session)
    except Exception as e:
        raise e


@router.put("/update/{id_connector}")
def update_conne(id_connector:int,create_data : Connector_update, session : Session=Depends(get_session)):
    try:
        update_connector(id_connector,create_data, session)
    except Exception as e:
        raise e