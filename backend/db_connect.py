from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Get absolute path to scripts/keys.env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, "scripts", "keys.env")

load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

print("DB URL:", DATABASE_URL)
print("Connected to DB successfully!")