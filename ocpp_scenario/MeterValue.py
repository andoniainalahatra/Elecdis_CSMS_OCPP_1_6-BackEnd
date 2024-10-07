import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging
logging.basicConfig(level=logging.INFO)

class MeterValue:
        
    @apply_types
    @on(Action.MeterValues)
    async def on_metervalues(self,charge_point_instance,connectorId,meterValue,**kwargs):
        logging.info(f"MV:{connectorId}+{meterValue}+{charge_point_instance}")
        return {}

