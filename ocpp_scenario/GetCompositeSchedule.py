# [2,"3786718","ChangeAvailability",{"connectorId":0,"type":"Inoperative"}]
import uuid
import json
from aio_pika import Message as AioPikaMessage, connect_robust
from fastapi import HTTPException
from core.config import CONNECTION_RABBIT

class GetCompositeSchedule:
    async def get_composite_schedule(self, duration: int,chargingRateUnit:str, connectorId: str, charge_point_id):
        unique_id = str(uuid.uuid4())
        du = str(duration)
        message='[2,"'+str(unique_id)+'","GetCompositeSchedule",{"connectorId":'+connectorId+',"duration":'+ du+',"chargingRateUnit":"'+chargingRateUnit+'"}]]'
        response_json = {
            "charge_point_id": charge_point_id,
            "payload": message
        }
        try:
            connection = await connect_robust(CONNECTION_RABBIT)
            async with connection:
                channel = await connection.channel()
                exchange = await channel.get_exchange("micro_ocpp")
                await exchange.publish(
                    AioPikaMessage(body=json.dumps(response_json).encode()),
                    routing_key="02"
                )
                # await ResetMessage().on_reset_message("Soft", charge_point_id)
                return {"status": "Message sent", "response": message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")
        return message