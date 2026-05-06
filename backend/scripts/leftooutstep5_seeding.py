import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_connect import session
from models import Skill
from sqlalchemy import text

# These are your specific 25 survivor skills and the domains they belong to
SURVIVOR_MAPPINGS = {
    "cloud": {"Data Science/Analytics": 3, "Engineering": 4, "Security": 3},
    "automation": {"Engineering": 4},
    "analytics": {"Data Science/Analytics": 5, "Marketing": 4},
    "data analytics": {"Data Science/Analytics": 5},
    "digital": {"Data Science/Analytics": 3, "Design": 3, "General Professional/Tech": 5, "Marketing": 5},
    "software": {"Engineering": 5, "General Professional/Tech": 3},
    "manufacturing": {"Finance/Ops": 4},
    "monitoring": {"Finance/Ops": 3, "Security": 4},
    "network": {"Engineering": 4, "Security": 5},
    "infrastructure": {"Engineering": 4, "Security": 4},
    "data science": {"Data Science/Analytics": 5},
    "rest": {"Engineering": 4},
    "finance": {"Finance/Ops": 5},
    "object": {"Engineering": 4},
    "payroll": {"Finance/Ops": 5, "HR": 5},
    "education": {"General Professional/Tech": 3},
    "security": {"Engineering": 4, "General Professional/Tech": 4, "Security": 5},
    "front": {"Engineering": 4},
    "social media": {"Marketing": 5},
    "android": {"Engineering": 5},
    "spring": {"Engineering": 5},
    "computer science": {"Engineering": 5, "General Professional/Tech": 4},
    "responsive": {"Design": 5},
    "cyber": {"Security": 5},
    "cyber security": {"Security": 5}
}

def seed_survivors():
    print("--- MAPPING 25 SURVIVOR SKILLS ---")
    
    total_mappings = 0

    for skill_name, domain_scores in SURVIVOR_MAPPINGS.items():
        # Look for the EXACT original string in your DB (IDs 2, 3, 4...)
        skill_obj = session.query(Skill).filter(Skill.skill_name == skill_name).first()
        
        if skill_obj:
            for domain, score in domain_scores.items():
                try:
                    # Map the existing ID to the domain benchmarks
                    query = text("""
                        INSERT INTO skill_benchmarks (skill_id, domain, importance_score)
                        VALUES (:s_id, :dom, :score)
                        ON CONFLICT (skill_id, domain) DO UPDATE 
                        SET importance_score = EXCLUDED.importance_score;
                    """)
                    session.execute(query, {"s_id": skill_obj.id, "dom": domain, "score": score})
                    total_mappings += 1
                except Exception as e:
                    print(f"Error mapping {skill_name}: {e}")
        else:
            print(f"Warning: Skill '{skill_name}' not found in master skills table.")

    session.commit()
    print(f"\nSuccessfully created {total_mappings} benchmarks for the 25 survivor skills.")

if __name__ == "__main__":
    seed_survivors()