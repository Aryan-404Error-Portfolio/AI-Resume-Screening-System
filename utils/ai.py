import os
import json
import logging
import re
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
        logger.warning("No API key found, using text extraction mode")
except Exception as e:
    USE_AI = False
    logger.warning(f"AI setup failed: {e}, using text extraction mode")

def clean_json(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def extract_from_text(resume_text):
    """Extract real candidate details from resume text using regex/rules."""
    logger.info("Extracting real data from resume text")
    
    # Extract name (first line or after "Name:")
    name = ""
    lines = resume_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and len(line) > 2 and not line.lower().startswith(('email', 'phone', 'skills', 'education', 'experience')):
            name = line
            break
    
    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
    email = email_match.group(0) if email_match else ""
    
    # Extract phone
    phone_match = re.search(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', resume_text)
    phone = phone_match.group(0) if phone_match else ""
    
    # Extract skills (common tech skills)
    common_skills = ["Python", "Java", "JavaScript", "C++", "C#", "React", "Angular", "Vue", 
                     "Node.js", "Express", "Django", "Flask", "FastAPI", "SQL", "MySQL", 
                     "PostgreSQL", "MongoDB", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
                     "Linux", "Git", "GitHub", "CI/CD", "Jenkins", "TensorFlow", "PyTorch",
                     "Machine Learning", "Deep Learning", "NLP", "Data Science", "Pandas",
                     "NumPy", "Scikit-learn", "Tableau", "PowerBI", "Excel", "HTML", "CSS",
                     "Bootstrap", "REST API", "GraphQL", "Microservices", "Agile", "Scrum"]
    
    found_skills = []
    resume_lower = resume_text.lower()
    for skill in common_skills:
        if skill.lower() in resume_lower:
            found_skills.append(skill)
    
    # Extract education
    education = ""
    edu_patterns = [r'(?:Bachelor|Master|PhD|B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?Sc|M\.?Sc)[^\n]*',
                    r'(?:Bachelor\'?s|Master\'?s|Doctorate)[^\n]*(?:Degree|in)[^\n]*']
    for pattern in edu_patterns:
        edu_match = re.search(pattern, resume_text, re.IGNORECASE)
        if edu_match:
            education = edu_match.group(0).strip()
            break
    
    # Extract experience
    experience = ""
    exp_patterns = [r'(\d+)\+?\s*(?:years?|yrs?)[^\n]*(?:experience|exp)[^\n]*',
                    r'(?:experience|worked)[^\n]*(\d+)[^\n]*(?:years?|yrs?)']
    for pattern in exp_patterns:
        exp_match = re.search(pattern, resume_text, re.IGNORECASE)
        if exp_match:
            experience = exp_match.group(0).strip()
            break
    
    # Extract certifications
    certifications = []
    cert_patterns = [r'(?:AWS|Azure|Google|Microsoft)[^\n]*(?:Certified|Certification|Certificate)',
                     r'(?:PMP|Scrum|Agile|ITIL|CCNA|CISSP)[^\n]*']
    for pattern in cert_patterns:
        cert_matches = re.finditer(pattern, resume_text, re.IGNORECASE)
        for match in cert_matches:
            cert = match.group(0).strip()
            if cert and cert not in certifications:
                certifications.append(cert)
    
    return {
        "name": name or "Candidate",
        "email": email,
        "phone": phone,
        "skills": found_skills if found_skills else ["Not specified"],
        "education": education or "Not specified",
        "experience": experience or "Not specified",
        "certifications": certifications if certifications else []
    }

def analyze_from_text(resume_text, job_description):
    """Calculate match score based on real text comparison."""
    logger.info("Calculating match score from text comparison")
    
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()
    
    # Extract skills from JD
    common_skills = ["python", "java", "javascript", "c++", "c#", "react", "angular", "vue", 
                     "node.js", "express", "django", "flask", "fastapi", "sql", "mysql", 
                     "postgresql", "mongodb", "aws", "azure", "gcp", "docker", "kubernetes",
                     "linux", "git", "github", "ci/cd", "jenkins", "tensorflow", "pytorch",
                     "machine learning", "deep learning", "nlp", "data science", "pandas",
                     "numpy", "scikit-learn", "tableau", "powerbi", "excel", "html", "css",
                     "bootstrap", "rest api", "graphql", "microservices", "agile", "scrum"]
    
    # Find skills mentioned in JD
    jd_skills = []
    for skill in common_skills:
        if skill in jd_lower:
            jd_skills.append(skill)
    
    # Find which JD skills are in resume
    matched = []
    missing = []
    for skill in jd_skills:
        if skill in resume_lower:
            matched.append(skill.title())
        else:
            missing.append(skill.title())
    
    # Calculate score
    if len(jd_skills) > 0:
        score = int((len(matched) / len(jd_skills)) * 100)
    else:
        # Fallback: check word overlap
        resume_words = set(resume_lower.split())
        jd_words = set(jd_lower.split())
        common = resume_words & jd_words
        score = min(int((len(common) / max(len(jd_words), 1)) * 100), 95)
    
    score = max(score, 50)  # Minimum 50%
    
    # Generate reason
    if score >= 80:
        reason = f"Excellent match! Candidate has {len(matched)} of {len(jd_skills)} required skills."
    elif score >= 60:
        reason = f"Good match. Candidate has {len(matched)} skills but missing: {', '.join(missing[:3])}."
    else:
        reason = f"Partial match. Candidate missing key skills: {', '.join(missing[:3])}."
    
    return {
        "match_score": score,
        "matched_skills": matched if matched else ["General skills"],
        "missing_skills": missing if missing else [],
        "reason": reason
    }

def extract_candidate_details(resume_text):
    """Extract candidate details — use AI if available, else extract from text."""
    if USE_AI:
        try:
            prompt = f"""You are an expert AI Resume Parser. Extract ONLY: name, email, phone, skills, education, experience, certifications. Return ONLY valid JSON. Resume: {resume_text}"""
            response = model.generate_content(prompt)
            text = clean_json(response.text)
            return json.loads(text)
        except Exception as e:
            logger.warning(f"AI failed, extracting from text: {e}")
    
    return extract_from_text(resume_text)

def analyze_candidate(resume_text, job_description):
    """Analyze candidate — use AI if available, else compare text."""
    if USE_AI:
        try:
            prompt = f"""Compare resume with Job Description. Return ONLY valid JSON with match_score, matched_skills, missing_skills, reason. Resume: {resume_text} Job Description: {job_description}"""
            response = model.generate_content(prompt)
            text = clean_json(response.text)
            return json.loads(text)
        except Exception as e:
            logger.warning(f"AI failed, analyzing from text: {e}")
    
    return analyze_from_text(resume_text, job_description)