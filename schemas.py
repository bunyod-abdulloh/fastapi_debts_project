from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from models import DebtType


class SignUpModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str
    is_staff: Optional[bool] = False
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "mohirdev",
                "email": "mohirdev@gmail.com",
                "password": "pass12345",
                "is_staff": False,
                "is_active": True,
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    authjwt_token_location: set = {"headers"}


class LoginModel(BaseModel):
    username_or_email: str
    password: str


class SettingsSchema(BaseModel):
    default_currency: CurrencyType
    reminder_hours_before: int

    class Config:
        orm_mode = True


from models import CurrencyType


class SettingsUpdateSchema(BaseModel):
    default_currency: CurrencyType
    reminder_hours_before: int

    class Config:
        orm_mode = True


class DebtCreateSchema(BaseModel):
    debt_type: DebtType
    person_name: str
    amount: float
    currency: CurrencyType
    description: str | None = None
    date_due: datetime | None = None


class DebtUpdateSchema(BaseModel):
    debt_type: DebtType
    person_name: str
    amount: float
    currency: CurrencyType
    description: str | None = None
    date_due: datetime | None = None
    is_paid: bool


class DebtTypeSchema(BaseModel):
    debt_type: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "debt_type": "owed_to",
            }
        }


class MonitoringSchema(BaseModel):
    total_owed_to: float
    total_owed_by: float
    balance: float
