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


class StartTransaction:
        
    @apply_types
    @on(Action.StartTransaction)
    async def on_starttransaction(self,charge_point_instance,connectorId,idTag,meterStart,timestamp,**kwargs):
        logging.info(f"Start:{connectorId}+{idTag}+{meterStart}+{timestamp}")
        return {
            "idTagInfo":{'status':'Accepted'},
            "transactionId":0
        }