from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT

from database import session, engine
from models import User, Debt, DebtType
from schemas import DebtCreateSchema

router = APIRouter(
    prefix="/debt",
)

session = session(bind=engine)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_debt(update_data: DebtCreateSchema, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    if user:
        new_debt = Debt(
            owner_id=user.id,
            debt_type=update_data.debt_type,
            person_name=update_data.person_name,
            amount=update_data.amount,
            currency=update_data.currency,
            description=update_data.description,
            date_due=update_data.date_due,
        )
        session.add(new_debt)
        session.commit()

        response = {
            "success": True,
            "code": status.HTTP_201_CREATED,
            "message": "Debt is created successfully",
            "data": {
                "owner_id": user.id,
                "debt_type": update_data.debt_type,
                "person_name": update_data.person_name,
                "amount": update_data.amount,
                "currency_type": update_data.currency,
                "description": update_data.description,
                "date_due": update_data.date_due,
            }
        }
        return jsonable_encoder(response)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized"
        )


@router.get("/list", status_code=status.HTTP_200_OK)
async def list_debts(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Enter valid access token"
        )

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized"
        )

    debts = session.query(Debt).filter(
        Debt.owner_id == user.id
    ).all()

    return {
        "success": True,
        "code": status.HTTP_200_OK,
        "message": "Debts retrieved successfully",
        "count": len(debts),
        "data": jsonable_encoder(debts)
    }


@router.get("/debt-type/{debt_type}", status_code=status.HTTP_200_OK)
async def get_debts_by_type(
        debt_type: DebtType,
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
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized"
        )

    debts = session.query(Debt).filter(
        Debt.owner_id == user.id,
        Debt.debt_type == debt_type
    ).all()

    return {
        "success": True,
        "code": status.HTTP_200_OK,
        "message": "Debts retrieved successfully",
        "count": len(debts),
        "data": jsonable_encoder(debts)
    }
