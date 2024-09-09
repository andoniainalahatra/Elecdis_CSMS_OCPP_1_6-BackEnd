from pydantic import BaseModel
from datetime import date, datetime
class Connector_create(BaseModel):
    id:str
    connector_type:str
    connector_id:int
    charge_point_id:str
    status:str
    valeur:float

class Connector_update(BaseModel):
    valeur:float
    status:str
    time:datetime

class Historique_status_create(BaseModel):
    real_connector_id:str
    status:str
    time_last_status:datetime

class Historique_metervalues_create(BaseModel):
    real_connector_id:str
    valeur:float