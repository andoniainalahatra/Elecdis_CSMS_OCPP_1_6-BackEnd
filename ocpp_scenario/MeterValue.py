import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
from core.database import meter_values_collection
import logging
logging.basicConfig(level=logging.INFO)

class MeterValue:
        
    @apply_types
    @on(Action.MeterValues)
    async def on_metervalues(self,charge_point_instance,connectorId,meterValue,**kwargs):
        #new_meter_value = await meter_values_collection.insert_one(meter_values_request.dict(by_alias=True))
        meter_values_data = {
            "connector_id": connectorId,
            "meter_value": meterValue
        }

        await meter_values_collection.insert_one(meter_values_data)
        #logging.info(f"MV:{connectorId}+{meterValue}")
        logging.info(f"MeterValues inserted: {meter_values_data}")
        return {}