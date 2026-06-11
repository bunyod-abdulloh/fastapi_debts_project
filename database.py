from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("postgresql://postgres:postgres@localhost/debtsdb",
                       echo=True)  # echo = True faqat development uchun, productionda olib tashlash kerak

Base = declarative_base()
session = sessionmaker(bind=engine)
