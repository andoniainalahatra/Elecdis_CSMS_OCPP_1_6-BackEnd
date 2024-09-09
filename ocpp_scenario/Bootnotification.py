import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging
from api.CP.CP_services import update_cp
from api.CP.CP_models import Cp_update
from models.elecdis_model import StatusEnum
from core.database import get_session
from sqlalchemy.orm import Session
from fastapi import Depends

logging.basicConfig(level=logging.INFO)

class BootNotification:
        
    @apply_types
    @on(Action.BootNotification)
    async def on_bootnotification(self,charge_point_instance,chargePointVendor, chargePointModel, **kwargs):
        charge_point_id=charge_point_instance.id
        logging.info(f"CPV:{chargePointVendor}+{chargePointModel}+{charge_point_id}")
        charge=Cp_update(charge_point_model=chargePointModel,charge_point_vendors=chargePointVendor,status=StatusEnum.available,time=datetime.now())
        update_cp(charge_point_id,charge,next(get_session()))
        
        return {
            "currentTime":datetime.now().isoformat(),
            "interval":10,
            "status":RegistrationStatus.accepted
        }
    
    