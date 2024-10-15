import asyncio
import websockets
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result
from propan import apply_types
from ocpp_scenario.Connexion_rabbit import Connexion_rabbit
import logging
from api.Connector.Connector_services import create_connector,update_connector_status
from api.Connector.Connector_models import Connector_create,Connector_update
from api.CP.CP_services import read_detail_cp,read_detail_cp_update
from core.database import get_session

logging.basicConfig(level=logging.INFO)

class StatusNotification:
    @apply_types
    @on(Action.StatusNotification)
    async def on_statusnotification(self,charge_point_instance,connectorId,errorCode, status, **kwargs):
        charge_point_id = charge_point_instance.id
        session=next(get_session())
        try:
            result=read_detail_cp_update(charge_point_id,session)
            existing_connectors = [row['id_connecteur'] for row in result]
            #logging.info(f"ChargePoint ID: {charge_point_id}")
            #logging.info(existing_connectors)
            if f"{connectorId}{charge_point_id}" not in existing_connectors :
                #logging.info(f"Status: ConnectorId={connectorId}, ErrorCode={errorCode}, Status={status}")
                conne=Connector_create(id=f"{connectorId}{charge_point_id}",connector_type="evse",connector_id=0,charge_point_id=charge_point_id,status=status,valeur=0)
                create_connector(conne,session)
            else:
                conne=Connector_update(status=status,time=kwargs.get('timestamp'))
                update_connector_status(f"{connectorId}{charge_point_id}",conne,session)

            session.commit()
        except Exception as e:
           session.rollback() 
           logging.error(f"rollback:{e}") 

        return {}