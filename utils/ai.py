import google.generativeai as genai
import json
import os
import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def clean_json(text):
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")

    if text.startswith("```"):
        text = text.replace("```", "")

    if text.endswith("```"):
        text = text.replace("```", "")

    return text.strip()


def extract_candidate_details(resume_text):

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

    response = model.generate_content(prompt)

    text = clean_json(response.text)

    return json.loads(text)


def analyze_candidate(resume_text, job_description):

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

    response = model.generate_content(prompt)

    text = clean_json(response.text)

    return json.loads(text)