"""
roles_data.py — Role Requirements Database
==========================================
The knowledge core of the app: maps each target role to the skills
it requires, split into CORE (must-have) and BONUS (good-to-have).

This is intentionally a plain Python dict so it is easy to read,
explain in a viva, and extend. To add a role, just add an entry.
"""

ROLE_REQUIREMENTS = {
    "AI Engineer": {
        "core": ["Python", "Machine Learning", "Deep Learning", "NLP",
                 "LangChain", "REST API", "Git"],
        "bonus": ["PyTorch", "TensorFlow", "Computer Vision", "Docker",
                  "AWS", "SQL"],
    },
    "ML Engineer": {
        "core": ["Python", "Machine Learning", "Deep Learning", "Statistics",
                 "Pandas", "NumPy", "SQL"],
        "bonus": ["TensorFlow", "PyTorch", "NLP", "Computer Vision",
                  "Docker", "Git"],
    },
    "Data Analyst": {
        "core": ["Python", "SQL", "Excel", "Data Visualization",
                 "Statistics", "Pandas"],
        "bonus": ["Power BI", "Tableau", "Machine Learning", "Git"],
    },
    "Data Scientist": {
        "core": ["Python", "Machine Learning", "Statistics", "SQL",
                 "Pandas", "NumPy", "Data Visualization"],
        "bonus": ["Deep Learning", "NLP", "Big Data", "R", "Git"],
    },
    "Frontend Developer": {
        "core": ["HTML", "CSS", "JavaScript", "React", "Git"],
        "bonus": ["TypeScript", "Tailwind", "Next.js", "Redux"],
    },
    "Backend Developer": {
        "core": ["Python", "SQL", "REST API", "Git", "Databases"],
        "bonus": ["Node.js", "Docker", "AWS", "MongoDB", "FastAPI"],
    },
    "Full Stack Developer": {
        "core": ["HTML", "CSS", "JavaScript", "React", "Python",
                 "SQL", "REST API", "Git"],
        "bonus": ["Node.js", "Docker", "AWS", "MongoDB", "TypeScript"],
    },
    "Android Developer": {
        "core": ["Java", "Kotlin", "Android Studio", "SQL", "Git"],
        "bonus": ["Flutter", "Firebase", "Jetpack Compose", "REST API"],
    },
    "Cloud / DevOps Engineer": {
        "core": ["Linux", "Docker", "AWS", "Git", "Python"],
        "bonus": ["Kubernetes", "Terraform", "CI/CD", "Azure", "Jenkins"],
    },
    "Data Engineer": {
        "core": ["Python", "SQL", "Databases", "Big Data", "Linux"],
        "bonus": ["AWS", "Docker", "Kubernetes", "Spark", "Git"],
    },
    "Business Analyst": {
        "core": ["Excel", "SQL", "Data Visualization", "Statistics", "Power BI"],
        "bonus": ["Tableau", "Python", "Data Analysis"],
    },
    "Cybersecurity Analyst": {
        "core": ["Linux", "Networking", "Python", "SQL"],
        "bonus": ["Cybersecurity", "Cloud Security", "Git"],
    },
    "UI/UX Designer": {
        "core": ["Figma", "HTML", "CSS", "JavaScript"],
        "bonus": ["Tailwind", "React"],
    },
    "QA / Automation Tester": {
        "core": ["Python", "Selenium", "SQL", "Git"],
        "bonus": ["Java", "REST API", "CI/CD"],
    },
    "Game Developer": {
        "core": ["C++", "C#", "Unity", "Git"],
        "bonus": ["Python"],
    },
}

# Master list of all skills the extractor can recognise.
# Built automatically from every role's core + bonus, plus common aliases.
def _build_master_skills():
    skills = set()
    for role in ROLE_REQUIREMENTS.values():
        skills.update(role["core"])
        skills.update(role["bonus"])
    # add common extra skills students may have
    extras = ["C", "C++", "Data Analysis", "Matplotlib", "Seaborn",
              "Flask", "Django", "Firebase", "MySQL", "MongoDB",
              "Power BI", "Tableau", "Keras", "OpenCV", "GitHub"]
    skills.update(extras)
    return sorted(skills)

MASTER_SKILLS = _build_master_skills()

# Aliases → canonical skill name (so "js" maps to "JavaScript", etc.)
SKILL_ALIASES = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "py": "Python",
    "python": "Python",
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "node": "Node.js",
    "nodejs": "Node.js",
    "postgres": "SQL",
    "postgresql": "SQL",
    "mysql": "MySQL",
    "html5": "HTML",
    "css3": "CSS",
    "spark": "Spark", "apache spark": "Spark", "pyspark": "Spark",
    "networking": "Networking", "computer networks": "Networking",
    "cybersecurity": "Cybersecurity", "cyber security": "Cybersecurity",
    "infosec": "Cybersecurity", "cloud security": "Cloud Security",
    "figma": "Figma", "selenium": "Selenium", "c#": "C#", "csharp": "C#",
    "c sharp": "C#", "unity": "Unity", "unity3d": "Unity",
}

# ---------------------------------------------------------------------------
# EXTENDED DATASETS (added for the advanced features)
# Each is a plain dict so it's easy to read, defend in a viva, and extend.
# Helper functions in analyzer.py use .get() with sensible defaults, so a
# skill missing from a dict never breaks the app.
# ---------------------------------------------------------------------------

# Approx. hours to reach working (job-ready) proficiency in each skill.
# Used by the "estimated learning timeline" feature.
SKILL_HOURS = {
    "Python": 80, "Java": 90, "JavaScript": 70, "Kotlin": 70, "C": 70,
    "C++": 90, "TypeScript": 40, "R": 50,
    "Machine Learning": 120, "Deep Learning": 120, "NLP": 90,
    "Computer Vision": 90, "Statistics": 60, "Data Analysis": 50,
    "Data Visualization": 40, "Big Data": 80,
    "TensorFlow": 60, "PyTorch": 60, "Keras": 40, "Pandas": 40, "NumPy": 30,
    "Matplotlib": 25, "Seaborn": 20, "OpenCV": 50, "LangChain": 40,
    "React": 70, "Next.js": 50, "Redux": 30, "Tailwind": 25, "Node.js": 60,
    "Flask": 40, "Django": 70, "FastAPI": 35, "Jetpack Compose": 50,
    "Flutter": 70, "HTML": 25, "CSS": 35, "REST API": 30,
    "SQL": 40, "MySQL": 35, "MongoDB": 40, "Databases": 50, "Excel": 25,
    "Git": 20, "GitHub": 15, "Docker": 50, "Kubernetes": 80, "AWS": 70,
    "Azure": 70, "Linux": 50, "CI/CD": 40, "Jenkins": 40, "Terraform": 50,
    "Android Studio": 40, "Firebase": 35, "Power BI": 40, "Tableau": 40,
    "Spark": 60, "Networking": 50, "Cybersecurity": 80, "Cloud Security": 60,
    "Figma": 30, "Selenium": 40, "C#": 80, "Unity": 70,
}
DEFAULT_SKILL_HOURS = 50

# Market demand score (0-100). Higher = more requested by employers.
# Used for the "skills in demand" badges and the curated market fallback.
SKILL_DEMAND = {
    "Python": 96, "SQL": 92, "Machine Learning": 90, "AWS": 90,
    "React": 88, "JavaScript": 88, "Git": 88, "GitHub": 80, "Docker": 86,
    "Deep Learning": 82, "Pandas": 82, "NLP": 80, "Node.js": 80,
    "Kubernetes": 80, "REST API": 80, "TypeScript": 80, "Azure": 80,
    "LangChain": 78, "PyTorch": 78, "Data Visualization": 78, "Java": 78,
    "Data Analysis": 76, "NumPy": 76, "TensorFlow": 76, "Next.js": 76,
    "Linux": 76, "Statistics": 75, "Power BI": 74, "Databases": 74,
    "CI/CD": 74, "Computer Vision": 72, "Tableau": 72, "Big Data": 70,
    "Tailwind": 70, "Kotlin": 70, "MongoDB": 70, "Terraform": 70,
    "Excel": 70, "HTML": 68, "CSS": 68, "Flutter": 68, "MySQL": 68,
    "FastAPI": 66, "Django": 64, "OpenCV": 64, "Firebase": 64, "C++": 62,
    "Flask": 62, "Jenkins": 60, "Redux": 60, "Android Studio": 60,
    "R": 58, "Keras": 58, "Jetpack Compose": 58, "Matplotlib": 58,
    "C": 55, "Seaborn": 52,
    "Spark": 72, "Networking": 66, "Cybersecurity": 82, "Cloud Security": 74,
    "Figma": 72, "Selenium": 64, "C#": 70, "Unity": 64,
}
DEFAULT_SKILL_DEMAND = 60
HIGH_DEMAND_THRESHOLD = 80  # >= this is flagged "in demand"

# Indicative fresher salary ranges in India (LPA = lakhs per annum).
# These are ballpark 2025-26 figures and vary by company, city and skills.
ROLE_SALARY_IN = {
    "AI Engineer":             {"low": 5.0, "median": 8.0,  "high": 16.0},
    "ML Engineer":             {"low": 4.5, "median": 7.0,  "high": 14.0},
    "Data Analyst":            {"low": 3.0, "median": 4.5,  "high": 8.0},
    "Data Scientist":          {"low": 5.0, "median": 8.0,  "high": 16.0},
    "Frontend Developer":      {"low": 3.0, "median": 4.5,  "high": 8.0},
    "Backend Developer":       {"low": 3.5, "median": 5.5,  "high": 10.0},
    "Full Stack Developer":    {"low": 4.0, "median": 6.0,  "high": 11.0},
    "Android Developer":       {"low": 3.0, "median": 4.5,  "high": 8.0},
    "Cloud / DevOps Engineer": {"low": 4.0, "median": 6.5,  "high": 12.0},
    "Data Engineer":            {"low": 4.5, "median": 7.5,  "high": 15.0},
    "Business Analyst":         {"low": 3.5, "median": 5.5,  "high": 10.0},
    "Cybersecurity Analyst":    {"low": 4.0, "median": 6.5,  "high": 13.0},
    "UI/UX Designer":           {"low": 3.0, "median": 5.0,  "high": 9.0},
    "QA / Automation Tester":   {"low": 3.5, "median": 5.5,  "high": 10.0},
    "Game Developer":           {"low": 3.5, "median": 5.5,  "high": 11.0},
}

# Indicative "typical applicant" baseline match score per role (our rubric).
# Used ONLY for the peer-comparison feature, which is clearly labelled in the
# UI as a heuristic benchmark, not real candidate data.
ROLE_BENCHMARK = {
    "AI Engineer": 48, "ML Engineer": 52, "Data Analyst": 60, "Data Scientist": 50,
    "Frontend Developer": 62, "Backend Developer": 58,
    "Full Stack Developer": 55, "Android Developer": 58,
    "Cloud / DevOps Engineer": 50,
    "Data Engineer": 50, "Business Analyst": 58, "Cybersecurity Analyst": 48,
    "UI/UX Designer": 55, "QA / Automation Tester": 55, "Game Developer": 50,
}
DEFAULT_BENCHMARK = 55


# Skill -> broad category, used by the radar chart to show coverage per area.
SKILL_CATEGORY = {
    # Languages
    "Python": "Languages", "Java": "Languages", "JavaScript": "Languages",
    "TypeScript": "Languages", "C": "Languages", "C++": "Languages",
    "C#": "Languages", "Kotlin": "Languages", "R": "Languages",
    # AI / ML
    "Machine Learning": "AI/ML", "Deep Learning": "AI/ML", "NLP": "AI/ML",
    "Computer Vision": "AI/ML", "TensorFlow": "AI/ML", "PyTorch": "AI/ML",
    "Keras": "AI/ML", "LangChain": "AI/ML", "OpenCV": "AI/ML",
    # Data
    "SQL": "Data", "Pandas": "Data", "NumPy": "Data", "Statistics": "Data",
    "Data Analysis": "Data", "Data Visualization": "Data", "Big Data": "Data",
    "Spark": "Data", "Excel": "Data", "Power BI": "Data", "Tableau": "Data",
    "Matplotlib": "Data", "Seaborn": "Data", "Databases": "Data",
    "MySQL": "Data", "MongoDB": "Data",
    # Web / UI
    "HTML": "Web/UI", "CSS": "Web/UI", "React": "Web/UI", "Next.js": "Web/UI",
    "Redux": "Web/UI", "Tailwind": "Web/UI", "Node.js": "Web/UI",
    "Flask": "Web/UI", "Django": "Web/UI", "FastAPI": "Web/UI",
    "REST API": "Web/UI", "Figma": "Web/UI",
    # Cloud / DevOps
    "Docker": "Cloud/DevOps", "Kubernetes": "Cloud/DevOps", "AWS": "Cloud/DevOps",
    "Azure": "Cloud/DevOps", "Linux": "Cloud/DevOps", "CI/CD": "Cloud/DevOps",
    "Jenkins": "Cloud/DevOps", "Terraform": "Cloud/DevOps",
    "Cloud Security": "Cloud/DevOps",
    # Mobile / Game
    "Flutter": "Mobile/Game", "Android Studio": "Mobile/Game",
    "Jetpack Compose": "Mobile/Game", "Firebase": "Mobile/Game", "Unity": "Mobile/Game",
    # Tools / Security
    "Git": "Tools", "GitHub": "Tools", "Selenium": "Tools",
    "Networking": "Security", "Cybersecurity": "Security",
}
DEFAULT_CATEGORY = "Other"
