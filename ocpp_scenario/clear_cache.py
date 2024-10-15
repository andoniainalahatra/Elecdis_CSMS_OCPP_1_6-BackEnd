from ocpp.v16 import call_result
from ocpp.v16.enums import ClearCacheStatus
from ocpp.routing import on

class ClearCacheHandler:
    
    @on('ClearCache')
    async def on_clear_cache(self):
        # Logique pour vider le cache de la station de recharge
        return call_result.ClearCachePayload(
            status=ClearCacheStatus.accepted
        )
