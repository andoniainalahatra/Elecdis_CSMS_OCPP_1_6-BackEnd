import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging

from api.transaction.Transaction_models import Session_update
from api.transaction.Transaction_service import update_session_service_on_stopTransaction
from core.database import get_session

logging.basicConfig(level=logging.INFO)


class StopTransaction:
        
    @apply_types
    @on(Action.StopTransaction)
    async def on_stoptransaction(self,meterStop,timestamp,transactionId,reason, **kwargs):
       logging.info(f"Stop:{meterStop}+{timestamp}+{transactionId}+{reason}")
       session_update_data = Session_update(
              end_time=timestamp,
              metter_stop=meterStop,
              transaction_id=transactionId,
              reason=reason
       )
       transaction= update_session_service_on_stopTransaction(session=next(get_session()), session_data=session_update_data)
       return {
            "idTagInfo":{'status':'Accepted'},
        }