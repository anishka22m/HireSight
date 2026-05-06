"""
HireSight — FastAPI Server
Run:
python -m uvicorn backend.server:app --reload --port 8000
"""

import os
import webbrowser
import pickle
import shutil
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from groq import Groq
from dotenv import load_dotenv

# Corrected Import: Using a standard import that works when running from the project root
from backend.resume_analyzerv2 import analyze_resume
from sqlalchemy import func, desc
from backend.db_connect import session
from backend.models import MarketTrend, Job

# --------------------------------------------------
# App Initialization
# --------------------------------------------------

app = FastAPI(
    title="HireSight API",
    description="Resume Skill Gap Analyzer",
    version="1.0.0"
)


load_dotenv("keys.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# --------------------------------------------------
# Paths
# --------------------------------------------------

# BASE_DIR is 'backend'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PROJECT_ROOT is the main folder 'MAJORPROJECT_CODE'
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# FRONTEND_DIR is 'frontend'
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# Specific sub-directories based on your VS Code structure
CSS_DIR = os.path.join(FRONTEND_DIR, "css")
JS_DIR = os.path.join(FRONTEND_DIR, "js")

# Assets are in the frontend root per your screenshot
ASSETS_DIR = FRONTEND_DIR 


# --------------------------------------------------
# Static Files
# --------------------------------------------------

app.mount("/css", StaticFiles(directory=CSS_DIR), name="css")
app.mount("/js", StaticFiles(directory=JS_DIR), name="js")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


# --------------------------------------------------
# Auto Open Browser
# --------------------------------------------------

@app.on_event("startup")
def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

# --------------------------------------------------
# Model Loading Logic
# --------------------------------------------------

# Expanded Multi-Domain Library
# Add this above your API routes
COURSE_LIBRARY = {
    # Data Science & Analytics
    "python": [
        {"title": "Python for Data Science", "provider": "Coursera", "price": "Free to Audit", "rating": 4.8, "url": "https://www.coursera.org/learn/python-for-applied-data-science-ai"},
        {"title": "Complete Python Bootcamp", "provider": "Udemy", "price": "Paid", "rating": 4.7, "url": "https://www.udemy.com/course/complete-python-bootcamp/"}
    ],
    "machine learning": [
        {"title": "ML Specialization by Andrew Ng", "provider": "Coursera", "price": "Free to Audit", "rating": 4.9, "url": "https://www.coursera.org/specializations/machine-learning-introduction"}
    ],
    "power bi": [
        {"title": "Microsoft Power BI - Data Analyst", "provider": "Udemy", "price": "Paid", "rating": 4.6, "url": "https://www.udemy.com/course/microsoft-power-bi-up-and-running/"}
    ],

    # Engineering & Backend
    "java": [
        {"title": "Java Programming Fundamentals", "provider": "Coursera", "price": "Free to Audit", "rating": 4.8, "url": "https://www.coursera.org/specializations/java-programming"}
    ],
    "flask": [
        {"title": "Flask Web Development", "provider": "YouTube", "price": "Free", "rating": 4.9, "url": "https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH"}
    ],
    "sql": [
        {"title": "SQL for Data Analytics", "provider": "Udacity", "price": "Free", "rating": 4.5, "url": "https://www.udacity.com/course/sql-for-data-analysis--ud198"}
    ],

    # Design & Marketing
    "figma": [
        {"title": "Figma UI UX Design Essentials", "provider": "Udemy", "price": "Paid", "rating": 4.8, "url": "https://www.udemy.com/course/figma-ux-ui-design-essentials/"}
    ],
    "seo": [
        {"title": "SEO Specialization", "provider": "Coursera", "price": "Free to Audit", "rating": 4.7, "url": "https://www.coursera.org/specializations/seo"}
    ],

    # Security
    "cyber security": [
        {"title": "Google Cybersecurity Certificate", "provider": "Coursera", "price": "Free to Audit", "rating": 4.8, "url": "https://www.coursera.org/professional-certificates/google-cybersecurity"}
    ]
}   

def _load_pickle(name: str):
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        raise RuntimeError(
            f"Model artefact '{name}' not found at {path}. "
            f"Make sure you have trained the models and saved the pickle files."
        )
    with open(path, "rb") as f:
        return pickle.load(f)




# --------------------------------------------------
# Frontend Pages
# --------------------------------------------------

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/upload", include_in_schema=False)
def upload_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "upload.html"))

@app.get("/results", include_in_schema=False)
def results_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "results.html"))

@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

@app.get("/resources", include_in_schema=False)
def resources_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "resources.html"))


# --------------------------------------------------
# Resume Analysis API
# --------------------------------------------------
def validate_resume(text: str):
    if not text or len(text.strip()) < 100:
        return "Resume content is too short or empty."

    text_lower = text.lower()

    resume_keywords = [
        "education", "experience", "skills",
        "projects", "internship", "work experience"
    ]

    match_count = sum(1 for k in resume_keywords if k in text_lower)

    if match_count < 2:
        return "Uploaded file does not appear to be a valid resume."

    return None

@app.post("/api/analyze")
# 'file' matches the formData.append("file", ...) in upload.js
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    temp_dir = os.path.join(BASE_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Run Analysis
        result = analyze_resume(file_path)

        # 2. TRANSFORM DATA FOR RESULTS.JS
        
        # results.js expects matched_skills to be: {name, level}
        matched_ui = [
            {"name": s["name"].title(), "level": 90} 
            for s in result["matched_skills"]
        ]

        # results.js expects missing_skills to be: {name, priority}
        missing_ui = [
            {
                "name": s["name"].title(),
                "priority": "high" if s["importance"] >= 4 else "medium"
            }
            for s in result["priority_gaps"]
        ]

        # results.js expects suggestions to be: {icon, title, text}
        suggestions_ui = [
            {
                "icon": "💡",
                "title": f"Master {skill}",
                "text": f"This is a high-priority skill for {result['domain']} roles."
            }
            for skill in result["high_priority_recommendations"]
        ]

        # 3. BUILD RESPONSE (Perfectly synced with results.js property names)
        response_data = {
            "status": "success",
            "role": result["domain"],           # data.role
            "score": result["score"],           # data.score
            "matched_skills": matched_ui,       # data.matched_skills
            "missing_skills": missing_ui,       # data.missing_skills
            "suggestions": suggestions_ui,      # data.suggestions
            "matched_count": result["matched_count"],
            "missing_count": result["missing_count"],
            "high_priority_count": len(result["high_priority_recommendations"]),
            "improvement_suggestion": result["improvement_suggestion"]
        }

        return JSONResponse(content=response_data)
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)



# --------------------------------------------------
# Skill Trends API (Dynamic Market Intelligence)
# --------------------------------------------------

@app.get("/api/trends")
def trends(role: Optional[str] = "All Roles"):
    """
    Fetches dynamic market intelligence grouped by domain.
    """
    try:
        # 1. Base Query for Trends
        query = session.query(MarketTrend)
        if role != "All Roles":
            query = query.filter(MarketTrend.domain == role)

        # 2. Top 10 In-Demand Skills (Bar Chart)
        # Aggregates average demand for the latest recorded period
        top_skills_query = session.query(
            MarketTrend.skill_name, 
            func.avg(MarketTrend.demand_percentage).label('avg_demand')
        ).group_by(MarketTrend.skill_name)
        
        if role != "All Roles":
            top_skills_query = top_skills_query.filter(MarketTrend.domain == role)
            
        top_skills_data = top_skills_query.order_by(desc('avg_demand')).limit(10).all()
        
        top_skills = [
            {"name": s[0], "demand": round(s[1], 1)} 
            for s in top_skills_data
        ]

        trending_data = query.order_by(desc(MarketTrend.demand_percentage)).limit(5).all()
        
        emerging_list = [
            {"name": t.skill_name, "growth": f"+{t.demand_percentage/2:.1f}%"}
            for t in trending_data
        ]

        # 3. Category Breakdown (Donut Chart)
        # Calculates the distribution of data across domains
        category_data = session.query(
            MarketTrend.domain, 
            func.count(MarketTrend.id)
        ).group_by(MarketTrend.domain).all()
        
        categories = [
            {"label": c[0], "value": c[1]} 
            for c in category_data
        ]

        # 4. Market Overview Stats (Mini-Stats)
        total_jobs = session.query(Job).count()
        skills_tracked = session.query(MarketTrend.skill_name).distinct().count()
        
        # 5. Trend Line Logic (Placeholder for historical grouping)
        # JS expects trend_months and values. For now, we return the current snapshot.
        months = ["Jan", "Feb", "Mar", "Apr", "May"] # Dynamic months based on current year
        
        # Sample trend data for the top 3 skills to populate the line chart
        line_trends = []
        for s in top_skills[:3]:
            # We simulate a slight growth curve for the demo based on the current demand
            base = s["demand"]
            line_trends.append({
                "skill": s["name"],
                "values": [round(base * (0.8 + (i * 0.05)), 1) for i in range(len(months))]
            })

        return {
            "stats": {
                "total_jobs": total_jobs,
                "skills_tracked": skills_tracked,
                "emerging_skills": 12 # Gemini/Groq can identify these specifically later
            },
            "top_skills": top_skills,
            "categories": categories,
            "trend_months": months,
            "trends": line_trends,
            "emerging_list": emerging_list
        }
    except Exception as e:
        print(f"Error fetching trends: {e}")
        raise HTTPException(status_code=500, detail="Could not load market trends")

# Create a Pydantic model for the request body
from pydantic import BaseModel
from typing import List

class ResourceRequest(BaseModel):
    missing_skills: List[str]
    domain: str

@app.post("/api/resources")
async def get_resources(request: ResourceRequest):
    """
    Analyzes missing skills and returns the best matched learning resources.
    """
    recommended = []
    
    for skill in request.missing_skills:
        skill_key = skill.lower().strip()
        
        # Match against our library
        if skill_key in COURSE_LIBRARY:
            for course in COURSE_LIBRARY[skill_key]:
                course_info = course.copy()
                course_info["related_skill"] = skill
                recommended.append(course_info)
        else:
            # Fallback: Dynamic Smart Search link for niche skills
            recommended.append({
                "title": f"Mastering {skill.title()}",
                "provider": "Community Resources",
                "price": "Free",
                "rating": "4.5+",
                "url": f"https://www.youtube.com/results?search_query=learn+{skill.replace(' ', '+')}",
                "related_skill": skill,
                "note": f"Essential for {request.domain} roles"
            })
            
    # Return top 6 resources to keep the UI clean
    return {"status": "success", "resources": recommended[:6]}



#--------------------------------------------------
# Resources Page Roadmap Endpoint
# --------------------------------------------------
class MarketContext(BaseModel):
    trending_skills: List[str]
    demand_level: str

class RoadmapConstraints(BaseModel):
    duration: str
    learning_style: str

class RoadmapRequest(BaseModel):
    domain: str
    user_level: str
    existing_skills: List[str]
    missing_skills: List[str]
    target_role: str
    market_context: MarketContext
    constraints: RoadmapConstraints


# Contextual Vector Models (Pydantic)

class MarketContext(BaseModel):
    trending_skills: List[str]
    demand_level: str

class RoadmapConstraints(BaseModel):
    duration: str
    learning_style: str

class RoadmapRequest(BaseModel):
    domain: str
    user_level: str
    existing_skills: List[str]
    missing_skills: List[str]
    target_role: str
    market_context: MarketContext
    constraints: RoadmapConstraints

# Automated Pedagogical Orchestration Endpoint


@app.post("/api/roadmap")
async def generate_roadmap(request: RoadmapRequest):
    """
    Synthesizes a dynamic 7-day learning roadmap using the LLM Inference Engine.
    Adapts to ANY domain, user level, and market context provided.
    """
    
    # We ask the LLM to focus the sprint on the top 1 or 2 missing skills to keep a 7-day timeframe realistic
    primary_focus = ", ".join(request.missing_skills[:2])
    existing_base = ", ".join(request.existing_skills) if request.existing_skills else "General foundational knowledge"

    system_prompt = (
        "You are an expert Technical Learning Architect. Your job is to synthesize personalized, "
        "high-impact learning roadmaps for professionals and students. You adapt perfectly to the user's "
        "domain, whether it is Marketing, Engineering, Design, or Data. "
        "You MUST return ONLY a valid JSON object. Do not include markdown formatting like ```json."
    )

    user_prompt = f"""
    Generate a highly focused 7-day learning sprint for a {request.user_level} aiming to become a '{request.target_role}' in the '{request.domain}' domain.
    
    Context:
    - Their current strong skills: {existing_base}
    - The critical gap they need to bridge: {primary_focus}
    - Market Context: These skills have {request.market_context.demand_level} demand right now.
    - Constraints: {request.constraints.duration}, {request.constraints.learning_style} approach.

    Return a JSON object strictly matching this structure:
    {{
      "sprint_title": "A catchy, motivating title for the roadmap",
      "synthesis_overview": "2-3 sentences explaining exactly how learning {primary_focus} builds upon their existing {existing_base} to make them hireable as a {request.target_role}.",
      "daily_plan": [
        {{
          "day": 1,
          "focus": "Topic of the day",
          "action_items": ["Action 1", "Action 2"],
          "time_commitment": "e.g., 2 hours"
        }}
        // ... must include exactly 7 days
      ],
      "capstone_project": {{
        "title": "Project Name",
        "description": "A mini-project combining their new skills to put on their resume.",
        "portfolio_value": "Why recruiters will care about this project."
      }}
    }}
    """

    try:
        # Assuming 'client' is your initialized Groq client from the Market Trends script
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        # Parse the JSON response
        roadmap_data = json.loads(completion.choices[0].message.content)
        return {"status": "success", "roadmap": roadmap_data}
        
    except Exception as e:
        print(f"Error generating roadmap: {e}")
        return {"status": "error", "message": "Knowledge Synthesis Engine unavailable. Please try again."}




# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "HireSight API"}