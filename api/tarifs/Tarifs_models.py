from datetime import time

from pydantic import BaseModel
from core.utils import *
class Tariff_create(BaseModel):
    start_hour:time = time(0,0)
    end_hour:time= time(0,0)
    price:float
    name_tarif:str=""
    description:str=""
    facteur_majoration:float=1
    currency:str=CURRENCY_AR
    energy_unit:str=UNIT_KWH
    backgroundColor:str=""
    textColor:str=""
    category:int



class Tariff_update(BaseModel):
    start_hour:time = None
    end_hour:time= None
    price:float=None
    name_tarif:str=None
    description:str=None
    facteur_majoration:float=None
    currency:str=None
    energy_unit:str=None
    backgroundColor:str=""
    textColor:str=""
    category:int

class TariffGroup_create(BaseModel):
    name: str

class TariffGroup_update(BaseModel):
    name: str = None
