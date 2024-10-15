import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
from api.transaction.Transaction_models import  Session_create
from api.transaction.Transaction_service import create_session_service
import logging

from core.database import get_session

logging.basicConfig(level=logging.INFO)


class StartTransaction:
        
    @apply_types
    @on(Action.StartTransaction)
    async def on_starttransaction(self,charge_point_instance,connectorId,idTag,meterStart,timestamp,**kwargs):
        # get user that corresponds to the tag
        try:
            session_data = Session_create(
                start_time=timestamp,
                connector_id=f"{connectorId}{charge_point_instance.id}",
                user_tag=idTag,
                metter_start=meterStart)
            transaction= create_session_service( session=next(get_session()), session_data=session_data)
        except Exception as e:
            logging.error(f"Error:{e}")
            return {
                "idTagInfo":{'status':'Rejected'},
            }
        logging.info(f"Start:{connectorId}+{idTag}+{meterStart}+{timestamp}")
        return {
            "idTagInfo":{'status':'Accepted'},
            "transactionId":transaction.id
        }