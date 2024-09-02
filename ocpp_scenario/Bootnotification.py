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

class BootNotification:
        
    @apply_types
    @on(Action.BootNotification)
    async def on_bootnotification(self,charge_point_instance,chargePointVendor, chargePointModel, **kwargs):
        logging.info(f"CPV:{chargePointVendor}+{chargePointModel}")
        return {
            "currentTime":datetime.now().isoformat(),
            "interval":10,
            "status":RegistrationStatus.accepted
        }
    
    