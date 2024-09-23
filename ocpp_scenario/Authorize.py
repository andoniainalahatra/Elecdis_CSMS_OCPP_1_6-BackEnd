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
        if tag is None:

            return {
                "idTagInfo":{
                    'status': 'Blocked',
                    'expiryDate': expiry_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                }
            }
        else:
            return {
                "idTagInfo":{
                    'status': 'Accepted',
                    'expiryDate': expiry_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                }
            }



