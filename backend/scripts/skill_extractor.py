import re
import sys
import os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_connect import session
from models import Job, Skill, JobSkill


# -------------------------
# SKILL DEFINITIONS
# -------------------------

CANONICAL_SKILLS = [
    "python", "java", "backend", "frontend", "react",
    "devops", "cloud", "apis", "infrastructure", "software", "web",
    "analytics", "machine learning", "data analysis", "models",
    "reporting", "insights",
    "seo", "social media", "content", "campaigns",
    "google ads", "branding",
    "recruitment", "onboarding", "payroll",
    "talent acquisition", "employee relations", "compliance",
    "figma", "ui", "ux", "prototyping",
    "graphic design", "visual design",
    "operations", "logistics", "supply chain",
    "inventory", "process optimization",
    "cybersecurity", "endpoint security"
]

SKILL_NORMALIZATION = {
    "py": "python",
    "python3": "python",

    "nodejs": "backend",
    "node.js": "backend",

    "aws": "cloud",
    "azure": "cloud",
    "gcp": "cloud",

    "docker": "devops",
    "kubernetes": "devops",
    "k8s": "devops",

    "ml": "machine learning",
    "ai": "machine learning",
    "data analytics": "analytics",

    "social": "social media",
    "ads": "google ads",

    "hr": "recruitment",

    "ui/ux": "ui",
    "ux/ui": "ux",

    "supplychain": "supply chain",

    "cyber security": "cybersecurity"
}

ALL_SKILL_TERMS = list(set(CANONICAL_SKILLS + list(SKILL_NORMALIZATION.keys())))


# -------------------------
# EXTRACTION FUNCTION
# -------------------------

def extract_skills(text):
    text = text.lower()
    found = set()

    for term in ALL_SKILL_TERMS:
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, text):
            normalized = SKILL_NORMALIZATION.get(term, term)
            found.add(normalized)

    return list(found)


# -------------------------
# DB HELPERS
# -------------------------

def get_or_create_skill(skill_name):
    skill = session.query(Skill).filter_by(skill_name=skill_name).first()

    if not skill:
        skill = Skill(skill_name=skill_name)
        session.add(skill)
        session.flush()  # get id

    return skill


# -------------------------
# MAIN PIPELINE
# -------------------------

def process_jobs():
    jobs = session.query(Job).all()

    total_mappings = 0

    for job in jobs:
        skills = extract_skills(job.description)

        for skill_name in skills:
            skill = get_or_create_skill(skill_name)

            # check if mapping exists
            exists = session.query(JobSkill).filter_by(
                job_id=job.id,
                skill_id=skill.id
            ).first()

            if not exists:
                mapping = JobSkill(
                    job_id=job.id,
                    skill_id=skill.id
                )
                session.add(mapping)
                total_mappings += 1

    session.commit()
    print(f"Total mappings added: {total_mappings}")


# -------------------------
# RUN
# -------------------------

if __name__ == "__main__":
    process_jobs()