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
    "Mechanical Design Engineer": {
        "core": ["AutoCAD", "SolidWorks", "CATIA", "GD&T", "Engineering Drawing", "Mechanical Design"],
        "bonus": ["ANSYS", "Creo", "Sheet Metal", "Product Design"],
    },
    "CAE / Simulation Engineer": {
        "core": ["ANSYS", "FEA", "CFD", "MATLAB", "Mechanical Design"],
        "bonus": ["SolidWorks", "Hypermesh", "Abaqus", "Python"],
    },
    "Manufacturing / Production Engineer": {
        "core": ["Manufacturing Process", "Lean Manufacturing", "Quality Control", "GD&T", "CNC"],
        "bonus": ["Six Sigma", "SAP", "AutoCAD", "Industrial Engineering"],
    },
    "HVAC Engineer": {
        "core": ["HVAC", "Thermodynamics", "AutoCAD", "Heat Transfer", "Duct Design"],
        "bonus": ["Revit MEP", "Energy Audit", "Mechanical Design"],
    },
    "Automobile Engineer": {
        "core": ["IC Engines", "Vehicle Dynamics", "CATIA", "Automotive Design", "Thermodynamics"],
        "bonus": ["MATLAB", "CFD", "ANSYS"],
    },
    "Maintenance Engineer": {
        "core": ["Preventive Maintenance", "Mechanical Maintenance", "Troubleshooting", "Pneumatics", "Hydraulics"],
        "bonus": ["PLC", "Root Cause Analysis", "SAP"],
    },
    "Electrical Design Engineer": {
        "core": ["Electrical Design", "AutoCAD Electrical", "Power Distribution", "Load Calculation", "Wiring"],
        "bonus": ["ETAP", "DIALux", "Revit MEP", "Switchgear"],
    },
    "Power Systems Engineer": {
        "core": ["Power Systems", "Power Distribution", "Transformers", "Switchgear", "Protection Systems"],
        "bonus": ["ETAP", "MATLAB", "SCADA", "Renewable Energy"],
    },
    "Control & Automation Engineer": {
        "core": ["PLC", "SCADA", "HMI", "Industrial Automation", "Instrumentation"],
        "bonus": ["DCS", "Ladder Logic", "Sensors", "MATLAB"],
    },
    "Electrical Maintenance Engineer": {
        "core": ["Electrical Maintenance", "Motors", "Switchgear", "Troubleshooting", "Preventive Maintenance"],
        "bonus": ["PLC", "VFD", "Root Cause Analysis"],
    },
    "Renewable Energy Engineer": {
        "core": ["Solar Energy", "Power Systems", "Energy Audit", "Electrical Design", "Renewable Energy"],
        "bonus": ["Wind Energy", "AutoCAD", "Battery Storage"],
    },
    "Embedded Systems Engineer": {
        "core": ["Embedded C", "Microcontrollers", "C", "RTOS", "Embedded Systems"],
        "bonus": ["ARM", "Python", "PCB Design", "IoT"],
    },
    "VLSI Design Engineer": {
        "core": ["VLSI", "Verilog", "VHDL", "Digital Electronics", "Cadence"],
        "bonus": ["SystemVerilog", "Synopsys", "FPGA", "Static Timing Analysis"],
    },
    "Electronics Design Engineer": {
        "core": ["PCB Design", "Analog Electronics", "Digital Electronics", "Altium", "Circuit Design"],
        "bonus": ["MATLAB", "Embedded C", "Eagle PCB"],
    },
    "IoT Engineer": {
        "core": ["IoT", "Embedded C", "Microcontrollers", "Python", "MQTT"],
        "bonus": ["Arduino", "Raspberry Pi", "Sensors", "Cloud"],
    },
    "RF / Telecom Engineer": {
        "core": ["RF Engineering", "Wireless Communication", "Antenna Design", "MATLAB", "Signal Processing"],
        "bonus": ["5G", "LTE", "Network Planning"],
    },
    "Structural Engineer": {
        "core": ["STAAD Pro", "ETABS", "Structural Analysis", "RCC Design", "AutoCAD"],
        "bonus": ["SAP2000", "Revit", "Steel Design", "Tekla"],
    },
    "Site / Construction Engineer": {
        "core": ["Construction Management", "AutoCAD", "Surveying", "Quantity Estimation", "Site Supervision"],
        "bonus": ["MS Project", "Primavera", "Concrete Technology"],
    },
    "Construction Project Manager": {
        "core": ["Project Management", "Primavera", "MS Project", "Construction Management", "Cost Estimation"],
        "bonus": ["Contract Management", "BIM", "Planning"],
    },
    "Transportation Engineer": {
        "core": ["Highway Engineering", "Surveying", "AutoCAD Civil 3D", "Transportation Planning", "Pavement Design"],
        "bonus": ["MX Road", "Traffic Engineering"],
    },
    "Geotechnical Engineer": {
        "core": ["Geotechnical Engineering", "Soil Mechanics", "Foundation Design", "Surveying"],
        "bonus": ["PLAXIS", "GeoStudio", "AutoCAD"],
    },
    "Quantity Surveyor": {
        "core": ["Quantity Estimation", "Cost Estimation", "BOQ", "AutoCAD", "Construction Management"],
        "bonus": ["MS Project", "Primavera", "Contract Management"],
    },
    "Process Engineer": {
        "core": ["Process Engineering", "Aspen Plus", "Chemical Process", "Heat Transfer", "Mass Transfer"],
        "bonus": ["HYSYS", "P&ID", "Process Simulation", "MATLAB"],
    },
    "Production (Chemical) Engineer": {
        "core": ["Chemical Process", "Production Planning", "Process Engineering", "Quality Control", "Unit Operations"],
        "bonus": ["Six Sigma", "SAP", "HAZOP", "GMP"],
    },
    "QA / QC Engineer (Chemical)": {
        "core": ["Quality Control", "Quality Assurance", "GMP", "Six Sigma", "Analytical Techniques"],
        "bonus": ["HPLC", "ISO Standards", "Documentation"],
    },
    "Safety (HSE) Engineer": {
        "core": ["HSE", "HAZOP", "Risk Assessment", "Safety Management", "Fire Safety"],
        "bonus": ["NEBOSH", "ISO 45001", "Process Safety"],
    },
    "R&D Chemical Engineer": {
        "core": ["Process Engineering", "Chemical Process", "Lab Techniques", "Process Simulation", "Design of Experiments"],
        "bonus": ["Aspen Plus", "Scale-up", "Research"],
    },
    "Product Manager": {
        "core": ["Product Management", "Market Research", "Agile", "Roadmapping", "Communication"],
        "bonus": ["SQL", "Data Analysis", "Wireframing", "Analytics"],
    },
    "Marketing Manager": {
        "core": ["Digital Marketing", "Market Research", "SEO", "Social Media Marketing", "Branding"],
        "bonus": ["Google Analytics", "Content Marketing", "CRM"],
    },
    "HR Manager": {
        "core": ["Recruitment", "HR Management", "Employee Relations", "Payroll", "Communication"],
        "bonus": ["HRIS", "Talent Management", "Labor Law"],
    },
    "Operations Manager": {
        "core": ["Operations Management", "Supply Chain", "Six Sigma", "Process Improvement", "Inventory Management"],
        "bonus": ["SAP", "Lean Manufacturing", "Logistics"],
    },
    "Management Consultant": {
        "core": ["Business Analysis", "Strategy", "Market Research", "Communication", "Problem Solving"],
        "bonus": ["Excel", "PowerPoint", "Financial Modeling"],
    },
    "Financial Analyst": {
        "core": ["Financial Modeling", "Excel", "Financial Analysis", "Accounting", "Valuation"],
        "bonus": ["SQL", "Power BI", "VBA", "Bloomberg"],
    },
    "Accountant": {
        "core": ["Accounting", "Tally", "GST", "Excel", "Bookkeeping"],
        "bonus": ["SAP FICO", "Taxation", "Auditing"],
    },
    "Investment Banking Analyst": {
        "core": ["Financial Modeling", "Valuation", "Excel", "Financial Analysis", "PowerPoint"],
        "bonus": ["DCF", "M&A", "Bloomberg"],
    },
    "Auditor": {
        "core": ["Auditing", "Accounting", "Internal Controls", "Excel", "Taxation"],
        "bonus": ["IFRS", "Risk Management", "SAP"],
    },
    "Tax Consultant": {
        "core": ["Taxation", "GST", "Income Tax", "Accounting", "Tally"],
        "bonus": ["TDS", "Excel", "Compliance"],
    },
    "Pharmacist": {
        "core": ["Pharmacology", "Pharmaceutics", "Drug Dispensing", "Pharmacy Practice", "Clinical Pharmacy"],
        "bonus": ["Hospital Pharmacy", "Inventory Management"],
    },
    "Clinical Research Associate": {
        "core": ["Clinical Research", "Clinical Trials", "GCP", "Pharmacovigilance", "Regulatory Affairs"],
        "bonus": ["Data Management", "Medical Writing", "ICH Guidelines"],
    },
    "Quality Control (Pharma)": {
        "core": ["Quality Control", "GMP", "HPLC", "Analytical Techniques", "Documentation"],
        "bonus": ["GLP", "Validation", "Stability Studies"],
    },
    "Regulatory Affairs Associate": {
        "core": ["Regulatory Affairs", "GMP", "Documentation", "Drug Regulations", "Compliance"],
        "bonus": ["DMF", "Submissions", "ICH Guidelines"],
    },
    "Biotech Research Associate": {
        "core": ["Molecular Biology", "Cell Culture", "PCR", "Lab Techniques", "Bioprocessing"],
        "bonus": ["Genomics", "Bioinformatics", "Fermentation"],
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


# ============================ ALL-BRANCH EXPANSION (2026-06-16) ============================
# Mechanical / Electrical / ECE / Civil / Chemical + Management / Finance / Pharma roles & data.
ROLE_SALARY_IN.update({'Mechanical Design Engineer': {'low': 2.5, 'median': 3.5, 'high': 6.0}, 'CAE / Simulation Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Manufacturing / Production Engineer': {'low': 2.5, 'median': 3.8, 'high': 6.5}, 'HVAC Engineer': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Automobile Engineer': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Maintenance Engineer': {'low': 2.5, 'median': 3.5, 'high': 6.0}, 'Electrical Design Engineer': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Power Systems Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Control & Automation Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.5}, 'Electrical Maintenance Engineer': {'low': 2.5, 'median': 3.8, 'high': 6.5}, 'Renewable Energy Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Embedded Systems Engineer': {'low': 3.5, 'median': 5.0, 'high': 10.0}, 'VLSI Design Engineer': {'low': 4.5, 'median': 7.0, 'high': 14.0}, 'Electronics Design Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'IoT Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'RF / Telecom Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Structural Engineer': {'low': 2.8, 'median': 4.0, 'high': 7.5}, 'Site / Construction Engineer': {'low': 2.5, 'median': 3.8, 'high': 6.5}, 'Construction Project Manager': {'low': 3.5, 'median': 5.5, 'high': 10.0}, 'Transportation Engineer': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Geotechnical Engineer': {'low': 3.0, 'median': 4.2, 'high': 7.5}, 'Quantity Surveyor': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Process Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.5}, 'Production (Chemical) Engineer': {'low': 2.8, 'median': 4.2, 'high': 7.5}, 'QA / QC Engineer (Chemical)': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Safety (HSE) Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'R&D Chemical Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Product Manager': {'low': 6.0, 'median': 10.0, 'high': 20.0}, 'Marketing Manager': {'low': 3.5, 'median': 5.5, 'high': 11.0}, 'HR Manager': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Operations Manager': {'low': 4.0, 'median': 6.0, 'high': 11.0}, 'Management Consultant': {'low': 6.0, 'median': 9.0, 'high': 16.0}, 'Financial Analyst': {'low': 3.5, 'median': 5.5, 'high': 10.0}, 'Accountant': {'low': 2.5, 'median': 3.5, 'high': 6.0}, 'Investment Banking Analyst': {'low': 8.0, 'median': 12.0, 'high': 22.0}, 'Auditor': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Tax Consultant': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Pharmacist': {'low': 2.5, 'median': 3.5, 'high': 5.5}, 'Clinical Research Associate': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Quality Control (Pharma)': {'low': 2.8, 'median': 4.0, 'high': 6.5}, 'Regulatory Affairs Associate': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Biotech Research Associate': {'low': 2.8, 'median': 4.0, 'high': 7.0}})
SKILL_DEMAND.update({'AutoCAD': 80, 'SolidWorks': 78, 'CATIA': 72, 'ANSYS': 74, 'MATLAB': 80, 'PLC': 80, 'SCADA': 76, 'Embedded C': 80, 'VLSI': 78, 'Verilog': 74, 'PCB Design': 72, 'IoT': 80, 'STAAD Pro': 76, 'ETABS': 74, 'Revit': 74, 'Primavera': 74, 'Project Management': 82, 'Process Engineering': 70, 'Aspen Plus': 66, 'GMP': 74, 'HPLC': 66, 'Quality Control': 74, 'Six Sigma': 78, 'Financial Modeling': 82, 'Excel': 80, 'Accounting': 74, 'Tally': 70, 'GST': 68, 'Taxation': 68, 'Digital Marketing': 80, 'SEO': 74, 'Product Management': 84, 'Supply Chain': 76, 'Regulatory Affairs': 70, 'Clinical Research': 70, 'Power Systems': 72, 'Industrial Automation': 76, 'Embedded Systems': 80, 'Structural Analysis': 72, 'Construction Management': 72, 'HVAC': 70, 'Recruitment': 72, 'Communication': 85, 'AutoCAD Electrical': 70})
SKILL_HOURS.update({'AutoCAD': 40, 'SolidWorks': 60, 'CATIA': 70, 'ANSYS': 70, 'FEA': 60, 'CFD': 70, 'MATLAB': 50, 'PLC': 60, 'SCADA': 50, 'Embedded C': 70, 'VLSI': 90, 'Verilog': 60, 'PCB Design': 50, 'IoT': 60, 'STAAD Pro': 50, 'ETABS': 50, 'Revit': 50, 'Primavera': 40, 'Project Management': 50, 'Aspen Plus': 60, 'GMP': 30, 'HPLC': 40, 'Six Sigma': 40, 'Financial Modeling': 60, 'Accounting': 50, 'Tally': 30, 'Digital Marketing': 40, 'Product Management': 60, 'Clinical Research': 50, 'Regulatory Affairs': 50})
SKILL_CATEGORY.update({'AutoCAD': 'Design/CAD', 'SolidWorks': 'Design/CAD', 'CATIA': 'Design/CAD', 'Creo': 'Design/CAD', 'GD&T': 'Design/CAD', 'Engineering Drawing': 'Design/CAD', 'Mechanical Design': 'Design/CAD', 'Sheet Metal': 'Manufacturing', 'Product Design': 'Design/CAD', 'Automotive Design': 'Design/CAD', 'AutoCAD Electrical': 'Design/CAD', 'AutoCAD Civil 3D': 'Design/CAD', 'Altium': 'Design/CAD', 'Eagle PCB': 'Design/CAD', 'PCB Design': 'Design/CAD', 'Circuit Design': 'Design/CAD', 'Revit MEP': 'Design/CAD', 'Revit': 'Design/CAD', 'Tekla': 'Design/CAD', 'BIM': 'Design/CAD', 'ANSYS': 'Simulation', 'FEA': 'Simulation', 'CFD': 'Simulation', 'Hypermesh': 'Simulation', 'Abaqus': 'Simulation', 'Process Simulation': 'Simulation', 'Aspen Plus': 'Simulation', 'HYSYS': 'Simulation', 'PLAXIS': 'Simulation', 'GeoStudio': 'Simulation', 'MATLAB': 'Simulation', 'Manufacturing Process': 'Manufacturing', 'Lean Manufacturing': 'Manufacturing', 'CNC': 'Manufacturing', 'Six Sigma': 'Manufacturing', 'Industrial Engineering': 'Manufacturing', 'Production Planning': 'Manufacturing', 'Unit Operations': 'Manufacturing', 'Thermodynamics': 'Mechanical Core', 'Heat Transfer': 'Mechanical Core', 'Mass Transfer': 'Mechanical Core', 'IC Engines': 'Mechanical Core', 'Vehicle Dynamics': 'Mechanical Core', 'HVAC': 'Mechanical Core', 'Duct Design': 'Mechanical Core', 'Hydraulics': 'Mechanical Core', 'Pneumatics': 'Mechanical Core', 'Preventive Maintenance': 'Maintenance', 'Mechanical Maintenance': 'Maintenance', 'Electrical Maintenance': 'Maintenance', 'Troubleshooting': 'Maintenance', 'Root Cause Analysis': 'Maintenance', 'Motors': 'Maintenance', 'VFD': 'Maintenance', 'Electrical Design': 'Electrical', 'Power Systems': 'Electrical', 'Power Distribution': 'Electrical', 'Transformers': 'Electrical', 'Switchgear': 'Electrical', 'Protection Systems': 'Electrical', 'Load Calculation': 'Electrical', 'Wiring': 'Electrical', 'ETAP': 'Electrical', 'DIALux': 'Electrical', 'Solar Energy': 'Electrical', 'Wind Energy': 'Electrical', 'Energy Audit': 'Electrical', 'Renewable Energy': 'Electrical', 'Battery Storage': 'Electrical', 'PLC': 'Automation', 'SCADA': 'Automation', 'HMI': 'Automation', 'Industrial Automation': 'Automation', 'Instrumentation': 'Automation', 'DCS': 'Automation', 'Ladder Logic': 'Automation', 'Sensors': 'Automation', 'Embedded C': 'Electronics', 'Microcontrollers': 'Electronics', 'RTOS': 'Electronics', 'Embedded Systems': 'Electronics', 'ARM': 'Electronics', 'VLSI': 'Electronics', 'Verilog': 'Electronics', 'VHDL': 'Electronics', 'SystemVerilog': 'Electronics', 'Cadence': 'Electronics', 'Synopsys': 'Electronics', 'FPGA': 'Electronics', 'Static Timing Analysis': 'Electronics', 'Digital Electronics': 'Electronics', 'Analog Electronics': 'Electronics', 'Signal Processing': 'Electronics', 'RF Engineering': 'Electronics', 'Wireless Communication': 'Electronics', 'Antenna Design': 'Electronics', '5G': 'Electronics', 'LTE': 'Electronics', 'IoT': 'Electronics', 'Arduino': 'Electronics', 'Raspberry Pi': 'Electronics', 'MQTT': 'Electronics', 'Network Planning': 'Electronics', 'STAAD Pro': 'Civil/Structural', 'ETABS': 'Civil/Structural', 'Structural Analysis': 'Civil/Structural', 'RCC Design': 'Civil/Structural', 'SAP2000': 'Civil/Structural', 'Steel Design': 'Civil/Structural', 'Construction Management': 'Civil/Structural', 'Surveying': 'Civil/Structural', 'Quantity Estimation': 'Civil/Structural', 'Site Supervision': 'Civil/Structural', 'Concrete Technology': 'Civil/Structural', 'Highway Engineering': 'Civil/Structural', 'Pavement Design': 'Civil/Structural', 'Transportation Planning': 'Civil/Structural', 'Traffic Engineering': 'Civil/Structural', 'Geotechnical Engineering': 'Civil/Structural', 'Soil Mechanics': 'Civil/Structural', 'Foundation Design': 'Civil/Structural', 'BOQ': 'Civil/Structural', 'Cost Estimation': 'Civil/Structural', 'MX Road': 'Civil/Structural', 'Project Management': 'Project Mgmt', 'Primavera': 'Project Mgmt', 'MS Project': 'Project Mgmt', 'Contract Management': 'Project Mgmt', 'Planning': 'Project Mgmt', 'Roadmapping': 'Project Mgmt', 'Agile': 'Project Mgmt', 'Process Engineering': 'Process/Chemical', 'Chemical Process': 'Process/Chemical', 'P&ID': 'Process/Chemical', 'HAZOP': 'Process/Chemical', 'Process Safety': 'Process/Chemical', 'Scale-up': 'Process/Chemical', 'Design of Experiments': 'Process/Chemical', 'Lab Techniques': 'Process/Chemical', 'Research': 'Process/Chemical', 'Quality Control': 'Quality/Safety', 'Quality Assurance': 'Quality/Safety', 'GMP': 'Quality/Safety', 'Analytical Techniques': 'Quality/Safety', 'HPLC': 'Quality/Safety', 'ISO Standards': 'Quality/Safety', 'Documentation': 'Quality/Safety', 'HSE': 'Quality/Safety', 'Risk Assessment': 'Quality/Safety', 'Safety Management': 'Quality/Safety', 'Fire Safety': 'Quality/Safety', 'NEBOSH': 'Quality/Safety', 'ISO 45001': 'Quality/Safety', 'GLP': 'Quality/Safety', 'Validation': 'Quality/Safety', 'Stability Studies': 'Quality/Safety', 'Product Management': 'Management', 'Market Research': 'Management', 'Communication': 'Management', 'Digital Marketing': 'Management', 'SEO': 'Management', 'Social Media Marketing': 'Management', 'Branding': 'Management', 'Google Analytics': 'Management', 'Content Marketing': 'Management', 'CRM': 'Management', 'Recruitment': 'Management', 'HR Management': 'Management', 'Employee Relations': 'Management', 'Payroll': 'Management', 'HRIS': 'Management', 'Talent Management': 'Management', 'Labor Law': 'Management', 'Operations Management': 'Management', 'Supply Chain': 'Management', 'Process Improvement': 'Management', 'Inventory Management': 'Management', 'Logistics': 'Management', 'Strategy': 'Management', 'Problem Solving': 'Management', 'PowerPoint': 'Management', 'Wireframing': 'Management', 'Analytics': 'Management', 'Business Analysis': 'Management', 'Financial Modeling': 'Finance', 'Financial Analysis': 'Finance', 'Accounting': 'Finance', 'Valuation': 'Finance', 'VBA': 'Finance', 'Bloomberg': 'Finance', 'Tally': 'Finance', 'GST': 'Finance', 'Bookkeeping': 'Finance', 'SAP FICO': 'Finance', 'Taxation': 'Finance', 'Auditing': 'Finance', 'DCF': 'Finance', 'M&A': 'Finance', 'Internal Controls': 'Finance', 'IFRS': 'Finance', 'Risk Management': 'Finance', 'Income Tax': 'Finance', 'TDS': 'Finance', 'Compliance': 'Finance', 'Pharmacology': 'Pharma/Bio', 'Pharmaceutics': 'Pharma/Bio', 'Drug Dispensing': 'Pharma/Bio', 'Pharmacy Practice': 'Pharma/Bio', 'Clinical Pharmacy': 'Pharma/Bio', 'Hospital Pharmacy': 'Pharma/Bio', 'Clinical Research': 'Pharma/Bio', 'Clinical Trials': 'Pharma/Bio', 'GCP': 'Pharma/Bio', 'Pharmacovigilance': 'Pharma/Bio', 'Regulatory Affairs': 'Pharma/Bio', 'Data Management': 'Pharma/Bio', 'Medical Writing': 'Pharma/Bio', 'ICH Guidelines': 'Pharma/Bio', 'Drug Regulations': 'Pharma/Bio', 'DMF': 'Pharma/Bio', 'Submissions': 'Pharma/Bio', 'Molecular Biology': 'Pharma/Bio', 'Cell Culture': 'Pharma/Bio', 'PCR': 'Pharma/Bio', 'Bioprocessing': 'Pharma/Bio', 'Genomics': 'Pharma/Bio', 'Bioinformatics': 'Pharma/Bio', 'Fermentation': 'Pharma/Bio', 'SAP': 'Tools', 'Cloud': 'Tools'})
SKILL_ALIASES.update({'plc': 'PLC', 'scada': 'SCADA', 'hmi': 'HMI', 'dcs': 'DCS', 'vfd': 'VFD', 'fea': 'FEA', 'cfd': 'CFD', 'gd&t': 'GD&T', 'gdt': 'GD&T', 'hvac': 'HVAC', 'vlsi': 'VLSI', 'iot': 'IoT', 'internet of things': 'IoT', 'rcc': 'RCC Design', 'boq': 'BOQ', 'gmp': 'GMP', 'gcp': 'GCP', 'glp': 'GLP', 'hplc': 'HPLC', 'gst': 'GST', 'hse': 'HSE', 'ic engine': 'IC Engines', 'ic engines': 'IC Engines', 'pcb': 'PCB Design', 'pcb design': 'PCB Design', 'solidworks': 'SolidWorks', 'solid works': 'SolidWorks', 'catia': 'CATIA', 'ansys': 'ANSYS', 'creo': 'Creo', 'staad': 'STAAD Pro', 'staad pro': 'STAAD Pro', 'staad.pro': 'STAAD Pro', 'etabs': 'ETABS', 'sap2000': 'SAP2000', 'primavera': 'Primavera', 'ms project': 'MS Project', 'tally': 'Tally', 'matlab': 'MATLAB', 'simulink': 'MATLAB', 'verilog': 'Verilog', 'vhdl': 'VHDL', 'autocad': 'AutoCAD', 'auto cad': 'AutoCAD', 'revit': 'Revit', 'aspen': 'Aspen Plus', 'aspen plus': 'Aspen Plus', 'hysys': 'HYSYS', 'p&id': 'P&ID', 'hazop': 'HAZOP', 'embedded c': 'Embedded C', 'microcontroller': 'Microcontrollers', 'microcontrollers': 'Microcontrollers', 'arduino': 'Arduino', 'raspberry pi': 'Raspberry Pi', 'fpga': 'FPGA', 'rtos': 'RTOS', 'arm': 'ARM', 'six sigma': 'Six Sigma', 'lean': 'Lean Manufacturing', 'cnc': 'CNC', 'sap': 'SAP', 'sap fico': 'SAP FICO', 'financial modeling': 'Financial Modeling', 'financial modelling': 'Financial Modeling', 'dcf': 'DCF', 'seo': 'SEO', 'crm': 'CRM', 'kpi': 'Analytics', 'pcr': 'PCR', 'power bi': 'Power BI'})
BRANCHES = {'Computer / IT': ['AI Engineer', 'ML Engineer', 'Data Analyst', 'Data Scientist', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer', 'Android Developer', 'Cloud / DevOps Engineer', 'Data Engineer', 'Business Analyst', 'Cybersecurity Analyst', 'UI/UX Designer', 'QA / Automation Tester', 'Game Developer'], 'Mechanical': ['Mechanical Design Engineer', 'CAE / Simulation Engineer', 'Manufacturing / Production Engineer', 'HVAC Engineer', 'Automobile Engineer', 'Maintenance Engineer'], 'Electrical': ['Electrical Design Engineer', 'Power Systems Engineer', 'Control & Automation Engineer', 'Electrical Maintenance Engineer', 'Renewable Energy Engineer'], 'Electronics / ECE': ['Embedded Systems Engineer', 'VLSI Design Engineer', 'Electronics Design Engineer', 'IoT Engineer', 'RF / Telecom Engineer'], 'Civil': ['Structural Engineer', 'Site / Construction Engineer', 'Construction Project Manager', 'Transportation Engineer', 'Geotechnical Engineer', 'Quantity Surveyor'], 'Chemical': ['Process Engineer', 'Production (Chemical) Engineer', 'QA / QC Engineer (Chemical)', 'Safety (HSE) Engineer', 'R&D Chemical Engineer'], 'Management / MBA': ['Product Manager', 'Marketing Manager', 'HR Manager', 'Operations Manager', 'Management Consultant', 'Business Analyst'], 'Finance / Commerce': ['Financial Analyst', 'Accountant', 'Investment Banking Analyst', 'Auditor', 'Tax Consultant'], 'Pharma / Bio': ['Pharmacist', 'Clinical Research Associate', 'Quality Control (Pharma)', 'Regulatory Affairs Associate', 'Biotech Research Associate']}
ROLE_TO_BRANCH = {r: b for b, rs in BRANCHES.items() for r in rs}
# experience salary bands: (label, multiplier on the fresher base)
SALARY_BAND_MULT = [("Fresher (0–2 yr)", 1.0), ("Mid (3–6 yr)", 2.0), ("Senior (7+ yr)", 3.3)]
MASTER_SKILLS = _build_master_skills()  # rebuild to include all new branch skills


# ===== MORE ROLES PER BRANCH (2026-06-16, batch 2) =====
ROLE_REQUIREMENTS.update({'iOS Developer': {'core': ['Swift', 'iOS', 'Xcode', 'Git'], 'bonus': ['Objective-C', 'REST API', 'Firebase']}, 'Database Administrator': {'core': ['SQL', 'Databases', 'MySQL', 'Linux', 'Performance Tuning'], 'bonus': ['MongoDB', 'Oracle', 'Shell Scripting']}, 'MLOps Engineer': {'core': ['Python', 'Docker', 'Kubernetes', 'Machine Learning', 'CI/CD'], 'bonus': ['AWS', 'MLflow', 'Airflow', 'Git']}, 'Site Reliability Engineer': {'core': ['Linux', 'Docker', 'Kubernetes', 'Python', 'Monitoring'], 'bonus': ['Terraform', 'AWS', 'CI/CD', 'Prometheus']}, 'Blockchain Developer': {'core': ['Solidity', 'Blockchain', 'JavaScript', 'Smart Contracts'], 'bonus': ['Web3.js', 'Ethereum', 'Node.js']}, 'Robotics Engineer': {'core': ['Robotics', 'ROS', 'Python', 'Control Systems', 'MATLAB'], 'bonus': ['Embedded C', 'Mechatronics', 'Sensors']}, 'Piping Design Engineer': {'core': ['Piping Design', 'AutoCAD', 'P&ID', 'SP3D', 'Isometric Drawing'], 'bonus': ['PDMS', 'CAESAR II', 'Pipe Stress Analysis']}, 'Quality Engineer (Mechanical)': {'core': ['Quality Control', 'GD&T', 'Six Sigma', 'Inspection', 'Quality Assurance'], 'bonus': ['CMM', 'SAP', 'Root Cause Analysis']}, 'Aerospace Engineer': {'core': ['Aerodynamics', 'CATIA', 'CFD', 'ANSYS', 'Aircraft Design'], 'bonus': ['MATLAB', 'Composites', 'FEA']}, 'Instrumentation Engineer': {'core': ['Instrumentation', 'PLC', 'SCADA', 'Control Systems', 'Calibration'], 'bonus': ['DCS', 'HART', 'Sensors']}, 'Electrical MEP Engineer': {'core': ['Electrical Design', 'MEP', 'AutoCAD', 'DIALux', 'Load Calculation'], 'bonus': ['Revit MEP', 'BIM', 'Lighting Design']}, 'EV / Battery Engineer': {'core': ['Electric Vehicles', 'Battery Storage', 'Power Electronics', 'MATLAB', 'Embedded C'], 'bonus': ['BMS', 'Motors', 'Power Systems']}, 'Testing & Commissioning Engineer': {'core': ['Testing', 'Commissioning', 'Switchgear', 'Protection Systems', 'Electrical Maintenance'], 'bonus': ['Relay Testing', 'Troubleshooting']}, 'Hardware Design Engineer': {'core': ['PCB Design', 'Circuit Design', 'Analog Electronics', 'Altium', 'Schematic Design'], 'bonus': ['Embedded C', 'Signal Integrity', 'Microcontrollers']}, 'Firmware Engineer': {'core': ['Embedded C', 'Firmware', 'Microcontrollers', 'RTOS', 'C'], 'bonus': ['ARM', 'Debugging', 'Device Drivers']}, 'DSP Engineer': {'core': ['Signal Processing', 'MATLAB', 'DSP', 'C++', 'Algorithms'], 'bonus': ['Python', 'FPGA', 'Image Processing']}, 'Telecom Network Engineer': {'core': ['Networking', 'Wireless Communication', '5G', 'Network Planning', 'Troubleshooting'], 'bonus': ['LTE', 'Routing', 'Optical Networks']}, 'Environmental Engineer': {'core': ['Environmental Engineering', 'Water Treatment', 'EIA', 'AutoCAD', 'Waste Management'], 'bonus': ['Air Quality', 'Sustainability', 'GIS']}, 'Water Resources Engineer': {'core': ['Water Resources', 'Hydrology', 'AutoCAD', 'Hydraulics', 'HEC-RAS'], 'bonus': ['GIS', 'Irrigation', 'WaterCAD']}, 'BIM Engineer': {'core': ['BIM', 'Revit', 'AutoCAD', 'Navisworks', '3D Modeling'], 'bonus': ['AutoCAD Civil 3D', 'Clash Detection', 'Tekla']}, 'Estimation & Billing Engineer': {'core': ['Cost Estimation', 'Quantity Estimation', 'BOQ', 'Excel', 'Billing'], 'bonus': ['AutoCAD', 'Rate Analysis', 'Tendering']}, 'Petroleum / Oil & Gas Engineer': {'core': ['Oil & Gas', 'Process Engineering', 'P&ID', 'Reservoir Engineering', 'Drilling'], 'bonus': ['Aspen Plus', 'HYSYS', 'Pipeline']}, 'Polymer Engineer': {'core': ['Polymer Science', 'Plastics Processing', 'Chemical Process', 'Quality Control', 'Material Science'], 'bonus': ['Injection Molding', 'Extrusion', 'Rheology']}, 'Plant Operations Engineer': {'core': ['Plant Operations', 'Chemical Process', 'Process Engineering', 'Safety Management', 'Troubleshooting'], 'bonus': ['DCS', 'SAP', 'Production Planning']}, 'Environmental Engineer (Chemical)': {'core': ['Environmental Engineering', 'Effluent Treatment', 'Waste Management', 'Pollution Control', 'Chemical Process'], 'bonus': ['ETP', 'Air Quality', 'ISO Standards']}, 'Business Development Manager': {'core': ['Business Development', 'Sales', 'Market Research', 'Negotiation', 'Communication'], 'bonus': ['CRM', 'Lead Generation', 'Strategy']}, 'Sales Manager': {'core': ['Sales', 'Communication', 'Negotiation', 'CRM', 'Team Management'], 'bonus': ['Market Research', 'Forecasting', 'B2B Sales']}, 'Supply Chain Manager': {'core': ['Supply Chain', 'Logistics', 'Inventory Management', 'Procurement', 'SAP'], 'bonus': ['Six Sigma', 'Demand Planning', 'Warehouse Management']}, 'Brand Manager': {'core': ['Branding', 'Marketing', 'Market Research', 'Communication', 'Advertising'], 'bonus': ['Digital Marketing', 'Social Media Marketing', 'Content Marketing']}, 'Chartered Accountant (CA)': {'core': ['Accounting', 'Auditing', 'Taxation', 'Financial Reporting', 'GST'], 'bonus': ['IFRS', 'SAP FICO', 'Compliance']}, 'Equity Research Analyst': {'core': ['Equity Research', 'Financial Modeling', 'Valuation', 'Excel', 'Financial Analysis'], 'bonus': ['Bloomberg', 'DCF', 'Industry Analysis']}, 'Credit Analyst': {'core': ['Credit Analysis', 'Financial Analysis', 'Excel', 'Risk Assessment', 'Accounting'], 'bonus': ['Financial Modeling', 'Banking', 'Underwriting']}, 'Risk Analyst': {'core': ['Risk Management', 'Financial Analysis', 'Excel', 'Statistics', 'Compliance'], 'bonus': ['SQL', 'VaR', 'Credit Risk']}, 'Formulation Scientist': {'core': ['Formulation', 'Pharmaceutics', 'Drug Development', 'Analytical Techniques', 'Research'], 'bonus': ['Stability Studies', 'GMP', 'Lab Techniques']}, 'Pharmacovigilance Associate': {'core': ['Pharmacovigilance', 'Drug Safety', 'Clinical Research', 'Medical Coding', 'ICH Guidelines'], 'bonus': ['Adverse Event Reporting', 'Regulatory Affairs']}, 'Medical Writer': {'core': ['Medical Writing', 'Clinical Research', 'Regulatory Affairs', 'Documentation', 'Research'], 'bonus': ['Literature Review', 'Publication', 'ICH Guidelines']}, 'Microbiologist': {'core': ['Microbiology', 'Lab Techniques', 'Quality Control', 'Sterility Testing', 'Documentation'], 'bonus': ['GLP', 'Culture Techniques', 'GMP']}})
ROLE_SALARY_IN.update({'iOS Developer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Database Administrator': {'low': 3.5, 'median': 5.5, 'high': 10.0}, 'MLOps Engineer': {'low': 5.0, 'median': 8.0, 'high': 15.0}, 'Site Reliability Engineer': {'low': 5.0, 'median': 8.0, 'high': 16.0}, 'Blockchain Developer': {'low': 5.0, 'median': 8.0, 'high': 16.0}, 'Robotics Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Piping Design Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Quality Engineer (Mechanical)': {'low': 2.8, 'median': 4.0, 'high': 6.5}, 'Aerospace Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Instrumentation Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Electrical MEP Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'EV / Battery Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Testing & Commissioning Engineer': {'low': 2.8, 'median': 4.2, 'high': 7.5}, 'Hardware Design Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Firmware Engineer': {'low': 3.5, 'median': 5.5, 'high': 10.0}, 'DSP Engineer': {'low': 3.5, 'median': 5.5, 'high': 10.0}, 'Telecom Network Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Environmental Engineer': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Water Resources Engineer': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'BIM Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Estimation & Billing Engineer': {'low': 2.8, 'median': 4.0, 'high': 6.5}, 'Petroleum / Oil & Gas Engineer': {'low': 4.0, 'median': 6.0, 'high': 12.0}, 'Polymer Engineer': {'low': 3.0, 'median': 4.2, 'high': 7.5}, 'Plant Operations Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Environmental Engineer (Chemical)': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Business Development Manager': {'low': 3.5, 'median': 6.0, 'high': 12.0}, 'Sales Manager': {'low': 3.5, 'median': 5.5, 'high': 11.0}, 'Supply Chain Manager': {'low': 4.0, 'median': 6.5, 'high': 12.0}, 'Brand Manager': {'low': 4.0, 'median': 6.5, 'high': 12.0}, 'Chartered Accountant (CA)': {'low': 6.0, 'median': 9.0, 'high': 16.0}, 'Equity Research Analyst': {'low': 5.0, 'median': 8.0, 'high': 15.0}, 'Credit Analyst': {'low': 3.5, 'median': 5.5, 'high': 10.0}, 'Risk Analyst': {'low': 4.0, 'median': 6.0, 'high': 11.0}, 'Formulation Scientist': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Pharmacovigilance Associate': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Medical Writer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Microbiologist': {'low': 2.8, 'median': 4.0, 'high': 6.5}})
SKILL_DEMAND.update({'Robotics': 76, 'ROS': 70, 'BIM': 78, 'MEP': 70, 'Oil & Gas': 72, 'Sales': 80, 'Business Development': 78, 'Supply Chain': 78, 'Equity Research': 70, 'Formulation': 66, 'Pharmacovigilance': 70, 'Solidity': 74, 'Blockchain': 72, 'MLflow': 72, 'Monitoring': 78, 'Prometheus': 72, 'Firmware': 78, 'DSP': 70, 'Instrumentation': 74, 'Environmental Engineering': 70, 'Swift': 78, 'iOS': 78, 'Microbiology': 62, 'Medical Writing': 66, 'Risk Management': 74, 'Procurement': 72, 'Marketing': 80, 'Negotiation': 78, 'Communication': 85, 'Power Electronics': 72, 'Electric Vehicles': 78, 'Aerospace': 68, 'Aerodynamics': 66})
SKILL_CATEGORY.update({'Swift': 'Mobile/Game', 'iOS': 'Mobile/Game', 'Xcode': 'Mobile/Game', 'Objective-C': 'Mobile/Game', 'Oracle': 'Data', 'Performance Tuning': 'Data', 'Airflow': 'Data', 'Shell Scripting': 'Cloud/DevOps', 'Backup & Recovery': 'Cloud/DevOps', 'Monitoring': 'Cloud/DevOps', 'Prometheus': 'Cloud/DevOps', 'MLflow': 'Cloud/DevOps', 'Solidity': 'Blockchain', 'Blockchain': 'Blockchain', 'Smart Contracts': 'Blockchain', 'Web3.js': 'Blockchain', 'Ethereum': 'Blockchain', 'Robotics': 'Robotics', 'ROS': 'Robotics', 'Control Systems': 'Robotics', 'Mechatronics': 'Robotics', 'Piping Design': 'Design/CAD', 'SP3D': 'Design/CAD', 'Isometric Drawing': 'Design/CAD', 'PDMS': 'Design/CAD', 'Schematic Design': 'Design/CAD', 'Aircraft Design': 'Design/CAD', '3D Modeling': 'Design/CAD', 'Navisworks': 'Design/CAD', 'CAESAR II': 'Simulation', 'Pipe Stress Analysis': 'Simulation', 'Aerodynamics': 'Simulation', 'HEC-RAS': 'Civil/Structural', 'WaterCAD': 'Civil/Structural', 'Rheology': 'Simulation', 'Inspection': 'Manufacturing', 'CMM': 'Manufacturing', 'Injection Molding': 'Manufacturing', 'Extrusion': 'Manufacturing', 'Composites': 'Mechanical Core', 'Calibration': 'Electrical', 'HART': 'Electrical', 'Lighting Design': 'Electrical', 'MEP': 'Electrical', 'Power Electronics': 'Electrical', 'BMS': 'Electrical', 'Electric Vehicles': 'Electrical', 'Relay Testing': 'Electrical', 'Testing': 'Electrical', 'Commissioning': 'Electrical', 'Firmware': 'Electronics', 'Debugging': 'Electronics', 'Device Drivers': 'Electronics', 'Signal Integrity': 'Electronics', 'DSP': 'Electronics', 'Algorithms': 'Electronics', 'Image Processing': 'Electronics', 'Routing': 'Electronics', 'Optical Networks': 'Electronics', 'Environmental Engineering': 'Environment', 'Water Treatment': 'Environment', 'EIA': 'Environment', 'Waste Management': 'Environment', 'Air Quality': 'Environment', 'Sustainability': 'Environment', 'Pollution Control': 'Environment', 'Effluent Treatment': 'Environment', 'ETP': 'Environment', 'Water Resources': 'Civil/Structural', 'Hydrology': 'Civil/Structural', 'Irrigation': 'Civil/Structural', 'GIS': 'Civil/Structural', 'Clash Detection': 'Civil/Structural', 'Billing': 'Civil/Structural', 'Rate Analysis': 'Civil/Structural', 'Tendering': 'Civil/Structural', 'Oil & Gas': 'Process/Chemical', 'Reservoir Engineering': 'Process/Chemical', 'Drilling': 'Process/Chemical', 'Pipeline': 'Process/Chemical', 'Polymer Science': 'Process/Chemical', 'Plastics Processing': 'Process/Chemical', 'Material Science': 'Process/Chemical', 'Plant Operations': 'Process/Chemical', 'Business Development': 'Management', 'Sales': 'Management', 'Negotiation': 'Management', 'Lead Generation': 'Management', 'Team Management': 'Management', 'Forecasting': 'Management', 'B2B Sales': 'Management', 'Procurement': 'Management', 'Demand Planning': 'Management', 'Warehouse Management': 'Management', 'Marketing': 'Management', 'Advertising': 'Management', 'Financial Reporting': 'Finance', 'Equity Research': 'Finance', 'Industry Analysis': 'Finance', 'Credit Analysis': 'Finance', 'Banking': 'Finance', 'Underwriting': 'Finance', 'VaR': 'Finance', 'Credit Risk': 'Finance', 'Formulation': 'Pharma/Bio', 'Drug Development': 'Pharma/Bio', 'Drug Safety': 'Pharma/Bio', 'Medical Coding': 'Pharma/Bio', 'Adverse Event Reporting': 'Pharma/Bio', 'Literature Review': 'Pharma/Bio', 'Publication': 'Pharma/Bio', 'Microbiology': 'Pharma/Bio', 'Sterility Testing': 'Pharma/Bio', 'Culture Techniques': 'Pharma/Bio'})
SKILL_ALIASES.update({'ros': 'ROS', 'bim': 'BIM', 'mep': 'MEP', 'bms': 'BMS', 'dsp': 'DSP', 'gis': 'GIS', 'etp': 'ETP', 'eia': 'EIA', 'sp3d': 'SP3D', 'pdms': 'PDMS', 'caesar ii': 'CAESAR II', 'hec-ras': 'HEC-RAS', 'cmm': 'CMM', 'swift': 'Swift', 'ios': 'iOS', 'xcode': 'Xcode', 'solidity': 'Solidity', 'blockchain': 'Blockchain', 'ethereum': 'Ethereum', 'web3': 'Web3.js', 'web3.js': 'Web3.js', 'airflow': 'Airflow', 'mlflow': 'MLflow', 'prometheus': 'Prometheus', 'oil and gas': 'Oil & Gas', 'oil & gas': 'Oil & Gas', 'b2b': 'B2B Sales', 'ev': 'Electric Vehicles', 'firmware': 'Firmware', 'instrumentation': 'Instrumentation', 'robotics': 'Robotics', 'microbiology': 'Microbiology', 'pharmacovigilance': 'Pharmacovigilance', 'equity research': 'Equity Research'})
for _b, _rs in {'Computer / IT': ['iOS Developer', 'Database Administrator', 'MLOps Engineer', 'Site Reliability Engineer', 'Blockchain Developer'], 'Mechanical': ['Robotics Engineer', 'Piping Design Engineer', 'Quality Engineer (Mechanical)', 'Aerospace Engineer'], 'Electrical': ['Instrumentation Engineer', 'Electrical MEP Engineer', 'EV / Battery Engineer', 'Testing & Commissioning Engineer'], 'Electronics / ECE': ['Hardware Design Engineer', 'Firmware Engineer', 'DSP Engineer', 'Telecom Network Engineer'], 'Civil': ['Environmental Engineer', 'Water Resources Engineer', 'BIM Engineer', 'Estimation & Billing Engineer'], 'Chemical': ['Petroleum / Oil & Gas Engineer', 'Polymer Engineer', 'Plant Operations Engineer', 'Environmental Engineer (Chemical)'], 'Management / MBA': ['Business Development Manager', 'Sales Manager', 'Supply Chain Manager', 'Brand Manager'], 'Finance / Commerce': ['Chartered Accountant (CA)', 'Equity Research Analyst', 'Credit Analyst', 'Risk Analyst'], 'Pharma / Bio': ['Formulation Scientist', 'Pharmacovigilance Associate', 'Medical Writer', 'Microbiologist']}.items():
    BRANCHES[_b].extend([r for r in _rs if r not in BRANCHES[_b]])
ROLE_TO_BRANCH = {r: b for b, rs in BRANCHES.items() for r in rs}
MASTER_SKILLS = _build_master_skills()


# ===== MORE ROLES PER BRANCH (2026-06-16, batch 3) =====
ROLE_REQUIREMENTS.update({'Cloud Architect': {'core': ['AWS', 'Azure', 'Cloud', 'Kubernetes', 'Terraform'], 'bonus': ['Docker', 'Linux', 'Networking']}, 'Computer Vision Engineer': {'core': ['Python', 'Computer Vision', 'Deep Learning', 'OpenCV', 'PyTorch'], 'bonus': ['TensorFlow', 'Machine Learning', 'Image Processing']}, 'NLP Engineer': {'core': ['Python', 'NLP', 'Deep Learning', 'Machine Learning', 'Hugging Face'], 'bonus': ['PyTorch', 'LangChain', 'Spacy']}, 'Tool & Die Engineer': {'core': ['Tool Design', 'AutoCAD', 'Sheet Metal', 'Manufacturing Process', 'GD&T'], 'bonus': ['SolidWorks', 'CNC', 'Die Design']}, 'Mechatronics Engineer': {'core': ['Mechatronics', 'PLC', 'Robotics', 'Control Systems', 'Embedded C'], 'bonus': ['MATLAB', 'Sensors', 'Industrial Automation']}, 'Project Engineer (Mechanical)': {'core': ['Project Management', 'Mechanical Design', 'AutoCAD', 'Planning', 'Execution'], 'bonus': ['MS Project', 'Cost Estimation']}, 'Power Electronics Engineer': {'core': ['Power Electronics', 'Embedded C', 'MATLAB', 'Control Systems', 'Converters'], 'bonus': ['PLC', 'Motors', 'Simulink']}, 'Solar Design Engineer': {'core': ['Solar Energy', 'Electrical Design', 'AutoCAD', 'PVsyst', 'Energy Audit'], 'bonus': ['Power Systems', 'Renewable Energy']}, 'SCADA Engineer': {'core': ['SCADA', 'PLC', 'HMI', 'Industrial Automation', 'Instrumentation'], 'bonus': ['DCS', 'Communication Protocols']}, 'IC Design Engineer': {'core': ['VLSI', 'Analog Electronics', 'Cadence', 'Circuit Design', 'Layout Design'], 'bonus': ['Verilog', 'SPICE', 'Semiconductor']}, 'Test Engineer (Electronics)': {'core': ['Testing', 'PCB Design', 'Debugging', 'Electronics', 'Instrumentation'], 'bonus': ['Industrial Automation', 'LabVIEW']}, 'Automotive Electronics Engineer': {'core': ['Embedded C', 'CAN Bus', 'Automotive Electronics', 'Microcontrollers', 'AUTOSAR'], 'bonus': ['Diagnostics', 'ECU']}, 'Highway / Road Engineer': {'core': ['Highway Engineering', 'AutoCAD Civil 3D', 'Pavement Design', 'Surveying', 'Road Design'], 'bonus': ['MX Road', 'Quantity Estimation']}, 'Bridge Engineer': {'core': ['Structural Analysis', 'STAAD Pro', 'Bridge Design', 'RCC Design', 'AutoCAD'], 'bonus': ['ETABS', 'Steel Design']}, 'Planning Engineer (Civil)': {'core': ['Project Planning', 'Primavera', 'MS Project', 'Construction Management', 'Scheduling'], 'bonus': ['Cost Control', 'Quantity Estimation']}, 'Food Technologist': {'core': ['Food Technology', 'Quality Control', 'Food Safety', 'HACCP', 'Microbiology'], 'bonus': ['Product Development', 'FSSAI']}, 'Energy / Sustainability Engineer': {'core': ['Energy Audit', 'Sustainability', 'Process Engineering', 'Renewable Energy', 'Carbon Footprint'], 'bonus': ['Energy Management', 'ISO 50001']}, 'Quality Assurance Engineer (Chemical)': {'core': ['Quality Assurance', 'GMP', 'Documentation', 'Auditing', 'ISO Standards'], 'bonus': ['Validation', 'Six Sigma']}, 'Project Manager': {'core': ['Project Management', 'Agile', 'Scrum', 'Planning', 'Stakeholder Management'], 'bonus': ['MS Project', 'JIRA', 'Risk Management']}, 'Digital Marketing Specialist': {'core': ['Digital Marketing', 'SEO', 'Google Ads', 'Social Media Marketing', 'Content Marketing'], 'bonus': ['Google Analytics', 'Email Marketing']}, 'Financial Manager': {'core': ['Financial Management', 'Accounting', 'Budgeting', 'Financial Analysis', 'Excel'], 'bonus': ['Financial Modeling', 'Forecasting']}, 'Investment Analyst': {'core': ['Investment Analysis', 'Financial Modeling', 'Valuation', 'Portfolio Management', 'Excel'], 'bonus': ['Bloomberg', 'Equity Research']}, 'Actuary': {'core': ['Actuarial Science', 'Statistics', 'Excel', 'Risk Management', 'Probability'], 'bonus': ['R', 'Financial Modeling']}, 'Banking Associate': {'core': ['Banking', 'Accounting', 'Customer Service', 'Financial Analysis', 'Compliance'], 'bonus': ['Excel', 'Credit Analysis']}, 'Production Pharmacist': {'core': ['Pharmaceutics', 'GMP', 'Production Planning', 'Quality Control', 'Documentation'], 'bonus': ['Validation', 'Tablet Manufacturing']}, 'Biotechnologist': {'core': ['Biotechnology', 'Molecular Biology', 'Cell Culture', 'Fermentation', 'Lab Techniques'], 'bonus': ['Genomics', 'Bioprocessing']}, 'Medical Representative': {'core': ['Pharmacology', 'Sales', 'Communication', 'Product Knowledge', 'Marketing'], 'bonus': ['CRM', 'Negotiation']}})
ROLE_SALARY_IN.update({'Cloud Architect': {'low': 8.0, 'median': 14.0, 'high': 28.0}, 'Computer Vision Engineer': {'low': 5.0, 'median': 8.0, 'high': 16.0}, 'NLP Engineer': {'low': 5.0, 'median': 8.0, 'high': 16.0}, 'Tool & Die Engineer': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Mechatronics Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Project Engineer (Mechanical)': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Power Electronics Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Solar Design Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'SCADA Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.5}, 'IC Design Engineer': {'low': 4.5, 'median': 7.0, 'high': 14.0}, 'Test Engineer (Electronics)': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Automotive Electronics Engineer': {'low': 3.5, 'median': 5.5, 'high': 10.0}, 'Highway / Road Engineer': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Bridge Engineer': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Planning Engineer (Civil)': {'low': 3.0, 'median': 4.5, 'high': 8.5}, 'Food Technologist': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Energy / Sustainability Engineer': {'low': 3.5, 'median': 5.0, 'high': 9.0}, 'Quality Assurance Engineer (Chemical)': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Project Manager': {'low': 5.0, 'median': 8.0, 'high': 16.0}, 'Digital Marketing Specialist': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Financial Manager': {'low': 5.0, 'median': 8.0, 'high': 15.0}, 'Investment Analyst': {'low': 5.0, 'median': 8.0, 'high': 15.0}, 'Actuary': {'low': 6.0, 'median': 10.0, 'high': 20.0}, 'Banking Associate': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Production Pharmacist': {'low': 2.8, 'median': 4.0, 'high': 7.0}, 'Biotechnologist': {'low': 3.0, 'median': 4.5, 'high': 8.0}, 'Medical Representative': {'low': 2.5, 'median': 3.8, 'high': 7.0}})
SKILL_DEMAND.update({'Cloud': 82, 'Hugging Face': 76, 'Computer Vision': 74, 'Scrum': 74, 'JIRA': 72, 'Actuarial Science': 64, 'Investment Analysis': 70, 'Food Technology': 60, 'AUTOSAR': 74, 'LabVIEW': 64, 'Portfolio Management': 68, 'Biotechnology': 62, 'Power Electronics': 72, 'Project Management': 84, 'Digital Marketing': 80, 'VLSI': 78})
SKILL_CATEGORY.update({'Hugging Face': 'AI/ML', 'Spacy': 'AI/ML', 'Tool Design': 'Manufacturing', 'Die Design': 'Manufacturing', 'Execution': 'Project Mgmt', 'Project Planning': 'Project Mgmt', 'Scheduling': 'Project Mgmt', 'Cost Control': 'Project Mgmt', 'Scrum': 'Project Mgmt', 'Stakeholder Management': 'Project Mgmt', 'JIRA': 'Project Mgmt', 'Converters': 'Electrical', 'PVsyst': 'Electrical', 'Communication Protocols': 'Electrical', 'Layout Design': 'Electronics', 'SPICE': 'Electronics', 'Semiconductor': 'Electronics', 'LabVIEW': 'Electronics', 'Electronics': 'Electronics', 'CAN Bus': 'Electronics', 'Automotive Electronics': 'Electronics', 'AUTOSAR': 'Electronics', 'Diagnostics': 'Electronics', 'ECU': 'Electronics', 'Road Design': 'Civil/Structural', 'Bridge Design': 'Civil/Structural', 'Food Technology': 'Quality/Safety', 'Food Safety': 'Quality/Safety', 'HACCP': 'Quality/Safety', 'FSSAI': 'Quality/Safety', 'Product Development': 'Process/Chemical', 'Carbon Footprint': 'Environment', 'Energy Management': 'Environment', 'ISO 50001': 'Environment', 'Google Ads': 'Management', 'Email Marketing': 'Management', 'Customer Service': 'Management', 'Product Knowledge': 'Management', 'Financial Management': 'Finance', 'Budgeting': 'Finance', 'Investment Analysis': 'Finance', 'Portfolio Management': 'Finance', 'Actuarial Science': 'Finance', 'Probability': 'Data', 'Tablet Manufacturing': 'Pharma/Bio', 'Biotechnology': 'Pharma/Bio'})
SKILL_ALIASES.update({'haccp': 'HACCP', 'fssai': 'FSSAI', 'autosar': 'AUTOSAR', 'ecu': 'ECU', 'labview': 'LabVIEW', 'jira': 'JIRA', 'scrum': 'Scrum', 'pvsyst': 'PVsyst', 'hugging face': 'Hugging Face', 'spacy': 'Spacy', 'actuary': 'Actuarial Science', 'actuarial': 'Actuarial Science', 'portfolio management': 'Portfolio Management', 'can bus': 'CAN Bus', 'investment analysis': 'Investment Analysis', 'biotechnology': 'Biotechnology', 'google ads': 'Google Ads'})
for _b, _rs in {'Computer / IT': ['Cloud Architect', 'Computer Vision Engineer', 'NLP Engineer'], 'Mechanical': ['Tool & Die Engineer', 'Mechatronics Engineer', 'Project Engineer (Mechanical)'], 'Electrical': ['Power Electronics Engineer', 'Solar Design Engineer', 'SCADA Engineer'], 'Electronics / ECE': ['IC Design Engineer', 'Test Engineer (Electronics)', 'Automotive Electronics Engineer'], 'Civil': ['Highway / Road Engineer', 'Bridge Engineer', 'Planning Engineer (Civil)'], 'Chemical': ['Food Technologist', 'Energy / Sustainability Engineer', 'Quality Assurance Engineer (Chemical)'], 'Management / MBA': ['Project Manager', 'Digital Marketing Specialist', 'Financial Manager'], 'Finance / Commerce': ['Investment Analyst', 'Actuary', 'Banking Associate'], 'Pharma / Bio': ['Production Pharmacist', 'Biotechnologist', 'Medical Representative']}.items():
    BRANCHES[_b].extend([r for r in _rs if r not in BRANCHES[_b]])
ROLE_TO_BRANCH = {r: b for b, rs in BRANCHES.items() for r in rs}
MASTER_SKILLS = _build_master_skills()
