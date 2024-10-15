from fastapi import APIRouter, Depends,status,HTTPException
from sqlalchemy.orm import Session
from api.Connector.Connector_services import create_connector,update_connector,graph_connector_status
from api.Connector.Connector_models import Connector_create,Connector_update,Historique_metervalues_create,Historique_status_create


from core.database import get_session

router = APIRouter()

@router.post("/create")
def create_conne(create_data : Connector_create, session : Session=Depends(get_session)):
    try:
        return create_connector(create_data, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))


@router.put("/update/{id_connector}")
def update_conne(id_connector:str,create_data : Connector_update, session : Session=Depends(get_session)):
    try:
        return update_connector(id_connector,create_data, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.get("/graph_connector_status")
def graph_connect_status(session : Session=Depends(get_session)):
    try:
      return  graph_connector_status(session)
    except Exception as e:
        raise e