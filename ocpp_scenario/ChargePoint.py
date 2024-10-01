import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
import logging
from models.elecdis_model import StatusEnum
from ocpp.exceptions import OCPPError
from datetime import datetime, timedelta
logging.basicConfig(level=logging.INFO)
from api.CP.CP_services import update_cp_status
from api.CP.CP_models import Cp_update
from api.Connector.Connector_services import update_connector_status
from api.Connector.Connector_models import Connector_update
from api.CP.CP_services import read_detail_cp
from core.database import get_session
import pytz
from core.config import *
timezone = pytz.timezone(TIME_ZONE)
class ChargePoint(cp):
    instances = {}  

    def __new__(cls, charge_point_id, *args, **kwargs):
        if charge_point_id not in cls.instances:
            instance = super(ChargePoint, cls).__new__(cls)
            cls.instances[charge_point_id] = instance
        return cls.instances[charge_point_id]

    def __init__(self, charge_point_id, connection, boot_notification_scenario, heartbeat_scenario,
                 statusnotification_scenario, start_scenario, stop_scenario, authorize, meter_value_scenario):
        if not hasattr(self, 'initialized'): 
            super().__init__(charge_point_id, connection)
            self.boot_notification_scenario = boot_notification_scenario
            self.heartbeat_scenario = heartbeat_scenario
            self.statusnotification_scenario = statusnotification_scenario
            self.start_scenario = start_scenario
            self.stop_scenario = stop_scenario
            self.authorize = authorize
            self.meter_value_scenario = meter_value_scenario

           
            self.heartbeat_count = 0
            self.min_heartbeats = int(MIN_HEARTBEAT)
            self.time=self.min_heartbeats*int(HEARTBEAT_INTERVAL)
            self.timeout = timedelta(seconds=self.time)
            self.monitoring_task = None
            self.lock = asyncio.Lock()
            self.last_heartbeat_time = datetime.now()

            self.initialized = True

    #@on(Action.BootNotification)
    async def on_bootnotification(self,chargePointVendor,chargePointModel,**kwargs):
        return await self.boot_notification_scenario.on_bootnotification(self,chargePointVendor, chargePointModel, **kwargs)
    
    #@on(Action.Heartbeat)
    async def on_heartbeat(self, **kwargs):
        async with self.lock:
            self.heartbeat_count += 1
            self.last_heartbeat_time = datetime.now()
            logging.info(f"Heartbeat received for {self.id}. Count: {self.heartbeat_count}")
            if self.monitoring_task is None:
                self.monitoring_task = asyncio.create_task(self.monitor_heartbeats())

        return await self.heartbeat_scenario.on_heartbeat(self, **kwargs)

    async def monitor_heartbeats(self):
        while True:
            await asyncio.sleep(self.time+62)  
            async with self.lock:
                elapsed_time = datetime.now() - self.last_heartbeat_time
                if self.heartbeat_count >= self.min_heartbeats:
                    logging.info(f"Received sufficient heartbeats for {self.id}: {self.heartbeat_count}. Resetting count for next period.")
                    self.heartbeat_count = 0  
                else:
                    logging.warning(f"Less than 2 heartbeats received in 102 seconds for {self.id}. Sending stop message.")
                    await self.stop_charge_point()
                    self.heartbeat_count = 0
                    break  #

            
        self.monitoring_task = None




    async def stop_charge_point(self):
        session=next(get_session())
        try:
            charge=Cp_update(status=StatusEnum.unavailable,time=datetime.now())
            update_cp_status(id_cp=self.id,cp=charge,session=session)
            result = read_detail_cp(self.id, session)
            conne=Connector_update(status=StatusEnum.unavailable,time=datetime.now()+timedelta(hours=3))
            for row in result:
                update_connector_status(row['id_connecteur'], conne, session)
            
        except Exception as e:
            session.rollback() 
            logging.error(f"rollback: {e}")
        
    
    #@on(Action.StatusNotification)
    async def on_statusnotification(self, connectorId, errorCode, status, **kwargs):
        return await self.statusnotification_scenario.on_statusnotification(self,connectorId, errorCode, status, **kwargs)
    #@on(Action.StartTransaction)
    async def on_starttransaction(self, connectorId, idTag, meterStart,timestamp,**kwargs):
        return await self.start_scenario.on_starttransaction(self,connectorId, idTag, meterStart,timestamp, **kwargs)
    #@on(Action.StopTransaction)
    async def on_stoptransaction(self, meterStop, timestamp, transactionId,reason,**kwargs):
        return await self.stop_scenario.on_stoptransaction(self,meterStop, timestamp, transactionId, reason,**kwargs)
    #@on(Action.Authorize)
    async def on_authorize(self, idTag,**kwargs):
        return await self.authorize.on_authorize(self,idTag, **kwargs)
    #@on(Action.MeterValues)
    async def on_metervalues(self, connectorId,meterValue,**kwargs):
        return await self.meter_value_scenario.on_metervalues(self,connectorId,meterValue, **kwargs)
    
    async def process_message(self, action, payload):
        """Process OCPP message dynamically based on action"""
        handler = getattr(self,f'on_{action.lower()}', None)
        if handler:
            return await handler(**payload) 
        else:
            raise OCPPError(
                "NotImplemented",
                "This action is not supported by the Charge Point."
            )
    
    