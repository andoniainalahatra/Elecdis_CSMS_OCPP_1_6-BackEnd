from pydantic import BaseModel
from datetime import date, datetime,timedelta
from models.elecdis_model import StatusEnum
from typing import Optional


class Historique_defaillance_create(BaseModel):
    charge_point_id:Optional[str]
    time:Optional[datetime]=None
    Error_code:Optional[str]=None
    Description:Optional[str]=None
    

class Historique_defaillance_update(BaseModel):
    etat:Optional[str]