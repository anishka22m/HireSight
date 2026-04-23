from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# CHANGE PASSWORD HERE
DATABASE_URL = "postgresql://postgres:anishka@localhost:5432/hiresight"

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

print("Connected to DB successfully!")