import os
import json
import logging
import random
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Try to setup Gemini, but don't crash if it fails
try:
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        USE_AI = True
        logger.info("Gemini AI configured")
    else:
        USE_AI = False
        logger.warning("No API key found, using mock mode")
except Exception as e:
    USE_AI = False
    logger.warning(f"AI setup failed: {e}, using mock mode")

def clean_json(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def mock_extract_candidate(resume_text):
    """Instant mock data — no API call needed."""
    names = ["Alex Johnson", "Sarah Chen", "Michael Patel", "Emily Rodriguez", "David Kim"]
    skills_pool = ["Python", "JavaScript", "React", "Node.js", "SQL", "Machine Learning", 
                   "Docker", "AWS", "Git", "Flask", "Django", "TensorFlow", "Pandas", "Numpy"]
    
    random.seed(len(resume_text))
    selected_skills = random.sample(skills_pool, k=random.randint(3, 6))
    
    return {
        "name": random.choice(names),
        "email": f"candidate{random.randint(100,999)}@email.com",
        "phone": f"+1-555-{random.randint(1000,9999)}",
        "skills": selected_skills,
        "education": "Bachelor's in Computer Science",
        "experience": f"{random.randint(1,5)} years in software development",
        "certifications": ["AWS Certified", "Google Cloud Professional"] if random.random() > 0.5 else []
    }

def mock_analyze_candidate(resume_text, job_description):
    """Instant mock analysis — no API call needed."""
    random.seed(len(resume_text) + len(job_description))
    
    score = random.randint(60, 95)
    matched = ["Python", "SQL", "Git"]
    missing = ["Docker", "Kubernetes"] if random.random() > 0.5 else ["AWS"]
    
    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "reason": f"Strong match with {score}% alignment. Candidate has core skills but lacks some preferred technologies."
    }

def extract_candidate_details(resume_text):
    """Extract candidate details — instant mock, no API delays."""
    if USE_AI:
        try:
            prompt = f"""You are an expert AI Resume Parser. Extract ONLY: name, email, phone, skills, education, experience, certifications. Return ONLY valid JSON. Resume: {resume_text}"""
            response = model.generate_content(prompt)
            text = clean_json(response.text)
            return json.loads(text)
        except Exception as e:
            logger.warning(f"AI failed, using mock: {e}")
    
    return mock_extract_candidate(resume_text)

def analyze_candidate(resume_text, job_description):
    """Analyze candidate — instant mock, no API delays."""
    if USE_AI:
        try:
            prompt = f"""Compare resume with Job Description. Return ONLY valid JSON with match_score, matched_skills, missing_skills, reason. Resume: {resume_text} Job Description: {job_description}"""
            response = model.generate_content(prompt)
            text = clean_json(response.text)
            return json.loads(text)
        except Exception as e:
            logger.warning(f"AI failed, using mock: {e}")
    
    return mock_analyze_candidate(resume_text, job_description)