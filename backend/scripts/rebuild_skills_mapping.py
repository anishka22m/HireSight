# =========================
# SETUP — IMPORTS + PATH
# =========================

import sys
import os
import re

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_connect import session
from models import Job, Skill, JobSkill, Resume, ResumeSkill


# =========================
# LOAD SKILLS
# =========================

def load_skills():
    skills = session.query(Skill).all()
    return {s.skill_name: s.id for s in skills}


# =========================
# CLEAN TEXT (SAFE)
# =========================

def clean_text(text):
    if not text:
        return ""
    return text.lower()


# =========================
# REGEX MATCH FUNCTION
# =========================

def skill_in_text(skill, text):
    pattern = r"\b" + re.escape(skill) + r"\b"
    return re.search(pattern, text) is not None


# =========================
# REBUILD JOB_SKILLS
# =========================

def rebuild_job_skills():
    print("\nRebuilding job_skills...")

    skill_map = load_skills()
    jobs = session.query(Job).all()

    inserted = 0

    for job in jobs:
        text = clean_text(job.description)

        for skill_name, skill_id in skill_map.items():

            if skill_in_text(skill_name, text):
                mapping = JobSkill(
                    job_id=job.id,
                    skill_id=skill_id
                )
                session.add(mapping)
                inserted += 1

    session.commit()
    print(f"Inserted {inserted} job-skill mappings")


# =========================
# REBUILD RESUME_SKILLS
# =========================

def rebuild_resume_skills():
    print("\nRebuilding resume_skills...")

    skill_map = load_skills()
    resumes = session.query(Resume).all()

    inserted = 0

    for resume in resumes:
        text = clean_text(resume.cleaned_text)

        for skill_name, skill_id in skill_map.items():

            if skill_in_text(skill_name, text):
                mapping = ResumeSkill(
                    resume_id=resume.id,
                    skill_id=skill_id
                )
                session.add(mapping)
                inserted += 1

    session.commit()
    print(f"Inserted {inserted} resume-skill mappings")


# =========================
# MAIN RUN
# =========================

if __name__ == "__main__":

    print("Connected to DB successfully!")

    # IMPORTANT: clear old mappings first
    print("\nClearing old mappings...")

    session.query(JobSkill).delete()
    session.query(ResumeSkill).delete()
    session.commit()

    print("Old mappings cleared.")

    # Rebuild mappings
    rebuild_job_skills()
    rebuild_resume_skills()

    print("\nDONE — Skill mappings rebuilt successfully.")