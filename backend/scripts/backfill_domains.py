from db_connect import session
from models import Job

def assign_domain(job_title):
    title = job_title.lower()

    # =========================
    # DATA SCIENCE / ANALYTICS
    # =========================
    if any(k in title for k in [
        "data", "analyst", "scientist", "ml", "ai",
        "quantitative", "research assistant", "research associate"
    ]):
        return "Data Science/Analytics"

    # =========================
    # ENGINEERING
    # =========================
    if any(k in title for k in [
        "engineer", "developer", "devops", "backend",
        "frontend", "software", "android", "flutter",
        "cloud", "systems", "python"
    ]):
        return "Engineering"

    # =========================
    # MARKETING
    # =========================
    if any(k in title for k in [
        "marketing", "seo", "social media", "brand",
        "content", "growth", "performance", "media"
    ]):
        return "Marketing"

    # =========================
    # HR
    # =========================
    if any(k in title for k in [
        "hr", "human resource", "talent", "recruitment"
    ]):
        return "HR"

    # =========================
    # DESIGN
    # =========================
    if any(k in title for k in [
        "design", "ux", "ui", "graphic", "motion",
        "visual", "product designer"
    ]):
        return "Design"

    # =========================
    # FINANCE / OPS
    # =========================
    if any(k in title for k in [
        "finance", "financial", "risk", "credit",
        "operations", "fp&a", "treasury", "compliance"
    ]):
        return "Finance/Ops"

    # =========================
    # SECURITY
    # =========================
    if any(k in title for k in [
        "security", "cyber", "soc"
    ]):
        return "Security"

    # =========================
    # FILTER / GENERAL
    # =========================
    if any(k in title for k in [
        "lecturer", "teaching", "trainer"
    ]):
        return "General Tech/Professional"

    return "General Tech/Professional"


# =========================
# BACKFILL
# =========================

jobs = session.query(Job).all()

updated = 0

for job in jobs:
    if not job.domain or job.domain.strip() == "":
        job.domain = assign_domain(job.job_title)
        updated += 1

session.commit()

print(f"Updated {updated} jobs")