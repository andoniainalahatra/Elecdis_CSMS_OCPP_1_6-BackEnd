from ocpp.v16 import call_result
from ocpp.v16.enums import DataTransferStatus
from ocpp.routing import on

class DataTransferHandler:
    
    @on('DataTransfer')
    async def on_data_transfer(self, vendor_id, message_id=None, data=None):
        # Logique pour gérer les transferts de données spécifiques au fournisseur
        return call_result.DataTransferPayload(
            status=DataTransferStatus.accepted,
            data="Data transfer successful."
        )
