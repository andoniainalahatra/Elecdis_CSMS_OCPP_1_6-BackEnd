from ocpp.v16 import call_result
from ocpp.v16.enums import ChargingProfileStatus
from ocpp.routing import on

class SetChargingProfileHandler:
    
    @on('SetChargingProfile')
    async def on_set_charging_profile(self, connector_id, cs_charging_profiles):
        # Logique pour définir un profil de recharge
        return call_result.SetChargingProfilePayload(
            status=ChargingProfileStatus.accepted
        )
