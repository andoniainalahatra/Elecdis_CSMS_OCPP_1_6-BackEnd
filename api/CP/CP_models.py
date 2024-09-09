from pydantic import BaseModel
class Cp_create(BaseModel):
    id:str
    serial_number:str
    charge_point_model:str
    charge_point_vendors:str
    status:str
    adresse:str
    longitude:float
    latitude:float
    

class Cp_update(BaseModel):
    charge_point_model:str
    charge_point_vendors:str
    status:str


   