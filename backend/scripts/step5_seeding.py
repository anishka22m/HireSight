import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_connect import session
from models import Skill
from sqlalchemy import text

# NORMALIZATION MAP
# Ensures variations all point to one "Gold Standard" name
DS_NORMALIZATION = {
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "tf": "tensorflow",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "dl": "deep learning",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "bigquery": "google bigquery",
    "bi": "business intelligence"
}
ENG_NORMALIZATION = {
    "cpp": "c++",
    "c#": "c-sharp",
    "k8s": "kubernetes",
    "js": "javascript",
    "ts": "typescript",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "embedded c": "embedded systems",
    "hdl": "hardware description language",
    "pcb": "pcb design",
    "dsp": "digital signal processing",
    "fpga": "field programmable gate array",
    "vlsi": "vlsi design",
    "cad": "autocad"
}
SEC_NORMALIZATION = {
    "pentesting": "penetration testing",
    "pen testing": "penetration testing",
    "iam": "identity and access management",
    "soc": "security operations center",
    "siem": "security information and event management",
    "infosec": "information security",
    "appsec": "application security",
    "netsec": "network security",
    "vuln mgmt": "vulnerability management",
    "incident handling": "incident response",
    "cybersec": "cybersecurity"
}
MKT_NORMALIZATION = {
    "seo": "search engine optimization",
    "sem": "search engine marketing",
    "ppc": "pay per click",
    "smm": "social media marketing",
    "cro": "conversion rate optimization",
    "crm": "customer relationship management",
    "ga": "google analytics",
    "pr": "public relations",
    "kwr": "keyword research",
    "cta": "call to action",
    "cac": "customer acquisition cost",
    "roas": "return on ad spend"
}

HR_NORMALIZATION = {
    "ta": "talent acquisition",
    "hris": "hr information systems",
    "ats": "applicant tracking systems",
    "l&d": "learning and development",
    "dei": "diversity and inclusion",
    "d&i": "diversity and inclusion",
    "er": "employee relations",
    "hrbp": "hr business partner",
    "hcm": "human capital management",
    "payroll mgmt": "payroll management",
    "comp & ben": "compensation and benefits"
}

DSGN_NORMALIZATION = {
    "ux": "user experience",
    "ui": "user interface",
    "ia": "information architecture",
    "ps": "adobe photoshop",
    "ai": "adobe illustrator",
    "xd": "adobe xd",
    "ae": "adobe after effects",
    "pr": "adobe premiere pro",
    "hcd": "human-centered design",
    "uhr": "user research",
    "ixd": "interaction design",
    "vc": "visual communication"
}

FIN_OPS_NORMALIZATION = {
    "fp&a": "financial planning and analysis",
    "p&l": "profit and loss",
    "erp": "enterprise resource planning",
    "scm": "supply chain management",
    "kpi": "key performance indicators",
    "roi": "return on investment",
    "gaap": "generally accepted accounting principles",
    "ifrs": "international financial reporting standards",
    "ap": "accounts payable",
    "ar": "accounts receivable",
    "cpa": "certified public accountant",
    "cfa": "chartered financial analyst",
    "six sigma": "lean six sigma"
}
GEN_NORMALIZATION = {
    "ms office": "microsoft office",
    "pmp": "project management professional",
    "comm": "communication",
    "biz dev": "business development",
    "it support": "it support",
    "qa": "quality assurance",
    "g-suite": "google workspace",
    "office 365": "microsoft 365"
}

def seed_all_domains(domain_data):
    print("--- INITIATING INTELLIGENT DOMAIN SEEDING ---")
    
    for domain_name, skills in domain_data.items():
        print(f"\nProcessing Domain: {domain_name.upper()}")
        inserted_skills = 0
        mapped_benchmarks = 0

        for skill_name, score in skills.items():
            # 1. NORMALIZE BEFORE PROCESSING
            raw_name = skill_name.lower().strip()
            clean_name = DS_NORMALIZATION.get(raw_name, raw_name)
            
            # 2. Ensure skill exists in master Skill table
            skill_obj = session.query(Skill).filter(Skill.skill_name == clean_name).first()
            if not skill_obj:
                skill_obj = Skill(skill_name=clean_name)
                session.add(skill_obj)
                session.flush() 
                inserted_skills += 1

            # 3. Insert or Update Importance in Benchmarks
            try:
                query = text("""
                    INSERT INTO skill_benchmarks (skill_id, domain, importance_score)
                    VALUES (:s_id, :dom, :score)
                    ON CONFLICT (skill_id, domain) DO UPDATE 
                    SET importance_score = EXCLUDED.importance_score;
                """)
                session.execute(query, {"s_id": skill_obj.id, "dom": domain_name, "score": score})
                mapped_benchmarks += 1
            except Exception as e:
                print(f"Error mapping {clean_name}: {e}")

        session.commit()
        print(f"Result: {inserted_skills} new added, {mapped_benchmarks} mapped.")

# =========================================================
# DATA SCIENCE & ANALYTICS (Expanded to 58 Skills)
# =========================================================
DOMAIN_DATA = {
    "Data Science/Analytics": {
        # 5: Critical (Core Foundations)
        "python": 5, "sql": 5, "machine learning": 5, "statistics": 5, "data analysis": 5,
        "pandas": 5, "numpy": 5, "scikit-learn": 5, "r": 5, "probability": 5, 
        "hypothesis testing": 5, "linear algebra": 5,
        
        # 4: Highly Preferred (Modeling & Modern AI)
        "deep learning": 4, "tensorflow": 4, "pytorch": 4, "tableau": 4, "power bi": 4, 
        "natural language processing": 4, "computer vision": 4, "predictive modeling": 4, 
        "big data": 4, "data wrangling": 4, "data cleaning": 4, "time series analysis": 4, 
        "generative ai": 4, "llms": 4, "google bigquery": 4, "scipy": 4,
        
        # 3: Important (Engineering & Ops)
        "spark": 3, "hadoop": 3, "etl": 3, "data mining": 3, "cloud computing": 3,
        "aws": 3, "docker": 3, "git": 3, "mongodb": 3, "postgresql": 3, "excel": 3,
        "jupyter notebooks": 3, "sas": 3, "apache kafka": 3, "nosql": 3, 
        "amazon sagemaker": 3, "mlflow": 3, "plotly": 3,
        
        # 2: Specialized / Bonus
        "keras": 2, "matplotlib": 2, "seaborn": 2, "snowflake": 2, "databricks": 2,
        "apache airflow": 2, "feature engineering": 2, "a/b testing": 2, 
        "apache hive": 2, "apache flink": 2, "dbt": 2, "kubeflow": 2
    }
    ,
    #Engineering
    "Engineering": {
    # 5: Critical (Core Foundations & Language)
    "java": 5, "c++": 5, "python": 5, "javascript": 5, "c": 5, 
    "embedded systems": 5, "sql": 5, "git": 5, "linux": 5, 
    "circuit design": 5, "matlab": 5, "microcontrollers": 5, 
    "data structures": 5, "algorithms": 5, "operating systems": 5,

    # 4: Highly Preferred (Industry Standards & Modern Stacks)
    "docker": 4, "kubernetes": 4, "amazon web services": 4, "react": 4, 
    "node.js": 4, "spring boot": 4, "typescript": 4, "vlsi design": 4, 
    "pcb design": 4, "fpga": 4, "digital signal processing": 4, 
    "plc": 4, "power electronics": 4, "control systems": 4, 
    "microservices": 4, "restful apis": 4, "ci/cd": 4, "system design": 4,

    # 3: Important (Frameworks, Tools & Sub-disciplines)
    "angular": 3, "vue.js": 3, "postgresql": 3, "mongodb": 3, 
    "jenkins": 3, "verilog": 3, "vhdl": 3, "labview": 3, 
    "scada": 3, "autocad": 3, "power systems": 3, "signal processing": 3, 
    "embedded c++": 3, "arduino": 3, "raspberry pi": 3, "networking": 3,
    "tcp/ip": 3, "unit testing": 3, "agile": 3, "scrum": 3,

    # 2: Specialized / Nice-to-Have
    "terraform": 2, "ansible": 2, "graphql": 2, "redis": 2, 
    "redux": 2, "raspberry pi": 2, "arm architecture": 2, "rtos": 2,
    "rf engineering": 2, "optical communication": 2, "cadence": 2, 
    "spice": 2, "pspice": 2, "proteus": 2, "solidworks": 2,
    "v-model": 2, "hardware security": 2, "edge computing": 2,
    "iot": 2, "mechatronics": 2
    
    }
    ,
    #Security
    "Security": {
    # 5: Critical (Core Foundations & Essential Certs)
    "cybersecurity": 5, "network security": 5, "information security": 5, 
    "penetration testing": 5, "ethical hacking": 5, "vulnerability assessment": 5, 
    "incident response": 5, "firewall": 5, "linux": 5, "python": 5, 
    "siem": 5, "ids/ips": 5, "cissp": 5, "ceh": 5, "comptia security+": 5,

    # 4: Highly Preferred (Infrastructure & Access Control)
    "identity and access management": 4, "cloud security": 4, "encryption": 4, 
    "cryptography": 4, "endpoint security": 4, "malware analysis": 4, 
    "wireshark": 4, "metasploit": 4, "nmap": 4, "burp suite": 4, "splunk": 4, 
    "nessus": 4, "aws security": 4, "azure sentinel": 4, "risk assessment": 4, 
    "security auditing": 4, "iso 27001": 4, "gdpr": 4, "nist framework": 4,

    # 3: Important (Application & Operations)
    "application security": 3, "owasp top 10": 3, "soc 2": 3, "hipaa": 3, 
    "pci dss": 3, "data privacy": 3, "threat intelligence": 3, "disaster recovery": 3, 
    "security operations center": 3, "vpn": 3, "bash": 3, "powershell": 3, 
    "active directory": 3, "digital forensics": 3, "security architecture": 3, 
    "zerotrust": 3, "devsecops": 3, "container security": 3, "okta": 3,

    # 2: Specialized / Bonus
    "reverse engineering": 2, "bug bounty": 2, "soar": 2, "osint": 2, 
    "physical security": 2, "blockchain security": 2, "iot security": 2, 
    "dark web monitoring": 2, "honeypots": 2, "cryptanalysis": 2, 
    "social engineering": 2, "phishing simulation": 2, "kali linux": 2, 
    "snort": 2, "suricata": 2, "crowdstrike": 2, "palo alto firewalls": 2,
    "cism": 2, "cisa": 2, "oscp": 2
    }
    ,
    #Marketing
"Marketing": {
    # 5: Critical (Core Performance & Strategy)
    "digital marketing": 5, "search engine optimization": 5, "search engine marketing": 5,
    "social media marketing": 5, "content marketing": 5, "email marketing": 5, 
    "google analytics": 5, "brand management": 5, "market research": 5, 
    "crm": 5, "data analysis": 5, "digital strategy": 5, "copywriting": 5,

    # 4: Highly Preferred (Platforms & Execution)
    "pay per click": 4, "facebook ads": 4, "google ads": 4, "linkedin ads": 4, 
    "campaign management": 4, "lead generation": 4, "hubspot": 4, "salesforce": 4, 
    "keyword research": 4, "conversion rate optimization": 4, "a/b testing": 4, 
    "public relations": 4, "influencer marketing": 4, "e-commerce": 4, 
    "product marketing": 4, "performance marketing": 4,

    # 3: Important (Creative Tools & Specialized Tactics)
    "adobe creative cloud": 3, "photoshop": 3, "illustrator": 3, "video editing": 3, 
    "canva": 3, "marketing automation": 3, "affiliate marketing": 3, 
    "growth hacking": 3, "event marketing": 3, "customer journey mapping": 3, 
    "competitive analysis": 3, "web analytics": 3, "b2b marketing": 3, "b2c marketing": 3,
    "direct mail marketing": 3, "guerrilla marketing": 3, "adobe experience manager": 3,

    # 2: Specialized / Nice-to-Have
    "motion graphics": 2, "3d modeling": 2, "podcast marketing": 2, 
    "sms marketing": 2, "loyalty programs": 2, "ux writing": 2, 
    "market segmentation": 2, "budget management": 2, "media buying": 2, 
    "wordpress": 2, "mailchimp": 2, "semrush": 2, "ahrefs": 2, "hootsuite": 2,
    "bufffer": 2, "sprout social": 2, "pivotal tracker": 2, "marketo": 2,
    "customer retention": 2, "omnichannel marketing": 2
    }
    ,
    #HR
    "HR": {
    # 5: Critical (Core Foundations & Compliance)
    "human resources": 5, "recruitment": 5, "talent acquisition": 5, 
    "employment law": 5, "payroll management": 5, "hr information systems": 5, 
    "applicant tracking systems": 5, "employee relations": 5, "compliance": 5, 
    "interviewing": 5, "talent sourcing": 5, "onboarding": 5,

    # 4: Highly Preferred (Strategy & Development)
    "performance management": 4, "strategic hr management": 4, "learning and development": 4, 
    "compensation and benefits": 4, "diversity and inclusion": 4, "hr analytics": 4, 
    "workforce planning": 4, "organizational development": 4, "employee engagement": 4, 
    "succession planning": 4, "leadership development": 4, "training and development": 4,
    "candidate experience": 4, "employer branding": 4, "change management": 4,

    # 3: Important (Ops & Specialized Tools)
    "labor relations": 3, "conflict resolution": 3, "hr policy development": 3, 
    "job analysis": 3, "total rewards": 3, "benefits administration": 3, 
    "workday": 3, "peopleops": 3, "technical recruiting": 3, "executive search": 3, 
    "grievance handling": 3, "hiring": 3, "background checks": 3, "career pathing": 3, 
    "exit interviews": 3, "salary surveys": 3, "performance appraisal": 3,

    # 2: Specialized / Tech / Bonus
    "successfactors": 2, "bamboohr": 2, "greenhouse": 2, "lever": 2, 
    "linkedin recruiter": 2, "adp": 2, "peoplesoft": 2, "culture transformation": 2, 
    "employee wellness": 2, "remote work management": 2, "dei strategy": 2, 
    "competency mapping": 2, "mediation": 2, "osha": 2, "handbook creation": 2, 
    "university relations": 2, "intern management": 2, "hr consulting": 2,
    "project management": 2, "administrative excellence": 2
    }
    ,
    #Design
    "Design": {
    # 5: Critical (Core Foundations & Industry Standards)
    "user experience": 5, "user interface": 5, "figma": 5, "adobe creative cloud": 5,
    "product design": 5, "visual design": 5, "user research": 5, "wireframing": 5,
    "prototyping": 5, "interaction design": 5, "information architecture": 5,
    "design systems": 5, "typography": 5, "color theory": 5, "layout design": 5,

    # 4: Highly Preferred (Strategy, Research & Advanced Tools)
    "adobe photoshop": 4, "adobe illustrator": 4, "sketch": 4, "user testing": 4,
    "usability testing": 4, "responsive design": 4, "mobile design": 4,
    "web design": 4, "graphic design": 4, "branding": 4, "logo design": 4,
    "human-centered design": 4, "service design": 4, "design thinking": 4,
    "accessibility": 4, "inclusive design": 4, "adobe xd": 4,

    # 3: Important (Execution & Cross-functional Skills)
    "motion graphics": 3, "adobe after effects": 3, "invision": 3, "zeplin": 3,
    "framer": 3, "storyboarding": 3, "copywriting": 3, "ux writing": 3,
    "customer journey mapping": 3, "persona development": 3, "concept development": 3,
    "art direction": 3, "print design": 3, "packaging design": 3, "illustration": 3,
    "html": 3, "css": 3, "agile": 3, "scrum": 3,

    # 2: Specialized / Bonus
    "3d modeling": 2, "blender": 2, "cinema 4d": 2, "adobe premiere pro": 2,
    "video editing": 2, "canva": 2, "infographic design": 2, "icon design": 2,
    "design management": 2, "photography": 2, "sketching": 2, "whiteboarding": 2,
    "creative direction": 2, "advertising design": 2, "environmental design": 2,
    "industrial design": 2, "design research": 2, "behavioral design": 2,
    "generative design": 2, "ai design tools": 2
    },
    #Finance and Ops

    "Finance & Ops": {
    # 5: Critical (Core Fiscal & Ops Control)
    "financial analysis": 5, "accounting": 5, "budgeting": 5, "financial modeling": 5, 
    "supply chain management": 5, "logistics": 5, "operations management": 5, 
    "project management": 5, "enterprise resource planning": 5, "sap": 5, 
    "financial reporting": 5, "forecasting": 5, "cash flow management": 5, 
    "internal controls": 5, "strategic planning": 5,

    # 4: Highly Preferred (Reporting, Audit & Compliance)
    "auditing": 4, "accounts payable": 4, "accounts receivable": 4, "quickbooks": 4, 
    "oracle": 4, "procurement": 4, "inventory management": 4, "risk management": 4, 
    "tax compliance": 4, "generally accepted accounting principles": 4, 
    "international financial reporting standards": 4, "cost accounting": 4, 
    "lean six sigma": 4, "process improvement": 4, "variance analysis": 4, 
    "working capital management": 4, "vendor management": 4,

    # 3: Important (Data Tools & Specialized Ops)
    "excel": 3, "vba": 3, "investment banking": 3, "lean manufacturing": 3, 
    "warehouse management": 3, "quality assurance": 3, "business process modeling": 3, 
    "data visualization": 3, "tableau": 3, "power bi": 3, "sql": 3, 
    "fixed assets": 3, "general ledger": 3, "financial auditing": 3, 
    "mergers and acquisitions": 3, "capital budgeting": 3, "demand planning": 3, 
    "change management": 3, "operational excellence": 3, "six sigma green belt": 3,

    # 2: Specialized / Tech / Bonus
    "kaizen": 2, "just-in-time": 2, "total quality management": 2, "netsuite": 2, 
    "microsoft dynamics": 2, "crm": 2, "corporate finance": 2, "treasury management": 2, 
    "asset management": 2, "equity research": 2, "portfolio management": 2, 
    "cost benefit analysis": 2, "regulatory reporting": 2, "import export": 2, 
    "contract negotiation": 2, "facility management": 2, "six sigma black belt": 2, 
    "business intelligence": 2, "fintech": 2, "ebitda": 2
    },
    #General
    "General Professional/Tech": {
    # 5: Critical (Universal Workplace Essentials)
    "communication": 5, "problem solving": 5, "project management": 5, 
    "time management": 5, "teamwork": 5, "leadership": 5, 
    "decision making": 5, "planning": 5, "adaptability": 5, 
    "microsoft office": 5, "critical thinking": 5, "organization": 5,

    # 4: Highly Preferred (Client-Facing & Strategic)
    "customer service": 4, "business development": 4, "presentation skills": 4, 
    "negotiation": 4, "conflict resolution": 4, "strategic thinking": 4, 
    "analytical skills": 4, "technical writing": 4, "data entry": 4, 
    "google workspace": 4, "public speaking": 4, "research": 4,
    "customer relationship management": 4, "attention to detail": 4,

    # 3: Important (Modern Workplace Tools & Admin)
    "documentation": 3, "it support": 3, "jira": 3, "slack": 3, 
    "zoom": 3, "microsoft teams": 3, "trello": 3, "asana": 3, 
    "meeting facilitation": 3, "business writing": 3, "quality assurance": 3, 
    "event planning": 3, "administrative support": 3, "scheduling": 3,
    "client relations": 3, "process management": 3, "collaboration": 3,

    # 2: Specialized / Soft Skill Bonus
    "multitasking": 2, "creativity": 2, "emotional intelligence": 2, 
    "interpersonal skills": 2, "networking": 2, "troubleshooting": 2, 
    "data literacy": 2, "cyber hygiene": 2, "social intelligence": 2, 
    "resource management": 2, "mentoring": 2, "coaching": 2,
    "active listening": 2, "cultural awareness": 2, "work ethic": 2,
    "project management professional": 2, "notion": 2, "basecamp": 2,
    "confluence": 2, "clickup": 2
    }

}

if __name__ == "__main__":
    seed_all_domains(DOMAIN_DATA)