from fastapi import APIRouter, HTTPException
from ocpp_scenario.set_charging_profile import *


router = APIRouter()

@router.post("/set_charging_profile/{charge_point_id}")
async def set_charging_profile(
    charge_point_id: str,
    request: SetChargingProfileRequest
):
    """
    Endpoint pour envoyer un profil de charge à une borne spécifique.
    
    Args:
        charge_point_id: Identifiant de la borne
        request: Données du profil de charge validées par Pydantic
    """
    try:
        handler = SetChargingProfileHandler()
        response = await handler.on_set_charging_profile(
            connector_id=request.connector_id,
            cs_charging_profiles=request.cs_charging_profiles.model_dump(),
            charge_point_id=charge_point_id
        )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'envoi du profil de charge: {str(e)}"
        )
