import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import json
from utils import clean_text

# Paths
RESUME_PATH = 'dataset/resumes.csv'
JOB_PATH = 'dataset/job_descriptions.csv'
SAMPLE_SIZE = 1000  # Use first 1000 rows only

print("📊 Loading and sampling 1000 resumes and 1000 jobs...")
resumes = pd.read_csv(RESUME_PATH).head(SAMPLE_SIZE)
jobs = pd.read_csv(JOB_PATH).head(SAMPLE_SIZE)

# Extract text columns (adjust if needed)
resume_text_col = 'Resume_str'  # from your log
job_text_col = 'Job Description'

print("🧹 Cleaning texts...")
resumes['clean_resume'] = resumes[resume_text_col].astype(str).apply(clean_text)
jobs['clean_job'] = jobs[job_text_col].astype(str).apply(clean_text)

# Create positive pairs (all combinations) - but that would be 1e6 pairs, too many.
# Instead, create balanced dataset: take all resumes and pair with a random job (positive)
# and also create negative pairs by shuffling.

print("🔗 Creating resume-job pairs...")
positive_pairs = []
for i, r in resumes.iterrows():
    # For each resume, pick a random job as positive (assuming all are potential matches)
    j = jobs.sample(1).iloc[0]
    positive_pairs.append({
        'resume': r['clean_resume'],
        'job': j['clean_job'],
        'label': 1
    })

# Create negative pairs: same resumes with random jobs that are different from the positive one
negative_pairs = []
for i, r in resumes.iterrows():
    # Pick a different random job
    j = jobs.sample(1).iloc[0]
    negative_pairs.append({
        'resume': r['clean_resume'],
        'job': j['clean_job'],
        'label': 0
    })

# Combine
pairs = positive_pairs + negative_pairs
df = pd.DataFrame(pairs)
df['combined'] = df['resume'] + " " + df['job']
df = df.dropna()
print(f"✅ Total pairs: {len(df)} (positive: {df['label'].sum()}, negative: {len(df)-df['label'].sum()})")

# Train model
print("🚀 Training classifier...")
X = df['combined']
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X_train_vec = vectorizer.fit_transform(X_train.astype(str))
X_test_vec = vectorizer.transform(X_test.astype(str))

clf = LogisticRegression(max_iter=1000)
clf.fit(X_train_vec, y_train)
y_pred = clf.predict(X_test_vec)

metrics = {
    'accuracy': round(accuracy_score(y_test, y_pred), 4),
    'precision': round(precision_score(y_test, y_pred, zero_division=0), 4),
    'recall': round(recall_score(y_test, y_pred, zero_division=0), 4),
    'f1': round(f1_score(y_test, y_pred, zero_division=0), 4)
}

# Save artifacts
os.makedirs('model', exist_ok=True)
joblib.dump(vectorizer, 'model/tfidf_vectorizer.pkl')
joblib.dump(clf, 'model/logistic_model.pkl')
with open('model/metrics.json', 'w') as f:
    json.dump(metrics, f)

print("\n🎉 Training complete!")
print("="*40)
print(f"Accuracy:  {metrics['accuracy']:.2%}")
print(f"Precision: {metrics['precision']:.2%}")
print(f"Recall:    {metrics['recall']:.2%}")
print(f"F1 Score:  {metrics['f1']:.2%}")
print("="*40)
print("\n✅ Model saved to 'model/' folder.")