from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from werkzeug.utils import secure_filename
from resume_analyzer import ResumeAnalyzer

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize resume analyzer
analyzer = ResumeAnalyzer()

# Ensure upload folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files or "job_description" not in request.form:
        logging.error("Missing resume file or job description")
        return jsonify({"error": "Resume file and job description required"}), 400

    resume_file = request.files["resume"]
    job_description = request.form["job_description"]

    # Ensure safe filename
    filename = secure_filename(resume_file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    resume_file.save(file_path)

    try:
        result = analyzer.analyze_resume(file_path, job_description)
        os.remove(file_path)  # Clean up after processing
        return jsonify(result)
    except Exception as e:
        logging.exception("Error processing resume")
        return jsonify({"error": str(e)}), 500

# Ensure app runs on the correct port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)
