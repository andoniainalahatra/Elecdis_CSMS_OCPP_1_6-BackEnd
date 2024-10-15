from pydantic import BaseModel
from datetime import date, datetime
from models.elecdis_model import StatusEnum
from typing import Optional

class Connector_create(BaseModel):
    id:str
    connector_type:str
    connector_id:Optional[int]=None
    charge_point_id:str
    status:Optional[str]=StatusEnum.unavailable
    valeur:Optional[float]=0

class Connector_update(BaseModel):
    valeur:Optional[float]=0
    status:Optional[str]=None
    time:Optional[datetime]=datetime.now

class Historique_status_create(BaseModel):
    real_connector_id:str
    status:str
    time_last_status:datetime

class Historique_metervalues_create(BaseModel):
    real_connector_id:str
    valeur:float