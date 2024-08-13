from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import date, datetime
from enum import Enum
from sqlalchemy import Index

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ChargePoint(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    
    status: str
    
    
    connectors: List["Connector"] = Relationship(back_populates="charge_point")

    __table_args__ = (Index("ix_chargepoint_id", "id"),)




# Pour les autres classes, les modifications restent les mêmes.

class Connector(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    charge_point_id: Optional[int] = Field(default=None, foreign_key="chargepoint.id")
    connector_type: str

    sessions: List["Session"] = Relationship(back_populates="connector")

    __table_args__ = (Index("ix_connector_id", "id"),)

class TariffGroup(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    new_column: int

    tariffs: List["Tariff"] = Relationship(back_populates="tariff_group")

    __table_args__ = (Index("ix_tariffgroup_id", "id"),)

class PaymentMethodUser(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_payment_method: int = Field(foreign_key="paymentmethod.id")
    id_user: int = Field(foreign_key="user.id")

    __table_args__ = (Index("ix_paymentmethoduser_id", "id"),)

class Partner(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    contracts: List["Contract"] = Relationship(back_populates="partner")
    users: List["User"] = Relationship(back_populates="partner")

    __table_args__ = (Index("ix_partner_id", "id"),)

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

    tariff_group: Optional["TariffGroup"] = Relationship(back_populates="tariffs")
    tariff_snapshots: List["TariffSnapshot"] = Relationship(back_populates="tariff")

    __table_args__ = (Index("ix_tariff_id", "id"),)

class Transaction(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: Optional[int] = Field(default=None, foreign_key="session.id")
    amount: float
    timestamp: datetime

    __table_args__ = (Index("ix_transaction_id", "id"),)

class User(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    password: str
    id_user_group: int = Field(foreign_key="usergroup.id")
    id_partner: int = Field(foreign_key="partner.id")
    id_subscription: Optional[int] = Field(default=None, foreign_key="subscription.id")

    user_group: Optional["UserGroup"] = Relationship(back_populates="users")
    partner: Optional["Partner"] = Relationship(back_populates="users")
    sessions: List["Session"] = Relationship(back_populates="user")
    tags: List["Tag"] = Relationship(back_populates="user")
    payment_methods: List["PaymentMethodUser"] = Relationship(back_populates="user")

    __table_args__ = (Index("ix_user_id", "id"),)

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

    __table_args__ = (Index("ix_tariffsnapshot_id", "id"),)

class Session(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime
    end_time: datetime
    connector_id: int = Field(foreign_key="connector.id")
    user_id: int = Field(foreign_key="user.id")

    connector: Optional["Connector"] = Relationship(back_populates="sessions")
    user: Optional["User"] = Relationship(back_populates="sessions")
    tariff_snapshots: List["TariffSnapshot"] = Relationship(back_populates="session")
    transactions: List["Transaction"] = Relationship(back_populates="session")

    __table_args__ = (Index("ix_session_id", "id"),)

class Tag(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    tag: str

    user: Optional["User"] = Relationship(back_populates="tags")

    __table_args__ = (Index("ix_tag_id", "id"),)