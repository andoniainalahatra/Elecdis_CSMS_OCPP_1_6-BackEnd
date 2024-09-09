from fastapi import APIRouter, Depends,status,HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from api.CP.CP_services import create_cp,update_cp,read_charge_point_connector,read_detail_cp,delete_cp,read_cp,upload_charge_points_from_csv,count_status_cp,detail_status_cp
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
def update_charge(id_cp:str,create_data:Cp_update,session : Session=Depends(get_session)):
    try:
        return update_cp(id_cp,create_data,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.delete("/update/{id_cp}")
def delete_charge(id_cp:str,session : Session=Depends(get_session)):
    try:
        return delete_cp(id_cp,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))

@router.get("/read_cp_connector")
def read_cp_connector(session : Session=Depends(get_session)):
    try:
        return read_charge_point_connector(session)
    except Exception as e:
        raise e

@router.get("/read_cp/{id}")
def read_charge_detail(id:str,session : Session=Depends(get_session)):
    try:
        return read_detail_cp(id,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.get("/read_cp")
def read_charge(session : Session=Depends(get_session)):
    try:
        return read_cp(session)
    except Exception as e:
        raise e
@router.get("/count_status_cp/{status}")
def count_status_charge(status:str,session : Session=Depends(get_session)):
    try:
        return count_status_cp(status,session)
    except Exception as e:
        raise e
    
@router.get("/detail_status_cp/{status}")
def detail_status_charge(status:str,session : Session=Depends(get_session)):
    try:
        return detail_status_cp(status,session)
    except Exception as e:
        raise e
@router.post("/import_from_csv_cp")
async def import_from_csv_cp(file: UploadFile = File(...), session : Session = Depends(get_session)):
    message = await upload_charge_points_from_csv(file, session)
    if message.get("logs"):
        print(message["logs"])
    else :
        print(message)
    return {}