import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types


class Heartbeat:
    @apply_types
    @on(Action.Heartbeat)
    async def on_heartbeat(self,charge_point_instance,**kwargs):
        return {
            "currentTime":datetime.now().isoformat()
        }
    