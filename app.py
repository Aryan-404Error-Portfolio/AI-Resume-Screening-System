import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request, send_file, redirect

from utils.parser import extract_text
from utils.ai import extract_candidate_details, analyze_candidate

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DATABASE = "database.db"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def init_db():
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
    conn.close()


init_db()


def fetch_candidates(skill="", min_score=0):

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

    conn.close()

    results = []

    for row in rows:

        results.append({

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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    resumes = request.files.getlist("resumes")
    job_description = request.form["job_description"]

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    for resume in resumes:

        if resume.filename == "":
            continue

        path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
        resume.save(path)

        resume_text = extract_text(path)

        candidate = extract_candidate_details(resume_text)

        analysis = analyze_candidate(resume_text, job_description)

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

    conn.commit()
    conn.close()

    results = fetch_candidates()

    return render_template("dashboard.html", results=results)


@app.route("/filter", methods=["GET"])
def filter_candidates():

    skill = request.args.get("skill", "").strip()

    try:
        min_score = int(request.args.get("score", 0))
    except:
        min_score = 0

    results = fetch_candidates(skill, min_score)

    return render_template("dashboard.html", results=results)


@app.route("/delete")
def delete():

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("DELETE FROM candidates")

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/export")
def export():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql_query(
        "SELECT * FROM candidates ORDER BY match_score DESC",
        conn
    )

    conn.close()

    filename = "shortlisted_candidates.csv"

    df.to_csv(filename, index=False)

    return send_file(
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)