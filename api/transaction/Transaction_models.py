from datetime import datetime
from typing import Optional

from pydantic import BaseModel
class Session_create(BaseModel):
    user_tag: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]=None
    connector_id: str
    metter_start: Optional[float]
    metter_stop: Optional[float]=None


class Session_update(BaseModel):
    end_time: Optional[datetime]
    metter_stop: Optional[float]
    transaction_id: int

class Session_list_model(BaseModel):
    id: int=None
    start_time: Optional[datetime]=None
    end_time: Optional[datetime]=None
    connector_id: str=None
    user_id: int=None
    user_name: str=None
    consumed_energy: Optional[float]=None
    energy_unit: Optional[str]=None
    rfid:str=None
    charge_point_id: int=None
    total_cost: Optional[float]=None
    currency: Optional[str]=None

class Session_data_affichage(BaseModel):
    id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    connector_id: str
    user_id: int
    user_name: str
    consumed_energy: Optional[str]
    rfid:str
    charge_point_id: int
    total_cost: Optional[str]

class Transaction_details(BaseModel):
    total_price: Optional[float]=None
    currency: Optional[str]=None
    energy_unit: Optional[str]=None
