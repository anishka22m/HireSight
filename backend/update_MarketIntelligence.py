import os
import json
import time
from groq import Groq
from datetime import datetime
from dotenv import load_dotenv
from backend.db_connect import session
from backend.models import Job, MarketTrend

# 1. Configuration
load_dotenv("keys.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ROLE_MAP = {
    "data": "Data Science/Analytics",
    "analyst": "Data Science/Analytics",
    "scientist": "Data Science/Analytics",
    "engineer": "Engineering",
    "developer": "Engineering",
    "marketing": "Marketing",
    "hr": "HR",
    "design": "Design",
    "finance": "Finance/Ops",
    "security": "Security"
}

# 2. Groq Analysis Function
def analyze_domain_trends(domain_name, combined_descriptions):
    """Uses Groq and the updated Llama 3.3 model to extract skill demand."""
    prompt = f"""
    Analyze these job descriptions for the '{domain_name}' domain.
    1. Identify the top 5 most frequently mentioned technical skills.
    2. For each, provide a 'demand_percentage' (0-100) based on frequency.
    
    Return ONLY a JSON list of objects:
    [
      {{"skill": "Python", "demand": 85}},
      {{"skill": "SQL", "demand": 70}}
    ]
    
    Descriptions:
    {combined_descriptions[:12000]}
    """
    
    try:
        # Switched to llama-3.3-70b-versatile for 2026 compatibility
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a labor market analyst. You output only raw JSON lists."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        raw_output = json.loads(completion.choices[0].message.content)
        
        if isinstance(raw_output, dict):
            for val in raw_output.values():
                if isinstance(val, list): return val
        return raw_output
    except Exception as e:
        print(f"Error for {domain_name}: {e}")
        return []

# 3. Main Intelligence Loop
def run_weekly_intelligence():
    print("Starting Market Intelligence Update via Groq...")
    current_month = datetime.now().strftime("%b %Y")
    unique_domains = list(set(ROLE_MAP.values()))
    
    for domain in unique_domains:
        print(f"--- Processing: {domain} ---")
        
        # Limit to 10-15 jobs per domain to stay within token limits
        recent_jobs = session.query(Job.description).filter(Job.domain == domain).limit(15).all()
        
        if not recent_jobs:
            print(f"No recent jobs found for {domain}. Skipping.")
            continue
            
        combined_text = " ".join([j[0] for j in recent_jobs])
        trends = analyze_domain_trends(domain, combined_text)
        
        if not trends:
            continue

        for item in trends:
            new_entry = MarketTrend(
                domain=domain,
                skill_name=item.get('skill'),
                demand_percentage=item.get('demand'),
                month_year=current_month
            )
            session.add(new_entry)
        
        print(f"Successfully recorded {len(trends)} skills for {domain}.")
        # 5 second delay to avoid Rate Limit Errors on free tier
        time.sleep(5)

    session.commit()
    print("Market Intelligence update complete.")

if __name__ == "__main__":
    run_weekly_intelligence()