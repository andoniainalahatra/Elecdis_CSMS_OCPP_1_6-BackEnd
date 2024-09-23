import uuid
class ReserveNow:
    def generate_message_id(self):
        return str(uuid.uuid4())
    def on_reserveNow(self,connectorId:str,expiryDate:str,idTag:str,reservationId:int):
        message_id=self.generate_message_id()
        return [2,message_id,"ReserveNow",{"connectorId":connectorId,"expiryDate":expiryDate,"idTag":idTag,"reservationId":reservationId}]