import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging

from api.userCredit.UserCredit_services import check_if_has_credit
from core.config import TIME_ZONE
from models.elecdis_model import Rfid_usage_history
from api.Reservation.Reservation_services import create_history_reservation,create_history,check_reservation,update_reservation_etat

logging.basicConfig(level=logging.INFO)
from core.database import get_session
from sqlmodel import Session
from api.RFID.RFID_Services import get_by_tag, check_if_user_should_use_credit
from datetime import datetime, timedelta
import pytz

class Authorize:
    @apply_types
    @on(Action.Authorize)
    async def on_authorize(self,charge_point_instance,idTag,**kwargs):
        charge_point_id=charge_point_instance.id
        # check if tag exists in the database
        session : Session = next(get_session())

        tag= get_by_tag(session,idTag)
        timezone = pytz.timezone(TIME_ZONE)

        expiry_date =(datetime.now(timezone) + timedelta(days=2))

        rfid_usage_history = Rfid_usage_history(date=datetime.now(timezone), action="authorize")
        status = "Accepted"
        reason=""
        if tag is None:
            status="Blocked"
            return {
                "idTagInfo":{
                    'status': status,
                    'expiryDate': expiry_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                }
            }
        # check subscription if type credit we do the function bellow else : we go ahead
        if check_if_user_should_use_credit(session,idTag):
            if not check_if_has_credit(session,tag.id):
                status="Blocked"
                reason="Not enough credit"
        date_obj = datetime.now(timezone) 
        date_without_ms = date_obj.replace(microsecond=0)
        formatted_date = date_without_ms.replace(tzinfo=None)
        reservation=check_reservation(date_utilisation=formatted_date,tag=idTag,charge_point_id=charge_point_id,session=session)
        logging.error(f"Résultat de check_reservation: {formatted_date}")
        if reservation: 
            if reservation.get("is_reserved") is True:
                val=create_history_reservation(tag_id=tag.id,date_utilisation=formatted_date,connector_id=reservation.get("connector_id"),etat=1)
                create_history(val,session)
                update_reservation_etat(2,session)
            else:
                status="Blocked"
                reason=reservation.get("status")
                val=create_history_reservation(tag_id=tag.id,date_utilisation=formatted_date,connector_id=reservation.get("connector_id"),etat=0)
                create_history(val,session)
                       
        rfid_usage_history.action += f" {status} : {reason}"
        rfid_usage_history.tag_id = tag.id
        session.add(rfid_usage_history)
        session.commit()
        return {
            "idTagInfo":{
                'status': status,
                'expiryDate': expiry_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            }
        }

