from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT

from routers.auth import router as auth_router
from routers.debt import router as debt_router
from schemas import Settings

app = FastAPI()


@AuthJWT.load_config
def config():
    return Settings()


app.include_router(auth_router)
app.include_router(debt_router)


@app.get("/")
async def root():
    return {"message": "Bu asosiy sahifa"}
