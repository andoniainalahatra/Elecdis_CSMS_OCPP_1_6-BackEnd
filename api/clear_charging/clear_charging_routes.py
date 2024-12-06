from fastapi import APIRouter, HTTPException
from ocpp_scenario.clear_charging_profile import ClearChargingProfileHandler, ClearChargingProfileRequest

router = APIRouter()

@router.post("/clear_charging_profile/{charge_point_id}")
async def clear_charging_profile(
    charge_point_id: str,
    request: ClearChargingProfileRequest
):
    """
    Endpoint pour effacer un profil de charge d'une borne spécifique.
    
    Args:
        charge_point_id: Identifiant de la borne
        request: Paramètres pour l'effacement du profil de charge
    """
    try:
        handler = ClearChargingProfileHandler()
        response = await handler.on_clear_charging_profile(
            clear_profile_request=request,
            charge_point_id=charge_point_id
        )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'effacement du profil de charge: {str(e)}"
        )
