import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import re
from nltk.stem import SnowballStemmer
from db_connect import session
from models import Skill, JobSkill, ResumeSkill

# --- 1. SETUP VALIDATOR ---
stemmer = SnowballStemmer("english")

def load_gold_roots(file_path):
    df = pd.read_csv(file_path)
    # Filter to atomic skills (1-3 words) and strip context
    gold_roots = set()
    for label in df['preferredLabel']:
        clean = re.sub(r'\(.*\)', '', str(label)).strip().lower()
        if len(clean.split()) <= 3:
            root = " ".join([stemmer.stem(w) for w in clean.split()])
            gold_roots.add(root)
    return gold_roots

def is_valid(skill_name, gold_roots):
    word_root = " ".join([stemmer.stem(w) for w in skill_name.lower().split()])
    for gold_root in gold_roots:
        if word_root in gold_root:
            return True
    return False

# --- 2. THE PURGE LOGIC ---
def purge_noise_skills():
    print("Loading ESCO Gold Roots...")
    gold_roots = load_gold_roots("backend\\data\\skills_en.csv")
    
    print("Fetching existing skills from Database...")
    all_skills = session.query(Skill).all()
    total_initial = len(all_skills)
    
    deleted_count = 0
    kept_skills = []

    print(f"Analyzing {total_initial} skills...")
    for skill in all_skills:
        if not is_valid(skill.skill_name, gold_roots):
            # It's noise! (e.g., 'brands', 'environment', 'team')
            # First, delete mappings to avoid foreign key errors
            session.query(JobSkill).filter(JobSkill.skill_id == skill.id).delete()
            session.query(ResumeSkill).filter(ResumeSkill.skill_id == skill.id).delete()
            # Then delete the skill itself
            session.delete(skill)
            deleted_count += 1
        else:
            kept_skills.append(skill.skill_name)

    session.commit()
    print(f"\n--- PURGE COMPLETE ---")
    print(f"Initial Skills: {total_initial}")
    print(f"Skills Deleted (Noise): {deleted_count}")
    print(f"Skills Retained (Valid): {total_initial - deleted_count}")
    
    print("\nExamples of Kept Skills:")
    print(kept_skills[:10])

if __name__ == "__main__":
    purge_noise_skills()