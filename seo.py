"""
seo.py — SEO head/body injection for SkillBridge (Streamlit)
============================================================
Streamlit gives us no direct control over the <head> of the served page, so
search engines see an almost-empty HTML shell (the SEOptimer audit graded
On-Page SEO "F": no meta description, no H1, no schema, 1 word of content).

Fix: at startup we patch Streamlit's own static index.html (the file the
server sends to every visitor) and add:

  * a longer <title> (50-60 chars)
  * meta description + keywords + robots + canonical
  * Open Graph tags (Facebook/WhatsApp/LinkedIn previews) + X (Twitter) cards
  * JSON-LD structured data (WebApplication + Person identity schema)
  * a rich <noscript> block with H1/H2 headers, real text content and
    profile links — this is what non-JS crawlers read

Safe by design: idempotent (marker check), keeps a .bak backup, and never
raises — if anything goes wrong the app just starts normally.
"""

import os
import re

# ------------------------------------------------------------------ constants
MARKER = "<!-- skillbridge-seo v1 -->"

APP_URL = "https://skillbridge-darshan.streamlit.app/"
REPO_URL = "https://github.com/darshan-dalvi-AI/skillbridge"
GITHUB_URL = "https://github.com/darshan-dalvi-AI"
LINKEDIN_URL = "https://www.linkedin.com/in/darshan-dalvi"
OG_IMAGE = "https://raw.githubusercontent.com/darshan-dalvi-AI/skillbridge/main/og-image.png"

# 53 chars — within the recommended 50-60 range
TITLE = "SkillBridge — AI Career Guidance & Skill Gap Analyzer"

# ~157 chars — within the recommended 120-160 range
DESCRIPTION = ("Free AI career tool for students: upload your resume, measure "
               "your skill gap for top tech roles, and get an AI learning "
               "roadmap, courses and live job demand.")

KEYWORDS = ("skill gap analysis, AI career guidance, resume analyzer, "
            "career roadmap, skill gap analyzer, learning roadmap, "
            "ATS resume check, job skills, tech careers, SkillBridge")

_JSON_LD = """
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebApplication",
      "@id": "%(url)s#app",
      "name": "SkillBridge",
      "url": "%(url)s",
      "description": "%(desc)s",
      "applicationCategory": "EducationalApplication",
      "operatingSystem": "Any (web browser)",
      "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
      "creator": {"@id": "%(url)s#person"},
      "image": "%(img)s"
    },
    {
      "@type": "Person",
      "@id": "%(url)s#person",
      "name": "Darshan Dalvi",
      "jobTitle": "Computer Engineering Student",
      "url": "%(github)s",
      "sameAs": ["%(github)s", "%(linkedin)s"]
    },
    {
      "@type": "WebSite",
      "@id": "%(url)s#website",
      "name": "SkillBridge",
      "url": "%(url)s"
    }
  ]
}
""" % {"url": APP_URL, "desc": DESCRIPTION, "img": OG_IMAGE,
       "github": GITHUB_URL, "linkedin": LINKEDIN_URL}

_HEAD_BLOCK = f"""{MARKER}
<meta name="description" content="{DESCRIPTION}"/>
<meta name="keywords" content="{KEYWORDS}"/>
<meta name="author" content="Darshan Dalvi"/>
<meta name="robots" content="index, follow"/>
<link rel="canonical" href="{APP_URL}"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="SkillBridge"/>
<meta property="og:title" content="{TITLE}"/>
<meta property="og:description" content="{DESCRIPTION}"/>
<meta property="og:url" content="{APP_URL}"/>
<meta property="og:image" content="{OG_IMAGE}"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="og:locale" content="en_US"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{TITLE}"/>
<meta name="twitter:description" content="{DESCRIPTION}"/>
<meta name="twitter:image" content="{OG_IMAGE}"/>
<script type="application/ld+json">{_JSON_LD}</script>
"""

# Real, honest content for non-JS crawlers (search engines + LLMs).
# This replaces Streamlit's default "You need to enable JavaScript" notice.
_NOSCRIPT_BLOCK = f"""<noscript>
<article>
<h1>SkillBridge — AI Career Guidance &amp; Skill Gap Analyzer</h1>
<p>SkillBridge is a free AI-powered career guidance tool built for engineering
students and early-career professionals. Upload your resume (PDF) or select
your skills manually, choose a target role, and SkillBridge instantly measures
the gap between the skills you have and the skills the job market expects —
then generates a personalised, step-by-step learning roadmap to close it.</p>

<h2>What SkillBridge does</h2>
<p>The skill gap analysis compares your current skills against curated
requirements for popular technology roles such as AI/ML Engineer, Data
Analyst, Data Scientist, Frontend Developer, Backend Developer and more. You
get a match percentage, a readiness verdict, the exact list of missing skills,
salary benchmarks in India, and live in-demand skills pulled from real job
postings.</p>

<h2>Key features</h2>
<ul>
<li>Resume analyzer — automatic skill extraction from your PDF resume</li>
<li>Skill gap report — match score, matched skills and missing skills</li>
<li>AI learning roadmap — an ordered study plan with free courses and projects</li>
<li>Live job-market data — top skills employers ask for right now</li>
<li>Progress tracker — mark skills as learned and watch your score climb</li>
<li>Resume quality check, ATS score and job-description (JD) matching</li>
<li>Compare roles side by side and chat with an AI career mentor</li>
<li>Downloadable PDF report of your full analysis</li>
</ul>

<h2>Who it is for</h2>
<p>Students preparing for placements, graduates planning a switch into tech,
and anyone who wants a clear, data-backed answer to the question: "What should
I learn next to get the job I want?" SkillBridge is free to use in any modern
browser — enable JavaScript to launch the interactive app.</p>

<h2>About the developer</h2>
<p>SkillBridge is a final-year Computer Engineering project by Darshan Dalvi.
Connect on <a href="{GITHUB_URL}">GitHub</a> and
<a href="{LINKEDIN_URL}">LinkedIn</a>, or browse the
<a href="{REPO_URL}">source code</a>. Start your own
<a href="{APP_URL}">skill gap analysis</a> now.</p>
</article>
</noscript>"""


# ------------------------------------------------------------------ injection
_done = False  # process-level guard so reruns skip instantly


def inject_seo() -> bool:
    """Patch Streamlit's static index.html with SEO tags. Returns True if the
    file now contains the tags (already patched counts as success)."""
    global _done
    if _done:
        return True
    try:
        import streamlit
        index_path = os.path.join(os.path.dirname(streamlit.__file__),
                                  "static", "index.html")
        with open(index_path, encoding="utf-8") as f:
            html = f.read()

        if MARKER in html:                       # already patched this install
            _done = True
            return True

        # keep an untouched backup once
        bak = index_path + ".skillbridge.bak"
        if not os.path.exists(bak):
            with open(bak, "w", encoding="utf-8") as f:
                f.write(html)

        # 1) real <title> (Streamlit ships "<title>Streamlit</title>")
        html = re.sub(r"<title>.*?</title>", f"<title>{TITLE}</title>",
                      html, count=1, flags=re.S)

        # 2) head block just before </head>
        html = html.replace("</head>", _HEAD_BLOCK + "</head>", 1)

        # 3) crawlable content: replace the default noscript notice
        if "<noscript>" in html:
            html = re.sub(r"<noscript>.*?</noscript>", _NOSCRIPT_BLOCK,
                          html, count=1, flags=re.S)
        else:                                    # fallback: right after <body>
            html = re.sub(r"(<body[^>]*>)", r"\1" + _NOSCRIPT_BLOCK,
                          html, count=1)

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        _done = True
        return True
    except Exception:
        # Never let SEO break the app (e.g. read-only file system).
        return False
