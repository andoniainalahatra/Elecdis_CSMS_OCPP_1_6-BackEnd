from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from ocpp_scenario.unlock_connector import *
import logging

router = APIRouter()
unlock_service = UnlockConnectorService()

@router.post(
    "/unlock",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    description="Déverrouille un connecteur spécifique sur une borne de recharge",
    responses={
        200: {"description": "Déverrouillage réussi"},
        400: {"description": "Paramètres invalides"},
        404: {"description": "Borne ou connecteur non trouvé"},
        500: {"description": "Erreur serveur"}
    }
)
async def send_unlock_connector(request: UnlockRequest):
    """
    Déverrouille un connecteur sur une borne de recharge.
    
    Args:
        request: UnlockRequest contenant:
            - charge_point_id: Identifiant de la borne
            - connector_id: Identifiant du connecteur
            
    Returns:
        dict: Réponse de la borne de recharge
    """
    try:
        # Validation des paramètres
        if not request.charge_point_id or not request.connector_id:
            logging.error("Paramètres manquants dans la requête de déverrouillage")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les paramètres charge_point_id et connector_id sont obligatoires"
            )
            
        if request.connector_id < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'identifiant du connecteur doit être supérieur à 0"
            )
            
        # Logging et appel du service
        logging.info(
            f"Tentative de déverrouillage - Borne: {request.charge_point_id}, "
            f"Connecteur: {request.connector_id}"
        )
                    
        response = await unlock_service.unlock_connector(
            charge_point_id=request.charge_point_id,
            connector_id=request.connector_id
        )
        
        logging.info(
            f"Déverrouillage réussi - Borne: {request.charge_point_id}, "
            f"Connecteur: {request.connector_id}"
        )
        
        return {
            "status": "success",
            "message": "Connecteur déverrouillé avec succès",
            "data": response
        }
        
    except HTTPException as e:
        logging.error(f"Erreur HTTP lors du déverrouillage: {str(e)}")
        raise e
        
    except Exception as e:
        logging.error(
            f"Erreur inattendue lors du déverrouillage - "
            f"Borne: {request.charge_point_id}, "
            f"Connecteur: {request.connector_id}, "
            f"Erreur: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du déverrouillage: {str(e)}"
        )
