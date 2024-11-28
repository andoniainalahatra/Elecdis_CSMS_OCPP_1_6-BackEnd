from fastapi import APIRouter

from ocpp_scenario.ChangeAvailability import ChangeAvailability
from ocpp_scenario.GetCompositeSchedule import GetCompositeSchedule
from ocpp_scenario.clear_cache import ClearCacheHandler

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

