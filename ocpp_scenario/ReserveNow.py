import uuid
from datetime import datetime, timedelta
from core.config import TIME_ZONE
import pytz
class ReserveNow:
    def generate_message_id(self):
        return str(uuid.uuid4())
    def on_reserveNow(self,connectorId:int,idTag:str,reservationId:int):
        message_id=self.generate_message_id()
        timezone = pytz.timezone(TIME_ZONE)
        expiry_date =(datetime.now(timezone) + timedelta(hours=2))
        return [2,message_id,"ReserveNow",{"connectorId":connectorId,"expiryDate":expiry_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',"idTag":idTag,"reservationId":reservationId}]