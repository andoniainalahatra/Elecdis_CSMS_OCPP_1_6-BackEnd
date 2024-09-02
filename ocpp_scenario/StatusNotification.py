import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
from ocpp_scenario.Connexion_rabbit import Connexion_rabbit
import logging
logging.basicConfig(level=logging.INFO)

class StatusNotification:
    @apply_types
    @on(Action.StatusNotification)
    async def on_statusnotification(self,charge_point_instance,connectorId,errorCode, status, **kwargs):
        charge_point_id = charge_point_instance.id
        
        # Logs pour débogage
        logging.info(f"ChargePoint ID: {charge_point_id}")
        logging.info(f"Status: ConnectorId={connectorId}, ErrorCode={errorCode}, Status={status}")

        return {}