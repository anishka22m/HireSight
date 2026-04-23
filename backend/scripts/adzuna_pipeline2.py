import requests
import re
import hashlib
from db_connect import session
from models import Job

# =========================
# CONFIG
# =========================

APP_ID = "f9e7aa2a"
APP_KEY = "b950747941f707dd9027083b425d8e79"

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search"

SEARCH_ROLES = [
    "data analyst",
    "data scientist",
    "software engineer",
    "backend developer",
    "frontend developer",
    "web developer",
    "devops engineer",
    "cyber security analyst",
    "hr executive",
    "digital marketing",
    "ui ux designer",
    "financial analyst"
]

MAX_PAGES = 3  # controls how much data you fetch per role

# =========================
# ROLE NORMALIZATION
# =========================

ROLE_MAP = {
    "data": "Data Science/Analytics",
    "analyst": "Data Science/Analytics",
    "scientist": "Data Science/Analytics",

    "engineer": "Engineering",
    "developer": "Engineering",
    "sde": "Engineering",

    "marketing": "Marketing",
    "seo": "Marketing",

    "hr": "HR",
    "human resource": "HR",

    "design": "Design",
    "ux": "Design",
    "ui": "Design",

    "finance": "Finance/Ops",
    "risk": "Finance/Ops",

    "security": "Security",
    "cyber": "Security"
}

def assign_domain(job_title):
    title = job_title.lower()
    for key, domain in ROLE_MAP.items():
        if key in title:
            return domain
    return "General Tech/Professional"

# =========================
# TEXT CLEANING
# =========================

def clean_text(text):
    text = re.sub(r"<.*?>", "", text)  # remove HTML
    text = re.sub(r"\s+", " ", text)   # remove extra spaces
    return text.strip()

# =========================
# HASH GENERATION (DEDUP)
# =========================

# def generate_job_hash(title, company, location, description):
#     text = f"{title}{company}{location}{description}"
#     return hashlib.md5(text.encode()).hexdigest()

def normalize_text(text):
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text
# =========================
# DUPLICATE CHECK
# =========================

def job_exists(title, company, location):
    title_n = normalize_text(title)
    company_n = normalize_text(company)
    location_n = normalize_text(location)

    existing_jobs = session.query(Job).filter(
        Job.job_title.ilike(f"%{title_n}%"),
        Job.company.ilike(company_n),
        Job.location.ilike(location_n)
    ).first()

    return existing_jobs is not None

# =========================
# FETCH + INSERT
# =========================

def fetch_and_store():
    total_inserted = 0
    total_skipped = 0

    for query in SEARCH_ROLES:
        print(f"\nFetching for: {query}")

        for page in range(1, MAX_PAGES + 1):
            print(f" Page: {page}")

            url = f"{BASE_URL}/{page}"

            params = {
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "results_per_page": 20,
                "what": query,
                "where": "india"
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
            except Exception as e:
                print("Request failed:", e)
                continue

            if "results" not in data:
                print("API Error:", data)
                continue

            for item in data["results"]:
                title = item.get("title", "")
                company = item.get("company", {}).get("display_name", "")
                location = item.get("location", {}).get("display_name", "")
                description = clean_text(item.get("description", ""))

                if not title or not description:
                    continue

                # job_hash = generate_job_hash(title, company, location, description)
                title = normalize_text(title)
                company = normalize_text(company)
                location = normalize_text(location)

                if job_exists(title,company, location):
                    total_skipped += 1
                    continue

                domain = assign_domain(title)

                job = Job(
                    job_title=title,
                    company=company,
                    location=location,
                    description=description,
                    domain=domain,
                    role=query,
                    source="Adzuna"
                )

                session.add(job)
                total_inserted += 1

    session.commit()

    print("\n=== INGESTION SUMMARY ===")
    print(f"Inserted: {total_inserted}")
    print(f"Skipped (duplicates): {total_skipped}")

# =========================
# RUN
# =========================

if __name__ == "__main__":
    fetch_and_store()