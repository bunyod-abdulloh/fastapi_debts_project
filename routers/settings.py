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
    prefix="/settings",
)

session = session(bind=engine)


@router.get("/")
async def welcome(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", )
    return {"message": "Bu auth_route signup sahifasi"}