from pydantic import BaseModel
from datetime import date, datetime,timedelta
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
    firmware_version:Optional[str]=None
    

class Cp_update(BaseModel):
    serial_number:Optional[str]=None
    charge_point_model:Optional[str]=None
    charge_point_vendors:Optional[str]=None
    status:Optional[str]=None
    adresse:Optional[str]=None
    longitude:Optional[float]=0
    latitude:Optional[float]=0
    firmware_version:Optional[str]=None
    time:Optional[datetime]=None
class Cp_form(BaseModel):
    id: str
    serial_number : str
    charge_point_model : str
    charge_point_vendors :str
    status: str
    adresse:str
    latitude:float
    longitude:float
    energie_consomme:float


   