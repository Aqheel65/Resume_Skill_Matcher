import re
import json
import os
from pdfminer.high_level import extract_text as pdf_extract
from docx import Document
from PIL import Image
import pytesseract
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")


class ResumeParser:

    # ------------------------
    # MAIN PARSER
    # ------------------------
    def parse_file(self, file_path):
        text = self._extract_text(file_path)
        text = self._clean_text(text)

        return {
            "contact_info": self._extract_contact(text),
            "skills": self._extract_skills(text),
            "education": self._extract_education(text),
            "experience": self._extract_experience(text)
        }

    # ------------------------
    # TEXT EXTRACTION
    # ------------------------
    def _extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return pdf_extract(file_path) or ""

        elif ext == ".docx":
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)

        elif ext in [".png", ".jpg", ".jpeg"]:
            img = Image.open(file_path)
            return pytesseract.image_to_string(img)

        return ""

    # ------------------------
    # CLEAN TEXT
    # ------------------------
    def _clean_text(self, text):
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        return text.strip()

    # ------------------------
    # CONTACT INFO
    # ------------------------
    def _extract_contact(self, text):
        email = re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            text
        )

        phone = re.findall(
            r"(\+?\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}",
            text
        )

        linkedin = re.findall(
            r"(https?://[^\s]*linkedin\.com/[^\s]*|linkedin\.com/[^\s]*)",
            text,
            re.I
        )

        return {
            "email": email[0] if email else "Not found",
            "phone": phone[0] if phone else "Not found",
            "linkedin": linkedin[0] if linkedin else None
        }

    # ------------------------
    # SKILLS
    # ------------------------
    def _extract_skills(self, text):
        try:
            with open("skills.json", encoding="utf-8") as f:
                skills_db = json.load(f)
        except Exception:
            return []

        found = []
        text_lower = text.lower()

        for skill in skills_db:
            if skill.lower() in text_lower:
                found.append(skill)

        return list(set(found))

    # ------------------------
    # EDUCATION
    # ------------------------
    def _extract_education(self, text):
        keywords = [
            "bachelor",
            "master",
            "phd",
            "university",
            "college",
            "institute"
        ]

        education = []
        sentences = text.split(".")

        for s in sentences:
            if any(k in s.lower() for k in keywords):
                education.append(s.strip())

        return list(set(education))

    # ------------------------
    # EXPERIENCE
    # ------------------------
    def _extract_experience(self, text):
        keywords = [
            "engineer",
            "developer",
            "experience",
            "worked",
            "designed",
            "implemented",
            "managed"
        ]

        experience = []
        sentences = text.split(".")

        for s in sentences:
            if any(k in s.lower() for k in keywords):
                experience.append(s.strip())

        return experience[:10]
