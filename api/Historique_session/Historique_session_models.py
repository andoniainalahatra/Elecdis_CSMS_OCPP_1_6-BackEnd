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
    is_credit:Optional[bool]=False
    is_expired:Optional[bool]=False

class Tarif_applique(BaseModel):
    tarif_name:Optional[str]=""
    description:Optional[str]=""
    price:Optional[float]=0.0
    kwh_applicable:Optional[float]=0.0
    majoration:Optional[float]=0.0
class Facture_data(BaseModel):
    id:Optional[int]=None
    user_name:Optional[str]=""
    total_price:Optional[float]=0.0
    total_energy_no_majoration:Optional[float]=0.0
    total_energy_with_majoration:Optional[float]=0.0
    debut_session:Optional[datetime]=None
    fin_session:Optional[datetime]=None
    currency:Optional[str]=""
    energy_unit:Optional[str]=""
    date:datetime
    address:Optional[str]=""
    is_credit:Optional[bool]=False
    status:Optional[str]=""
    tarif_applique:Optional[list[Tarif_applique]]=None
