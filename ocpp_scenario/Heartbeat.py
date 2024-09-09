import asyncio
import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging
from api.CP.CP_models import Cp_update
from api.CP.CP_services import update_cp
from api.Connector.Connector_models import Connector_update
from api.Connector.Connector_services import update_connector
from models.elecdis_model import StatusEnum
from core.database import get_session
logging.basicConfig(level=logging.INFO)

# class Heartbeat:
#     @apply_types
#     @on(Action.Heartbeat)
#     async def on_heartbeat(self,charge_point_instance,**kwargs):
#         charge_point_id = charge_point_instance.id
#         return {
#             "currentTime":datetime.now().isoformat()
#         }
    
import asyncio
from datetime import datetime, timedelta

class Heartbeat:
    def __init__(self):
        self.last_heartbeat_times = {}
        self.check_interval = 10
    
    async def on_heartbeat(self, charge_point_instance, **kwargs):
        charge_point_id = charge_point_instance.id
        self.last_heartbeat_times[charge_point_id] = datetime.now()
        return {
            "currentTime": datetime.now().isoformat()
        }
    
    async def check_heartbeat_timeouts(self):
        """Vérifie en continu les délais d'expiration des heartbeats toutes les 10 secondes."""
        while True:
            current_time = datetime.now()
            for charge_point_id, last_heartbeat in list(self.last_heartbeat_times.items()):
                logging.info(f"heartbeat reçu du Point de Charge {charge_point_id} dans les 10 dernières secondes. Dernier reçu à {last_heartbeat}")
                if current_time - last_heartbeat > timedelta(seconds=self.check_interval):
                    session=next(get_session())
                    cpp=Cp_update(charge_point_vendors="null",charge_point_model="null",status=StatusEnum.unavailable,time=current_time)
                    update_cp(charge_point_id,cpp,session)
                    logging.info(f"Pas de heartbeat reçu du Point de Charge {charge_point_id} dans les 10 dernières secondes. Dernier reçu à {last_heartbeat}")
                    del self.last_heartbeat_times[charge_point_id]
                    
            await asyncio.sleep(self.check_interval)

    async def start(self):
        asyncio.create_task(self.check_heartbeat_timeouts())
