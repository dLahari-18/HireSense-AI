import re
import PyPDF2
import docx
from io import BytesIO

# Optional: try to load sentence-transformers for better similarity
try:
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer('all-MiniLM-L6-v2')
    USE_TRANSFORMER = True
except:
    USE_TRANSFORMER = False
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

STOPWORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them', 'their',
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'have', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'this', 'to', 'was', 'were',
    'will', 'with', 'about', 'but', 'or', 'so', 'than', 'that', 'these', 'those', 'through'
])

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    words = text.split()
    words = [w for w in words if w not in STOPWORDS]
    return ' '.join(words)

def parse_resume(file_bytes, filename):
    text = ""
    if filename.lower().endswith('.pdf'):
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    elif filename.lower().endswith('.docx'):
        doc = docx.Document(BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError("Unsupported file type")
    return text

def compute_semantic_similarity(resume_text, job_text):
    if USE_TRANSFORMER:
        emb1 = model.encode(resume_text, convert_to_tensor=True)
        emb2 = model.encode(job_text, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(emb1, emb2).item()
        return round(sim * 100, 2)
    else:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([resume_text, job_text])
        sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return round(sim * 100, 2)

def extract_skills_fallback(text):
    static_skills = [
        'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'nodejs',
        'sql', 'mongodb', 'postgresql', 'mysql', 'docker', 'kubernetes', 'aws', 'azure',
        'gcp', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'git', 'ci/cd',
        'machine learning', 'deep learning', 'nlp', 'data analysis', 'excel', 'tableau',
        'power bi', 'agile', 'scrum', 'leadership', 'project management', 'communication'
    ]
    found = [skill for skill in static_skills if skill in text.lower()]
    return list(set(found))

# Alias for compatibility
extract_skills_ner = extract_skills_fallback