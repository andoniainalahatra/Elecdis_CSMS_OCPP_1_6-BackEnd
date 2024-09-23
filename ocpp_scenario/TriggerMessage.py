# [2,\"51754620-bdb9-4d44-899d-5b6cef63273a\",\"TriggerMessage\",{\"requestedMessage\":\"MeterValues\"}]
import logging
from fastapi import HTTPException
import uuid
import aio_pika
import json
from aio_pika import ExchangeType, Message as AioPikaMessage,IncomingMessage

from core.config import CONNECTION_RABBIT


class TriggerMessage:
    async def  on_trigger_message(self, requested_message: str, charge_point_id):
        unique_id = generate_unique_uuid()
        message='[2,"'+str(unique_id)+'","TriggerMessage",{ "requestedMessage":"'+requested_message+'"}]'
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
def generate_unique_uuid():
    return str(uuid.uuid4())