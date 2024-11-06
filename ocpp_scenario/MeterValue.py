import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
import logging

from api.RFID.RFID_Services import get_by_tag
from api.tarifs.Tarifs_services import manage_tarif_snapshots_on_meter_values
from api.transaction.Transaction_service import create_metervalue_from_mvdata, stop_transactions_on_sold_out, \
    get_session_by_id
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
        session = get_session_by_id(session_db,meter.transactionId)
        tag=get_by_tag(session_db,session.tag)
        await stop_transactions_on_sold_out(session_db, tag.id, meter.transactionId, meter.metervalue,charge_point_instance)
        session_db.commit()
        return {}

