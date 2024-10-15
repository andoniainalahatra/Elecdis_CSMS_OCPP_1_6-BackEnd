import asyncio
import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging
from api.CP.CP_services import update_cp_status
from api.Connector.Connector_models import Connector_update
from models.elecdis_model import StatusEnum
from api.Connector.Connector_services import update_connector_status
from api.Connector.Connector_models import Connector_update
from api.CP.CP_services import read_detail_cp
from core.database import get_session
from ocpp_scenario.TriggerMessage import *
logging.basicConfig(level=logging.INFO)
import pytz
from core.config import *
timezone = pytz.timezone(TIME_ZONE)
    
import asyncio
from datetime import datetime, timedelta

class Heartbeat:
    
    
    async def on_heartbeat(self, charge_point_instance, **kwargs):
        charge_point_id = charge_point_instance.id
        session=next(get_session())
        result = read_detail_cp(charge_point_id, session)
        if isinstance(result, list) and len(result) > 0:
            status_charge_point = result[0].get('status_charge_point', None)
            if status_charge_point == StatusEnum.unavailable:
                await TriggerMessage().on_trigger_message('BootNotification',charge_point_id)
                await TriggerMessage().on_trigger_message('StatusNotification',charge_point_id)

                
        return{
            "currentTime": datetime.now(timezone).isoformat()
        }
    
    # async def check_heartbeat_timeouts(self):
  
    #     while True:
    #         current_time = datetime.now()
    #         for charge_point_id, last_heartbeat in list(self.last_heartbeat_times.items()):
    #             elapsed_time = (current_time - last_heartbeat).total_seconds()
    #             timeout_duration_seconds = self.timeout_duration.total_seconds()

    #             logging.debug(f"Current time: {current_time}, Last heartbeat: {last_heartbeat}, Elapsed time: {elapsed_time}")


    #             # Check if elapsed time since last heartbeat is greater than the timeout duration
    #             if elapsed_time > timeout_duration_seconds:
    #                 with next(get_session()) as session:
    #                     result = read_detail_cp(charge_point_id, session)
    #                     charging_connector_exists = any(row['status_connector'] == StatusEnum.charging for row in result)

    #                     if charging_connector_exists:
    #                         logging.info(f"Charge Point {charge_point_id} is charging. Status update ignored.")
    #                     else:
    #                         cpp = Cp_update(status=StatusEnum.unavailable, time=current_time)
    #                         update_cp_status(charge_point_id, cpp, session)

    #                         conne = Connector_update(status=StatusEnum.unavailable, time=last_heartbeat)
    #                         for row in result:
    #                             update_connector_status(row['id_connecteur'], conne, session)

    #                         logging.info(f"No heartbeat received from Charge Point {charge_point_id} in {elapsed_time}. Last received at {last_heartbeat}")
    #                         del self.last_heartbeat_times[charge_point_id]

    #         # Ensure the check runs at the correct inter
    #         await asyncio.sleep(self.check_interval)
 
    
    # async def _heartbeat_timer(self, charge_point_id):
    #     await asyncio.sleep(self.time_limit)
    #     # Check the number of heartbeats received
    #     current_count = self.heartbeat_counts.get(charge_point_id, 0)
    #     if current_count< 2:
    #         logging.info(f"Pas assez de Heartbeat {charge_point_id} +{self.heartbeat_counts.get(charge_point_id)}")
    #         self.heartbeat_counts[charge_point_id] = 0
    #     else:
    #         logging.info(f"Heartbeat suffisant {charge_point_id}+{self.heartbeat_counts.get(charge_point_id)} ")
    #         self.heartbeat_counts[charge_point_id] = 0

    #     # Remove the timer
    #     self.timers.pop(charge_point_id, None)
    #     self.timers[charge_point_id] = asyncio.create_task(self._heartbeat_timer(charge_point_id))

   







        
