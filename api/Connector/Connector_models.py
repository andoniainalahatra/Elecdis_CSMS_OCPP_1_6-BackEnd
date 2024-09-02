from pydantic import BaseModel
class Connector_create(BaseModel):
    connector_type:str
    connector_id:int
    charge_point_id:int
    status:str
    valeur:float

class Connector_update(BaseModel):
    valeur:float
    status:str

class Historique_status_create(BaseModel):
    real_connector_id:int
    status:str

class Historique_metervalues_create(BaseModel):
    real_connector_id:int
    valeur:float