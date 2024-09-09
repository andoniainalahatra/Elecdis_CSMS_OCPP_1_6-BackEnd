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

