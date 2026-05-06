import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from db_connect import session
from models import Job, Skill, JobSkill, ResumeSkill

def run_tfidf_refinement():
    print("Fetching jobs and grouping by domain...")
    jobs = session.query(Job).all()
    
    domain_docs = {}
    for job in jobs:
        if job.domain not in domain_docs:
            domain_docs[job.domain] = ""
        domain_docs[job.domain] += " " + (job.description if job.description else "").lower()

    domains = list(domain_docs.keys())
    documents = [domain_docs[d] for d in domains]

    # Fetch skills from DB
    db_skills = session.query(Skill).all()
    skill_names = [s.skill_name for s in db_skills]
    
    # FIX: Use a pattern that allows spaces so phrases like 'data science' get scored
    vectorizer = TfidfVectorizer(vocabulary=skill_names, token_pattern=r"(?u)\b[\w\s+#]+\b")
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    tfidf_df = pd.DataFrame(
        tfidf_matrix.toarray(), 
        columns=vectorizer.get_feature_names_out(), 
        index=domains
    )

    print("\n--- REFINED TF-IDF DOMAIN SCORES ---")
    
    # THRESHOLD: If a skill's max uniqueness across all domains is below 0.05, it's global noise
    THRESHOLD = 0.05 
    noise_to_delete = []

    for skill_obj in db_skills:
        name = skill_obj.skill_name
        max_score = tfidf_df[name].max() if name in tfidf_df.columns else 0
        print(f"Skill: {name:<20} | Max Uniqueness: {max_score:.4f}")
        
        if max_score < THRESHOLD:
            noise_to_delete.append(skill_obj)

    print(f"\nSkills identified as Global Noise: {[s.skill_name for s in noise_to_delete]}")
    
    # THE PURGE FIX: Delete mappings first, then the skill
    if noise_to_delete:
        for skill in noise_to_delete:
            # Delete children first to satisfy Foreign Key constraints
            session.query(JobSkill).filter(JobSkill.skill_id == skill.id).delete()
            session.query(ResumeSkill).filter(ResumeSkill.skill_id == skill.id).delete()
            # Delete the parent
            session.delete(skill)
        
        session.commit()
        print(f"Successfully purged {len(noise_to_delete)} noise skills and their mappings.")

if __name__ == "__main__":
    run_tfidf_refinement()