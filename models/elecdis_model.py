from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import date, datetime, timedelta, time
from enum import Enum
from sqlalchemy import Index
from sqlalchemy import PrimaryKeyConstraint, Index, UniqueConstraint
from core.utils import *


class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"
    available="Available"
    unavailable="Unavailable"
    preparing="Preparing"
    charging="charging"
    resolve="Resolved"
    no_resolve="Unresolved"
    




def get_current_time_plus_3_hours() -> datetime:
    return datetime.utcnow() + timedelta(hours=3)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=get_current_time_plus_3_hours, nullable=False)
    updated_at: datetime = Field(default_factory=get_current_time_plus_3_hours, nullable=False)


class ChargePoint(TimestampMixin, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    serial_number: Optional[str]
    charge_point_model: Optional[str]
    charge_point_vendors: Optional[str]
    status: Optional[str]
    connectors: List["Connector"] = Relationship(back_populates="charge_point")
    adresse: Optional[str]
    latitude: float
    longitude: float
    state: int
    firmware_version: Optional[str]

    __table_args__ = (Index("ix_chargepoint_id", "id"),)

class Historique_defailllance(TimestampMixin, table=True):
    id : Optional[int] = Field(default=None, primary_key=True)
    charge_point_id: Optional[str] = Field(default=None, foreign_key="chargepoint.id")
    time:datetime= Field(nullable=False)
    Error_code:Optional[str]
    Description:Optional[str]
    etat:Optional[str]


# Pour les autres classes, les modifications restent les mêmes.

class Connector(TimestampMixin, table=True):
    # TY NO MAKANY @ LE HISTORIQUE
    id: Optional[str] = Field(primary_key=True)
    charge_point_id: Optional[str] = Field(default=None, foreign_key="chargepoint.id")
    connector_type: Optional[str]

    # NUMERO
    connector_id: Optional[int]
    valeur: Optional[float] = Field(default=0)
    status: Optional[str]
    sessions: List["Session"] = Relationship(back_populates="connector")
    charge_point: Optional["ChargePoint"] = Relationship(back_populates="connectors")
    historique_status: List["Historique_status"] = Relationship(back_populates="connector")
    historique_metter_value: List["Historique_metter_value"] = Relationship(back_populates="connector")
    __table_args__ = (
        # PrimaryKeyConstraint('id', 'charge_point_id'),
        UniqueConstraint('id', 'charge_point_id', name='uq_connector_id_charge_point_id'),

        Index("ix_connector_id", "id"),)


class Historique_status(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # le id an'le connecteur no eto fa tsy le connector_id
    real_connector_id: Optional[str] = Field(foreign_key="connector.id")
    statut: str
    time_last_statut: datetime = Field(nullable=False)
    connector: Optional["Connector"] = Relationship(back_populates="historique_status")


class Historique_metter_value(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    real_connector_id: Optional[str] = Field(foreign_key="connector.id")
    valeur: float
    connector: Optional["Connector"] = Relationship(back_populates="historique_metter_value")


class TariffGroup(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    new_column: int

    tariffs: List["Tariff"] = Relationship(back_populates="tariff_group")

    __table_args__ = (Index("ix_tariffgroup_id", "id"),)


class UserGroup(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    users: List["User"] = Relationship(back_populates="user_group")

    __table_args__ = (Index("ix_usergroup_id", "id"),)


class Contract(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    partner_id: Optional[int] = Field(default=None, foreign_key="partner.id")
    circuit_id: Optional[int] = Field(default=None)
    start_date: date
    end_date: date

    partner: Optional["Partner"] = Relationship(back_populates="contracts")

    __table_args__ = (Index("ix_contract_id", "id"),)


class Tariff(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tariff_group_id: int = Field(foreign_key="tariffgroup.id")
    start_hour: time
    end_hour: time
    price: float
    currency: Optional[str]
    energy_unit: Optional[str]

    tariff_group: Optional["TariffGroup"] = Relationship(back_populates="tariffs")
    tariff_snapshots: List["TariffSnapshot"] = Relationship(back_populates="tariff")

    __table_args__ = (Index("ix_tariff_id", "id"),)


class Transaction(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: Optional[int] = Field(default=None, foreign_key="session.id")
    currency: Optional[str]
    unit_price: float
    total_price: float
    consumed_energy: float
    currency: Optional[str]
    energy_unit: Optional[str]
    session: Optional["Session"] = Relationship(back_populates="transactions")

    __table_args__ = (Index("ix_transaction_id", "id"),)


class Partner(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    contracts: List["Contract"] = Relationship(back_populates="partner")
    users: list["User"] = Relationship(back_populates="partner")

    __table_args__ = (Index("ix_partner_id", "id"),)


class User(TimestampMixin, table=True):
    __tablename__ = "user_table"
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    password: str
    phone: Optional[str]
    id_user_group: Optional[int] = Field(foreign_key="usergroup.id")
    id_subscription: Optional[int] = Field(default=None, foreign_key="subscription.id")
    id_partner: Optional[int] = Field(default=None, foreign_key="partner.id")
    state: Optional[int] = DEFAULT_STATE

    user_group: Optional["UserGroup"] = Relationship(back_populates="users")
    sessions: List["Session"] = Relationship(back_populates="user")
    tags: List["Tag"] = Relationship(back_populates="user")
    subscription: Optional["Subscription"] = Relationship(back_populates="users")
    partner: Optional["Partner"] = Relationship(back_populates="users")

    payment_methods: List["PaymentMethodUser"] = Relationship(back_populates="user")
    reset_codes: List["User_reset_code"] = Relationship(back_populates="user")

    __table_args__ = (Index("ix_user_table_id", "id"),)


class PaymentMethodUser(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_payment_method: int = Field(foreign_key="paymentmethod.id")
    id_user: int = Field(foreign_key="user_table.id")

    user: Optional["User"] = Relationship(back_populates="payment_methods")
    payment_method: Optional["PaymentMethod"] = Relationship(back_populates="payment_method_users")

    __table_args__ = (Index("ix_paymentmethoduser_id", "id"),)


class Subscription(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type_subscription: str

    users: List["User"] = Relationship(back_populates="subscription")

    __table_args__ = (Index("ix_subscription_id", "id"),)


class PaymentMethod(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    payment_method_users: List["PaymentMethodUser"] = Relationship(back_populates="payment_method")

    __table_args__ = (Index("ix_paymentmethod_id", "id"),)


class TariffSnapshot(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tariff_id: int = Field(foreign_key="tariff.id")
    effective_date: date
    session_id: int = Field(foreign_key="session.id")

    tariff: Optional["Tariff"] = Relationship(back_populates="tariff_snapshots")
    session: Optional["Session"] = Relationship(back_populates="tariff_snapshots")

    __table_args__ = (Index("ix_tariffsnapshot_id", "id"),)


class Session(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    connector_id: Optional[str] = Field(default=None, foreign_key="connector.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user_table.id")
    metter_start: Optional[float]
    metter_stop: Optional[float]
    tag: Optional[str]
    reason: Optional[str]

    connector: Optional["Connector"] = Relationship(back_populates="sessions")
    user: Optional["User"] = Relationship(back_populates="sessions")
    tariff_snapshots: List["TariffSnapshot"] = Relationship(back_populates="session")
    transactions: List["Transaction"] = Relationship(back_populates="session")
    rfid_usage_history: List["Rfid_usage_history"] = Relationship(back_populates="session")

    __table_args__ = (Index("ix_session_id", "id"),)


class Tag(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user_table.id")
    tag: str
    state: Optional[int] = DEFAULT_STATE
    status: Optional[str] = StatusEnum.active

    user: Optional["User"] = Relationship(back_populates="tags")
    rfid_usage_history: List["Rfid_usage_history"] = Relationship(back_populates="tag")

    __table_args__ = (Index("ix_tag_id", "id"),)


# TEST MANY TO MANY RELATIONSHIP

class Subscription_History(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user_table.id")
    subscription_id: int = Field(foreign_key="subscription.id")


class User_reset_code(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user_table.id")
    code: str
    is_used: bool
    expiration_date: datetime

    user: Optional["User"] = Relationship(back_populates="reset_codes")

    __table_args__ = (Index("ix_user_reset_code_id", "id"),)


class Rfid_usage_history(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tag_id: int = Field(foreign_key="tag.id")
    session_id: Optional[int] = Field(foreign_key="session.id", default=True)
    action: str
    session : Optional["Session"] = Relationship(back_populates="rfid_usage_history")
    tag : Optional["Tag"] = Relationship(back_populates="rfid_usage_history")
    __table_args__ = (Index("ix_rfid_usage_history_id", "id"),)
