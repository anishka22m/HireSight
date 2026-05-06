#All imports
import os
import re
import pdfplumber
import numpy as np
import joblib

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from backend.db_connect import session
from backend.models import Job, Skill
from backend.models import JobSkill

import sys

#Path definitions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


#Loading the pre-trained SVM model and BERT model for domain classification and skill extraction
svm_model = joblib.load(

    os.path.join(BASE_DIR, "models/domain_classifier_v2.pkl")
)

bert_model = SentenceTransformer('all-MiniLM-L6-v2')


#Function to extract text from PDF resumes using pdfplumber
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

#Function to clean the text by converting it to lowercase and removing extra whitespace
def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

#Function to predict the domain of the resume using the pre-trained SVM model and BERT embeddings
def predict_domain(text):
    embedding = bert_model.encode([text])
    return svm_model.predict(embedding)[0]

def load_skills():
    skills = session.query(Skill).all()
    return {s.skill_name: s.id for s in skills}



#Function to fetch all skills required for jobs in a specific domain from the database
def get_job_skills_by_domain(domain):
    """
    Fetch domain-specific required skills
    """

    jobs = session.query(Job).filter(Job.domain == domain).limit(50).all()

    job_ids = [job.id for job in jobs]

    if not job_ids:
        return set()

    mappings = session.query(JobSkill).filter(JobSkill.job_id.in_(job_ids)).all()

    skill_ids = {m.skill_id for m in mappings}

    skills = session.query(Skill).filter(Skill.id.in_(skill_ids)).all()

    return {s.skill_name for s in skills}


#Function to extract skills from the resume text by matching it against the skills required for the predicted domain
def extract_resume_skills(text, skill_map):
    """
    Extract skills from resume using DB skills
    """

    found = set()

    for skill in skill_map.keys():
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            found.add(skill)

    return found

# def get_embedding(text):
#     return bert_model.encode([text])

# STEP 1 — Fetch jobs for predicted domain
def get_jobs_by_domain(domain):
    """
    Get relevant jobs for a domain (used for similarity + context)
    Limit to avoid heavy computation
    """
    return session.query(Job).filter(Job.domain == domain).limit(50).all()

# STEP 2 — Compute skill match score
def compute_skill_score(resume_skills, job_skills):

    if not job_skills:
        return 0, set(), set()

    matched = resume_skills & job_skills
    missing = job_skills - resume_skills

    # NEW: normalize denominator
    effective_total = min(len(job_skills), 25)   # cap demand

    score = len(matched) / effective_total

    # cap to 1
    score = min(score, 1)

    return score, matched, missing

# STEP 3 — Semantic similarity using BERT
def compute_similarity(resume_text, domain):
    """
    Compare resume with job descriptions in same domain
    """

    # fetch jobs (limit for performance)
    jobs = session.query(Job).filter(Job.domain == domain).limit(50).all()

    if not jobs:
        return 0

    # encode resume
    resume_emb = bert_model.encode([resume_text])

    # encode job descriptions
    job_texts = [job.description for job in jobs]
    job_embs = bert_model.encode(job_texts)

    # cosine similarity
    sims = cosine_similarity(resume_emb, job_embs)

    # take best match
    return float(np.max(sims))

# STEP 4 — MAIN ANALYSIS FUNCTION
# --- HELPER FOR WEIGHTED SCORING ---
def get_weighted_benchmarks(domain):
    """
    Fetches the 'Ground Truth' skills and importance for a specific domain.
    Used for weighted scoring and prioritized suggestions.
    """
    from sqlalchemy import text
    query = text("""
        SELECT s.skill_name, sb.importance_score 
        FROM skill_benchmarks sb
        JOIN skills s ON sb.skill_id = s.id
        WHERE sb.domain = :dom
    """)
    result = session.execute(query, {"dom": domain}).fetchall()
    return {row[0]: row[1] for row in result}




def generate_suggestion(score, domain, priority_gaps):
    """Generates professional framing for the dashboard."""
    top_two = [g['name'] for g in priority_gaps[:2]]
    skills_str = " and ".join(top_two) if top_two else "core technical areas"
    if score < 50:
        return f"Your profile shows potential, but to align with the {domain} gold standard, immediate focus is required on {skills_str}."
    elif score < 75:
        return f"You have a solid technical foundation. You can increase your marketability by bridging gaps in {skills_str}."
    return f"Excellent alignment with the {domain} market. Consider refining expertise in {top_two[0] if top_two else 'advanced niche tools'}."


# --- UPDATED MAIN ANALYSIS FUNCTION (WITH TARGET WEIGHT) ---
def analyze_resume(pdf_path):
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned = clean_text(raw_text)
    domain = predict_domain(cleaned)
    skill_map = load_skills()
    resume_skills_set = extract_resume_skills(cleaned, skill_map)
    benchmarks = get_weighted_benchmarks(domain)
    
    matched = []
    missing = []
    earned_weight = 0

    # 1. Calculate the 'Target Weight' (The denominator)
    # We take the top 25 highest-weighted skills in the domain to represent a 'Full Match'
    top_benchmark_weights = sorted(benchmarks.values(), reverse=True)[:16 ]
    target_weight = sum(top_benchmark_weights)

    # 2. Map and Sum Earned Weight
    for skill_name, importance in benchmarks.items():
        if skill_name in resume_skills_set:
            matched.append({"name": skill_name, "importance": importance})
            earned_weight += importance
        else:
            missing.append({"name": skill_name, "importance": importance})

    # 3. Calculate Normalized Skill Score
    # We cap it at 1.0 so a candidate doesn't get 110% 
    skill_score = min(earned_weight / target_weight, 1.0) if target_weight > 0 else 0

    # 4. Final Combined Score (Balanced 50/50)
    semantic_score = compute_similarity(cleaned, domain)
    final_score = (0.5 * skill_score) + (0.5 * semantic_score)

    # 5. Sorting for Output
    matched_sorted = sorted(matched, key=lambda x: x['importance'], reverse=True)
    missing_sorted = sorted(missing, key=lambda x: x['importance'], reverse=True)

    # Calculate final returned values
    suggestion = generate_suggestion(final_score * 100, domain, missing_sorted)
    high_priority = [g['name'].title() for g in missing_sorted if g['importance'] == 5]

    return {
        "domain": domain,
        "score": round(final_score * 100, 2),
        "skill_score": round(skill_score * 100, 2),
        "semantic_score": round(semantic_score * 100, 2),
        "matched_skills": matched_sorted,
        "priority_gaps": missing_sorted[:8], # Top 8 important ones
        "high_priority_recommendations": high_priority[:3],
        "improvement_suggestion": suggestion,
        "matched_count": len(matched),
        "missing_count": len(missing),
        "raw_text": raw_text
    }
def print_analysis(result):
    print("\n" + "="*60)
    print("RESUME ANALYSIS REPORT (WEIGHTED)")
    print("="*60)

    print(f"\nPredicted Domain : {result['domain']}")
    print(f"Final Match Score: {result['score']}%")
    print(f"Skill Match      : {result['skill_score']}% (Weighted)")
    print(f"Semantic Feel    : {result['semantic_score']}%")

    print("\n" + "-"*60)
    # Extracting just the names for the 'Matched' list
    matched_names = [s['name'] for s in result['matched_skills']]
    print(f"MATCHED SKILLS ({result['matched_count']}):")
    print("-" * 60)
    print(", ".join(matched_names[:20])) # Show first 20 names

    print("\n" + "-"*60)
    # Showing 'Priority Gaps' with their Importance Level
    print(f"PRIORITY GAPS (Top {len(result['priority_gaps'])} out of {result['missing_count']} total missing):")
    print("-" * 60)
    for gap in result['priority_gaps']:
        print(f" - {gap['name'].ljust(25)} (Importance: {gap['importance']}/5)")

    print("\n" + "="*60 + "\n")

# # Run the analysis
# if __name__ == "__main__":
#     # Ensure this path is correct for your local machine
#     resume_path = r"backend\ML Resume V1.1 - Laksh Nijhawan.pdf"
    
#     try:
#         result = analyze_resume(resume_path)
#         print_analysis(result)
#     except Exception as e:
#         print(f"Error during analysis: {e}")