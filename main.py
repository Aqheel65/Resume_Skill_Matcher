from flask import Flask, request, render_template
from parser import ResumeParser
from roles import JOB_ROLES
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
parser = ResumeParser()

# ------------------------
# UPLOAD CONFIG
# ------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ------------------------
# HOME PAGE
# ------------------------
@app.route("/")
def home():
    return render_template(
        "index.html",
        roles=JOB_ROLES.keys()
    )


# ------------------------
# ANALYZE RESUME
# ------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    # ---- VALIDATION ----
    if "resume" not in request.files:
        return "No resume uploaded", 400

    file = request.files["resume"]
    role = request.form.get("role")

    if file.filename == "":
        return "No file selected", 400

    if not role or role not in JOB_ROLES:
        return "Invalid job role selected", 400

    # ---- SAVE FILE ----
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # ---- PARSE RESUME ----
    parsed = parser.parse_file(file_path)

    resume_skills = [s.lower() for s in parsed.get("skills", [])]
    role_skills = JOB_ROLES[role]

    # ---- SKILL MATCHING ----
    matched = [s for s in role_skills if s.lower() in resume_skills]
    missing = [s for s in role_skills if s not in matched]

    # ---- ATS SCORE ----
    score = int((len(matched) / len(role_skills)) * 100) if role_skills else 0

    # ------------------------
    # RESUME IMPROVEMENT TIPS
    # ------------------------
    tips = []

    if score < 40:
        tips.append(
            "Your ATS score is low. Focus on learning the core skills required for this role."
        )
    elif score < 70:
        tips.append(
            "You are doing well. Adding a few missing skills can significantly improve your chances."
        )
    else:
        tips.append(
            "Excellent ATS score. Focus on improving resume presentation and project quality."
        )

    for skill in missing[:3]:
        tips.append(f"Try adding projects or experience related to {skill}.")

    tips.extend([
        "Quantify achievements using numbers (e.g., improved speed by 30%).",
        "Add GitHub or portfolio links to show real work.",
        "Use strong action verbs like designed, implemented, optimized."
    ])

    # ------------------------
    # YOUTUBE LEARNING LINKS
    # ------------------------
    youtube_links = {
        skill: f"https://www.youtube.com/results?search_query=learn+{skill.replace(' ', '+')}"
        for skill in missing
    }

    # ---- RENDER RESULT ----
    return render_template(
        "result.html",
        data=parsed,
        role=role,
        score=score,
        matched=matched,
        missing=missing,
        youtube_links=youtube_links,
        tips=tips
    )


# ------------------------
# RUN SERVER
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)

