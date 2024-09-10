from pydantic import BaseModel
class Rfid_create(BaseModel):
    rfid: str
    user_id: int

class Rfid_update(BaseModel):
    rfid:str
    user_id: int
    id:int

class Rfid_data(BaseModel):
    id: int
    rfid: str
    user_id: int
    user_name: str
