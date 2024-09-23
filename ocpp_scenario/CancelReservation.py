class CancelReservation:
    def on_cancelReservation(self,reservationId:int):
        return [2,"15455","CancelReservation",{"reservationId":reservationId}]