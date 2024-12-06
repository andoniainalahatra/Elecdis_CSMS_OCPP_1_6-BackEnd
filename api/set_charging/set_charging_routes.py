from fastapi import APIRouter, HTTPException, status
from ocpp_scenario.set_charging_profile import *
import logging


router = APIRouter()

@router.post(
    "/set_charging_profile/{charge_point_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    description="Configure un profil de charge pour une borne spécifique",
    responses={
        200: {"description": "Profil de charge configuré avec succès"},
        400: {"description": "Paramètres invalides"},
        404: {"description": "Borne non trouvée"},
        500: {"description": "Erreur serveur"}
    }
)
async def set_charging_profile(
    charge_point_id: str,
    request: SetChargingProfileRequest
):
    """
    Endpoint pour configurer un profil de charge sur une borne spécifique.
    
    Args:
        charge_point_id: Identifiant de la borne
        request: Données du profil de charge contenant:
            - connector_id: Identifiant du connecteur
            - cs_charging_profiles: Configuration détaillée du profil de charge
            
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

        # Validation du connector_id
        if request.connector_id < 0:
            logging.error(f"Identifiant de connecteur invalide: {request.connector_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'identifiant du connecteur doit être positif ou nul"
            )

        logging.info(f"Configuration du profil de charge - Borne: {charge_point_id}")
        logging.debug(f"Paramètres de la requête: {request.dict()}")
            
        handler = SetChargingProfileHandler()
        response = await handler.on_set_charging_profile(
            connector_id=request.connector_id,
            cs_charging_profiles=request.cs_charging_profiles.model_dump(),
            charge_point_id=charge_point_id
        )
        
        logging.info(f"Profil de charge configuré avec succès - Borne: {charge_point_id}")
        return {
            "status": "success",
            "message": "Profil de charge configuré avec succès",
            "data": response
        }

    except HTTPException as e:
        logging.error(f"Erreur HTTP lors de la configuration: {str(e)}")
        raise e
        
    except Exception as e:
        logging.error(f"Erreur lors de la configuration du profil de charge - Borne: {charge_point_id}, Erreur: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la configuration du profil de charge: {str(e)}"
        )
