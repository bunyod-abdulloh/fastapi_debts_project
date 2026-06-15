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


@router.get("/", status_code=status.HTTP_200_OK)
async def get_debts(
        debt_type: str | None = None,
        person_name: str | None = None,
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

    query = session.query(Debt).filter(
        Debt.owner_id == user.id
    )

    # Berilgan qarzlar
    if debt_type == "owed_to":
        query = query.filter(
            Debt.debt_type == DebtType.OWED_TO
        )

    # Olingan qarzlar
    elif debt_type == "owed_by":
        query = query.filter(
            Debt.debt_type == DebtType.OWED_BY
        )

    # Bir odam bo'yicha qarzlar
    elif debt_type == "individual":

        if not person_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="person_name is required when debt_type=individual"
            )

        query = query.filter(
            Debt.person_name.ilike(f"%{person_name}%")
        )

    # Noto'g'ri debt_type
    elif debt_type is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="debt_type must be one of: owed_to, owed_by, individual"
        )

    debts = query.order_by(
        Debt.created_at.desc()
    ).all()

    return {
        "success": True,
        "code": status.HTTP_200_OK,
        "message": "Debts retrieved successfully",
        "count": len(debts),
        "data": jsonable_encoder(debts)
    }



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
        session.refresh(new_debt)

        response = {
            "success": True,
            "code": status.HTTP_201_CREATED,
            "message": "Debt is created successfully",
            "data": {
                "id": new_debt.id,
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


@router.put("/update/{debt_id}", status_code=status.HTTP_200_OK)
async def update_debt(
        debt_id: int,
        update_data: DebtCreateSchema,
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

    debt = session.query(Debt).filter(
        Debt.id == debt_id,
        Debt.owner_id == user.id
    ).first()

    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt not found"
        )

    debt.debt_type = update_data.debt_type
    debt.person_name = update_data.person_name
    debt.amount = update_data.amount
    debt.currency = update_data.currency
    debt.description = update_data.description
    debt.date_due = update_data.date_due

    session.commit()

    return {
        "success": True,
        "message": "Debt updated successfully"
    }


@router.delete("/delete/{debt_id}", status_code=status.HTTP_200_OK)
async def delete_debt(
        debt_id: int,
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

    debt = session.query(Debt).filter(
        Debt.id == debt_id,
        Debt.owner_id == user.id
    ).first()

    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt not found"
        )

    session.delete(debt)
    session.commit()

    return {
        "success": True,
        "message": "Debt deleted successfully"
    }


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
