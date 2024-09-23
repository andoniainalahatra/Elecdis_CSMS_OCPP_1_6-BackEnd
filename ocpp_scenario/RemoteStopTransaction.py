class RemoteStopTransaction:
    @staticmethod
    def on_remoteStop(transaction_id:int):
        return [2, "15455", "RemoteStopTransaction", {"transactionId": transaction_id}]
