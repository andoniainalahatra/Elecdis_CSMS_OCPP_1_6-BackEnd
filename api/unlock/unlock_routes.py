from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# from services.unlock_connector_service import UnlockConnectorService
from ocpp_scenario.unlock_connector import *
# Création du routeur
router = APIRouter()
unlock_service = UnlockConnectorService()


# Définition de l'endpoint
@router.post("/unlock", response_model=dict)
async def send_unlock_connector(request: UnlockRequest):
    try:
        response = await unlock_service.unlock_connector(
            charge_point_id=request.charge_point_id,
            connector_id=request.connector_id
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
