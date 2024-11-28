import logging
from fastapi import HTTPException
import uuid

import json
from aio_pika import ExchangeType, Message as AioPikaMessage
from pydantic import BaseModel
from core.config import CONNECTION_RABBIT 

# Assurez-vous que cette configuration est correcte
class DataTransferRequest(BaseModel):
    vendor_id: str
    message_id: str
    data: dict
    charge_point_id: str
    
class DataTransfer:
    async def on_data_transfer(self, vendor_id: str, message_id: str, data: dict, charge_point_id: str):
        unique_id = self.generate_unique_uuid()
        # Construction du message DataTransfer
        message = json.dumps([
            2,
            unique_id,
            "DataTransfer",
            {
                "vendorId": vendor_id,
                "messageId": message_id,
                "data": data
            }
        ])
        
        response_json = {
            "charge_point_id": charge_point_id,
            "payload": message
        }
        
        try:
            # Connexion à RabbitMQ
            connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
            async with connection:
                channel = await connection.channel()
                exchange = await channel.get_exchange("micro_ocpp")
                # Publication du message
                await exchange.publish(
                    AioPikaMessage(body=json.dumps(response_json).encode()),
                    routing_key="data_transfer"
                )
            return {"status": "Message sent", "response": message}
        
        except Exception as e:
            logging.error(f"Failed to send DataTransfer message: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")

    @staticmethod
    def generate_unique_uuid():
        return str(uuid.uuid4())
