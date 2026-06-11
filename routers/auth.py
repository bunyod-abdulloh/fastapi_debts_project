import datetime

from fastapi import APIRouter, status, HTTPException, Depends, Security
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from database import session, engine
from models import User
from schemas import LoginModel
from schemas import SignUpModel

router = APIRouter(
    prefix="/auth",
)

session = session(bind=engine)


@router.get("/")
async def welcome(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", )
    return {"message": "Bu auth_route signup sahifasi"}


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This email already registered")

    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This username already registered")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff,
    )

    session.add(new_user)
    session.commit()
    return new_user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
    db_user = session.query(User).filter(
        or_(
            User.username == user.username_or_email,
            User.email == user.username_or_email,
        )
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username/email or password",
        )

    if not check_password_hash(db_user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username/email or password",
        )

    access_lifetime = datetime.timedelta(minutes=1)
    refresh_lifetime = datetime.timedelta(days=3)

    access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)
    refresh_token = Authorize.create_refresh_token(subject=db_user.username, expires_time=refresh_lifetime)

    return jsonable_encoder({
        "success": True,
        "code": status.HTTP_200_OK,
        "message": "Logged in successfully",
        "token": {
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    })


security = HTTPBearer()


@router.get("/login/refresh/")
async def refresh(
        credentials: HTTPAuthorizationCredentials = Security(security),
        Authorize: AuthJWT = Depends()
):
    try:
        access_lifetime = datetime.timedelta(minutes=1)
        refresh_lifetime = datetime.timedelta(days=3)
        Authorize.jwt_refresh_token_required()
        current_username = Authorize.get_jwt_subject()

        db_user = session.query(User).filter(User.username == current_username).first()

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        new_access_token = Authorize.create_access_token(subject=db_user.username, expires_time=access_lifetime)

        response = {
            "success": True,
            "code": status.HTTP_200_OK,
            "message": "New access token created",
            "data": {
                "access_token": new_access_token,

            }
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token", )
