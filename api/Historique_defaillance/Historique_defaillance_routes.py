from fastapi import APIRouter, Depends,status,HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from datetime import date, datetime
from core.database import get_session
from fastapi import HTTPException
from api.Historique_defaillance.Historique_defaillance_models import Historique_defaillance_create,Historique_defaillance_update
from core.config import *
from api.Historique_defaillance.Historique_defaillance_services import update_historique_defaillance,create_historique_defaillance,read_historique_defaillance

router = APIRouter()

@router.post("/create")
def create_histo_defaillance(create_data:Historique_defaillance_create,session : Session=Depends(get_session)):
    try:
      return create_historique_defaillance(create_data,session)
    except Exception as e:
        raise e
    
@router.put("/update/{id_histo}")
def update_charge(id_histo:str,create_data:Historique_defaillance_update,session : Session=Depends(get_session)):
    try:
        return update_historique_defaillance(id_histo,create_data,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    

@router.get("/read_historique_defaillance")
def read_histo_defaillance(session : Session=Depends(get_session), page: int = 1, number_items: int = 50):
    try:
        return read_historique_defaillance(session,page,number_items)
    except Exception as e:
        raise e