from database import engine, Base

from models import User, Debt, UserSettings

Base.metadata.create_all(bind=engine)