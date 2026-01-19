import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://yurii:yuriipy@localhost:5432/scrapper")

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Create table")


def get_db():
    db = SessionLocal()

    try:
        yield db
    except:
        db.close()
