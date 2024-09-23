import uuid
class CancelReservation:
    def generate_message_id(self):
        return str(uuid.uuid4())
    def on_cancelReservation(self,reservationId:int):
        message_id=self.generate_message_id()
        return [2,message_id,"CancelReservation",{"reservationId":reservationId}]