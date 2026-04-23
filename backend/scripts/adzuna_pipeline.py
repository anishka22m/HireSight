import requests
import re
from db_connect import session
from models import Job

# =========================
# CONFIG
# =========================

APP_ID = "f9e7aa2a"
APP_KEY = "b950747941f707dd9027083b425d8e79"

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

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
# DUPLICATE CHECK
# =========================

def job_exists(title, company):
    return session.query(Job).filter_by(
        job_title=title,
        company=company
    ).first() is not None

# =========================
# FETCH + INSERT
# =========================

def fetch_and_store():
    total_inserted = 0

    for query in SEARCH_ROLES:
        print(f"\nFetching for: {query}")

        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 20,
            "what": query,
            "where": "india"
        }

        response = requests.get(BASE_URL, params=params)
        data = response.json()

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

            # Avoid duplicates
            if job_exists(title, company):
                continue

            # Assign domain
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
    print(f"\nTotal jobs inserted: {total_inserted}")


# =========================
# RUN
# =========================

if __name__ == "__main__":
    fetch_and_store()