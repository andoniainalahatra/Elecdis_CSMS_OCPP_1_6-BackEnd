from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends

from core.database import get_session
from models.elecdis_model import LocalList
from ocpp_scenario.ChangeAvailability import ChangeAvailability
from ocpp_scenario.GetCompositeSchedule import GetCompositeSchedule
from ocpp_scenario.clear_cache import ClearCacheHandler
from ocpp_scenario.getLocalList import GetLocalListVersionMessage
from ocpp_scenario.send_local_list import SendLocalListMessage
from sqlmodel import Session

from ocpp_scenario.updateFirmware import UpdateFirmwareMessage

router = APIRouter()

from ocpp_scenario.GetConfiguration import *

possible_keys=[
    "Cst_BackendUrl",
    "Cst_ChargeBoxId",
    "AuthorizationKey",
    "WebSocketPingInterval",
    "Cst_ReconnectInterval",
    "Cst_StaleTimeout",
    "Cst_PreBootTransactions",
    "ConnectionTimeOut",
    "MinimumStatusDuration",
    "StopTransactionOnInvalidId",
    "StopTransactionOnEVSideDisconnect",
    "LocalPreAuthorize",
    "LocalAuthorizeOffline",
    "AllowOfflineTxForUnknownId",
    "Cst_SilentOfflineTransactions",
    "Cst_AuthorizationTimeout",
    "Cst_FreeVendActive",
    "Cst_FreeVendIdTag",
    "Cst_TxStartOnPowerPathClosed",
    "HeartbeatInterval",
    "LocalAuthListEnabled",
    "ResetRetries",
    "MeterValuesSampledData",
    "StopTxnSampledData",
    "MeterValuesAlignedData",
    "StopTxnAlignedData",
    "Cst_MeterValueCacheSize",
    "MeterValueSampleInterval",
    "ClockAlignedDataInterval",
    "Cst_MeterValuesInTxOnly",
    "Cst_StopTxnDataCapturePeriodic",
    "NumberOfConnectors",
    "AuthorizeRemoteTxRequests",
    "GetConfigurationMaxKeys",
    "UnlockConnectorOnEVSideDisconnect",
    "LocalAuthListMaxLength",
    "SendLocalListMaxLength",
    "ReserveConnectorZeroSupported",
    "MeterValuesSampledDataMaxLength",
    "StopTxnSampledDataMaxLength",
    "MeterValuesAlignedDataMaxLength",
    "ChargeProfileMaxStackLevel",
    "ChargingScheduleAllowedChargingRateUnit",
    "ChargingScheduleMaxPeriods",
    "MaxChargingProfilesInstalled",
    "SupportedFeatureProfiles"
]

summary = f'Get configuration possible keys: \n \t {possible_keys}'

@router.get("/get_configuration", description=summary)
async def get_configuration(key:str, charge_point_id:str):
    return await GetConfiguration().on_get_configuration(key,charge_point_id)

@router.post("/change_configuration", description=summary)
async def change_configuration(key:str, value:str, charge_point_id:str):
    return await GetConfiguration().change_configuration(key,value,charge_point_id)
@router.post("/change_availability", description="permet de modifier l'etat d'un connecteur : deux états possible : Inoperative ou Operative")
async def change_availability(state_type:str, connectorId:str, charge_point_id:str):
    return await ChangeAvailability().change_availability(state_type,connectorId,charge_point_id)
@router.post("/get_composite_schedule", description="")
async def change_availability(duration: int,chargingRateUnit:str, connectorId:str, charge_point_id:str):
    return await GetCompositeSchedule().get_composite_schedule(duration,chargingRateUnit,connectorId,charge_point_id)


@router.post("/reset", description="redeamare la charge point")
async def reset(charge_point_id:str, reset_type:str):
    return await ResetMessage().on_reset_message(reset_type, charge_point_id)

@router.post("/send_local_list", description="send local list ||||  UPDATE TYPE : FULL or DIFFERENTIAL")
async def reset(charge_point_id:str,  update_type:Optional[str]="", session_models:Session = Depends(get_session)):
    from api.RFID.RFID_Services import get_local_lists_details, get_update_type
    local_authorization_list = get_local_lists_details(session_models)
    print("local_authorization_list",local_authorization_list)
    update_type = get_update_type(update_type)
    local_list : LocalList= LocalList(update_type = update_type, charge_point_id = charge_point_id)
    session_models.add(local_list)
    session_models.commit()
    session_models.refresh(local_list)
    return await SendLocalListMessage().on_send_local_list(list_version=local_list.id, update_type=update_type, local_authorization_list=local_authorization_list, charge_point_id=charge_point_id)

@router.get("/on_get_local_list_version", description="get local list version")
async def on_get_local_list_version(charge_point_id:str):
    try:
        return await GetLocalListVersionMessage().on_get_local_list_version(charge_point_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send Get Local List Version message: {e}")

@router.post("/update_firmware", description="update firmware")
async def update_firmware(charge_point_id:str, firmware_url:str, retry:int=5, retry_interval:int=60):
    retrieve_date:str=  datetime.now().isoformat()
    return await UpdateFirmwareMessage().on_update_firmware(charge_point_id=charge_point_id, firmware_url=firmware_url, retrieve_date=retrieve_date, retries=retry, retry_interval=retry_interval)

