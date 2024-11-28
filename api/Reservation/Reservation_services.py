from ocpp_scenario.ReserveNow import ReserveNow
from ocpp_scenario.CancelReservation import CancelReservation
import aio_pika
from aio_pika import Message as AioPikaMessage
from core.config import *
from core.utils import *
import json
from fastapi import HTTPException
async def reserve_now(connectorId:int,idTag:str,reservationId:int,charge_point_id:str):
    reserve=ReserveNow()
    message = reserve.on_reserveNow(connectorId,idTag,reservationId)
    response_json = {
        "charge_point_id": charge_point_id,
        "payload": message
    }
        
    try:
        connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.get_exchange("micro_ocpp") 
            await exchange.publish(
                AioPikaMessage(body=json.dumps(response_json).encode()),
                routing_key="02"
            )
        return {"status": "Message sent", "response": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")
    
async def cancel_reservation(reservationId:int,charge_point_id:str):
    cancel=CancelReservation()
    message = cancel.on_cancelReservation(reservationId)
    response_json = {
        "charge_point_id": charge_point_id,
        "payload": message
    }
        
    try:
        connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.get_exchange("micro_ocpp") 
            await exchange.publish(
                AioPikaMessage(body=json.dumps(response_json).encode()),
                routing_key="02"
            )
        return {"status": "Message sent", "response": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")
