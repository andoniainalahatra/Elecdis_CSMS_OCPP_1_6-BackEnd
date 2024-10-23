import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging

from api.tarifs.Tarifs_services import manage_tarif_snapshots_on_meter_values
from api.transaction.Transaction_service import create_metervalue_from_mvdata
from core.database import get_session

logging.basicConfig(level=logging.INFO)


class MeterValue:
    @apply_types
    @on(Action.MeterValues)
    async def on_metervalues(self,charge_point_instance,connectorId,meterValue,**kwargs):
        # logging.info(f"======{kwargs.get('transactionId')}======>>>>>>>>>:{meterValue} ")
        session_db=next(get_session())
        meter= create_metervalue_from_mvdata(mvdata=meterValue[0].get('sampledValue'),connectorId=connectorId,transactionId=int(kwargs.get('transactionId')),dateMeter= datetime.strptime(meterValue[0].get('timestamp'), "%Y-%m-%dT%H:%M:%S.%fZ"))
        manage_tarif_snapshots_on_meter_values(meter, session_db,logging)
        session_db.commit()
        return {}

