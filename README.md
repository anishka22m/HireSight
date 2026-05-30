# HireSight

HireSight is an AI-powered Resume Intelligence Platform that evaluates student and fresher resumes against current industry expectations using Natural Language Processing, Machine Learning, semantic similarity analysis, and market intelligence.

Unlike traditional Applicant Tracking Systems (ATS) that rely primarily on keyword matching, HireSight performs contextual resume analysis using Sentence-BERT embeddings, identifies skill gaps, predicts suitable career domains, analyzes market demand trends, and generates personalized upskilling recommendations.

## Problem Statement

Fresh graduates often struggle to understand how well their resumes align with industry requirements. Traditional resume screening systems focus heavily on keyword matching and frequently fail to capture contextual meaning, transferable skills, and emerging market expectations.

HireSight addresses this challenge by combining semantic resume analysis with market intelligence to provide actionable employability insights.

---

## Key Features

### Resume Intelligence Engine

* Upload resumes in PDF format
* Automated resume text extraction and preprocessing
* Context-aware skill extraction and normalization
* Semantic understanding of resume content using Sentence-BERT

### Domain Classification

* Predicts the most suitable career domain for a candidate
* Supports domains such as:

  * Engineering
  * Data Science
  * Marketing
  * Human Resources
  * Design
  * Security
* Uses a trained Linear SVM classifier on SBERT embeddings

### Hybrid Resume Scoring

* Combines:

  * Semantic similarity analysis
  * Weighted benchmark skill matching
* Generates a realistic resume alignment score
* Avoids limitations of traditional keyword-only ATS systems

### Skill Gap Analysis

* Identifies missing skills based on domain benchmarks
* Highlights strengths and weaknesses in the resume
* Generates matched and missing skill reports

### Market Intelligence Dashboard

* Tracks domain-wise skill demand trends
* Analyzes job market datasets
* Identifies emerging technologies and high-demand skills
* Visualizes market insights using interactive charts

### Personalized Recommendations

* Generates role-specific improvement suggestions
* Recommends learning resources based on missing skills
* Creates AI-generated 7-day upskilling sprint plans using a cloud-hosted LLaMA model

### Interactive Analytics Dashboard

* Resume score visualization
* Skill comparison reports
* Market trend analysis
* Recommendation interface

---

## System Architecture

```text
Resume Upload
      │
      ▼
Resume Parsing & Preprocessing
      │
      ▼
SBERT Semantic Embedding Generation
      │
      ▼
Linear SVM Domain Classification
      │
      ▼
Skill Validation & Benchmark Matching
      │
      ▼
Semantic Similarity Analysis
      │
      ▼
Hybrid Resume Scoring
      │
      ▼
Recommendation Engine
      │
      ▼
Results Dashboard & Market Intelligence
```

---

## Technology Stack

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* Chart.js

### Backend

* Python
* FastAPI
* Uvicorn

### Database

* PostgreSQL
* SQLAlchemy ORM

### Machine Learning & NLP

* Scikit-learn
* Sentence-BERT (all-MiniLM-L6-v2)
* NLTK
* NumPy
* Pandas

### AI & Recommendation Layer

* LLaMA-based recommendation generation
* Semantic similarity analysis
* Cosine similarity scoring

### Resume Processing

* pdfplumber
* Regular Expressions (Regex)

---

## Machine Learning Pipeline

### Semantic Embeddings

The system uses the Sentence-BERT (all-MiniLM-L6-v2) model to convert resumes and benchmark datasets into dense semantic vectors.

### Classification Models Evaluated

| Model               | Accuracy | Weighted F1 |
| ------------------- | -------- | ----------- |
| Logistic Regression | 94.6%    | 0.94        |
| Random Forest       | 90.7%    | 0.89        |
| Linear SVM          | 94.6%    | 0.94        |

Linear SVM was selected as the final deployment model due to its stability and strong performance on high-dimensional semantic embeddings.

---

## Resume Scoring Methodology

The final score is generated using a hybrid approach:

* Semantic Similarity Score

  * Measures contextual alignment between resume content and industry benchmarks

* Weighted Skill Matching Score

  * Compares extracted skills against domain-specific benchmark skills
  * Uses weighted importance values to prioritize critical competencies

The final score combines both components to provide a balanced employability assessment.

---

## Database Design

The platform uses PostgreSQL to manage:

* Uploaded resumes
* Extracted resume content
* Benchmark skills
* Job descriptions
* Market trend records
* Recommendation mappings

The database follows a relational architecture supporting efficient skill comparison and recommendation workflows.

---

## Testing & Validation

The system was evaluated using:

### White Box Testing

* PDF extraction validation
* Text preprocessing verification
* SBERT embedding generation
* Domain classification validation
* Weighted score calculation checks
* Recommendation engine testing

### Black Box Testing

* Strong candidate profiles
* Weak fresher profiles
* ATS-unfriendly resumes
* Multi-domain resumes
* Ambiguous resume structures
* Sparse resumes with limited skills

### Error Analysis

* Confusion matrix evaluation
* Misclassification analysis
* Class-wise performance analysis
* Semantic drift investigation

---

## Results

* Achieved approximately 94.6% classification accuracy using Linear SVM
* Successfully identified domain-specific skill gaps
* Generated personalized learning recommendations
* Demonstrated robust performance across varied resume structures
* Improved contextual understanding compared to traditional keyword-based evaluation systems

---

## Future Enhancements

* Real-time job portal integration
* Adaptive confidence-based scoring
* Multilingual resume analysis
* Recruiter-focused analytics dashboard
* Portfolio and GitHub integration
* Advanced market forecasting
* Personalized long-term career roadmap generation

---

## Project Objective

The primary objective of HireSight is to help students and fresh graduates understand how their skills align with current industry requirements, identify employability gaps, and receive structured guidance for continuous improvement through AI-driven analysis and recommendations.
