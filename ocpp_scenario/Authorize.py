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

class Authorize:
    @apply_types
    @on(Action.Authorize)
    async def on_authorize(self,charge_point_instance,idTag,**kwargs):
        Idtaglist=["idtag_1","idtag_2","idtag_3"]
        logging.info(f"idTag:{idTag}")
        if idTag in Idtaglist: 
            return {
                "idTagInfo":{
                        'status': 'Accepted',
                        'expiryDate': '2025-12-31T23:59:59Z'  
                    }
            }
        else:
            return {
                "idTagInfo":{
                        'status': 'Blocked',
                        'expiryDate': '2025-12-31T23:59:59Z'  
                    }
            }
        