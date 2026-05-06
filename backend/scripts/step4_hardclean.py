import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from nltk.stem import SnowballStemmer
from db_connect import session
from models import Skill, JobSkill, ResumeSkill

# Initialize stemmer
stemmer = SnowballStemmer("english")

# THE BLACKLIST - Persistent noise terms to be removed
BLACKLIST_WORDS = {
    "com", "use", "soc", "lab", "core", "model", "project", 
    "environment", "type", "healthcare", "people", "site",
    "standard", "unit", "access", "intern", "identity","health",
    "implement","multi","training"
}

def execute_hard_purge():
    print("--- INITIATING FINAL SKILL PURGE ---")
    
    # Fetch all skills currently in the DB
    db_skills = session.query(Skill).all()
    deleted_count = 0
    
    for skill in db_skills:
        name_lower = skill.skill_name.lower().strip()
        root = stemmer.stem(name_lower)
        
        should_delete = False
        # Rule 1: Manual Blacklist
        if name_lower in BLACKLIST_WORDS or root in BLACKLIST_WORDS:
            should_delete = True
            
        # Rule 2: Short fragments (3 chars or less) unless tech-specific
        elif len(name_lower) <= 3 and name_lower not in ["sql", "aws", "git", "php", "r", "go"]:
            should_delete = True

        if should_delete:
            print(f"Deleting noise skill: '{name_lower}'")
            # 1. Delete children (mappings) first to satisfy Foreign Key constraints
            session.query(JobSkill).filter(JobSkill.skill_id == skill.id).delete()
            session.query(ResumeSkill).filter(ResumeSkill.skill_id == skill.id).delete()
            # 2. Delete the parent skill
            session.delete(skill)
            deleted_count += 1

    session.commit()
    print(f"\n--- PURGE COMPLETE ---")
    print(f"Total noise skills permanently removed: {deleted_count}")
    print("Your database is now clean of identified noise.")

if __name__ == "__main__":
    execute_hard_purge()    