from pydantic import BaseModel
class Solde_data(BaseModel):
    solde: float
    user_id: int
    unit: str