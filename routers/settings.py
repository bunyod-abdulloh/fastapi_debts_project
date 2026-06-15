import datetime
from fastapi import APIRouter, status, HTTPException, Depends, Security
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from database import session, engine
from models import User, UserSettings

router = APIRouter(
    prefix="/settings",
)

session = session(bind=engine)


@router.get("/")
async def get_settings(
        Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Enter valid access token"
        )

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(
        User.username == current_user
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    settings = session.query(UserSettings).filter(
        UserSettings.owner_id == user.id
    ).first()

    if not settings:
        settings = UserSettings(
            owner_id=user.id,
            default_currency="UZS",
            reminder_hours_before=24
        )

        session.add(settings)
        session.commit()
        session.refresh(settings)

    return {
        "success": True,
        "data": {
            "default_currency": settings.default_currency,
            "reminder_hours_before": settings.reminder_hours_before
        }
    }


@router.put("/")
async def update_settings(
        update_data: SettingsUpdateSchema,
        Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Enter valid access token"
        )

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(
        User.username == current_user
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    settings = session.query(UserSettings).filter(
        UserSettings.owner_id == user.id
    ).first()

    if not settings:
        settings = UserSettings(
            owner_id=user.id
        )
        session.add(settings)

    settings.default_currency = update_data.default_currency
    settings.reminder_hours_before = update_data.reminder_hours_before

    session.commit()
    session.refresh(settings)

    return {
        "success": True,
        "message": "Settings updated successfully",
        "data": {
            "default_currency": settings.default_currency,
            "reminder_hours_before": settings.reminder_hours_before
        }
    }
