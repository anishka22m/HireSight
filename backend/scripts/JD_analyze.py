import sys
import os

# Fix import path (important for your structure)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_connect import session
from models import Job

import re
from collections import Counter

# -------------------------
# STOPWORDS (basic filter)
# -------------------------
STOPWORDS = {
    "the", "and", "with", "for", "you", "are", "our",
    "this", "that", "will", "have", "from", "your",
    "all", "can", "not", "but", "has", "was", "were",
    "they", "their", "them", "his", "her", "its",
    "who", "what", "when", "where", "how",
    "job", "role", "work", "team", "company",
    "experience", "skills", "required", "ability"
}

# -------------------------
# FETCH DATA FROM DB
# -------------------------
def fetch_job_descriptions():
    jobs = session.query(Job.description).all()
    return [j[0] for j in jobs if j[0]]

# -------------------------
# ANALYZE TEXT
# -------------------------
def analyze_text(job_descriptions):
    all_text = " ".join(job_descriptions).lower()

    # extract words (only alphabets, length >=3)
    words = re.findall(r"\b[a-zA-Z]{3,}\b", all_text)

    freq = Counter(words)

    print("\n=== TOP WORDS (Filtered) ===\n")

    count = 0
    for word, freq_count in freq.most_common(300):
        if word not in STOPWORDS:
            print(f"{word}: {freq_count}")
            count += 1
        if count >= 100:
            break

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    print("Fetching job descriptions...")
    job_descriptions = fetch_job_descriptions()

    print(f"Total jobs: {len(job_descriptions)}")

    analyze_text(job_descriptions)