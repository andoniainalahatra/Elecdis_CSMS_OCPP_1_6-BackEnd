from fastapi import APIRouter, Depends,status,HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from api.CP.CP_services import create_cp,update_cp,read_charge_point_connector,read_detail_cp,delete_cp,read_cp,upload_charge_points_from_csv,count_status_cp,detail_status_cp,recherche_cp,send_remoteStopTransaction,send_remoteStartTransaction,graph_conso_energie_cp,graph_trimestriel_conso_energie_cp,graph_semestriel_conso_energie_cp,graph_conso_energie,graph_semestriel_conso_energie,graph_trimestriel_conso_energie,send_getdiagnostic,map_cp
from api.CP.CP_models import Cp_create,Cp_update
from datetime import date, datetime
from core.database import get_session
import aio_pika
from aio_pika import ExchangeType, Message as AioPikaMessage,IncomingMessage
import json
from fastapi import HTTPException
from core.config import *

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
    
@router.delete("/delete/{id_cp}")
def delete_charge(id_cp:str,session : Session=Depends(get_session)):
    try:
        return delete_cp(id_cp,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))

@router.get("/read_cp_connector")
def read_cp_connector(session : Session=Depends(get_session), page: int = 1, number_items: int = 50):
    try:
        return read_charge_point_connector(session,page,number_items)
    except Exception as e:
        raise e

@router.get("/read_cp/{id}")
def read_charge_detail(id:str,session : Session=Depends(get_session)):
    try:
        return read_detail_cp(id,session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
    
@router.get("/read_cp")
def read_charge(session : Session=Depends(get_session), page: int = 1, number_items: int = 50):
    try:
        return read_cp(session,page,number_items)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=str(e))
@router.get("/recherche_cp")
def recherche_charge(query : str,session : Session=Depends(get_session) ,page: int = 1, number_items: int = 50):
    try:
        return recherche_cp(session,query,page,number_items)
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(message["logs"]))
    else :
        print(message)
    return {"message": "Charge points imported successfully"}

@router.post("/send_remoteStopTransaction/{charge_point_id}/{transaction_id}")
async def send_messageRemoteStopTransaction(charge_point_id: str, transaction_id: int):
    try:
      return await send_remoteStopTransaction(charge_point_id,transaction_id)
    except Exception as e:
        raise e
@router.post("/send_remoteStartTransaction/{charge_point_id}/{idTag}/{connectorId}")
async def send_messageRemoteStartTransaction(charge_point_id: str, idTag:str,connectorId:str):
    try:
      return await send_remoteStartTransaction(charge_point_id,idTag,connectorId)
    except Exception as e:
        raise e
@router.post("/getdiagno/")
async def send_diagno(charge_point_id: str, startTime:datetime,stopTime:datetime,path:str):
   
    try:
        
        return await send_getdiagnostic(charge_point_id, startTime, stopTime, path)
        
    except ValueError:
        return {"error": "Invalid datetime format"}
    
    

@router.get("/graph_conso_energie_status/{id_cp}")
def graph_conso_energie_charge(id_cp:str,session : Session=Depends(get_session),CurrentYear:int = None):
    try:
      return  graph_conso_energie_cp(id_cp,session,CurrentYear)
    except Exception as e:
        raise e

@router.get("/graph_trimestriel_conso_energie_status/{id_cp}")
def graph_trimestriel_conso_energie_charge(id_cp:str,session : Session=Depends(get_session),CurrentYear:int = None):
    try:
      return  graph_trimestriel_conso_energie_cp(id_cp,session,CurrentYear)
    except Exception as e:
        raise e
    
@router.get("/graph_semestriel_conso_energie_status/{id_cp}")
def graph_semestriel_conso_energie_charge(id_cp:str,session : Session=Depends(get_session),CurrentYear:int = None):
    try:
      return  graph_semestriel_conso_energie_cp(id_cp,session,CurrentYear)
    except Exception as e:
        raise e
    



@router.get("/graph_conso_energie/")
def graph_conso_energie_dashboard(session : Session=Depends(get_session),CurrentYear:int = None):
    try:
      return  graph_conso_energie(session,CurrentYear)
    except Exception as e:
        raise e

@router.get("/graph_trimestriel_conso_energie/")
def graph_trimestriel_conso_energie_dashboard(session : Session=Depends(get_session),CurrentYear:int = None):
    try:
      return  graph_trimestriel_conso_energie(session,CurrentYear)
    except Exception as e:
        raise e
    
@router.get("/graph_semestriel_conso_energie/")
def graph_semestriel_conso_energie_dashboard(session : Session=Depends(get_session),CurrentYear:int = None):
    try:
      return  graph_semestriel_conso_energie(session,CurrentYear)
    except Exception as e:
        raise e
    
@router.get("/map_cp/")
def map_charge(session : Session=Depends(get_session)):
    try:
      return  map_cp(session)
    except Exception as e:
        raise e

    

    
