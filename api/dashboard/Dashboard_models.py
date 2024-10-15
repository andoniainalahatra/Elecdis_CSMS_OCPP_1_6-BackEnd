from typing import Optional

from pydantic import BaseModel
class Dashboard_data(BaseModel):
    revenus: Optional[float]=0
    nombres_sessions: Optional[int]=0
    nombre_utilisateurs: Optional[int]=0
    energy_kwh: Optional[float]=0