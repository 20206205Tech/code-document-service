from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import env
from utils.log_function import log_function

engine = create_engine(env.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@log_function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
