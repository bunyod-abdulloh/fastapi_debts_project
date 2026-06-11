import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(70), unique=True)
    password = Column(Text)
    is_active = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)

    debts = relationship("Debt", back_populates="owner", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="owner", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class DebtType(str, enum.Enum):
    OWED_TO = "owed_to"  # menga qarzdor (men qarz berdim)
    OWED_BY = "owed_by"  # men qarzdorman (men qarz oldim)


class CurrencyType(str, enum.Enum):
    UZS = "UZS"
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


class Debt(Base):
    __tablename__ = "debt"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    debt_type = Column(SAEnum(DebtType), nullable=False, index=True)
    person_name = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(SAEnum(CurrencyType), default=CurrencyType.UZS)
    description = Column(Text, nullable=True)
    is_paid = Column(Boolean, default=False)
    date_incurred = Column(DateTime, default=datetime.utcnow)
    date_due = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User bilan bog'lanish
    owner = relationship("User", back_populates="debts")


class UserSettings(Base):
    __tablename__ = "user_settings"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id"), unique=True, index=True)
    default_currency = Column(SAEnum(CurrencyType), default="UZS")
    reminder_hours_before = Column(Integer)

    owner = relationship("User", back_populates="settings")
