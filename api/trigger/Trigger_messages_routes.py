from fastapi import APIRouter, Depends

router=APIRouter()
from ocpp_scenario.TriggerMessage import *
import logging

@router.get("/trigger")
async def trigger_message(message_type:str, charge_point_id:str):
    return await TriggerMessage().on_trigger_message(message_type,charge_point_id)
