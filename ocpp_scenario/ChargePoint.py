import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
import logging
from ocpp.exceptions import OCPPError
logging.basicConfig(level=logging.INFO)
class ChargePoint(cp):
    def __init__(self,charge_point_id,connection,boot_notification_scenario,heartbeat_scenario,statusnotification_scenario,start_scenario,stop_scenario,authorize,meter_value_scenario):
        super().__init__(charge_point_id,connection)
        self.boot_notification_scenario = boot_notification_scenario
        self.heartbeat_scenario=heartbeat_scenario
        self.statusnotification_scenario=statusnotification_scenario
        self.start_scenario=start_scenario
        self.stop_scenario=stop_scenario
        self.authorize=authorize
        self.meter_value_scenario=meter_value_scenario
    
        

    #@on(Action.BootNotification)
    async def on_bootnotification(self,chargePointVendor,chargePointModel,**kwargs):
        return await self.boot_notification_scenario.on_bootnotification(self,chargePointVendor, chargePointModel, **kwargs)
    
    #@on(Action.Heartbeat)
    async def on_heartbeat(self,**kwargs):
        return  await self.heartbeat_scenario.on_heartbeat(self,**kwargs)
    
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
    
    