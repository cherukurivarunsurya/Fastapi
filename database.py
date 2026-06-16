from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 

DATABASE_URL = "postgresql://postgres:Username@localhost:5432/table_db"

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

