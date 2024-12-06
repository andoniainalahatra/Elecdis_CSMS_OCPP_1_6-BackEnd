from fastapi import APIRouter, HTTPException, status
from ocpp_scenario.clear_charging_profile import ClearChargingProfileHandler, ClearChargingProfileRequest
import logging

router = APIRouter()

@router.post(
    "/clear_charging_profile/{charge_point_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    description="Efface un profil de charge d'une borne spécifique",
    responses={
        200: {"description": "Profil de charge effacé avec succès"},
        400: {"description": "Paramètres invalides"},
        404: {"description": "Borne non trouvée"},
        500: {"description": "Erreur serveur"}
    }
)
async def clear_charging_profile(
    charge_point_id: str,
    request: ClearChargingProfileRequest
):
    """
    Endpoint pour effacer un profil de charge d'une borne spécifique.
    
    Args:
        charge_point_id: Identifiant de la borne
        request: Paramètres pour l'effacement du profil de charge contenant:
            - id: Identifiant optionnel du profil à effacer
            - connector_id: Identifiant optionnel du connecteur
            - charging_profile_purpose: But optionnel du profil de charge
            - stack_level: Niveau optionnel de la pile
            
    Returns:
        dict: Réponse de la borne de recharge
    """
    try:
        # Validation du charge_point_id
        if not charge_point_id:
            logging.error("Identifiant de borne manquant")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'identifiant de la borne est obligatoire"
            )

        logging.info(f"Tentative d'effacement du profil de charge - Borne: {charge_point_id}")
        logging.debug(f"Paramètres de la requête: {request.dict()}")
            
        handler = ClearChargingProfileHandler()
        response = await handler.on_clear_charging_profile(
            clear_profile_request=request,
            charge_point_id=charge_point_id
        )
        
        logging.info(f"Profil de charge effacé avec succès - Borne: {charge_point_id}")
        
        return {
            "status": "success",
            "message": "Profil de charge effacé avec succès",
            "data": response
        }

    except HTTPException as e:
        logging.error(f"Erreur HTTP lors de l'effacement du profil: {str(e)}")
        raise e
        
    except Exception as e:
        logging.error(f"Erreur inattendue lors de l'effacement du profil - Borne: {charge_point_id}, Erreur: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'effacement du profil de charge: {str(e)}"
        )
