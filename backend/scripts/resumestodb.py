import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys

# Add backend folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Load ENV
ENV_PATH = r"C:\Users\anish\Desktop\Mp - Refs\MajorProject_Code\HireSight\backend\scripts\keys.env"
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

# DB setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Import model AFTER engine setup
from models import Resume

# Folder path
RESUME_FOLDER = r"datasets\convertedresumes"

# -------------------------
# CLEANING
# -------------------------

def clean_text(text):
    text = text.replace("\x00", "")  # REMOVE NULL BYTES
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()
# -------------------------
# DUPLICATE CHECK (basic)
# -------------------------

def resume_exists(file_name):
    return session.query(Resume).filter_by(file_name=file_name).first() is not None

# -------------------------
# MAIN INGESTION
# -------------------------

def ingest_resumes():
    total = 0
    skipped = 0

    files = os.listdir(RESUME_FOLDER)

    for file in files:
        if not file.endswith(".txt"):
            continue

        print(f"Processing: {file}")

        if resume_exists(file):
            print("Already exists, skipping")
            skipped += 1
            continue

        file_path = os.path.join(RESUME_FOLDER, file)

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
                raw_text = raw_text.replace("\x00", "")
        except:
            print("Error reading file, skipping")
            skipped += 1
            continue

        if not raw_text or len(raw_text) < 100:
            print("Low content, skipping")
            skipped += 1
            continue

        cleaned = clean_text(raw_text)

        resume = Resume(
            file_name=file,
            extracted_text=raw_text,
            cleaned_text=cleaned
        )

        session.add(resume)
        total += 1

    session.commit()

    print("\n=== RESUME INGESTION SUMMARY ===")
    print(f"Inserted: {total}")
    print(f"Skipped: {skipped}")

# -------------------------
# RUN
# -------------------------

if __name__ == "__main__":
    ingest_resumes()