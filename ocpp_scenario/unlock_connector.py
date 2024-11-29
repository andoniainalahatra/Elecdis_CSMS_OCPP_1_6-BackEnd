import logging
import uuid
import aio_pika
import json
from fastapi import HTTPException
from core.config import CONNECTION_RABBIT
from pydantic import BaseModel


class UnlockRequest(BaseModel):
    charge_point_id: str
    connector_id: int

class UnlockConnectorService:
    async def unlock_connector(self, charge_point_id: str, connector_id: int):
        unique_id = self.generate_unique_uuid()
        message = json.dumps([
            2,
            unique_id,
            "UnlockConnector",
            {
                "connectorId": connector_id
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
                await exchange.publish(
                    aio_pika.Message(body=json.dumps(response_json).encode()),
                    routing_key="02"
                )
            return {"status": "Message sent", "response": message}
        
        except Exception as e:
            logging.error(f"Failed to send UnlockConnector message: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")

    @staticmethod
    def generate_unique_uuid():
        return str(uuid.uuid4())
