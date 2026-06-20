# 🎯 SkillBridge — AI Career Guidance & Skill-Gap Analyzer

> Upload your resume or pick your skills, choose a target role, and get an
> instant skill-gap report **plus an AI-generated personalized learning roadmap.**

![Python](https://img.shields.io/badge/Python-3.10+-00f5ff?style=flat-square&logo=python&logoColor=white&labelColor=04060d)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-7b2ff7?style=flat-square&logo=streamlit&logoColor=white&labelColor=04060d)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-00f5ff?style=flat-square&logo=google&logoColor=white&labelColor=04060d)
![NLP](https://img.shields.io/badge/NLP-Skill_Extraction-00f5a0?style=flat-square&labelColor=04060d)

**🔗 Live demo:** **https://skillbridge-darshan.streamlit.app**

> A project by **Darshan Dalvi** · Computer Engineering

**© 2026 Darshan Dalvi — All rights reserved.** The code is public for viewing & evaluation only; please do not copy or reuse it without permission (see [LICENSE](LICENSE)).

---

## 🧩 The problem

Students don't know **how far** they are from their dream job or **what to
learn next**. SkillBridge measures the gap between a student's current
skills and a target role, then generates a concrete roadmap to close it.

## ✨ Features

- 📄 **Resume upload** — extracts skills automatically from a PDF
- ✅ **Manual skill select** — alternative to uploading
- 🎯 **8 target roles** — AI/ML Engineer, Data Analyst, Frontend, Backend, and more
- 📊 **Visual gap report** — match score, skills you have ✓, skills missing ✗
- 🤖 **AI roadmap** — Gemini generates an ordered learning plan with free resources
- 🎨 **Futuristic glassmorphism UI** — animated, modern, mobile-friendly

## 🏗️ Architecture

```
        ┌──────────────────────────────┐
        │   Resume PDF  OR  Skill pick  │
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │  analyzer.extract_skills()    │  ← NLP: keyword + alias matching
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │  analyzer.analyze_gap()       │  ← compare vs roles_data.py
        │  → match %, matched, missing  │
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │  Visual gap report (Streamlit)│
        └──────────────┬───────────────┘
                       ▼
        ┌──────────────────────────────┐
        │  Gemini → personalized roadmap│  ← AI generation
        └──────────────────────────────┘
```

## 📂 Project structure

| File | Role |
|---|---|
| `app.py` | Streamlit UI + Gemini roadmap generation |
| `analyzer.py` | PDF parsing, skill extraction (NLP), gap logic |
| `roles_data.py` | Role→skills database + skill aliases |
| `requirements.txt` | Dependencies |

## 🛠️ Tech stack

Python · Streamlit · Google Gemini 2.0 Flash · pdfplumber · custom NLP
(keyword + alias matching) · glassmorphism CSS.

## 🚀 Run locally

```bash
git clone https://github.com/darshan-dalvi-AI/skillbridge.git
cd skillbridge
pip install -r requirements.txt
mkdir -p .streamlit
echo 'GEMINI_API_KEY = "your-key"' > .streamlit/secrets.toml
streamlit run app.py
```

## ☁️ Deploy free (Streamlit Cloud)

1. Push to a **public GitHub repo**
2. **share.streamlit.io** → New app → select repo
3. Advanced → Secrets → `GEMINI_API_KEY = "your-key"`
4. Deploy → public `*.streamlit.app` link 🎉

## 🔮 Future scope

- Live job-market data (scrape required skills from real postings)
- Downloadable PDF report
- More roles + sub-specializations
- Course recommendations with direct enrollment links

## 📌 What I learned

- NLP skill extraction with keyword + alias matching and word-boundary regex
- Weighted scoring logic (core vs bonus skills)
- PDF text extraction with pdfplumber
- Prompt engineering for structured roadmap generation
- Modular code design (UI / logic / data separated for clean viva defense)

---

*Built by **Darshan Dalvi** · [LinkedIn](https://linkedin.com/in/darshan-dalvi) · [GitHub](https://github.com/darshan-dalvi)*
