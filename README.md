# AI-Powered Resume Screening & Candidate Ranking System

## Overview

The AI Resume Screening System is a Flask-based web application that automates resume screening using Google's Gemini AI. It extracts candidate information from resumes, compares it with a job description, calculates a match score, ranks candidates, and stores results in a SQLite database.

---

## Problem Statement

Manual resume screening is time-consuming and inconsistent. This system leverages Natural Language Processing (NLP) and Large Language Models (LLM) to automatically parse resumes, extract structured data, and score candidates against job descriptions — providing a ranked, filterable dashboard for recruiters.

---

## Features

- Upload multiple resumes (PDF/DOCX)
- AI-based resume parsing (Name, Email, Skills, Education, Experience, Certifications)
- Job Description matching
- Match score calculation (0–100%)
- Candidate ranking by score
- Missing/preferred skills highlighting
- SQLite database storage
- CSV export
- Skill filtering
- Minimum score filtering
- Delete all candidate records
- Responsive Bootstrap UI

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend language |
| Flask | REST API & Web framework |
| SQLite | Database storage |
| Google Gemini AI (LLM) | Resume parsing & candidate analysis |
| NLP (via LLM) | Text extraction and semantic understanding |
| Pandas | Data processing & CSV export |
| pdfplumber | PDF text extraction |
| python-docx | DOCX text extraction |
| Bootstrap 5 | Frontend UI |
| Flasgger | Swagger / OpenAPI documentation |
| Gunicorn | Production WSGI server |

---

## Project Structure
AI-Resume-Screening-System/
│
├── app.py                  # Main Flask application (routes, API, logging)
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database (auto-generated)
├── README.md               # Project documentation
├── .gitignore              # Ignored files (.env, logs, uploads, etc.)
│
├── templates/
│   ├── index.html          # Resume upload & JD input page
│   └── dashboard.html      # Candidate ranking & filter dashboard
│
├── static/
│   └── style.css           # Custom styling
│
├── utils/
│   ├── init.py
│   ├── ai.py               # Gemini AI integration (parsing + analysis)
│   └── parser.py           # PDF & DOCX text extraction
│
├── uploads/                # Temporary uploaded resumes
└── logs/                   # Application logs (auto-generated)
plain

---

## Database Schema

**Table: `candidates`**

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| name | TEXT | Candidate full name |
| email | TEXT | Candidate email |
| phone | TEXT | Candidate phone |
| education | TEXT | Education details |
| experience | TEXT | Work experience |
| skills | TEXT | Comma-separated skills list |
| certifications | TEXT | Comma-separated certifications |
| match_score | INTEGER | AI match score (0–100) |
| matched_skills | TEXT | Skills matched with JD |
| missing_skills | TEXT | Skills missing from JD |
| reason | TEXT | AI reasoning for score |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page (upload form) |
| POST | `/analyze` | Upload resumes + JD, process and rank |
| GET | `/filter` | Filter candidates by skill & min score |
| GET | `/delete` | Delete all candidate records |
| GET | `/export` | Export candidates to CSV |
| GET | `/api/candidates` | REST API: Get all candidates as JSON |
| GET | `/apidocs/` | **Swagger UI** — Interactive API documentation |

---

## Installation

Clone the repository
git clone https://github.com/Error-Portfolio/AI-Resume-Screening-System.git
cd AI-Resume-Screening-System
plain

Create virtual environment
python -m venv venv
plain

Activate environment

**Windows:**
venv\Scripts\activate
plain

**Linux/Mac:**
source venv/bin/activate
plain

Install dependencies
pip install -r requirements.txt
plain

Configure API Key

Create a `.env` file in the project root:
GEMINI_API_KEY=your_google_gemini_api_key_here
plain

Run the application
python app.py
plain

Open browser
http://127.0.0.1:5000
plain

View API Documentation (Swagger)
http://127.0.0.1:5000/apidocs/
plain

---

## Logging & Exception Handling

All operations are logged to `logs/app.log`:
- Resume processing status
- API errors and retries
- Database operations
- Export/downloads

View logs:
cat logs/app.log
plain

Error handling includes:
- **API Quota Exceeded**: Automatic retry (3 attempts) with 35s delay, then mock fallback
- **Invalid File Format**: Skipped with logged warning
- **Database Errors**: Graceful fallback with logged error
- **Missing API Key**: Clear error message on startup
- **JSON Parse Errors**: Returns empty safe structure instead of crashing

---

## Sample Dataset

The system accepts any PDF or DOCX resume. For testing, use sample resumes with:
- **Skills**: Python, SQL, Machine Learning, Flask, React, etc.
- **Experience**: 1–5 years in software/AI development
- **Education**: Bachelor's/Master's in CS or related field

Upload 2–3 sample resumes and provide a job description like:
> "Looking for a Python developer with 2+ years experience in Flask, SQL, and Machine Learning. Knowledge of Docker and cloud platforms is a plus."

---

## Deployment

### Render (Free)
1. Push code to GitHub
2. Go to [render.com](https://render.com), create Web Service
3. Connect your GitHub repo
4. Set environment variable: `GEMINI_API_KEY`
5. Deploy

### PythonAnywhere
1. Upload files via Git
2. Configure WSGI to point to `app.py`
3. Set environment variables in dashboard
4. Reload app

---

## Future Improvements

- Login Authentication
- Email Notifications
- Advanced AI Ranking
- Resume Recommendation
- Interview Scheduling
- PostgreSQL / MySQL database migration
- OCR support for scanned resumes
- Semantic search using vector embeddings
- AI-generated interview questions
- Docker containerization

---

## Author

**Aryan Gupta**

Developed as an Academic AI Project.

- GitHub: [Aryan-404Error-Portfolio](https://github.com/Aryan-404Error-Portfolio)
- Project: [AI-Resume-Screening-System](https://github.com/Aryan-404Error-Portfolio/AI-Resume-Screening-System)
