from ocpp.v16 import call_result
from ocpp.v16.enums import ClearChargingProfileStatus
from ocpp.routing import on

class ClearChargingProfileHandler:
    
    @on('ClearChargingProfile')
    async def on_clear_charging_profile(self, **kwargs):
        # Logique pour effacer le profil de recharge
        return call_result.ClearChargingProfilePayload(
            status=ClearChargingProfileStatus.accepted
        )
