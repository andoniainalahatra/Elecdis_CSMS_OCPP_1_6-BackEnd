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


class StopTransaction:
        
    @apply_types
    @on(Action.StopTransaction)
    async def on_stoptransaction(self,charge_point_instance,meterStop,timestamp,transactionId,reason, **kwargs):
       logging.info(f"Stop:{meterStop}+{timestamp}+{transactionId}+{reason}")
       return {
            "idTagInfo":{'status':'Accepted'},
        }