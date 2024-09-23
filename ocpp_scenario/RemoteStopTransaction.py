import uuid
class RemoteStopTransaction:
    def generate_message_id(self):
        return str(uuid.uuid4())
    def on_remoteStop(self,transaction_id:int):
        message_id=self.generate_message_id()
        return [2, message_id, "RemoteStopTransaction", {"transactionId": transaction_id}]
