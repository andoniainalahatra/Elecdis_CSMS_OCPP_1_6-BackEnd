from ocpp_scenario.data_transfer import *
import logging
from fastapi import APIRouter, HTTPException
from ocpp_scenario.data_transfer import DataTransfer, DataTransferRequest

router = APIRouter()

data_transfer_service = DataTransfer()

@router.post("/send", response_model=dict, 
    description="Endpoint pour envoyer des données à une borne de recharge spécifique",
    responses={
        200: {"description": "Données envoyées avec succès"},
        500: {"description": "Erreur lors de l'envoi des données"}
    })
async def send_data_transfer(request: DataTransferRequest):
    """
    Envoie des données à une borne de recharge via le protocole OCPP.
    
    Args:
        request: Les données à envoyer contenant:
            - vendor_id: Identifiant du vendeur
            - message_id: Identifiant du message
            - data: Données à transférer
            - charge_point_id: Identifiant de la borne
    """
    try:
        logging.info(f"Tentative d'envoi de données à la borne {request.charge_point_id}")
        logging.debug(f"Données à envoyer: {request.data}")
        
        response = await data_transfer_service.on_data_transfer(
            vendor_id=request.vendor_id,
            message_id=request.message_id,
            data=request.data,
            charge_point_id=request.charge_point_id
        )
        
        logging.info(f"Données envoyées avec succès à la borne {request.charge_point_id}")
        return response
        
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi des données: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'envoi des données: {str(e)}"
        )