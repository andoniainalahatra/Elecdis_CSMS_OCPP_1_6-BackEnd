from fastapi import APIRouter,Depends
from api.Reservation.Reservation_services import reserve_now,cancel_reservation,create_reservation,create_history,take_reservation,take_user_match_with_tag,check_reservation,take_history_match_with_reservation,check_reservation_api,update_reservation_etat,update_history_etat,get_reservation_by_date,get_reservation_reserve_now
from core.database import get_session
from sqlalchemy.orm import Session
from api.Reservation.Resercation_models import reservation_create,data_history_reservation,create_history_reservation
from datetime import date, datetime,timedelta


router = APIRouter()
@router.post("/reserveNow")
async def reserveNow(connectorId:int,idTag:str,reservationId:int,charge_point_id:str):
    try:
      return await reserve_now(connectorId,idTag,reservationId,charge_point_id)
    except Exception as e:
        raise e
@router.post("/cancelReservation")
async def cancelReservation(reservationId:int,charge_point_id:str):
    try:
      return await cancel_reservation(reservationId,charge_point_id)
    except Exception as e:
        raise e

@router.post("/create_reservation")
def createReservation(reserve:reservation_create, session:Session=Depends(get_session)):
  try:
      return  create_reservation(reserve,session)
  except Exception as e:
        raise e
  
@router.post("/create_history")
def createHistory(reserve:create_history_reservation, session:Session=Depends(get_session)):
  try:
      return  create_history(reserve,session)
  except Exception as e:
        raise e
  
@router.get("/take_reservation")
def TakeReservation(charge_point_id: str, date_utilisation: datetime, session:Session=Depends(get_session)):
  try:
      return  take_reservation(charge_point_id,date_utilisation,session)
  except Exception as e:
        raise e
  
@router.get("/take_user_match_with_tag")
def takeUserMatchWithTag(tags:str, session:Session=Depends(get_session)):
  try:
      return  take_user_match_with_tag(tags,session)
  except Exception as e:
        raise e
  
@router.get("/check_reservation")
def checkReservation(date_utilisation:datetime,tag:str,charge_point_id:str, session:Session=Depends(get_session)):
  try:
      return  check_reservation(date_utilisation,tag,charge_point_id,session)
  except Exception as e:
        raise e
  
@router.get("/take_history_match_with_reservation")
def takeHistoryMatchWithReservation(date_reservation:datetime,expirate_date:datetime,connector_id:str,session:Session=Depends(get_session)):
  try:
      return  take_history_match_with_reservation(date_reservation,expirate_date,connector_id,session)
  except Exception as e:
        raise e
  
@router.get("/check_reservation_api")
def checkReservation_api(session:Session=Depends(get_session),page: int = 1, number_items: int = 50):
  try:
      return  check_reservation_api(session,page,number_items)
  except Exception as e:
        raise e
  
@router.get("/get_reservation_by_date")
def getReservation_by_date(id_cp:str = None,day:date = None,session:Session=Depends(get_session),page: int = 1, number_items: int = 50):
  try:
      return  get_reservation_by_date(id_cp,day,session,page,number_items)
  except Exception as e:
        raise e
  

@router.put("/update_reservation_etat")
def updateReservation_etat(reservation_id:int,session:Session=Depends(get_session)):
  try:
      return  update_reservation_etat(reservation_id,session)
  except Exception as e:
        raise e
  
@router.put("/update_history_etat")
def updateHistory_etat(history_id:int,session:Session=Depends(get_session)):
  try:
      return  update_history_etat(history_id,session)
  except Exception as e:
        raise e
  

@router.get("/get_reservation_reserve_now")
def getReservation_reserve_now(session:Session=Depends(get_session),page: int = 1, number_items: int = 50):
  try:
      return  get_reservation_reserve_now(session,page,number_items)
  except Exception as e:
        raise e
