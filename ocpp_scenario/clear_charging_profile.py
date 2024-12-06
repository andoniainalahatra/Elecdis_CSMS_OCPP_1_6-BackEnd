import logging
from fastapi import HTTPException
import uuid
import aio_pika
import json
from aio_pika import ExchangeType, Message as AioPikaMessage
from core.config import CONNECTION_RABBIT
from pydantic import BaseModel
from typing import Optional


class ClearChargingProfileRequest(BaseModel):
    id: Optional[int] = None
    connector_id: Optional[int] = None
    charging_profile_purpose: Optional[str] = None  # "ChargePointMaxProfile", "TxDefaultProfile", "TxProfile"
    stack_level: Optional[int] = None


class ClearChargingProfileHandler:
    async def on_clear_charging_profile(self, clear_profile_request: ClearChargingProfileRequest, charge_point_id: str):
        unique_id = self.generate_unique_uuid()
        
        # Création du payload en ne incluant que les champs non-None
        payload = {}
        if clear_profile_request.id is not None:
            payload["id"] = clear_profile_request.id
        if clear_profile_request.connector_id is not None:
            payload["connectorId"] = clear_profile_request.connector_id
        if clear_profile_request.charging_profile_purpose is not None:
            payload["chargingProfilePurpose"] = clear_profile_request.charging_profile_purpose
        if clear_profile_request.stack_level is not None:
            payload["stackLevel"] = clear_profile_request.stack_level

        message = f'[2,"{unique_id}","ClearChargingProfile",{json.dumps(payload)}]'
        
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
            return {"status": "Clear charging profile sent", "response": message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send clear charging profile: {e}")

    def generate_unique_uuid(self):
        return str(uuid.uuid4())
