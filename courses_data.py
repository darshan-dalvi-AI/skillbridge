"""
courses_data.py — Curated Learning Resources
============================================
Hand-picked, real, FREE resources for each skill. These are stable landing
pages / official docs / well-known free platforms (MDN, Kaggle Learn,
freeCodeCamp, official docs, Khan Academy, etc.) chosen because they don't
rot like individual video URLs.

For any skill not in the curated map, get_courses() returns a guaranteed-valid
YouTube + Google search link, so a recommendation is ALWAYS available and never
404s. This is the honest version of "course recommendations with real links":
verified where we're confident, safe search fallback everywhere else.
"""

from urllib.parse import quote_plus

COURSES = {
    "Python": [
        {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/"},
        {"title": "freeCodeCamp – Python", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/"},
    ],
    "Machine Learning": [
        {"title": "Google ML Crash Course", "url": "https://developers.google.com/machine-learning/crash-course"},
        {"title": "Kaggle – Intro to ML", "url": "https://www.kaggle.com/learn/intro-to-machine-learning"},
    ],
    "Deep Learning": [
        {"title": "Kaggle – Intro to Deep Learning", "url": "https://www.kaggle.com/learn/intro-to-deep-learning"},
        {"title": "DeepLearning.AI", "url": "https://www.deeplearning.ai/"},
    ],
    "NLP": [
        {"title": "Hugging Face NLP Course", "url": "https://huggingface.co/learn/nlp-course"},
    ],
    "Computer Vision": [
        {"title": "Kaggle – Computer Vision", "url": "https://www.kaggle.com/learn/computer-vision"},
    ],
    "Statistics": [
        {"title": "Khan Academy – Statistics", "url": "https://www.khanacademy.org/math/statistics-probability"},
    ],
    "Data Visualization": [
        {"title": "Kaggle – Data Visualization", "url": "https://www.kaggle.com/learn/data-visualization"},
    ],
    "Data Analysis": [
        {"title": "Kaggle – Pandas", "url": "https://www.kaggle.com/learn/pandas"},
    ],
    "Pandas": [
        {"title": "Kaggle – Pandas", "url": "https://www.kaggle.com/learn/pandas"},
        {"title": "Pandas Getting Started", "url": "https://pandas.pydata.org/docs/getting_started/"},
    ],
    "NumPy": [
        {"title": "NumPy – Learn", "url": "https://numpy.org/learn/"},
    ],
    "SQL": [
        {"title": "Kaggle – Intro to SQL", "url": "https://www.kaggle.com/learn/intro-to-sql"},
        {"title": "SQLBolt (interactive)", "url": "https://sqlbolt.com/"},
    ],
    "TensorFlow": [
        {"title": "TensorFlow Tutorials", "url": "https://www.tensorflow.org/tutorials"},
    ],
    "PyTorch": [
        {"title": "PyTorch Tutorials", "url": "https://pytorch.org/tutorials/"},
    ],
    "Keras": [
        {"title": "Keras Developer Guides", "url": "https://keras.io/guides/"},
    ],
    "OpenCV": [
        {"title": "OpenCV-Python Tutorials", "url": "https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html"},
    ],
    "LangChain": [
        {"title": "LangChain Tutorials", "url": "https://python.langchain.com/docs/tutorials/"},
    ],
    "HTML": [
        {"title": "MDN – Learn HTML", "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML"},
        {"title": "freeCodeCamp – Responsive Web", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"},
    ],
    "CSS": [
        {"title": "web.dev – Learn CSS", "url": "https://web.dev/learn/css"},
        {"title": "MDN – Learn CSS", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS"},
    ],
    "JavaScript": [
        {"title": "javascript.info", "url": "https://javascript.info/"},
        {"title": "freeCodeCamp – JS", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"},
    ],
    "TypeScript": [
        {"title": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/handbook/intro.html"},
    ],
    "React": [
        {"title": "React Official – Learn", "url": "https://react.dev/learn"},
    ],
    "Next.js": [
        {"title": "Next.js – Learn", "url": "https://nextjs.org/learn"},
    ],
    "Redux": [
        {"title": "Redux Essentials", "url": "https://redux.js.org/tutorials/essentials/part-1-overview-concepts"},
    ],
    "Tailwind": [
        {"title": "Tailwind Docs", "url": "https://tailwindcss.com/docs/installation"},
    ],
    "Node.js": [
        {"title": "Node.js – Learn", "url": "https://nodejs.org/en/learn"},
    ],
    "Flask": [
        {"title": "Flask Tutorial", "url": "https://flask.palletsprojects.com/en/latest/tutorial/"},
    ],
    "Django": [
        {"title": "Django Tutorial", "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/"},
    ],
    "FastAPI": [
        {"title": "FastAPI Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"},
    ],
    "REST API": [
        {"title": "REST API Tutorial", "url": "https://restfulapi.net/"},
    ],
    "Git": [
        {"title": "Learn Git Branching", "url": "https://learngitbranching.js.org/"},
        {"title": "Pro Git (book)", "url": "https://git-scm.com/book/en/v2"},
    ],
    "GitHub": [
        {"title": "GitHub Skills", "url": "https://skills.github.com/"},
    ],
    "Docker": [
        {"title": "Docker – Get Started", "url": "https://docs.docker.com/get-started/"},
    ],
    "Kubernetes": [
        {"title": "Kubernetes Tutorials", "url": "https://kubernetes.io/docs/tutorials/"},
    ],
    "AWS": [
        {"title": "AWS Skill Builder", "url": "https://explore.skillbuilder.aws/"},
    ],
    "Azure": [
        {"title": "Microsoft Learn – Azure", "url": "https://learn.microsoft.com/en-us/training/azure/"},
    ],
    "Linux": [
        {"title": "Linux Journey", "url": "https://linuxjourney.com/"},
    ],
    "CI/CD": [
        {"title": "GitHub Actions – Learn", "url": "https://docs.github.com/en/actions/learn-github-actions"},
    ],
    "Jenkins": [
        {"title": "Jenkins Tutorials", "url": "https://www.jenkins.io/doc/tutorials/"},
    ],
    "Terraform": [
        {"title": "Terraform Tutorials", "url": "https://developer.hashicorp.com/terraform/tutorials"},
    ],
    "Java": [
        {"title": "dev.java – Learn", "url": "https://dev.java/learn/"},
    ],
    "Kotlin": [
        {"title": "Kotlin – Getting Started", "url": "https://kotlinlang.org/docs/getting-started.html"},
    ],
    "C": [
        {"title": "Learn-C.org", "url": "https://www.learn-c.org/"},
    ],
    "C++": [
        {"title": "LearnCpp.com", "url": "https://www.learncpp.com/"},
    ],
    "R": [
        {"title": "RStudio – Beginners", "url": "https://education.rstudio.com/learn/beginner/"},
    ],
    "Flutter": [
        {"title": "Flutter – Learn", "url": "https://docs.flutter.dev/get-started/learn-more"},
    ],
    "Android Studio": [
        {"title": "Android Basics", "url": "https://developer.android.com/courses/android-basics-compose/course"},
    ],
    "Jetpack Compose": [
        {"title": "Jetpack Compose Tutorial", "url": "https://developer.android.com/jetpack/compose/tutorial"},
    ],
    "Firebase": [
        {"title": "Firebase Docs", "url": "https://firebase.google.com/docs"},
    ],
    "MongoDB": [
        {"title": "MongoDB University", "url": "https://learn.mongodb.com/"},
    ],
    "MySQL": [
        {"title": "MySQL Tutorial", "url": "https://www.mysqltutorial.org/"},
    ],
    "Databases": [
        {"title": "CS50 – SQL/Databases", "url": "https://cs50.harvard.edu/sql/"},
    ],
    "Excel": [
        {"title": "Excel Help & Learning", "url": "https://support.microsoft.com/en-us/excel"},
    ],
    "Power BI": [
        {"title": "Microsoft Learn – Power BI", "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi"},
    ],
    "Tableau": [
        {"title": "Tableau – Free Training", "url": "https://www.tableau.com/learn/training/elearning"},
    ],
    "Big Data": [
        {"title": "Apache Spark – Docs", "url": "https://spark.apache.org/docs/latest/"},
    ],
    "Matplotlib": [
        {"title": "Matplotlib Tutorials", "url": "https://matplotlib.org/stable/tutorials/index.html"},
    ],
    "Seaborn": [
        {"title": "Seaborn Tutorial", "url": "https://seaborn.pydata.org/tutorial.html"},
    ],
}


def get_courses(skill: str) -> list:
    """
    Return curated resources for a skill, or a guaranteed-valid search
    fallback so a recommendation is always available (never a 404).
    """
    if skill in COURSES:
        return COURSES[skill]
    q = quote_plus(f"learn {skill} free course tutorial")
    return [
        {"title": f"YouTube – learn {skill} (free)",
         "url": f"https://www.youtube.com/results?search_query={q}"},
        {"title": f"Google – best free {skill} course",
         "url": f"https://www.google.com/search?q={q}"},
    ]
