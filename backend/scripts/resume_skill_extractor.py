import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_connect import session
from models import Resume, Skill, ResumeSkill

# -------------------------
# NORMALIZATION MAP
# -------------------------

SKILL_MAP = {
    "js": "javascript",
    "node.js": "node",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "reactjs": "react",
    "py": "python"
}

# -------------------------
# LOAD SKILLS FROM DB
# -------------------------

def load_skills():
    skills = session.query(Skill).all()
    return {s.skill_name: s.id for s in skills}

# -------------------------
# BUILD REGEX PATTERNS
# -------------------------

def build_patterns(skill_dict):
    patterns = {}

    for skill in skill_dict.keys():
        pattern = r"\b" + re.escape(skill) + r"\b"
        patterns[skill] = re.compile(pattern)

    return patterns

# -------------------------
# LIGHT NORMALIZATION
# -------------------------

def normalize_text(text):
    text = text.replace("\x00", "")

    # Apply normalization mapping only
    for short, full in SKILL_MAP.items():
        text = re.sub(rf"\b{re.escape(short)}\b", full, text)

    return text

# -------------------------
# EXTRACT SKILLS
# -------------------------

def extract_skills(text, patterns):
    found = set()

    for skill, pattern in patterns.items():
        if pattern.search(text):
            found.add(skill)

    return list(found)

# -------------------------
# MAIN PROCESS
# -------------------------

def process_resumes():
    skill_dict = load_skills()
    patterns = build_patterns(skill_dict)

    resumes = session.query(Resume).all()

    total_added = 0
    total_skipped = 0

    for resume in resumes:
        if not resume.cleaned_text:
            continue

        text = normalize_text(resume.cleaned_text)

        skills_found = extract_skills(text, patterns)

        for skill_name in skills_found:
            skill_id = skill_dict[skill_name]

            exists = session.query(ResumeSkill).filter_by(
                resume_id=resume.id,
                skill_id=skill_id
            ).first()

            if exists:
                total_skipped += 1
                continue

            mapping = ResumeSkill(
                resume_id=resume.id,
                skill_id=skill_id
            )

            session.add(mapping)
            total_added += 1

    session.commit()

    print("\n=== RESUME SKILL EXTRACTION SUMMARY ===")
    print(f"Skills Added: {total_added}")
    print(f"Duplicates Skipped: {total_skipped}")


if __name__ == "__main__":
    process_resumes()