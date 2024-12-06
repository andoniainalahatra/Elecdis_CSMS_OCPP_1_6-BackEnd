import logging
from fastapi import HTTPException
import uuid
import aio_pika
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
        logging.info(f"Démarrage du transfert de données pour la borne {charge_point_id}")
        logging.debug(f"Paramètres reçus - vendor_id: {vendor_id}, message_id: {message_id}, data: {data}")
        
        unique_id = self.generate_unique_uuid()
        logging.debug(f"UUID généré: {unique_id}")

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
        logging.debug(f"Message OCPP construit: {message}")
        
        response_json = {
            "charge_point_id": charge_point_id,
            "payload": message
        }
        logging.debug(f"Payload RabbitMQ préparé: {response_json}")
        
        try:
            logging.info("Tentative de connexion à RabbitMQ...")
            connection = await aio_pika.connect_robust(CONNECTION_RABBIT)
            async with connection:
                logging.debug("Connexion RabbitMQ établie")
                channel = await connection.channel()
                exchange = await channel.get_exchange("micro_ocpp")
                logging.debug("Canal et exchange RabbitMQ configurés")

                # Publication du message
                await exchange.publish(
                    AioPikaMessage(body=json.dumps(response_json).encode()),
                    routing_key="02"
                )
                logging.info(f"Message publié avec succès dans RabbitMQ pour la borne {charge_point_id}")
            return {"status": "Message sent", "response": message}
        
        except Exception as e:
            error_msg = f"Échec de l'envoi du message DataTransfer pour la borne {charge_point_id}: {str(e)}"
            logging.error(error_msg)
            logging.exception("Détails de l'erreur:")
            raise HTTPException(status_code=500, detail=error_msg)

    @staticmethod
    def generate_unique_uuid():
        return str(uuid.uuid4())
