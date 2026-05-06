import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_connect import session
from models import Job

import re
from collections import Counter


STOPWORDS = {
    "the", "and", "with", "for", "you", "are", "our",
    "this", "that", "will", "have", "from", "your",
    "all", "can", "not", "but", "has", "was", "were",
    "they", "their", "them", "his", "her", "its",
    "job", "role", "work", "team", "company",
    "experience", "skills", "required", "ability",
    "looking", "support", "responsibilities",
    "candidate", "candidates", "position"
}


def analyze_domain(domain):
    jobs = session.query(Job.description).filter_by(domain=domain).all()
    texts = [j[0] for j in jobs if j[0]]

    all_text = " ".join(texts).lower()

    words = re.findall(r"\b[a-zA-Z]{3,}\b", all_text)

    freq = Counter(words)

    print(f"\n=== {domain} ===\n")

    count = 0
    for word, freq_count in freq.most_common(200):
        if word not in STOPWORDS:
            print(f"{word}: {freq_count}")
            count += 1
        if count >= 50:
            break


def run():
    domains = session.query(Job.domain).distinct().all()
    domains = [d[0] for d in domains]

    for domain in domains:
        analyze_domain(domain)


if __name__ == "__main__":
    run()