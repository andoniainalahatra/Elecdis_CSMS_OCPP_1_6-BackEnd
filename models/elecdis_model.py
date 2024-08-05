from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import date, datetime


class Location(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    charge_points: List["ChargePoint"] = Relationship(back_populates="location")


class Connector(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    charge_point_id: Optional[int] = Field(default=None, foreign_key="chargepoint.id")
    connector_type: str

    sessions: List["Session"] = Relationship(back_populates="connector")


class ChargePoint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    location_id: Optional[int] = Field(default=None, foreign_key="location.id")
    location_id: Optional[int] = Field(default=None)
    status: str
    
    location: Optional["Location"] = Relationship(back_populates="charge_points")
    connectors: List["Connector"] = Relationship(back_populates="charge_point")


class TariffGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    new_column: int

    tariffs: List["Tariff"] = Relationship(back_populates="tariff_group")


class PaymentMethodUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_payment_method: int = Field(foreign_key="paymentmethod.id")
    id_user: int = Field(foreign_key="user.id")


class Partner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    contracts: List["Contract"] = Relationship(back_populates="partner")
    users: List["User"] = Relationship(back_populates="partner")


class UserGroup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    users: List["User"] = Relationship(back_populates="user_group")


class Contract(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    partner_id: Optional[int] = Field(default=None, foreign_key="partner.id")
    circuit_id: Optional[int] = Field(default=None)
    start_date: date
    end_date: date

    partner: Optional["Partner"] = Relationship(back_populates="contracts")


class Tariff(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tariff_group_id: int = Field(foreign_key="tariffgroup.id")

    tariff_group: Optional["TariffGroup"] = Relationship(back_populates="tariffs")
    tariff_snapshots: List["TariffSnapshot"] = Relationship(back_populates="tariff")


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: Optional[int] = Field(default=None, foreign_key="session.id")
    amount: float
    timestamp: datetime


class User(SQLModel, table=True):
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


class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type_subscription: str

    users: List["User"] = Relationship(back_populates="subscription")


class PaymentMethod(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    payment_method_users: List["PaymentMethodUser"] = Relationship(back_populates="payment_method")


class TariffSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tariff_id: int = Field(foreign_key="tariff.id")
    effective_date: date
    session_id: int = Field(foreign_key="session.id")

    tariff: Optional["Tariff"] = Relationship(back_populates="tariff_snapshots")


class Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime
    end_time: datetime
    connector_id: int = Field(foreign_key="connector.id")
    user_id: int = Field(foreign_key="user.id")

    connector: Optional["Connector"] = Relationship(back_populates="sessions")
    user: Optional["User"] = Relationship(back_populates="sessions")
    tariff_snapshots: List["TariffSnapshot"] = Relationship(back_populates="session")
    transactions: List["Transaction"] = Relationship(back_populates="session")


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    tag: str

    user: Optional["User"] = Relationship(back_populates="tags")