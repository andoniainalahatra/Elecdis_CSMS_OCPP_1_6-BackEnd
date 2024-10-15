import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging

from core.config import TIME_ZONE
from models.elecdis_model import Rfid_usage_history

logging.basicConfig(level=logging.INFO)
from core.database import get_session
from sqlmodel import Session
from api.RFID.RFID_Services import get_by_tag
from datetime import datetime, timedelta
import pytz

class Authorize:
    @apply_types
    @on(Action.Authorize)
    async def on_authorize(self,charge_point_instance,idTag,**kwargs):
        # check if tag exists in the database
        session : Session = next(get_session())
        tag= get_by_tag(session,idTag)
        timezone = pytz.timezone(TIME_ZONE)
        expiry_date =(datetime.now(timezone) + timedelta(days=2))
        rfid_usage_history = Rfid_usage_history(date=datetime.now(timezone),tag_id=tag.id, action="authorize", session_id=charge_point_instance.id)
        status = "Accepted"
        if tag is None:
            status="Blocked"
        rfid_usage_history.action += f" {status}"
        session.add(rfid_usage_history)
        session.commit()
        return {
            "idTagInfo":{
                'status': status,
                'expiryDate': expiry_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            }
        }

