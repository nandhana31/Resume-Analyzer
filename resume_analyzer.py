import os
import json
import pdfplumber
import docx2txt
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

class ResumeAnalyzer:
    def __init__(self):
        """Initialize the ResumeAnalyzer with NLP model and skills database."""
        self.nlp = spacy.load("en_core_web_sm")
        self.skills_db = self._load_skills_db()

        self.education_terms = [
            "bachelor", "master", "phd", "doctorate", "bs", "ms", "ba", "ma", "mba",
            "degree", "university", "college", "school", "institute"
        ]

        self.experience_terms = [
            "experience", "work", "job", "position", "role", "employment", "career",
            "worked", "led", "managed", "developed", "implemented", "created", "designed"
        ]

    def _load_skills_db(self):
        """Load skills database from JSON file or use a default set."""
        default_skills = {"python", "java", "sql", "flask", "machine learning", "aws"}
        try:
            if os.path.exists("skills_db.json"):
                with open("skills_db.json", "r") as f:
                    return set(json.load(f))
            return default_skills
        except:
            return default_skills

    def extract_text(self, file_path):
        """Extract text from PDF or DOCX files."""
        if file_path.endswith(".pdf"):
            return self._extract_text_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            return self._extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")

    def _extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file."""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def _extract_text_from_docx(self, docx_path):
        """Extract text from a DOCX file."""
        try:
            return docx2txt.process(docx_path)
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")

    def extract_skills(self, text):
        """Extract skills using NLP and skill patterns."""
        doc = self.nlp(text.lower())
        extracted_skills = set()

        for token in doc:
            if token.text in self.skills_db:
                extracted_skills.add(token.text)

        return extracted_skills

    def analyze_resume(self, resume_path, job_description):
        """Analyze the resume and compare with job description."""
        resume_text = self.extract_text(resume_path)
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)

        matching_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills

        skill_match_percentage = len(matching_skills) / len(job_skills) * 100 if job_skills else 0

        vectorizer = TfidfVectorizer(stop_words="english")
        vectors = vectorizer.fit_transform([resume_text, job_description])
        content_match_percentage = cosine_similarity(vectors[0], vectors[1])[0][0] * 100

        overall_match = (skill_match_percentage * 0.7) + (content_match_percentage * 0.3)

        return {
            "skills": list(resume_skills),
            "matching_skills": list(matching_skills),
            "missing_skills": list(missing_skills),
            "match_score": round(overall_match, 2),
        }
