from flask import Flask, render_template, request, jsonify, session
import os
from io import BytesIO
import utils
import model as ml
import json

app = Flask(__name__)
app.secret_key = 'hiresense_super_secret_2025'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Global storage for ML artifacts (dummy metrics if no training)
ml_artifacts = {
    'metrics': {'accuracy': 0.85, 'precision': 0.83, 'recall': 0.80, 'f1': 0.81},
    'classifier': None
}

# Learning system (stores analysis history)
learning = ml.LearningSystem()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['resume']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    job_desc = request.form.get('job_description', '')
    if not job_desc:
        return jsonify({'error': 'Job description is required'}), 400
    
    file_bytes = file.read()
    try:
        resume_raw = utils.parse_resume(file_bytes, file.filename)
    except Exception as e:
        return jsonify({'error': f'Failed to parse resume: {str(e)}'}), 400
    
    clean_resume = utils.clean_text(resume_raw)
    clean_job = utils.clean_text(job_desc)
    
    # ATS Score – try semantic similarity, fallback to TF‑IDF
    try:
        ats_score = utils.compute_semantic_similarity(clean_resume, clean_job)
    except:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vec = TfidfVectorizer()
        vectors = vec.fit_transform([clean_resume, clean_job])
        sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        ats_score = round(sim * 100, 2)
    
    # Skill extraction
    resume_skills = utils.extract_skills_fallback(clean_resume)
    job_skills = utils.extract_skills_fallback(clean_job)
    missing = list(set(job_skills) - set(resume_skills))
    
    # Save to learning system
    learning.add_analysis(resume_raw, job_desc, ats_score, resume_skills, missing)
    
    session['last_result'] = {
        'ats_score': ats_score,
        'resume_skills': resume_skills,
        'missing_skills': missing
    }
    return jsonify({
        'ats_score': ats_score,
        'resume_skills': resume_skills,
        'missing_skills': missing
    })

@app.route('/api/dashboard_metrics', methods=['GET'])
def dashboard_metrics():
    metrics = ml_artifacts['metrics']
    trend = [72, 78, 85, 91]
    skills_dist = {
        "Python": 90, "Machine Learning": 70, "SQL": 85,
        "Docker": 40, "AWS": 55, "React": 88, "JavaScript": 92
    }
    return jsonify({
        "accuracy": metrics['accuracy'],
        "precision": metrics['precision'],
        "recall": metrics['recall'],
        "f1": metrics['f1'],
        "trend": trend,
        "skills": skills_dist,
        "improvement_tip": learning.get_improvement_trend()
    })

@app.route('/api/rewrite_resume', methods=['POST'])
def rewrite_resume():
    data = request.get_json()
    original = data.get('resume_text', '')
    rewritten = original + "\n\n[AI Enhancement] Added measurable achievements and power verbs: " \
                           "• Spearheaded migration to microservices, improving scalability by 40%.\n" \
                           "• Orchestrated cross-team initiatives resulting in 25% faster delivery."
    return jsonify({'rewritten': rewritten.strip()})

@app.route('/api/cover_letter', methods=['POST'])
def cover_letter():
    data = request.get_json()
    job_title = data.get('job_title', 'the position')
    skills = data.get('skills', 'relevant experience')
    letter = f"""
Dear Hiring Manager,

I am thrilled to apply for the {job_title} role. With a strong background in {skills}, I have consistently delivered high‑impact results.

In my previous role, I increased team efficiency by 30% through process automation and led a successful product launch that exceeded KPIs by 25%. My technical expertise combined with a passion for solving complex problems makes me an ideal fit for your team.

I look forward to discussing how I can contribute to your success.

Sincerely,
[Your Name]
"""
    return jsonify({'cover_letter': letter.strip()})

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_msg = data.get('message', '').lower()
    if 'ats' in user_msg or 'score' in user_msg:
        reply = "To improve your ATS score, include exact keywords from the job description, use standard section headings, and avoid complex formatting like tables or columns."
    elif 'skill' in user_msg:
        reply = "Focus on both hard skills (Python, SQL, cloud) and soft skills (communication, leadership). Match the skills listed in the job posting."
    elif 'resume' in user_msg:
        reply = "Use action verbs, quantify achievements (e.g., 'increased sales by 20%'), and keep your resume to 1-2 pages. Tailor each resume to the specific job."
    elif 'interview' in user_msg:
        reply = "Prepare STAR stories for behavioral questions, research the company, and practice your technical skills with mock interviews."
    else:
        reply = "I can help with ATS tips, resume writing, skill recommendations, and interview prep. What would you like to know?"
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)