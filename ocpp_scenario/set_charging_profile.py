import logging
from fastapi import HTTPException
import uuid
import aio_pika
import json
from datetime import datetime
from aio_pika import ExchangeType, Message as AioPikaMessage
from core.config import CONNECTION_RABBIT
from pydantic import BaseModel
from typing import List, Optional

class SetChargingProfileHandler:
    
    async def on_set_charging_profile(self, connector_id, cs_charging_profiles, charge_point_id):
        unique_id = self.generate_unique_uuid()
        
        # Convertir les dates en format ISO string avant la sérialisation JSON
        if isinstance(cs_charging_profiles, dict):
            if 'chargingSchedule' in cs_charging_profiles:
                if 'startSchedule' in cs_charging_profiles['chargingSchedule']:
                    start_schedule = cs_charging_profiles['chargingSchedule']['startSchedule']
                    if isinstance(start_schedule, datetime):
                        cs_charging_profiles['chargingSchedule']['startSchedule'] = start_schedule.isoformat()

            if 'validFrom' in cs_charging_profiles:
                valid_from = cs_charging_profiles['validFrom']
                if isinstance(valid_from, datetime):
                    cs_charging_profiles['validFrom'] = valid_from.isoformat()

            if 'validTo' in cs_charging_profiles:
                valid_to = cs_charging_profiles['validTo']
                if isinstance(valid_to, datetime):
                    cs_charging_profiles['validTo'] = valid_to.isoformat()

        message = f'[2,"{unique_id}","SetChargingProfile",{{"connectorId":{connector_id},"csChargingProfiles":{json.dumps(cs_charging_profiles)}}}]'
        
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
            return {"status": "Charging profile sent", "response": message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send charging profile: {str(e)}")

    def generate_unique_uuid(self):
        return str(uuid.uuid4())



class ChargingSchedulePeriod(BaseModel):
    startPeriod: int
    limit: float
    numberPhases: Optional[int] = None

class ChargingSchedule(BaseModel):
    duration: Optional[int] = None
    startSchedule: Optional[datetime] = None
    chargingRateUnit: str  # "W" ou "A"
    chargingSchedulePeriod: List[ChargingSchedulePeriod]
    minChargingRate: Optional[float] = None

class ChargingProfile(BaseModel):
    chargingProfileId: int
    transactionId: Optional[int] = None
    stackLevel: int
    chargingProfilePurpose: str  # "ChargePointMaxProfile", "TxDefaultProfile", "TxProfile"
    chargingProfileKind: str  # "Absolute", "Recurring", "Relative"
    recurrencyKind: Optional[str] = None  # "Daily", "Weekly"
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    chargingSchedule: ChargingSchedule

class SetChargingProfileRequest(BaseModel):
    connector_id: int
    cs_charging_profiles: ChargingProfile