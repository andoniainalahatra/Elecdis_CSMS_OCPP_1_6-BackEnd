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
