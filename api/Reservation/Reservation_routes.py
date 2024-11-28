from fastapi import APIRouter
from api.Reservation.Reservation_services import reserve_now,cancel_reservation
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
