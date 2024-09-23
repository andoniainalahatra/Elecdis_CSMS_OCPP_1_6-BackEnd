class ReserveNow:
    def on_reserveNow(connectorId:str,expiryDate:str,idTag:str,reservationId:int):
        return [2,"15455","ReserveNow",{"connectorId":connectorId,"expiryDate":expiryDate,"idTag":idTag,"reservationId":reservationId}]