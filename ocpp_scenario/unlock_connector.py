from ocpp.v16 import call_result
from ocpp.v16.enums import UnlockStatus
from ocpp.routing import on

class UnlockConnectorHandler:
    
    @on('UnlockConnector')
    async def on_unlock_connector(self, connector_id):
        # Logique pour débloquer un connecteur
        return call_result.UnlockConnectorPayload(
            status=UnlockStatus.unlocked
        )
