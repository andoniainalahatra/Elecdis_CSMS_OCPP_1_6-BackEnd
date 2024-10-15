import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging
from api.CP.CP_services import update_cp_boot,create_cp,read_cp
from api.CP.CP_models import Cp_update,Cp_create
from models.elecdis_model import StatusEnum
from core.database import get_session
from sqlalchemy.orm import Session
from fastapi import Depends
import pytz
from core.config import *
timezone = pytz.timezone(TIME_ZONE)

class BootNotification:
        
    @apply_types
    @on(Action.BootNotification)
    async def on_bootnotification(self,charge_point_instance,chargePointVendor, chargePointModel, **kwargs):
        charge_point_id=charge_point_instance.id
        session=next(get_session())
        try:
            result=read_cp(session)
            data = result.get('data', [])
            existing_cp = [row['id'] for row in data if isinstance(row, dict)]
            #logging.info(f"CPV:{chargePointVendor}+{chargePointModel}+{charge_point_id}")
            if(charge_point_id not in existing_cp):
                charge=Cp_create(id=charge_point_id,serial_number=charge_point_id,charge_point_model=chargePointModel,charge_point_vendors=chargePointVendor,status=StatusEnum.available,adresse="Andraharo",longitude=0,latitude=0,firmware_version=kwargs.get("firmwareVersion"))
                create_cp(charge,session)
            else:
                charge=Cp_update(charge_point_model=chargePointModel,charge_point_vendors=chargePointVendor,status=StatusEnum.available,time=datetime.now(),firmware_version=kwargs.get("firmwareVersion"))
                update_cp_boot(charge_point_id,charge,session)
        except Exception as e:
           session.rollback() 
           logging.error(f"rollback: {e}") 
        return {
            "currentTime":datetime.now(timezone).isoformat(),
            "interval":int(HEARTBEAT_INTERVAL),
            "status":RegistrationStatus.accepted
        }
    
    