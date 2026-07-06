import os
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, send_file, redirect, jsonify
from flasgger import Swagger

from utils.parser import extract_text
from utils.ai import extract_candidate_details, analyze_candidate

app = Flask(__name__)

# ========== LOGGING SETUP ==========
if not os.path.exists('logs'):
    os.makedirs('logs')

handler = RotatingFileHandler('logs/app.log', maxBytes=100000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# ========== SWAGGER / OPENAPI SETUP ==========
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}
Swagger(app, config=swagger_config)

UPLOAD_FOLDER = "uploads"
DATABASE = "database.db"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def init_db():
    """Initialize SQLite database with candidates table."""
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS candidates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            education TEXT,
            experience TEXT,
            skills TEXT,
            certifications TEXT,
            match_score INTEGER,
            matched_skills TEXT,
            missing_skills TEXT,
            reason TEXT
        )
        """)

        conn.commit()
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Database initialization error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


init_db()


def fetch_candidates(skill="", min_score=0):
    """Fetch candidates from database with optional filters."""
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        query = """
        SELECT *
        FROM candidates
        WHERE match_score >= ?
        """

        values = [min_score]

        if skill.strip() != "":
            query += " AND skills LIKE ?"
            values.append(f"%{skill}%")

        query += " ORDER BY match_score DESC"

        cur.execute(query, values)
        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "education": row[4],
                "experience": row[5],
                "skills": row[6].split(",") if row[6] else [],
                "certifications": row[7].split(",") if row[7] else [],
                "match_score": row[8],
                "matched_skills": row[9].split(",") if row[9] else [],
                "missing_skills": row[10].split(",") if row[10] else [],
                "reason": row[11]
            })

        return results
    except Exception as e:
        app.logger.error(f"Error fetching candidates: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()


@app.route("/")
def home():
    """
    Home page with resume upload form.
    ---
    responses:
      200:
        description: Returns the home page
    """
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze resume(s) against job description.
    Supports both file upload and pasted text.
    ---
    parameters:
      - name: resumes
        in: formData
        type: file
        required: false
        description: Resume files (PDF/DOCX)
        collectionFormat: multi
      - name: resume_text
        in: formData
        type: string
        required: false
        description: Pasted resume text
      - name: job_description
        in: formData
        type: string
        required: true
        description: Job description text
    responses:
      200:
        description: Returns dashboard with ranked candidates
      400:
        description: Bad request
      500:
        description: Server error
    """
    try:
        # Read job description
        job_description = request.form.get("job_description", "").strip()

        app.logger.info(f"Request method: {request.method}")
        app.logger.info(f"Content type: {request.content_type}")
        app.logger.info(f"Job description length: {len(job_description)}")

        # Validate job description
        if not job_description:
            app.logger.warning("No job description provided")
            return "Job description is required", 400

        # Collect resume texts from all sources
        resume_texts = []

        # Source 1: Pasted text
        pasted_text = request.form.get("resume_text", "").strip()
        if pasted_text:
            resume_texts.append(pasted_text)
            app.logger.info(f"Using pasted resume text, length: {len(pasted_text)}")

        # Source 2: Uploaded files
        resumes = request.files.getlist("resumes")
        if resumes:
            for resume in resumes:
                if resume.filename and resume.filename != "":
                    try:
                        path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
                        resume.save(path)
                        app.logger.info(f"Processing uploaded file: {resume.filename}")
                        file_text = extract_text(path)
                        if file_text and file_text.strip():
                            resume_texts.append(file_text)
                            app.logger.info(f"Extracted text from file, length: {len(file_text)}")
                    except Exception as e:
                        app.logger.error(f"Failed to process file {resume.filename}: {e}")

        # Validate: at least one resume source required
        if not resume_texts:
            app.logger.warning("No resume text or file provided")
            return "Please upload a resume file or paste resume text", 400

        # Process all resume texts
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        processed = 0
        failed = 0

        for text in resume_texts:
            try:
                candidate = extract_candidate_details(text)
                analysis = analyze_candidate(text, job_description)

                cur.execute("""
                INSERT INTO candidates(
                    name,email,phone,
                    education,experience,
                    skills,certifications,
                    match_score,
                    matched_skills,
                    missing_skills,
                    reason
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    candidate.get("name", ""),
                    candidate.get("email", ""),
                    candidate.get("phone", ""),
                    candidate.get("education", ""),
                    candidate.get("experience", ""),
                    ",".join(candidate.get("skills", [])),
                    ",".join(candidate.get("certifications", [])),
                    analysis.get("match_score", 0),
                    ",".join(analysis.get("matched_skills", [])),
                    ",".join(analysis.get("missing_skills", [])),
                    analysis.get("reason", "")
                ))
                processed += 1
                app.logger.info(f"Successfully processed resume")

            except Exception as e:
                failed += 1
                app.logger.error(f"Failed to process resume: {e}")
                continue

        conn.commit()
        conn.close()

        app.logger.info(f"Batch complete: {processed} processed, {failed} failed")
        results = fetch_candidates()
        return render_template("dashboard.html", results=results)

    except Exception as e:
        app.logger.error(f"Error in analyze route: {e}")
        return "An error occurred while processing resumes", 500


@app.route("/filter", methods=["GET"])
def filter_candidates():
    """
    Filter candidates by skill and minimum score.
    ---
    parameters:
      - name: skill
        in: query
        type: string
        required: false
        description: Skill to filter by
      - name: score
        in: query
        type: integer
        required: false
        description: Minimum match score
    responses:
      200:
        description: Returns filtered dashboard
    """
    try:
        skill = request.args.get("skill", "").strip()

        try:
            min_score = int(request.args.get("score", 0))
        except ValueError:
            min_score = 0

        results = fetch_candidates(skill, min_score)
        return render_template("dashboard.html", results=results)
    except Exception as e:
        app.logger.error(f"Error in filter route: {e}")
        return "An error occurred while filtering", 500


@app.route("/delete")
def delete():
    """
    Delete all candidate records.
    ---
    responses:
      302:
        description: Redirects to home page
    """
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("DELETE FROM candidates")
        conn.commit()
        conn.close()
        app.logger.info("All candidates deleted")
        return redirect("/")
    except Exception as e:
        app.logger.error(f"Error deleting candidates: {e}")
        return "An error occurred while deleting records", 500


@app.route("/export")
def export():
    """
    Export candidates to CSV.
    ---
    responses:
      200:
        description: Returns CSV file
    """
    try:
        conn = sqlite3.connect(DATABASE)
        df = pd.read_sql_query(
            "SELECT * FROM candidates ORDER BY match_score DESC",
            conn
        )
        conn.close()

        filename = "shortlisted_candidates.csv"
        df.to_csv(filename, index=False)
        app.logger.info("CSV export generated")

        return send_file(filename, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error exporting CSV: {e}")
        return "An error occurred while exporting", 500


@app.route("/api/candidates", methods=["GET"])
def api_candidates():
    """
    API endpoint to get all candidates as JSON.
    ---
    responses:
      200:
        description: Returns list of candidates
    """
    try:
        results = fetch_candidates()
        return jsonify({"candidates": results, "count": len(results)})
    except Exception as e:
        app.logger.error(f"Error in API candidates: {e}")
        return jsonify({"error": "Failed to fetch candidates"}), 500


@app.errorhandler(404)
def not_found(error):
    app.logger.warning(f"404 error: {request.url}")
    return "Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 error: {error}")
    return "Internal server error", 500


if __name__ == "__main__":
    app.run(debug=True)