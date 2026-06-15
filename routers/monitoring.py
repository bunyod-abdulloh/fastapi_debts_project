from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import func

from database import session, engine
from models import User, Debt, DebtType

router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"]
)

session = session(bind=engine)


@router.get("/")
async def get_monitoring(
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

    total_owed_to = session.query(
        func.coalesce(func.sum(Debt.amount), 0)
    ).filter(
        Debt.owner_id == user.id,
        Debt.debt_type == DebtType.OWED_TO
    ).scalar()

    total_owed_by = session.query(
        func.coalesce(func.sum(Debt.amount), 0)
    ).filter(
        Debt.owner_id == user.id,
        Debt.debt_type == DebtType.OWED_BY
    ).scalar()

    balance = total_owed_to - total_owed_by

    return {
        "success": True,
        "code": status.HTTP_200_OK,
        "message": "Monitoring data retrieved successfully",
        "data": {
            "total_owed_to": total_owed_to,
            "total_owed_by": total_owed_by,
            "balance": balance
        }
    }
