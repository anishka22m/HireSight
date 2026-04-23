import pickle
import re
import nltk
import pdfplumber
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os
import random

# --- 1. SETUP & LOADING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, 'best_svm_model.pkl')
vectorizer_path = os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl')

with open(model_path, 'rb') as f:
    model = pickle.load(f)
    
with open(vectorizer_path, 'rb') as f:
    vectorizer = pickle.load(f)

# The full list of skills you curated in your notebook
curated_skills = [
    "python", "sql", "r", "go", "golang", "java", "c++", "c#", "typescript", "rust", 
    "kotlin", "swift", "dart", "php", "ruby", "perl", "bash", "powershell", "scala", 
    "javascript", "html", "css", "machine learning", "deep learning", "statistics", 
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "xgboost", 
    "lightgbm", "catboost", "hugging face", "langchain", "langgraph", "transformers", 
    "bert", "llama 3", "openai gpt", "claude sonnet", "gemini flash", "rag", 
    "prompt engineering", "nlp", "computer vision", "opencv", "mediapipe", 
    "reinforcement learning", "supervised learning", "unsupervised learning", 
    "pydantic", "ollama", "fastapi", "django", "flask", "nestjs", "spring boot", 
    ".net 8+", "restful api design", "graphql", "microservices", "grpc", 
    "asynchronous logic", "node.js", "angular", "react", "vue.js", "tailwind css 4", 
    "bootstrap", "flutter", "jetpack compose", "kotlin multiplatform", "kmp", 
    "impeller engine", "provider", "riverpod", "bloc", "ktor", "firebase", 
    "responsive design", "shadcn/ui", "apache spark", "pyspark", "mllib", "hadoop", 
    "apache kafka", "amazon kinesis", "apache flink", "snowflake", "dbt", "airflow", 
    "jinja", "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "pulumi", 
    "ansible", "jenkins", "github actions", "gitlab ci/cd", "argocd", "gitops", 
    "helm", "prometheus", "grafana", "elk stack", "opentelemetry", "datadog", 
    "cloudwatch", "infrastructure as code", "siem", "splunk", "microsoft sentinel", 
    "ibm qradar", "xdr", "edr", "crowdstrike", "carbon black", "ids", "ips", "nmap", 
    "nessus", "qualys", "rapid7", "openvas", "penetration testing", "forensic analysis", 
    "autopsy", "ftk imager", "encase", "misp", "mitre att&ck", "threat hunting", 
    "incident response", "malware analysis", "zero trust", "pci dss", "hipaa", 
    "gdpr", "nist csf", "figma", "adobe xd", "sketch", "axure rp", "balsamiq", 
    "invision", "photoshop", "illustrator", "after effects", "premiere pro", 
    "blender", "autodesk maya", "cinema 4d", "houdini", "unreal engine 5", "unity", 
    "substance 3d painter", "zbrush", "typography", "color theory", "wcag accessibility", 
    "design systems", "motion graphics", "vfx", "runway ml", "adobe sensei", "nuke", 
    "toon boom harmony", "ga4", "looker studio", "power bi", "tableau", "google ads", 
    "meta ads", "semrush", "ahrefs", "moz", "google search console", "seo", "sem", 
    "content marketing", "social media marketing", "email marketing", "hubspot", 
    "salesforce", "mailchimp", "marketo", "lead generation", "crm management", 
    "performance marketing", "roas analysis", "hotjar", "sprout social", "hootsuite", 
    "business analysis", "forecasting", "jira", "confluence", "trello", "asana", 
    "waterfall", "agile", "scrum", "kanban", "lean six sigma", "swot analysis", 
    "pestle analysis", "vrio framework", "porter's five forces", "ansoff matrix", 
    "bcg matrix", "cost-benefit analysis", "okr", "balanced scorecard", "hris", 
    "workday", "bamboohr", "adp", "ats", "talent sourcing", "onboarding", 
    "employer branding", "workforce metrics", "statutory compliance", "labor law", 
    "negotiation", "cultural intelligence", "financial modeling", "excel", 
    "power query", "pivot tables", "risk assessment", "aml", "kyc", 
    "transaction monitoring", "actimize", "sas", "oracle mantas", "fenergo", 
    "discounted cash flow", "quantitative analysis", "credit risk", "market risk", 
    "operational risk", "articulate storyline 360", "adobe captivate", "camtasia", 
    "vyond", "moodle", "canvas", "talentlms", "addie model", "bloom's taxonomy", 
    "xapi", "learning record stores", "microlearning", "qualitative analysis", 
    "literature review", "spss", "stata", "survey design", "data cleaning", 
    "hypothesis testing", "bayesian statistics", "ethnographic studies"
]

lemmatizer = WordNetLemmatizer()
EN_STOPWORDS = set(stopwords.words("english"))

# --- 2. NEW: SKILL MATCHING & RECOMMENDATION LOGIC ---

# ADDITION: Define benchmark skills for each of your broad categories
# This allows the system to identify "Missing" skills
# ADDITION: These are the "ideal" skill sets for each category
CATEGORY_BENCHMARKS = {
    "Security": ["siem", "splunk", "nmap", "penetration testing", "firewalls", "linux", "python"],
    "Marketing": ["seo", "sem", "google ads", "content marketing", "ga4", "social media marketing"],
    "HR": ["hris", "recruitment", "onboarding", "talent sourcing", "labor law", "payroll"],
    "Data Science/Analytics": ["python", "sql", "machine learning", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"],
    "Engineering": ["java", "python", "javascript", "docker", "kubernetes", "rest api", "git", "aws", "nodejs", "react"],
    "Design": ["figma", "adobe xd", "ui designer", "responsive design", "design systems"],
    "Finance/Ops": ["financial modeling", "excel", "risk assessment", "aml", "pivot tables"],
    "General Tech/Professional": ["communication", "teamwork", "problem solving", "leadership", "excel"],
    "Data Science/Analytics": [
        "python", "pandas", "numpy", "scikit-learn", "tensorflow", 
        "pytorch", "keras", "xgboost", "tableau", "nlp", "machine learning"
    ],
    "Engineering": [
        "java", "html", "css", "react", "mongodb", "git", "aws", "tailwind css"
    ],
    "General Tech/Professional": ["communication", "teamwork", "leadership", "excel"]
}

# UPDATED: Improved Skill Extraction
def extract_skills_from_text(text):
    found = set()
    t = text.lower()  # Force lowercase for matching
    for skill in curated_skills:
        # \b ensures we don't match 'java' inside 'javascript'
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, t):
            found.add(skill.lower())
    return found

def generate_suggestions(missing_skills):
    """Creates improvement tips with varied framing for better user experience."""
    if not missing_skills:
        return ["Your skill set is already a perfect match for this category!"]
    
    # Selection of different ways to frame a suggestion
    framing_templates = [
        "To stand out, consider highlighting projects involving {skill}.",
        "Your profile would be much stronger with a certification in {skill}.",
        "Try to incorporate {skill} into your technical summary to improve ATS matching.",
        "Demonstrating proficiency in {skill} is highly recommended for this career path.",
        "We noticed {skill} is missing; adding this could significantly boost your score.",
        "Focus on learning {skill} to bridge the gap for this specific job role."
    ]
    
    suggestions = []
    missing_list = list(missing_skills)
    
    # Generate up to 4 unique suggestions with different framings
    num_suggestions = min(len(missing_list), 4)
    selected_skills = random.sample(missing_list, num_suggestions)
    
    for i, skill in enumerate(selected_skills):
        # Pick a random template or cycle through them
        template = framing_templates[i % len(framing_templates)]
        suggestions.append(template.format(skill=skill.title()))
        
    return suggestions

# --- 3. PIPELINE FUNCTIONS ---
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = nltk.word_tokenize(text)
    cleaned = [lemmatizer.lemmatize(t) for t in tokens if t not in EN_STOPWORDS]
    return " ".join(cleaned)

# --- 4. THE UPDATED SCORING LOGIC ---
# --- 4. THE UPDATED SCORING LOGIC ---
def get_resume_score(pdf_path):
    raw_text = extract_text_from_pdf(pdf_path)
    clean_text = normalize_text(raw_text)
    
    # 1. Model Prediction
    vectorized_text = vectorizer.transform([clean_text])
    predicted_class = model.predict(vectorized_text)[0]
    
    # SVM Confidence Logic
    decision_scores = model.decision_function(vectorized_text)
    exp_scores = np.exp(decision_scores - np.max(decision_scores))
    prob_scores = exp_scores / exp_scores.sum()
    model_confidence = np.max(prob_scores) 
    
    # 2. Skill Analysis
    user_skills = extract_skills_from_text(raw_text)
    required_skills = set(CATEGORY_BENCHMARKS.get(predicted_class, ["communication"]))
    
    matched_skills = user_skills.intersection(required_skills)
    missing_skills = required_skills.difference(matched_skills)
    
    # --- SMART SCORING LOGIC ---
    
    # A. Base Skill Match (0.0 - 1.0)
    skill_ratio = len(matched_skills) / len(required_skills) if len(required_skills) > 0 else 0
    
    # B. Smart Weighting
    # If the model is not very sure (confidence < 30%), we rely 95% on the skill match
    # so that a "misclassified" resume still gets a fair score based on its content.
    if model_confidence < 0.30:
        final_score = (skill_ratio * 0.95) + (model_confidence * 0.05)
    else:
        final_score = (skill_ratio * 0.80) + (model_confidence * 0.20)
    
    # C. "High Achiever" Boosts
    if skill_ratio >= 0.7:
        final_score += 0.10  # 10 point boost for matching most benchmarks
    elif skill_ratio >= 0.4:
        final_score += 0.05  # 5 point boost for mid-tier
        
    # D. Scaling & Caps
    final_score = min(final_score * 100, 99.0)
    
    # Force a 'Pass' score if they have any technical skills found
    if final_score < 50 and len(user_skills) > 5:
        final_score = 65.0

    improvement_tips = generate_suggestions(missing_skills)
    
    return {
        "raw_text": raw_text,
        "category": predicted_class,
        "score": round(final_score, 2),
        "matched_skills": list(matched_skills),
        "matched_count": len(matched_skills),
        "missing_skills": list(missing_skills),
        "missing_count": len(missing_skills),
        "suggestions": improvement_tips,
        "high_priority_count": min(len(missing_skills), 3)
    }
# --- 5. TEST IT ---
# Using os.path.join for the test to avoid path errors
test_pdf = os.path.join(BASE_DIR, "ML Resume V1.1 - Laksh Nijhawan.pdf")

if os.path.exists(test_pdf):
    result = get_resume_score(test_pdf)
    
    print(f"\n" + "="*50)
    print(f"ANALYSIS REPORT: {os.path.basename(test_pdf)}")
    print(f"="*50)
    print(f"IDENTIFIED ROLE : {result['category']}")
    print(f"MATCH CONFIDENCE: {result['score']}%")
    print(f"-"*50)
    
    print(f"MATCHED SKILLS ({result['matched_count']}):")
    print(f" -> {', '.join(result['matched_skills']) if result['matched_skills'] else 'None found'}")
    
    print(f"\nMISSING SKILLS ({result['missing_count']}):")
    print(f" -> {', '.join(result['missing_skills']) if result['missing_skills'] else 'None missing'}")
    
    print(f"\nIMPROVEMENT SUGGESTIONS:")
    for i, suggestion in enumerate(result['suggestions'], 1):
        print(f" {i}. {suggestion}")
    
    print(f"="*50 + "\n")
else:
    print(f"CRITICAL: Could not find test file at: {test_pdf}")
    # List files in the directory to help you debug the filename
    print(f"Files in backend folder: {os.listdir(BASE_DIR)}")