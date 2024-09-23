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
    id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    connector_id: str
    user_id: int
    user_name: str
    metter_start: Optional[float]
    metter_stop: Optional[float]
    tag:str
    charge_point_id: int


