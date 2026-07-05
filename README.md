# AI-Resume-Screening-System
AI-powered Resume Screening and Candidate Ranking System




# AI Resume Screening System

## Overview

The AI Resume Screening System is a Flask-based web application that automates resume screening using Google's Gemini AI. It extracts candidate information from resumes, compares it with a job description, calculates a match score, ranks candidates, and stores results in a SQLite database.

---

## Features

- Upload multiple resumes (PDF/DOCX)
- AI-based resume parsing
- Job Description matching
- Match score calculation
- Candidate ranking
- SQLite database storage
- CSV export
- Skill filtering
- Minimum score filtering
- Delete all candidate records
- Responsive Bootstrap UI

---

## Technologies Used

- Python
- Flask
- SQLite
- Bootstrap 5
- HTML
- CSS
- Pandas
- pdfplumber
- python-docx
- Google Gemini API

---

## Project Structure

```
AIResume/

│── app.py

│── requirements.txt

│── database.db

│── README.md

│── .gitignore

│

├── templates/

│ ├── index.html

│ └── dashboard.html

│

├── static/

│ └── style.css

│

├── utils/

│ ├── ai.py

│ └── parser.py

│

└── uploads/
```

---

## Installation

Clone the repository

```
git clone <repository-link>
```

Open project folder

```
cd AIResume
```

Create virtual environment

```
python -m venv venv
```

Activate environment

Windows

```
venv\Scripts\activate
```

Install dependencies

```
pip install -r requirements.txt
```

Run the application

```
python app.py
```

Open browser

```
http://127.0.0.1:5000
```

---

## Future Improvements

- Login Authentication
- Email Notifications
- Advanced AI Ranking
- Resume Recommendation
- Interview Scheduling

---

## Author

Developed as an Academic AI Project.
