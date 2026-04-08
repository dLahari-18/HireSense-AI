# 🧠 HireSense AI – Smart Resume Analysis Platform

**HireSense AI** is a production‑grade web application that analyzes resumes against job descriptions using **semantic similarity** (BERT‑based) and **TF‑IDF** fallback. It provides an ATS score (0–100), identifies missing skills, offers AI‑powered resume improvements, cover letter generation, and a career chatbot.

> 🚀 Live Demo: *[Add your deployed URL here after deployment]*

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Resume Upload** | Drag & drop PDF/DOCX, text extraction via PyPDF2 / python‑docx |
| 🎯 **ATS Score** | Semantic similarity using `all-MiniLM-L6-v2` (or TF‑IDF fallback) |
| 🧠 **Skill Gap Analysis** | Extracts skills from a curated list + NER‑like matching |
| ✍️ **AI Resume Improver** | Mock AI rewriting (ready for OpenAI integration) |
| 📝 **Cover Letter Generator** | Instant professional cover letter based on job title |
| 🤖 **Career Chatbot** | Rule‑based advice on ATS, resumes, interviews |
| 📊 **Analytics Dashboard** | ATS trend chart, skill distribution, ML metrics (Accuracy, Precision, Recall, F1) |
| 🌙 **Dark / Light Mode** | Persistent theme toggle with system preference detection |
| 🧠 **Learning System** | Stores analysis history, shows improvement trends |
| 📦 **No Database Required** | Uses JSON file for history, session for temporary data |

---

## 🛠️ Tech Stack

- **Backend:** Flask, scikit‑learn, sentence‑transformers, PyPDF2, python‑docx
- **Frontend:** HTML5, CSS3 (glassmorphism, CSS variables), JavaScript, Chart.js
- **ML / NLP:** Sentence‑Transformer (`all-MiniLM-L6-v2`), TF‑IDF, Logistic Regression (optional)
- **Deployment:** Gunicorn + Nginx (AWS EC2) / Railway / Render

---

## 📁 Project Structure
