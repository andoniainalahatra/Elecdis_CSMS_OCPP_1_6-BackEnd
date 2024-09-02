from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.CP.CP_services import create_cp,update_cp,read_charge_point,read_detail_cp
from api.CP.CP_models import Cp_create,Cp_update

from core.database import get_session

router = APIRouter()

@router.post("/create")
def create_charge(create_data:Cp_create,session : Session=Depends(get_session)):
    try:
      return create_cp(create_data,session)
    except Exception as e:
        raise e

@router.put("/update/{id_cp}")
def update_charge(id_cp:int,create_data:Cp_update,session : Session=Depends(get_session)):
    try:
        return update_cp(id_cp,create_data,session)
    except Exception as e:
        raise e

@router.get("/read_cp")
def read_cp(session : Session=Depends(get_session)):
    try:
        return read_charge_point(session)
    except Exception as e:
        raise e

@router.get("/read_cp/{id}")
def read_charge_detail(id:int,session : Session=Depends(get_session)):
    try:
        return read_detail_cp(id,session)
    except Exception as e:
        raise e