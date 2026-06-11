from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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


class DebtCreateSchema(BaseModel):
    debt_type: str
    person_name: str
    amount: float
    currency: str
    description: str
    date_due: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "debt_type": "owed_to",
                "person_name": "Bunyod",
                "amount": 100,
                "currency": "UZS",
                "description": "Do'stimga qarz berdim",
                "date_due": "2025-12-31T13:00:00"
            }
        }

class DebtTypeSchema(BaseModel):
    debt_type: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "debt_type": "owed_to",
            }
        }