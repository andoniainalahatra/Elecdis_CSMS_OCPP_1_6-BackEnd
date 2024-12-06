from pydantic import BaseModel
from datetime import date, datetime,timedelta
from models.elecdis_model import StatusEnum
from typing import Optional


class reservation_create(BaseModel):
    connector_id:str
    date_reservation:datetime
    user_id:int
    expirate_date:Optional[datetime]=""
    etat:Optional[int]=1
class update_reservation_etat(BaseModel):
    etat:int
class data_history_reservation(BaseModel):
    reservation_id:int
    client:str
    date_reservation:datetime
    date_expirate:datetime
    connector_id:str
    charge_point_location:str
    charge_point_vendors:str
    charge_point_id:str
    status:str
class create_history_reservation(BaseModel):
    tag_id:int
    date_utilisation:datetime
    connector_id:str
    etat:Optional[int]=1
