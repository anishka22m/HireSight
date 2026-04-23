from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, String, ForeignKey

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