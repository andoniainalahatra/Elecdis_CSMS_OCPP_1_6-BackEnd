import logging
from fastapi import HTTPException
import uuid
import aio_pika
import json
from aio_pika import ExchangeType, Message as AioPikaMessage
from core.config import CONNECTION_RABBIT

class ResetMessage:
    async def on_reset_message(self, reset_type: str, charge_point_id: str):
        unique_id = generate_unique_uuid()
        message = f'[2,"{unique_id}","Reset",{{"type":"{reset_type}"}}]'
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
            return {"status": "Reset command sent", "response": message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send Reset message: {e}")

def generate_unique_uuid():
    return str(uuid.uuid4())
