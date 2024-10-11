from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
class Rfid_create(BaseModel):
    rfid: str
    user_id: int

class Rfid_update(BaseModel):
    rfid:Optional[str]=None
    user_id: Optional[int]=None


class Historique_rfids(BaseModel):
    date: datetime
    action: str
    session_id: Optional[int]=None


class Rfid_data(BaseModel):
    id: int
    rfid: str
    user_id: int
    user_name: str
    status:Optional[str]=""
    last_used:Optional[datetime]=""
    registration:Optional[datetime]=""
    history: Optional[list]=[]



