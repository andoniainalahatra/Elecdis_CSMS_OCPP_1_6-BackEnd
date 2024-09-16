from pydantic import BaseModel
from datetime import date, datetime
from models.elecdis_model import StatusEnum
from typing import Optional
class Cp_create(BaseModel):
    id:str
    serial_number:Optional[str]=None
    charge_point_model:Optional[str]=None
    charge_point_vendors:Optional[str]=None
    status:Optional[str]=StatusEnum.unavailable
    adresse:str
    longitude:float
    latitude:float
    

class Cp_update(BaseModel):
    charge_point_model:Optional[str]=None
    charge_point_vendors:Optional[str]=None
    status:Optional[str]=None
    time:Optional[datetime]=datetime.now


   