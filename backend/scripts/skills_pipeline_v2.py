# =========================
# STEP 1 — LOAD JOB DATA
# =========================
import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_connect import session
from models import Job

def fetch_job_descriptions(limit=None):
    """
    Fetch job descriptions from DB
    """
    query = session.query(Job)

    if limit:
        query = query.limit(limit)

    jobs = query.all()

    job_data = []

    for job in jobs:
        if job.description:
            job_data.append({
                "id": job.id,
                "description": job.description,
                "domain": job.domain
            })

    print(f"Fetched {len(job_data)} job descriptions")

    return job_data


# =========================
# STEP 2 — TEXT PREPROCESSING
# =========================

import re

def clean_text(text):
    """
    Clean job description text for skill extraction
    """

    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r"<.*?>", " ", text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Keep only alphabets, numbers, +, # (important for C++, C#)
    text = re.sub(r"[^a-z0-9+#\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def preprocess_jobs(job_data):
    """
    Apply cleaning to all job descriptions
    """

    processed = []

    for job in job_data:
        cleaned = clean_text(job["description"])

        if cleaned:  # skip empty after cleaning
            processed.append({
                "id": job["id"],
                "domain": job["domain"],
                "cleaned_text": cleaned
            })

    print(f"Processed {len(processed)} job descriptions")

    return processed


# =========================
# STEP 3 — N-GRAM EXTRACTION
# =========================

from collections import Counter


def generate_ngrams(tokens, n):
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


def extract_candidate_skills(processed_data, min_freq=5):
    """
    Extract candidate skills using n-grams + frequency filtering
    """

    all_candidates = []

    for job in processed_data:
        text = job["cleaned_text"]
        tokens = text.split()

        # 1-grams
        unigrams = tokens

        # 2-grams
        bigrams = generate_ngrams(tokens, 2)

        # 3-grams
        trigrams = generate_ngrams(tokens, 3)

        all_candidates.extend(unigrams)
        all_candidates.extend(bigrams)
        all_candidates.extend(trigrams)

    # Count frequency
    freq = Counter(all_candidates)

    # Filter by frequency threshold
    candidates = {
        skill: count
        for skill, count in freq.items()
        if count >= min_freq and len(skill) > 2
    }

    print(f"Total candidate skills (after filtering): {len(candidates)}")

    return candidates


# =========================
# STEP 4 — FILTER + NORMALIZE (FINAL FIXED)
# =========================

from nltk.corpus import stopwords
import nltk

STOP_WORDS = set(stopwords.words('english'))
nltk.download('averaged_perceptron_tagger_eng')
CUSTOM_STOPWORDS = {
    # existing
    "experience", "role", "job", "work", "team", "company",
    "candidate", "responsibilities", "skills", "requirements",
    "looking", "support", "years", "strong", "ability",
    "knowledge", "good", "excellent", "working",

    # NEW (from your bad output)
    "data", "using", "based", "across", "key", "high",
    "business", "solutions", "system", "systems",
    "process", "processes", "development",
    "performance", "location", "description",
    "hiring", "candidates", "operations", "management",
    "building", "teams", "product", "end", "across",
    "analyst", "developer", "engineering"
}

STOP_WORDS = STOP_WORDS.union(CUSTOM_STOPWORDS)


STOP_PHRASES = {
    "job description", "looking for", "responsible for",
    "work closely", "team player", "good communication",
    "ability to", "we are looking", "roles and responsibilities",
    "preferred candidate", "skills required",
    "you will", "we are", "you are", "our team"
}


NORMALIZATION_MAP = {
    "js": "javascript",
    "node js": "node.js",
    "nodejs": "node.js",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "reactjs": "react",
    "html5": "html",
    "css3": "css"
}

MIN_FREQ = 10  # tune between 5–15 

GENERIC_WORDS = {
    "data", "business", "performance", "process",
    "system", "solution", "operations", "management",
    "development", "design", "product", "work"
}


def is_noun_phrase(skill):
    """
    Keep only noun-based phrases
    """
    words = skill.split()
    tags = nltk.pos_tag(words)

    # Keep if at least one noun present
    for word, tag in tags:
        if tag.startswith("NN"):  # NN, NNS, NNP
            return True

    return False

GENERIC_SKILL_WORDS = {
    "tools", "tool", "user", "users",
    "build", "building", "develop", "development",
    "manage", "management", "process", "processes",
    "content", "client", "clients",
    "employee", "employees", "industry",
    "company", "team", "teams",
    "service", "services", "application", "applications",
    "system", "systems", "technology", "tech"
}

def is_valid_skill(skill):
    words = skill.split()

    # 1. Exact stop phrase
    if skill in STOP_PHRASES:
        return False

    # 2. Partial stop phrase match
    for phrase in STOP_PHRASES:
        if phrase in skill:
            return False

    # 3. Remove if all words are stopwords
    if all(w in STOP_WORDS for w in words):
        return False

    # 4. Remove if mostly stopwords (important fix)
    stop_count = sum(1 for w in words if w in STOP_WORDS)
    if stop_count / len(words) > 0.6:
        return False

    # 5. Too short
    if len(skill) < 3:
        return False

    # 6. Too long (likely sentence fragments)
    if len(words) > 3:
        return False

    # 7. Numeric
    if skill.isdigit():
        return False
    
    # 8. Remove overly generic words
    if skill in GENERIC_WORDS:
        return False
    
    # 9. Must be noun-like (important fix)
    if not is_noun_phrase(skill):
        return False
    
    # Remove generic domain words
    if skill in GENERIC_SKILL_WORDS:
        return False

    if skill.endswith(("and", "or", "like")):
        return False
    
    return True


def normalize_skill(skill):
    return NORMALIZATION_MAP.get(skill, skill)

def has_skill_context(skill, text):
    """
    Check if skill appears in meaningful context in job description
    """

    patterns = [
        f"experience with {skill}",
        f"experience in {skill}",
        f"knowledge of {skill}",
        f"proficient in {skill}",
        f"hands on experience with {skill}",
        f"familiar with {skill}",
        f"working with {skill}",
        f"expertise in {skill}"
    ]

    for p in patterns:
        if p in text:
            return True

    return False

def refine_skills(candidates, processed_data): 
    refined = {}

    for skill, count in candidates.items():
        if count < MIN_FREQ:
            continue

        if not is_valid_skill(skill):
            continue

        # NEW: context filtering
        context_match = False

        for job in processed_data:
            if has_skill_context(skill, job["cleaned_text"]):
                context_match = True
                break

        if not context_match:
            continue

        skill = normalize_skill(skill)

        refined[skill] = refined.get(skill, 0) + count

    print(f"Refined skills count: {len(refined)}")

    return refined

def filter_by_resume_presence(refined_skills):
    """
    Keep only skills that also appear in resumes
    """

    from models import Resume
    resumes = session.query(Resume).all()

    resume_text = " ".join([r.cleaned_text.lower() for r in resumes if r.cleaned_text])

    final = {}

    for skill, count in refined_skills.items():
        if skill in resume_text:
            final[skill] = count

    print(f"After resume filtering: {len(final)}")

    return final

def insert_skills_into_db(final_skills):
    from models import Skill

    inserted = 0

    for skill_name in final_skills.keys():
        skill = Skill(skill_name=skill_name)
        session.add(skill)
        inserted += 1

    session.commit()
    print(f"Inserted {inserted} skills into DB")
# =========================
# TEST RUN
# =========================

if __name__ == "__main__":
    data = fetch_job_descriptions()
    processed_data = preprocess_jobs(data)

    candidates = extract_candidate_skills(processed_data)

    refined = refine_skills(candidates, processed_data)

    final_skills = filter_by_resume_presence(refined)

    # top_skills = sorted(refined.items(), key=lambda x: x[1], reverse=True)[:30]

    sorted_skills = sorted(final_skills.items(), key=lambda x: x[1], reverse=True)

    print("\n--- ALL CLEANED SKILLS ---\n")
    for skill, count in sorted_skills:
        print(skill, "->", count)
    
    print("\nTotal final skills:", len(sorted_skills))

    with open("cleaned_skills.txt", "w", encoding="utf-8") as f:
        for skill, count in sorted_skills:
            f.write(f"{skill} -> {count}\n")

    insert_skills_into_db(final_skills)

