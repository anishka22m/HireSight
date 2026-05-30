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
    """Uses the updated Llama 3.3 model to extract skill demand safely."""
    # CHANGED: We now explicitly ask for a JSON Object with a 'skills' array. 
    # This prevents the Groq 400 tool_use_failed error and formats correctly.
    prompt = f"""
    Analyze these job descriptions for the '{domain_name}' domain.
    1. Identify the top 5 most frequently mentioned technical skills.
    2. STRONGLY ENFORCE GROUPING: Combine synonyms and acronyms (e.g., merge "Machine Learning" and "ML" into "Machine Learning", merge "javascript", "JS" into "JavaScript").
    3. Ensure proper capitalization (e.g., "Node.js", "MySQL").
    4. CRITICAL RULE: DO NOT list the domain name itself as a skill! (e.g., If the domain is 'Marketing', do NOT output 'Marketing'. Output actual skills like 'SEO', 'Google Analytics').
    5. For each, provide a 'demand_percentage' (0-100).
    
    You MUST return a JSON Object with a single key called "skills" containing a list:
    {{
      "skills": [
        {{"skill": "Python", "demand": 85}},
        {{"skill": "SQL", "demand": 70}}
      ]
    }}
    
    Descriptions:
    {combined_descriptions[:12000]}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a labor market analyst. You output strictly valid JSON objects."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        raw_output = json.loads(completion.choices[0].message.content)
        
        # Safely extract the list from the dictionary, regardless of what the LLM named the key
        if isinstance(raw_output, dict):
            for val in raw_output.values():
                if isinstance(val, list): return val
        return []
    except Exception as e:
        print(f"Error for {domain_name}: {e}")
        return []

# 3. Main Intelligence Loop
def run_weekly_intelligence():
    print("Starting Market Intelligence Update via Adzuna and LLama...")
    current_month = datetime.now().strftime("%b %Y")
    unique_domains = list(set(ROLE_MAP.values()))
    
    for domain in unique_domains:
        print(f"--- Processing: {domain} ---")
        
        recent_jobs = session.query(Job.description).filter(Job.domain == domain).limit(15).all()
        
        if not recent_jobs:
            print(f"No recent jobs found for {domain}. Skipping.")
            continue
            
        combined_text = " ".join([j[0] for j in recent_jobs])
        trends = analyze_domain_trends(domain, combined_text)
        
        if not trends:
            continue

        for item in trends:
            # Bulletproof Fallback: Catch whatever keys the LLM decides to use
            skill_name = "Unknown"
            demand_val = 50.0
            
            if isinstance(item, dict):
                skill_name = item.get('skill') or item.get('name') or item.get('technology') or "Unknown"
                demand_val = item.get('demand') or item.get('percentage') or item.get('value') or 50.0
            
            clean_skill_name = str(skill_name).strip().title()
            
            # Skip saving if the AI failed to extract a real word
            if clean_skill_name == "Unknown" or not clean_skill_name:
                continue
                
            try:
                demand_val = float(demand_val)
            except:
                demand_val = 50.0

            new_entry = MarketTrend(
                domain=domain,
                skill_name=clean_skill_name,
                demand_percentage=demand_val,
                month_year=current_month
            )
            session.add(new_entry)
        
        print(f"Successfully recorded {len(trends)} skills for {domain}.")
        time.sleep(5)

    session.commit()
    print("Market Intelligence update complete.")

if __name__ == "__main__":
    run_weekly_intelligence()