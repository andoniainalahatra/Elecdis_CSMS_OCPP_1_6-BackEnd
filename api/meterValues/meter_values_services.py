from fastapi import HTTPException, APIRouter
from core.database import meter_values_collection
from bson import ObjectId

router = APIRouter()


# Route pour récupérer tous les documents `MeterValues`
@router.get("/meter_values/")
async def get_all_meter_values():
    meter_values = []
    async for meter_value in meter_values_collection.find():
        meter_values.append(meter_value)
    return meter_values

@router.get("/meter_values/{id}")
async def get_meter_value_by_id(id: str):
    # Vérifier si l'ID est valide
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    meter_value = await meter_values_collection.find_one({"_id": ObjectId(id)})
    if meter_value is None:
        raise HTTPException(status_code=404, detail="MeterValue not found")
    
    return meter_value
