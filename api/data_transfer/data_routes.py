from ocpp_scenario.data_transfer import *
import logging
from fastapi import APIRouter, Depends
from ocpp_scenario.data_transfer import *

router = APIRouter()

data_transfer_service = DataTransfer()

@router.post("/data_transfer")
async def send_data_transfer(request: DataTransferRequest):
    response = await data_transfer_service.send_data_transfer(
        vendor_id=request.vendor_id,
        message_id=request.message_id,
        data=request.data,
        charge_point_id=request.charge_point_id
    )
    return response