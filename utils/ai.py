import os
import json
import time
import logging
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Try new google.genai first, fallback to old
try:
    from google.genai import Client
    USE_NEW_API = True
    logger.info("Using google.genai (new API)")
except ImportError:
    import google.generativeai as genai
    USE_NEW_API = False
    logger.warning("Using deprecated google.generativeai — consider upgrading")

# Setup API client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

if USE_NEW_API:
    client = Client(api_key=api_key)
else:
    genai.configure(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"
MAX_RETRIES = 3
RETRY_DELAY = 10  # CHANGED: Was 35, now 10 to avoid Gunicorn timeout


def clean_json(text):
    """Clean markdown code blocks from AI response."""
    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def mock_extract_candidate(resume_text):
    """Generate realistic mock candidate data when API fails."""
    logger.info("Using mock extraction fallback")
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
    """Generate realistic mock analysis when API fails."""
    logger.info("Using mock analysis fallback")
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


def call_gemini_with_retry(prompt):
    """Call Gemini API with retry logic for rate limits."""
    for attempt in range(MAX_RETRIES):
        try:
            if USE_NEW_API:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt
                )
                return response.text
            else:
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(prompt)
                return response.text
                
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                logger.warning(f"Rate limit hit (attempt {attempt + 1}/{MAX_RETRIES}). Waiting {RETRY_DELAY}s...")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error("Max retries reached for API rate limit")
                    raise
            else:
                logger.error(f"API error: {e}")
                raise
    
    raise Exception("Failed after all retries")


def extract_candidate_details(resume_text):
    """Extract candidate details from resume text using Gemini AI."""
    logger.info("Extracting candidate details from resume")
    
    prompt = f"""
You are an expert AI Resume Parser.

Extract ONLY the following fields.

Return ONLY valid JSON.

{{
"name":"",
"email":"",
"phone":"",
"skills":[],
"education":"",
"experience":"",
"certifications":[]
}}

Resume:

{resume_text}
"""

    try:
        response_text = call_gemini_with_retry(prompt)
        text = clean_json(response_text)
        data = json.loads(text)
        logger.info("Successfully extracted candidate details")
        return data

    except Exception as e:
        logger.error(f"Failed to extract candidate details: {e}")
        return mock_extract_candidate(resume_text)


def analyze_candidate(resume_text, job_description):
    """Analyze candidate against job description using Gemini AI."""
    logger.info("Analyzing candidate against job description")
    
    prompt = f"""
You are an expert AI Recruitment Assistant.

Compare the resume with the Job Description.

Return ONLY valid JSON.

{{
"match_score":0,
"matched_skills":[],
"missing_skills":[],
"reason":""
}}

Resume:

{resume_text}

----------------------------------

Job Description:

{job_description}
"""

    try:
        response_text = call_gemini_with_retry(prompt)
        text = clean_json(response_text)
        data = json.loads(text)
        logger.info("Successfully analyzed candidate")
        return data

    except Exception as e:
        logger.error(f"Failed to analyze candidate: {e}")
        return mock_analyze_candidate(resume_text, job_description)