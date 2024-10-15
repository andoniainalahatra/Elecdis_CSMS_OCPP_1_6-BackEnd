from datetime import date, datetime
from typing import Optional

from fastapi   import APIRouter, Depends
from sqlalchemy.orm import Session as Session_db

from api.dashboard.Dashboard_services import get_dashboard_datas_by_date, count_users_by_date, count_users_by_month, \
    total_revenus_by_date, total_revenus_by_month, get_currency, count_session_charge_by_date, \
    count_session_charge_by_month, total_energy_by_date, total_energy_by_year_month, get_energy_unit, count_all_users, \
    get_total_revenus, total_session_charge, get_total_energy
from core.database import get_session

router = APIRouter()

@router.get("/datas", summary="liste des données à utiliser dans le dashboard")
def get_datas(date_selected: date, session: Session_db = Depends(get_session) ):
    print(date_selected)
    return get_dashboard_datas_by_date(session, date_selected)

@router.get("/new_users_date", summary="nombre de nouveaux clients en fonction d'une date")
def get_new_users(date_selected: date, session: Session_db = Depends(get_session) ):
    return {
        "new_users_numbers": count_users_by_date(session, date_selected),
        "date_selected":date_selected
    }

@router.get("/new_users_year", summary="nombre de nouveaux clients en fonction du mois et de l'année")
def get_new_users_by_month(month: Optional[int]=None, year: Optional[int]=datetime.now().year, session: Session_db = Depends(get_session) ):
    return {
        "new_users_numbers": count_users_by_month(session, month, year),
        "month":month,
        "year":year
    }
@router.get("/total_clients", summary="nombre total de clients")
def get_total_clients(session: Session_db = Depends(get_session) ):
    return {"users_numbers":count_all_users(session)}


@router.get("/total_revenus_date" , summary="total des revenus en fonction d'une date")
def get_total_revenu_date(date_selected: date, session: Session_db = Depends(get_session) ):
    return {
        "total_revenus": total_revenus_by_date(session, date_selected),
        "currency":get_currency(session),
        "date_selected":date_selected
    }

@router.get("/total_revenus_year" , summary="total des revenus en fonction du mois et de l'année")
def get_total_revenus_by_month(month: Optional[int]=None, year: Optional[int]=datetime.now().year, session: Session_db = Depends(get_session) ):
    return {
        "total_revenus": total_revenus_by_month(session, month, year),
        "currency":get_currency(session),
        "month":month,
        "year":year
    }
@router.get("/total_revenus", summary="total des revenus")
def get_total_revenu(session: Session_db = Depends(get_session) ):
    return {
        "total_revenus": get_total_revenus(session),
        "currency":get_currency(session),

    }

@router.get("/sessions_by_date", summary="nombre de sessions de charge en fonction d'une date")
def get_sessions_by_date(date_selected: date, session: Session_db = Depends(get_session) ):
    return {
        "sessions_numbers": count_session_charge_by_date(session, date_selected),
        "date_selected":date_selected
    }

@router.get("/sessions_by_year_month", summary="nombre de sessions de charge en fonction du mois et de l'année")
def get_sessions_by_month(month: Optional[int]=None, year: Optional[int]=datetime.now().year, session: Session_db = Depends(get_session) ):
    return {
        "sessions_numbers": count_session_charge_by_month(session, month, year),
        "month":month,
        "year":year
    }
@router.get("/total_sessions", summary="nombre total de sessions de charge")
def get_total_sessions(session: Session_db = Depends(get_session) ):
    return {
        "sessions_numbers": total_session_charge(session)
    }


@router.get("/energy_by_date", summary="total de l'énergie consommée en fonction d'une date")
def get_energy_by_date(date_selected: date, session: Session_db = Depends(get_session) ):
    return {
        "energy": total_energy_by_date(session, date_selected),
        "energy_unit":get_energy_unit(session),
        "date_selected":date_selected
    }

@router.get("/energy_by_year_month", summary="total de l'énergie consommée en fonction du mois et de l'année")
def get_energy_by_month(month: Optional[int]=None, year: Optional[int]=datetime.now().year, session: Session_db = Depends(get_session) ):
    return {
        "energy": total_energy_by_year_month(session, month, year),
        "energy_unit":get_energy_unit(session),
        "month":month,
        "year":year
   }

@router.get("/total_energy", summary="total de l'énergie consommée")
def get_total_energy_0(session: Session_db = Depends(get_session) ):
    return {
        "energy": get_total_energy(session),
        "energy_unit":get_energy_unit(session)
    }

