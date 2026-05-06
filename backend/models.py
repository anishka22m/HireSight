from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, String, ForeignKey, Float, DateTime, func
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    job_title = Column(Text)
    company = Column(Text)
    location = Column(Text)
    description = Column(Text)
    domain = Column(Text)
    role = Column(Text)
    source = Column(Text)

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    skill_name = Column(Text, unique=True)

class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id = Column(Integer, ForeignKey("jobs.id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, unique=True)
    extracted_text = Column(Text)
    cleaned_text = Column(Text)
    predicted_role = Column(String)

class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    resume_id = Column(Integer, ForeignKey("resumes.id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)

class MarketTrend(Base):
    __tablename__ = "market_trends"
    id = Column(Integer, primary_key=True)
    domain = Column(String)           # e.g., "Data Science/Analytics"
    skill_name = Column(String)       # e.g., "Python"
    demand_percentage = Column(Float) # Frequency in JDs (0-100)
    month_year = Column(String)       # e.g., "May 2026"
    recorded_at = Column(DateTime, default=func.now())