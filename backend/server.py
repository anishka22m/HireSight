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

# Corrected Import: Using a standard import that works when running from the project root
from backend.resume_analyzer import get_resume_score


# --------------------------------------------------
# App Initialization
# --------------------------------------------------

app = FastAPI(
    title="HireSight API",
    description="Resume Skill Gap Analyzer",
    version="1.0.0"
)


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

def _load_pickle(name: str):
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        raise RuntimeError(
            f"Model artefact '{name}' not found at {path}. "
            f"Make sure you have trained the models and saved the pickle files."
        )
    with open(path, "rb") as f:
        return pickle.load(f)

# CHANGE: Updated filenames to match your actual folder contents
vectorizer = _load_pickle("tfidf_vectorizer.pkl")
model = _load_pickle("best_svm_model.pkl")

# NOTE: These files are currently missing from your backend folder, 
# so they are commented out to prevent the server from crashing.
# jd_vectors = _load_pickle("jd_vectors.pkl")
# jd_df = _load_pickle("jd_df.pkl")
# skill_list = _load_pickle("skill_list.pkl")


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

@app.post("/api/analyze")
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    # 1. Save the uploaded file temporarily to a 'temp' folder
    temp_dir = os.path.join(BASE_DIR, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Run your SVM + Skill Match logic
        # This function is imported from resume_analyzer.py
        result = get_resume_score(file_path)

        # 3. Format data for the specific frontend JS (results.js)
        matched = [{"name": s.title(), "level": 90} for s in result["matched_skills"]]
        
        missing = []
        for i, s in enumerate(result["missing_skills"]):
            prio = "high" if i < result.get("high_priority_count", 3) else "medium"
            missing.append({"name": s.title(), "priority": prio})

        suggestions = []
        for s in result["suggestions"]:
            suggestions.append({
                "icon": "💡",
                "title": "Strategy",
                "text": s
            })

        response = {
            "score": result["score"],
            "role": result["category"],
            "matched_skills": matched,
            "missing_skills": missing,
            "suggestions": suggestions,
            "matched_count": result["matched_count"],
            "missing_count": result["missing_count"]
        }

        return JSONResponse(content=response)
    
    finally:
        # Clean up: remove the temp file after analysis
        if os.path.exists(file_path):
            os.remove(file_path)


# --------------------------------------------------
# Skill Trends API (Static for Presentation)
# --------------------------------------------------

@app.get("/api/trends")
def trends():
    return {
        "top_skills": [
            {"name": "Python", "demand": 88},
            {"name": "SQL", "demand": 82},
            {"name": "Power BI", "demand": 76},
            {"name": "Tableau", "demand": 74}
        ],
        "categories": [
            {"label": "Data Engineering", "value": 28},
            {"label": "Analytics", "value": 24},
            {"label": "Machine Learning", "value": 19}
        ],
        "trend_months": ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb"],
        "trends": [
            {"skill": "Python", "values": [72,75,78,81,85,88]},
            {"skill": "Tableau", "values": [60,63,65,69,71,74]}
        ]
    }

# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "HireSight API"}