from datetime import datetime
from typing import Optional

from pydantic import BaseModel
class historique_session_data(BaseModel):
    id : Optional[int]=None
    rfid:Optional[str]=""
    user_name:Optional[str]=""
    start_time:datetime
    end_time:Optional[datetime]=""
    state:Optional[str]=""
    connector_id:Optional[str]=""
    chargepoint_id:Optional[str]=""
    address:Optional[str]=""
    total_energy:Optional[float]=0.0
    total_price:Optional[float]=0.0
    currency:Optional[str]=""
    energy_unit:Optional[str]=""
