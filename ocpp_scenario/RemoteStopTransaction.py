class RemoteStopTransaction:
    def on_remoteStop(self,transaction_id:int):
        return [2, "15455", "RemoteStopTransaction", {"transactionId": transaction_id}]
