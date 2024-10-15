import uuid
class RemoteStartTransaction:
    def generate_message_id(self):
        return str(uuid.uuid4())
    def on_remoteStart(self,idTag:str,connectorId:str):
        message_id=self.generate_message_id()
        return [2, message_id, "RemoteStartTransaction", {"idTag":idTag,"connectorId":connectorId}]