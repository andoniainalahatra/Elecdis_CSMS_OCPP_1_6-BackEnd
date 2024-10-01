import uuid
import aio_pika
import json
from aio_pika import Message as AioPikaMessage
from fastapi import HTTPException
from core.config import CONNECTION_RABBIT
from ocpp_scenario.reset import ResetMessage


# get configuration keys

class GetConfiguration :
    async def on_get_configuration(self, key: str, charge_point_id):
        unique_id = str(uuid.uuid4())
        message='[2,"'+str(unique_id)+'","GetConfiguration",{"key":["'+key+'"]}]'
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
        return message

    async def change_configuration(self, key: str, value: str, charge_point_id):
        unique_id = str(uuid.uuid4())
        message='[2,"'+str(unique_id)+'","ChangeConfiguration",{"key":"'+key+'","value":"'+value+'"}]'
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
                # await ResetMessage().on_reset_message("Soft", charge_point_id)
                print("lasa any le message ")
                return {"status": "Message sent", "response": message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")
        return message