import logging
from fastapi import HTTPException
import uuid
import aio_pika
import json
from aio_pika import ExchangeType, Message as AioPikaMessage
from core.config import CONNECTION_RABBIT



class UpdateFirmwareMessage:
    async def on_update_firmware(self, firmware_url: str, retrieve_date: str, retries: int, retry_interval: int, charge_point_id: str):
        unique_id = generate_unique_uuid()
        message = f'[2,"{unique_id}","UpdateFirmware",{{"location":"{firmware_url}","retrieveDate":"{retrieve_date}","retries":{retries},"retryInterval":{retry_interval}}}]'
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
            return {"status": "Firmware update message sent", "response": message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send Update Firmware message: {e}")

def generate_unique_uuid():
    return str(uuid.uuid4())
