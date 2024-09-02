import json
from typing import List, Dict
class Response:
    def __init__(self, charge_point_id: str, payload: str):
            self.charge_point_id = charge_point_id
            self.payload = payload
    
    def to_dict(self) -> Dict[str, any]:
        return {
            'charge_point_id': self.charge_point_id,
            'payload': self.payload
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())