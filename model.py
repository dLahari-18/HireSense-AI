import os
import json
from datetime import datetime

class LearningSystem:
    def __init__(self, history_file='analysis_history.json'):
        self.history_file = history_file
        self.history = []
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                self.history = json.load(f)
    
    def add_analysis(self, resume_text, job_desc, ats_score, skills_present, skills_missing):
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'ats_score': ats_score,
            'skills_present': skills_present,
            'skills_missing': skills_missing,
            'resume_snippet': resume_text[:200],
            'job_snippet': job_desc[:200]
        })
        if len(self.history) > 50:
            self.history = self.history[-50:]
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)
    
    def get_improvement_trend(self):
        if len(self.history) < 2:
            return "Not enough data yet. Upload more resumes to see trends."
        scores = [h['ats_score'] for h in self.history]
        if scores[-1] > scores[0]:
            return f"Your ATS score has improved by {scores[-1] - scores[0]} points over your last {len(scores)} analyses! 🎉"
        else:
            return "Your ATS score hasn't improved much. Try adding missing keywords from job descriptions."
    
    def recommend_learning_path(self, missing_skills_aggregated):
        if not missing_skills_aggregated:
            return "You're covering all required skills! Keep applying."
        top_missing = missing_skills_aggregated[:3]
        return f"Focus on learning: {', '.join(top_missing)}. Consider online courses or side projects."