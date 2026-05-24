"""
╔══════════════════════════════════════════════════════════════════╗
║     ADITHYA'S ALL-IN-ONE INTERNSHIP PIPELINE v3.0               ║
║     Internshala + LinkedIn + Indeed + Naukri + Wellfound        ║
║     + Unstop + HackerEarth  (7 PLATFORMS!)                      ║
║     Locations: Hyderabad + Remote + Bangalore                    ║
║     ATS Resume + Cover Letter + Cold Message + Interview Prep    ║
║     ML Engineer Focused | AI: Ollama (FREE forever!)            ║
╚══════════════════════════════════════════════════════════════════╝

SETUP:
1. pip install ollama pdfplumber beautifulsoup4 requests reportlab python-dotenv
2. Create a .env file in this folder:
       SENDER_EMAIL=adithyaadi104@gmail.com
       SENDER_APP_PASSWORD=your_gmail_app_password
       RECEIVER_EMAIL=adithyaadi104@gmail.com
3. Make sure Ollama is running: ollama serve
4. Run: python internship_pipeline.py
5. Optional - run daily at 9am automatically:
   Linux/Mac: crontab -e  →  0 9 * * * python /path/to/internship_pipeline.py
   Windows  : Task Scheduler → run daily at 9am
"""

import ollama
import smtplib
import json
import os
import re
import requests
import pdfplumber
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER
from dotenv import load_dotenv

# ============================================================
# 🔐 LOAD CREDENTIALS FROM .env (NEVER hardcode passwords!)
# ============================================================
load_dotenv()
SENDER_EMAIL        = os.getenv("SENDER_EMAIL",        "adithyaadi104@gmail.com")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD", "")
RECEIVER_EMAIL      = os.getenv("RECEIVER_EMAIL",      "adithyaadi104@gmail.com")

# ============================================================
# 📄 RESUME
# ============================================================
RESUME_PATH = "resume.pdf"

# ============================================================
# 🤖 OLLAMA MODEL
# ============================================================
OLLAMA_MODEL = "llama3.2:3b"

# ============================================================
# 🎯 PREFERENCES — ML Engineer focused
# ============================================================
LOCATIONS   = ["Hyderabad", "Remote", "Bangalore"]
MIN_STIPEND = 5000
SEEN_FILE   = "seen_internships.json"

ML_ENGINEER_KEYWORDS = [
    ("machine-learning-engineer",   "Python, PyTorch, Scikit-learn, ML Pipelines"),
    ("llm-engineer",                "Python, LangChain, LangGraph, RAG, LLMs"),
    ("generative-ai",               "Python, LLMs, RAG, Pinecone, LangGraph"),
    ("mlops",                       "Docker, MLflow, CI/CD, Python, FastAPI"),
    ("deep-learning",               "Python, PyTorch, Neural Networks, GPU"),
    ("nlp-engineer",                "Python, NLP, Transformers, HuggingFace"),
    ("machine-learning",            "Python, ML, Scikit-learn, TensorFlow"),
    ("artificial-intelligence",     "Python, TensorFlow, PyTorch, Deep Learning"),
    ("computer-vision",             "Python, OpenCV, PyTorch, Deep Learning"),
    ("data-science",                "Python, Pandas, SQL, Scikit-learn"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def ask_ollama(prompt):
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"  ⚠️  Ollama error: {e}")
        print("  💡 Make sure Ollama is running: ollama serve")
        return "Ollama not available — please check if it's running."


def read_resume():
    print("\n📄 Reading your resume...")
    try:
        with pdfplumber.open(RESUME_PATH) as pdf:
            text = "".join(p.extract_text() or "" for p in pdf.pages)
        print("  ✅ Resume read successfully!")
        return text
    except Exception as e:
        print(f"  ⚠️  PDF read failed ({e}), using default profile...")
        return """
Adithya Vaddadi | Hyderabad | adithyaadi104@gmail.com | +91-7075615349
B.Tech AI/ML — Sphoorthy Engineering College (2027) | CGPA: 7.4
ML Intern — Infosys Springboard (Dec 2025 - Feb 2026)
Skills: Python, TensorFlow, Scikit-learn, Pandas, LangGraph, Pinecone, RAG, NLP
Projects: ClauseAI (multi-agent RAG), Food Classification (87% accuracy)
Certifications: IBM AI (Coursera), HackerRank Python & Java
"""


def detect_work_mode(text):
    text = text.lower()
    if "remote" in text or "work from home" in text:
        return "Remote"
    if "hybrid" in text:
        return "Hybrid"
    if "onsite" in text or "office" in text:
        return "Onsite"
    return "Not specified"


def score_internship(job):
    """ML Engineer focused scoring."""
    score    = 0
    title    = job.get("title",    "").lower()
    skills   = job.get("skills",   "").lower()
    mode     = job.get("mode",     job.get("location", "")).lower()
    location = job.get("location", "").lower()
    source   = job.get("source",   "").lower()

    # Title
    if "ml engineer"      in title: score += 10
    if "machine learning" in title: score += 8
    if "llm"              in title: score += 8
    if "generative ai"    in title: score += 8
    if "mlops"            in title: score += 7
    if "deep learning"    in title: score += 6
    if "nlp"              in title: score += 6
    if "computer vision"  in title: score += 6
    if "ai engineer"      in title: score += 6
    if "data science"     in title: score += 4

    # Skills
    if "pytorch"          in skills: score += 4
    if "langchain"        in skills: score += 4
    if "langgraph"        in skills: score += 4
    if "rag"              in skills: score += 4
    if "mlflow"           in skills: score += 3
    if "docker"           in skills: score += 3
    if "python"           in skills: score += 2

    # Location/mode
    if "remote"           in mode:     score += 3
    if "hyderabad"        in location: score += 2
    if "bangalore"        in location: score += 2

    # Platform bonus (startups > services)
    if "wellfound"        in source:   score += 3

    return score


def deduplicate(internships):
    seen_keys, unique = set(), []
    for i in internships:
        key = f"{i.get('title','').lower().strip()}|{i.get('company','').lower().strip()}"
        if key not in seen_keys:
            seen_keys.add(key)
            unique.append(i)
    print(f"  ✅ After dedup: {len(unique)} unique listings")
    return unique


# ════════════════════════════════════════════════════════════
# HR FINDER
# ════════════════════════════════════════════════════════════
def find_hr(job):
    company = job.get("company", "Unknown").replace(" ", "+")
    return {
        "company":        job.get("company", "Unknown"),
        "hr_search":      f"https://www.linkedin.com/search/results/people/?keywords=HR+Recruiter+{company}",
        "talent_search":  f"https://www.linkedin.com/search/results/people/?keywords=Talent+Acquisition+{company}",
        "founder_search": f"https://www.linkedin.com/search/results/people/?keywords=Founder+CTO+{company}",
        "suggested_roles": ["HR Manager", "Technical Recruiter", "Talent Acquisition", "CTO", "Founder"],
    }


# ════════════════════════════════════════════════════════════
# COLD MESSAGE
# ════════════════════════════════════════════════════════════
def generate_cold_message(job):
    print(f"  💬 Writing cold message for {job['title']}...")
    prompt = f"""
Write a short LinkedIn cold message from a student to a recruiter at {job['company']}.

Student profile:
- Name: Adithya Vaddadi
- Degree: B.Tech AI/ML (2027), Hyderabad
- Experience: ML Intern at Infosys Springboard
- Key project: ClauseAI (multi-agent RAG system using LangGraph + Pinecone)
- Skills: Python, Machine Learning, TensorFlow, LangGraph, RAG, NLP

Role applying for: {job['title']} at {job['company']}

Rules:
- Under 80 words
- Friendly and professional tone
- Mention ClauseAI briefly with one concrete detail
- End with a polite ask for consideration
- Do NOT use "I hope this message finds you well"
- Do NOT use "passionate about"
- Sound human, not templated

Output ONLY the message text, nothing else.
"""
    return ask_ollama(prompt)


# ════════════════════════════════════════════════════════════
# INTERVIEW PREP
# ════════════════════════════════════════════════════════════
def prepare_interview(job):
    print(f"  🎯 Preparing interview questions for {job['title']}...")
    prompt = f"""
Generate targeted interview preparation for this ML Engineer internship.

Role: {job['title']}
Company: {job['company']}
Required Skills: {job['skills']}

Provide:
1. 5 technical questions with brief model answers
2. 2 Python coding questions (describe problem + approach, no full code)
3. 2 machine learning theory questions with model answers
4. 1 behavioral question about Adithya's ClauseAI RAG project
5. A 30-second elevator pitch for Adithya to introduce himself

Be specific and practical. Focus on ML Engineer skills.
"""
    return ask_ollama(prompt)


# ════════════════════════════════════════════════════════════
# PLATFORM 1 — INTERNSHALA
# ════════════════════════════════════════════════════════════
def scrape_internshala():
    print("\n🔍 [1/7] Scraping Internshala...")
    results = []

    for location in LOCATIONS:
        for slug, skills in ML_ENGINEER_KEYWORDS[:5]:
            try:
                url  = f"https://internshala.com/internships/keywords-{slug},location-{location.lower()}"
                resp = requests.get(url, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")

                for card in soup.select(".individual_internship")[:2]:
                    title    = card.select_one(".profile a")
                    company  = card.select_one(".company_name a")
                    stipend  = card.select_one(".stipend")
                    duration = card.select_one(".duration-mobile")
                    link     = card.select_one(".profile a")

                    results.append({
                        "source":   "Internshala",
                        "title":    title.get_text(strip=True)    if title    else f"{slug.replace('-',' ').title()} Intern",
                        "company":  company.get_text(strip=True)  if company  else "Unknown",
                        "location": location,
                        "mode":     detect_work_mode(card.text),
                        "stipend":  stipend.get_text(strip=True)  if stipend  else "Not mentioned",
                        "duration": duration.get_text(strip=True) if duration else "2-6 months",
                        "skills":   skills,
                        "url":      "https://internshala.com" + link["href"] if link else url,
                    })
            except Exception as e:
                print(f"  ⚠️  Internshala [{slug}/{location}]: {e}")

    results += [
        {"source":"Internshala","title":"Machine Learning Engineer Intern","company":"Multiple Companies",
         "location":"Hyderabad","mode":"Not specified","stipend":"Rs.8,000-Rs.25,000/month","duration":"2-6 months",
         "skills":"Python, PyTorch, Scikit-learn, ML Pipelines",
         "url":"https://internshala.com/internships/machine-learning-internship-in-hyderabad/"},
        {"source":"Internshala","title":"Generative AI / LLM Intern","company":"Multiple Companies",
         "location":"Remote","mode":"Remote","stipend":"Rs.10,000-Rs.30,000/month","duration":"2-6 months",
         "skills":"Python, LangChain, RAG, LLMs, Pinecone",
         "url":"https://internshala.com/internships/artificial-intelligence-internship/"},
        {"source":"Internshala","title":"MLOps Intern","company":"Multiple Companies",
         "location":"Remote","mode":"Remote","stipend":"Rs.10,000-Rs.20,000/month","duration":"2-6 months",
         "skills":"Docker, MLflow, Python, CI/CD, FastAPI",
         "url":"https://internshala.com/internships/keywords-mlops/"},
    ]

    print(f"  ✅ Internshala: {len(results)} listings")
    return results


# ════════════════════════════════════════════════════════════
# PLATFORM 2 — LINKEDIN
# ════════════════════════════════════════════════════════════
def scrape_linkedin():
    print("\n🔍 [2/7] Scraping LinkedIn Jobs...")
    results = []
    searches = [
        ("machine learning engineer intern", "Python, PyTorch, ML Pipelines"),
        ("llm engineer intern",              "Python, LangChain, RAG, LLMs"),
        ("generative ai intern",             "Python, LLMs, RAG, LangGraph"),
        ("mlops intern",                     "Docker, MLflow, Python, FastAPI"),
        ("deep learning intern",             "Python, PyTorch, Neural Networks"),
    ]

    for query, skills in searches:
        for location in LOCATIONS:
            try:
                encoded = requests.utils.quote(query)
                enc_loc = requests.utils.quote(location)
                url     = f"https://www.linkedin.com/jobs/search/?keywords={encoded}&location={enc_loc}&f_JT=I&f_TPR=r604800"
                resp    = requests.get(url, headers=HEADERS, timeout=10)
                soup    = BeautifulSoup(resp.text, "html.parser")

                for card in soup.select(".base-card")[:2]:
                    title   = card.select_one(".base-search-card__title")
                    company = card.select_one(".base-search-card__subtitle")
                    loc     = card.select_one(".job-search-card__location")
                    link    = card.select_one("a.base-card__full-link")

                    if title:
                        results.append({
                            "source":   "LinkedIn",
                            "title":    title.get_text(strip=True),
                            "company":  company.get_text(strip=True) if company else "Company",
                            "location": loc.get_text(strip=True)     if loc     else location,
                            "mode":     detect_work_mode(loc.get_text() if loc else location),
                            "stipend":  "Check on LinkedIn",
                            "duration": "N/A",
                            "url":      link["href"].split("?")[0]   if link and link.get("href") else url,
                            "skills":   skills,
                        })
            except Exception as e:
                print(f"  ⚠️  LinkedIn [{query}/{location}]: {e}")

    results += [
        {"source":"LinkedIn","title":"ML Engineer Intern","company":"Search Results",
         "location":"Remote","mode":"Remote","stipend":"Check on LinkedIn","duration":"N/A",
         "skills":"Python, PyTorch, ML Pipelines, Scikit-learn",
         "url":"https://www.linkedin.com/jobs/search/?keywords=ml+engineer+intern&f_JT=I"},
        {"source":"LinkedIn","title":"Generative AI Intern","company":"Search Results",
         "location":"Remote","mode":"Remote","stipend":"Check on LinkedIn","duration":"N/A",
         "skills":"Python, LLMs, RAG, LangGraph, Pinecone",
         "url":"https://www.linkedin.com/jobs/search/?keywords=generative+ai+intern&f_JT=I"},
    ]

    print(f"  ✅ LinkedIn: {len(results)} listings")
    return results


# ════════════════════════════════════════════════════════════
# PLATFORM 3 — INDEED
# ════════════════════════════════════════════════════════════
def scrape_indeed():
    print("\n🔍 [3/7] Scraping Indeed...")
    results = []
    searches = [
        ("machine+learning+engineer+intern", "Python, PyTorch, ML Pipelines"),
        ("llm+engineer+intern",              "Python, LangChain, RAG, LLMs"),
        ("mlops+intern",                     "Docker, MLflow, Python, FastAPI"),
        ("deep+learning+intern",             "Python, PyTorch, Neural Networks"),
        ("data+science+intern",              "Python, Pandas, SQL, Scikit-learn"),
    ]

    for query, skills in searches:
        for location in LOCATIONS:
            try:
                url  = f"https://in.indeed.com/jobs?q={query}&l={location}&fromage=7&jt=internship"
                resp = requests.get(url, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")

                for card in soup.select(".job_seen_beacon")[:2]:
                    title   = card.select_one(".jobTitle span")
                    company = card.select_one(".companyName")
                    loc     = card.select_one(".companyLocation")
                    salary  = card.select_one(".salary-snippet-container")   # Fixed: sselect_one → select_one
                    link    = card.select_one(".jcs-JobTitle")

                    if title:
                        job_id = link.get("data-jk", "") if link else ""
                        results.append({
                            "source":   "Indeed",
                            "title":    title.get_text(strip=True),
                            "company":  company.get_text(strip=True) if company else "Company",
                            "location": loc.get_text(strip=True)     if loc     else location,
                            "mode":     detect_work_mode(loc.get_text() if loc else location),
                            "stipend":  salary.get_text(strip=True)  if salary  else "Check on Indeed",
                            "duration": "N/A",
                            "url":      f"https://in.indeed.com/viewjob?jk={job_id}" if job_id else url,
                            "skills":   skills,
                        })
            except Exception as e:
                print(f"  ⚠️  Indeed [{query}/{location}]: {e}")

    results += [
        {"source":"Indeed","title":"ML Engineer Intern","company":"Multiple Companies",
         "location":"Remote","mode":"Remote","stipend":"Check on Indeed","duration":"N/A",
         "skills":"Python, PyTorch, ML Pipelines",
         "url":"https://in.indeed.com/jobs?q=machine+learning+engineer+intern&jt=internship"},
    ]

    print(f"  ✅ Indeed: {len(results)} listings")
    return results


# ════════════════════════════════════════════════════════════
# PLATFORM 4 — NAUKRI (HIGH VOLUME IN INDIA)
# ════════════════════════════════════════════════════════════
def scrape_naukri():
    print("\n🔍 [4/7] Scraping Naukri...")
    results = []
    searches = [
        ("machine-learning-engineer",  "Python, ML, Scikit-learn, PyTorch"),
        ("llm-engineer",               "Python, LLMs, RAG, LangChain"),
        ("mlops-engineer",             "Docker, MLflow, Python, CI/CD"),
        ("deep-learning-engineer",     "Python, PyTorch, TensorFlow, CV"),
        ("data-scientist",             "Python, Pandas, SQL, Scikit-learn"),
    ]

    for slug, skills in searches:
        for location in ["hyderabad", "remote", "bangalore"]:
            try:
                url  = f"https://www.naukri.com/{slug}-jobs-in-{location}?jobAge=7"
                resp = requests.get(url, headers=HEADERS, timeout=12)
                soup = BeautifulSoup(resp.text, "html.parser")

                for card in soup.select("article.joblistingCard, .jobTuple, .job-tuple")[:2]:
                    title   = card.select_one(".title, .jobTitle, h2 a")
                    company = card.select_one(".companyInfo a, .comp-name, .companyName")
                    loc     = card.select_one(".location, .loc, .jobLocation")
                    salary  = card.select_one(".salary, .sal")
                    link    = card.select_one("a.title, a.jobTitle, h2 a")

                    if title:
                        results.append({
                            "source":   "Naukri",
                            "title":    title.get_text(strip=True),
                            "company":  company.get_text(strip=True) if company else "Company",
                            "location": loc.get_text(strip=True)     if loc     else location.title(),
                            "mode":     detect_work_mode(loc.get_text() if loc else location),
                            "stipend":  salary.get_text(strip=True)  if salary  else "Check on Naukri",
                            "duration": "N/A",
                            "url":      link["href"]                  if link and link.get("href") else url,
                            "skills":   skills,
                        })
            except Exception as e:
                print(f"  ⚠️  Naukri [{slug}/{location}]: {e}")

    results += [
        {"source":"Naukri","title":"Machine Learning Engineer Fresher","company":"Multiple Companies",
         "location":"Hyderabad","mode":"Not specified","stipend":"Check on Naukri","duration":"N/A",
         "skills":"Python, ML, PyTorch, Scikit-learn",
         "url":"https://www.naukri.com/machine-learning-engineer-jobs-in-hyderabad"},
        {"source":"Naukri","title":"LLM / GenAI Engineer Fresher","company":"Multiple Companies",
         "location":"Remote","mode":"Remote","stipend":"Check on Naukri","duration":"N/A",
         "skills":"Python, LLMs, RAG, LangChain, Pinecone",
         "url":"https://www.naukri.com/llm-jobs"},
        {"source":"Naukri","title":"Data Scientist Fresher","company":"Multiple Companies",
         "location":"Bangalore","mode":"Not specified","stipend":"Check on Naukri","duration":"N/A",
         "skills":"Python, SQL, Pandas, Scikit-learn, ML",
         "url":"https://www.naukri.com/data-scientist-jobs-in-bangalore"},
    ]

    print(f"  ✅ Naukri: {len(results)} listings")
    return results


# ════════════════════════════════════════════════════════════
# PLATFORM 5 — WELLFOUND / ANGELLIST (BEST FOR STARTUPS)
# ════════════════════════════════════════════════════════════
def scrape_wellfound():
    print("\n🔍 [5/7] Scraping Wellfound (AngelList)...")
    results = []
    searches = [
        ("machine-learning",  "Python, ML, PyTorch, Scikit-learn"),
        ("llm",               "Python, LLMs, RAG, LangChain, Pinecone"),
        ("generative-ai",     "Python, GenAI, LLMs, RAG, LangGraph"),
        ("mlops",             "Docker, MLflow, Python, FastAPI, CI/CD"),
        ("deep-learning",     "Python, PyTorch, Neural Networks"),
    ]

    for slug, skills in searches:
        try:
            url  = f"https://wellfound.com/role/r/{slug}"
            resp = requests.get(url, headers=HEADERS, timeout=12)
            soup = BeautifulSoup(resp.text, "html.parser")

            for card in soup.select("div[class*='JobListingCard'], div[class*='styles_component']")[:3]:
                title   = card.select_one("a[class*='jobTitle'], h2, h3")
                company = card.select_one("a[class*='company'], span[class*='company']")
                loc     = card.select_one("span[class*='location'], div[class*='location']")
                link    = card.select_one("a[href*='/jobs/']")

                if title:
                    results.append({
                        "source":   "Wellfound",
                        "title":    title.get_text(strip=True),
                        "company":  company.get_text(strip=True) if company else "Startup",
                        "location": loc.get_text(strip=True)     if loc     else "Remote",
                        "mode":     detect_work_mode(loc.get_text() if loc else "remote"),
                        "stipend":  "Check on Wellfound",
                        "duration": "N/A",
                        "url":      "https://wellfound.com" + link["href"] if link and link.get("href") else url,
                        "skills":   skills,
                    })
        except Exception as e:
            print(f"  ⚠️  Wellfound [{slug}]: {e}")

    results += [
        {"source":"Wellfound","title":"ML Engineer Intern (Startup)","company":"AI Startups",
         "location":"Remote","mode":"Remote","stipend":"Check on Wellfound","duration":"3-6 months",
         "skills":"Python, PyTorch, ML, LLMs, FastAPI",
         "url":"https://wellfound.com/role/r/machine-learning-engineer"},
        {"source":"Wellfound","title":"LLM / RAG Engineer Intern","company":"AI Startups",
         "location":"Remote","mode":"Remote","stipend":"Check on Wellfound","duration":"3-6 months",
         "skills":"Python, LangChain, RAG, Pinecone, LangGraph",
         "url":"https://wellfound.com/role/r/llm"},
        {"source":"Wellfound","title":"Generative AI Intern","company":"AI Startups",
         "location":"Remote","mode":"Remote","stipend":"Check on Wellfound","duration":"3-6 months",
         "skills":"Python, LLMs, RAG, Prompt Engineering, LangGraph",
         "url":"https://wellfound.com/role/r/generative-ai"},
    ]

    print(f"  ✅ Wellfound: {len(results)} listings")
    return results


# ════════════════════════════════════════════════════════════
# PLATFORM 6 — UNSTOP
# ════════════════════════════════════════════════════════════
def scrape_unstop():
    print("\n🔍 [6/7] Scraping Unstop...")
    results = []
    searches = [
        ("machine-learning", "Python, ML, Scikit-learn"),
        ("data-science",     "Python, Pandas, SQL"),
        ("ai-ml",            "Python, TensorFlow, Deep Learning"),
    ]

    for slug, skills in searches:
        try:
            url  = f"https://unstop.com/internships?search={slug}&opportunity=internship"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            for card in soup.select(".opportunity-card, div[class*='card']")[:2]:
                title   = card.select_one("h2, h3, .title, a[class*='title']")
                company = card.select_one(".comp-name, .company, span[class*='company']")
                loc     = card.select_one(".location, span[class*='location']")
                link    = card.select_one("a[href*='/internship'], a[href*='/opportunity']")

                if title:
                    results.append({
                        "source":   "Unstop",
                        "title":    title.get_text(strip=True),
                        "company":  company.get_text(strip=True) if company else "Company",
                        "location": loc.get_text(strip=True)     if loc     else "India",
                        "mode":     detect_work_mode(loc.get_text() if loc else ""),
                        "stipend":  "Check on Unstop",
                        "duration": "N/A",
                        "url":      "https://unstop.com" + link["href"] if link and link.get("href") else url,
                        "skills":   skills,
                    })
        except Exception as e:
            print(f"  ⚠️  Unstop [{slug}]: {e}")

    results += [
        {"source":"Unstop","title":"ML / AI Intern","company":"Multiple Companies",
         "location":"Remote","mode":"Remote","stipend":"Check on Unstop","duration":"N/A",
         "skills":"Python, ML, TensorFlow, Scikit-learn",
         "url":"https://unstop.com/internships?search=machine+learning&opportunity=internship"},
    ]

    print(f"  ✅ Unstop: {len(results)} listings")
    return results


# ════════════════════════════════════════════════════════════
# PLATFORM 7 — HACKEREARTH JOBS
# ════════════════════════════════════════════════════════════
def scrape_hackerearth():
    print("\n🔍 [7/7] Scraping HackerEarth Jobs...")
    results = []

    try:
        url  = "https://www.hackerearth.com/jobs/filter/?role=machine-learning-engineer&location=remote&location=hyderabad&location=bangalore"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        for card in soup.select(".job-card, div[class*='job']")[:5]:
            title   = card.select_one("h2, h3, .job-title, a[class*='title']")
            company = card.select_one(".company-name, .company")
            loc     = card.select_one(".location, .job-location")
            link    = card.select_one("a[href*='/jobs/']")

            if title:
                results.append({
                    "source":   "HackerEarth",
                    "title":    title.get_text(strip=True),
                    "company":  company.get_text(strip=True) if company else "Company",
                    "location": loc.get_text(strip=True)     if loc     else "Remote",
                    "mode":     detect_work_mode(loc.get_text() if loc else "remote"),
                    "stipend":  "Check on HackerEarth",
                    "duration": "N/A",
                    "url":      "https://www.hackerearth.com" + link["href"] if link and link.get("href") else url,
                    "skills":   "Python, ML, Data Science",
                })
    except Exception as e:
        print(f"  ⚠️  HackerEarth: {e}")

    results += [
        {"source":"HackerEarth","title":"ML Engineer / Data Scientist","company":"Multiple Companies",
         "location":"Remote","mode":"Remote","stipend":"Check on HackerEarth","duration":"N/A",
         "skills":"Python, ML, PyTorch, SQL",
         "url":"https://www.hackerearth.com/jobs/filter/?role=machine-learning-engineer"},
    ]

    print(f"  ✅ HackerEarth: {len(results)} listings")
    return results


# ════════════════════════════════════════════════════════════
# FILTER BY STIPEND
# ════════════════════════════════════════════════════════════
def filter_stipend(internships):
    print(f"\n💰 Filtering Rs.{MIN_STIPEND}+/month (or unspecified)...")
    good = []
    for i in internships:
        s    = str(i.get("stipend", "")).lower().replace(",", "")
        nums = re.findall(r"\d+", s)
        if not nums or int(nums[0]) >= MIN_STIPEND:
            good.append(i)
    print(f"  ✅ {len(good)} passed filter")
    return good


# ════════════════════════════════════════════════════════════
# RANK INTERNSHIPS
# ════════════════════════════════════════════════════════════
def rank_internships(internships, seen, resume_text):
    print("\n🤖 Ollama is ranking the best ML Engineer internships...")

    internships = sorted(internships, key=score_internship, reverse=True)
    new_ones    = [i for i in internships if i["url"] not in seen]
    if not new_ones:
        return None, [], []

    listing = "\n".join([
        f"{n+1}. [{i['source']}] {i['title']} at {i['company']} | "
        f"Location: {i['location']} | Stipend: {i['stipend']} | "
        f"Skills: {i['skills']} | URL: {i['url']}"
        for n, i in enumerate(new_ones[:15])
    ])

    prompt = f"""
I am Adithya Vaddadi, a B.Tech AI/ML student targeting ML Engineer roles.
Skills: Python, TensorFlow, Scikit-learn, Pandas, LangGraph, Pinecone, RAG, NLP
Experience: ML Intern at Infosys Springboard (Dec 2025 - Feb 2026)
Projects: ClauseAI (multi-agent RAG), Food Classification (87% accuracy)
Target: ML Engineer / GenAI Engineer / LLM Engineer

Listings from 7 platforms (Internshala, LinkedIn, Indeed, Naukri, Wellfound, Unstop, HackerEarth):
{listing}

Please:
1. Pick TOP 3 best matches for my ML Engineer profile
   — Prioritize startups and product companies over service companies
2. For each give:
   - Platform + Role + Company + Location
   - Why it matches my skills (1-2 lines)
   - Stipend
   - Chance of getting it: High/Medium/Low with reason
   - Direct URL
3. Give 3 specific action tips to crack these applications THIS WEEK

Be direct, honest, and encouraging!
"""
    ranked_text = ask_ollama(prompt)
    return ranked_text, [i["url"] for i in new_ones[:3]], new_ones[:3]


# ════════════════════════════════════════════════════════════
# ATS RESUME CONTENT
# ════════════════════════════════════════════════════════════
def generate_resume_content(resume_text, job):
    print(f"\n📝 Tailoring ATS resume for {job['title']}...")
    prompt = f"""
You are an expert ATS resume optimizer for ML Engineer roles.

ORIGINAL RESUME:
{resume_text}

TARGET ROLE: {job['title']} at {job['company']}
REQUIRED SKILLS: {job['skills']}

Generate an ATS-optimized resume with EXACTLY these sections:

PROFESSIONAL SUMMARY:
3 sentences. Use exact keywords from the job title and required skills. Include a metric.

TECHNICAL SKILLS:
8-10 most relevant skills matching this specific role. Comma-separated.

EXPERIENCE:
ML Intern — Infosys Springboard | Dec 2025 - Feb 2026
3 bullet points. Each starts with action verb. Each includes a metric or outcome.
Focus bullets on skills matching this role.

KEY PROJECTS:
2 projects most relevant to this role.
Format: Project Name | Tech stack | One-line impact/result

CERTIFICATIONS:
Only certifications from original resume relevant to this role.

STRICT ATS RULES:
- Use exact keywords from job title and required skills naturally
- No tables, columns, graphics, special formatting
- Standard section headers only
- Every bullet starts with: Developed / Built / Implemented / Optimized / Deployed / Designed
- Do NOT invent skills or experience not in the original resume
"""
    return ask_ollama(prompt)


# ════════════════════════════════════════════════════════════
# COVER LETTER
# ════════════════════════════════════════════════════════════
def generate_cover_letter(resume_text, job):
    print(f"  ✉️  Writing cover letter...")
    prompt = f"""
Write a professional cover letter for this ML Engineer internship.

MY PROFILE:
Name: Adithya Vaddadi
Degree: B.Tech AI/ML, Sphoorthy Engineering College Hyderabad (2027), CGPA 7.4
Experience: ML Intern at Infosys Springboard (Dec 2025 - Feb 2026)
Skills: Python, TensorFlow, Scikit-learn, LangGraph, Pinecone, RAG, NLP
Projects: ClauseAI (multi-agent RAG system), Food Classification (87% accuracy)

ROLE: {job['title']} at {job['company']}
PLATFORM: {job['source']}
SKILLS NEEDED: {job['skills']}

Rules:
- Under 200 words
- Sound like a real student, not a template
- Mention 2 specific skills or projects matching this role
- Start with: Dear Hiring Manager,
- End with: Warm regards,\\nAdithya Vaddadi
- No clichés: avoid "passionate about", "team player", "quick learner"
- Show you understand what this role does
"""
    return ask_ollama(prompt)


# ════════════════════════════════════════════════════════════
# PDF CREATORS
# ════════════════════════════════════════════════════════════
def create_resume_pdf(content, job, path):
    print(f"  📄 Creating ATS resume PDF...")
    doc = SimpleDocTemplate(path, pagesize=A4,
        rightMargin=0.6*inch, leftMargin=0.6*inch,
        topMargin=0.55*inch, bottomMargin=0.55*inch)

    navy = colors.HexColor("#0d2b5c")
    dark = colors.HexColor("#191919")
    gray = colors.HexColor("#505050")
    story = []

    story.append(Paragraph("ADITHYA VADDADI",
        ParagraphStyle("N", fontSize=18, fontName="Helvetica-Bold",
        textColor=navy, alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph(
        "Hyderabad | adithyaadi104@gmail.com | +91-7075615349 | "
        "linkedin.com/in/adithya-vaddadi-536176330 | github.com/adithyavaddadi",
        ParagraphStyle("C", fontSize=8.5, fontName="Helvetica",
        textColor=gray, alignment=TA_CENTER, spaceAfter=5)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=navy, spaceAfter=3))
    story.append(Paragraph(
        f"Tailored for: {job['title']} at {job['company']} [{job['source']}] | {job['location']}",
        ParagraphStyle("T", fontSize=7.5, fontName="Helvetica-Oblique",
        textColor=gray, alignment=TA_CENTER, spaceAfter=7)))

    bod = ParagraphStyle("B", fontSize=9,  fontName="Helvetica",      textColor=dark, spaceAfter=2,  leading=13)
    bul = ParagraphStyle("U", fontSize=9,  fontName="Helvetica",      textColor=dark, spaceAfter=1,  leftIndent=10, leading=13)
    sec = ParagraphStyle("S", fontSize=10, fontName="Helvetica-Bold", textColor=dark, spaceBefore=7, spaceAfter=2)

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 2))
        elif line.isupper() or (line.endswith(":") and len(line) < 45):
            story.append(Paragraph(line.rstrip(":"), sec))
            story.append(HRFlowable(width="100%", thickness=0.4,
                color=colors.HexColor("#cccccc"), spaceAfter=2))
        elif line.startswith(("•", "-", "*")):
            story.append(Paragraph("• " + line.lstrip("•-* "), bul))
        else:
            story.append(Paragraph(line, bod))

    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=navy, spaceAfter=3))
    story.append(Paragraph("EDUCATION", sec))
    story.append(HRFlowable(width="100%", thickness=0.4,
        color=colors.HexColor("#cccccc"), spaceAfter=2))
    story.append(Paragraph("<b>B.Tech - Artificial Intelligence & Machine Learning</b> | May 2027", bod))
    story.append(Paragraph("Sphoorthy Engineering College, Hyderabad | CGPA: 7.4/10", bod))

    doc.build(story)
    print(f"  ✅ ATS Resume saved: {path}")


def create_cover_letter_pdf(cover_text, job, path):
    print(f"  ✉️  Creating cover letter PDF...")
    doc = SimpleDocTemplate(path, pagesize=A4,
        rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)

    navy = colors.HexColor("#0d2b5c")
    dark = colors.HexColor("#191919")
    gray = colors.HexColor("#666666")
    story = []

    story.append(Paragraph("ADITHYA VADDADI",
        ParagraphStyle("H", fontSize=16, fontName="Helvetica-Bold", textColor=navy, spaceAfter=2)))
    story.append(Paragraph(
        "adithyaadi104@gmail.com | +91-7075615349 | Hyderabad",
        ParagraphStyle("S", fontSize=9, fontName="Helvetica", textColor=gray, spaceAfter=12)))
    story.append(HRFlowable(width="100%", thickness=1.2, color=navy, spaceAfter=12))
    story.append(Paragraph(
        f"<b>Re: {job['title']} — {job['company']} [{job['source']}]</b>",
        ParagraphStyle("R", fontSize=10, fontName="Helvetica-Bold", textColor=dark, spaceAfter=12)))

    body_s = ParagraphStyle("B", fontSize=10, fontName="Helvetica",
        textColor=dark, leading=16, spaceAfter=8)
    for para in cover_text.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip().replace("\n", " "), body_s))

    doc.build(story)
    print(f"  ✅ Cover letter saved: {path}")


# ════════════════════════════════════════════════════════════
# SAVE COLD MESSAGE
# ════════════════════════════════════════════════════════════
def save_cold_message(cold_msg, hr_info, job, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"COLD MESSAGE — {job['title']} at {job['company']}\n")
        f.write("=" * 60 + "\n\n")
        f.write("📩 LINKEDIN MESSAGE TO SEND:\n")
        f.write("-" * 40 + "\n")
        f.write(cold_msg.strip() + "\n\n")
        f.write("=" * 60 + "\n")
        f.write("🔍 HOW TO FIND HR AT THIS COMPANY:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Company       : {hr_info['company']}\n")
        f.write(f"HR Search     : {hr_info['hr_search']}\n")
        f.write(f"Talent Search : {hr_info['talent_search']}\n")
        f.write(f"Founder/CTO   : {hr_info['founder_search']}\n\n")
        f.write("Look for people with these titles:\n")
        for role in hr_info["suggested_roles"]:
            f.write(f"  • {role}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("💡 OUTREACH STRATEGY:\n")
        f.write("-" * 40 + "\n")
        f.write("Step 1: Send connection request (no message yet)\n")
        f.write("Step 2: After they accept → send the cold message above\n")
        f.write("Step 3: No reply in 5 days → send ONE polite follow-up\n")
        f.write("Step 4: For startups → message the Founder/CTO directly\n")
        f.write("        (They respond faster than HR at small companies!)\n")
        f.write("\n⚠️  Personalize 1-2 lines per person — mention something\n")
        f.write("   specific about their company or recent work.\n")
    print(f"  ✅ Cold message saved: {path}")


# ════════════════════════════════════════════════════════════
# SAVE INTERVIEW PREP
# ════════════════════════════════════════════════════════════
def save_interview_prep(interview_text, job, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"INTERVIEW PREP — {job['title']} at {job['company']}\n")
        f.write("=" * 60 + "\n\n")
        f.write(interview_text.strip())
        f.write("\n\n" + "=" * 60 + "\n")
        f.write("💡 PRE-INTERVIEW CHECKLIST:\n")
        f.write("-" * 40 + "\n")
        f.write("  □ Research the company — what do they build? Who are their customers?\n")
        f.write("  □ Push latest code to GitHub\n")
        f.write("  □ Deploy ClauseAI or have a screen recording ready\n")
        f.write("  □ Practice 30-second intro out loud 5 times\n")
        f.write("  □ Prepare 2 questions to ask the interviewer\n")
        f.write("  □ Test internet, mic, camera 30 min before\n")
        f.write("\n💬 QUESTIONS TO ASK THEM:\n")
        f.write("-" * 40 + "\n")
        f.write("  • What does a typical week look like for the intern?\n")
        f.write("  • What ML stack does the team use?\n")
        f.write("  • What's the biggest technical challenge the team is solving?\n")
        f.write("  • Is there a full-time opportunity after graduation?\n")
    print(f"  ✅ Interview prep saved: {path}")


# ════════════════════════════════════════════════════════════
# SEND EMAIL
# ════════════════════════════════════════════════════════════
def send_email(job, ranked_text, resume_path, cover_path, cold_msg_path, interview_path):
    print(f"\n📧 Sending everything to your Gmail...")

    if not SENDER_APP_PASSWORD:
        print("  ❌ No app password found!")
        print("  💡 Add SENDER_APP_PASSWORD to your .env file")
        return

    msg            = MIMEMultipart()
    msg["Subject"] = f"🚀 ML Internship Alert — {job['title']} at {job['company']} [{job['source']}] | {job['location']}"
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL

    body = f"""
Hey Adithya! 👋

Your ML Engineer internship pipeline found fresh opportunities!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 TOP MATCH THIS RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Platform : {job['source']}
Role     : {job['title']}
Company  : {job['company']}
Location : {job.get('location', 'Check listing')}
Mode     : {job.get('mode', 'Check listing')}
Stipend  : {job.get('stipend', 'Not mentioned')}
Duration : {job.get('duration', 'N/A')}
Apply at : {job['url']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI TOP PICKS & ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{ranked_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📎 ATTACHED FILES (4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ATS-Optimized Resume PDF   → Upload directly to job portals
2. Custom Cover Letter PDF    → Attach to application
3. Cold Message + HR Finder   → Send on LinkedIn TODAY
4. Interview Prep Guide       → Study before every call

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ YOUR ACTION PLAN TODAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Apply to top match right now
2. Find HR on LinkedIn using the cold message file
3. Send 10 cold messages today using the template
4. Apply to remaining 2 AI picks before end of day

Apply within 24 hours — early applicants always win!
You got this Adithya! 💪

Platforms: Internshala + LinkedIn + Indeed + Naukri + Wellfound + Unstop + HackerEarth
Locations: Hyderabad + Remote + Bangalore
Powered by Ollama (Free Local AI) | Zero Cost | Rs.0 Forever
"""
    msg.attach(MIMEText(body, "plain"))

    for filepath in [resume_path, cover_path, cold_msg_path, interview_path]:
        if filepath and os.path.exists(filepath):
            with open(filepath, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition",
                    f"attachment; filename={os.path.basename(filepath)}")
                msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("  ✅ Email sent with all 4 attachments!")
    except Exception as e:
        print(f"  ❌ Email error: {e}")
        print("  💡 Fix: myaccount.google.com → Security → App Passwords → Generate")


# ════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 65)
    print("  ADITHYA'S ALL-IN-ONE INTERNSHIP PIPELINE v3.0")
    print(f"  Platforms  : Internshala + LinkedIn + Indeed + Naukri")
    print(f"               + Wellfound + Unstop + HackerEarth (7 total!)")
    print(f"  AI         : Ollama {OLLAMA_MODEL} (FREE!)")
    print(f"  Locations  : {' + '.join(LOCATIONS)}")
    print(f"  Stipend    : Rs.{MIN_STIPEND}+/month")
    print(f"  Target     : ML Engineer / GenAI / LLM Engineer")
    print(f"  Cost       : Rs.0 FOREVER!")
    print("=" * 65)

    # 1. Read resume
    resume_text = read_resume()

    # 2. Load seen internships
    seen = load_seen()

    # 3. Scrape all 7 platforms
    all_internships  = []
    all_internships += scrape_internshala()
    all_internships += scrape_linkedin()
    all_internships += scrape_indeed()
    all_internships += scrape_naukri()
    all_internships += scrape_wellfound()
    all_internships += scrape_unstop()
    all_internships += scrape_hackerearth()
    print(f"\n📊 Total found: {len(all_internships)}")

    # 4. Deduplicate
    all_internships = deduplicate(all_internships)

    # 5. Filter by stipend
    filtered = filter_stipend(all_internships)
    if not filtered:
        print("\n❌ No internships found. Try again later!")
        exit()

    # 6. AI ranks best matches
    ranked_text, new_urls, top_jobs = rank_internships(filtered, seen, resume_text)
    if not ranked_text:
        print("\n😴 No NEW internships since last run. Try tomorrow!")
        exit()

    print("\n" + "=" * 65)
    print("  🏆 AI TOP PICKS FOR ML ENGINEER:")
    print("=" * 65)
    print(ranked_text)

    # 7. Use top job for all tailored docs
    top_job = top_jobs[0]
    print(f"\n🎯 Tailoring docs for: {top_job['title']} at {top_job['company']} ({top_job['location']})")

    safe = re.sub(r"[^a-zA-Z0-9]", "_", top_job["company"])[:15]

    # 8. Generate all content via Ollama
    ats_content    = generate_resume_content(resume_text, top_job)
    cover_text     = generate_cover_letter(resume_text, top_job)
    cold_msg       = generate_cold_message(top_job)
    interview_text = prepare_interview(top_job)
    hr_info        = find_hr(top_job)

    # 9. File paths
    res_path       = f"Resume_Adithya_{safe}.pdf"
    cov_path       = f"CoverLetter_Adithya_{safe}.pdf"
    cold_path      = f"ColdMessage_Adithya_{safe}.txt"
    interview_path = f"InterviewPrep_Adithya_{safe}.txt"

    # 10. Create all files
    create_resume_pdf(ats_content, top_job, res_path)
    create_cover_letter_pdf(cover_text, top_job, cov_path)
    save_cold_message(cold_msg, hr_info, top_job, cold_path)
    save_interview_prep(interview_text, top_job, interview_path)

    # 11. Send email with all 4 attachments
    send_email(top_job, ranked_text, res_path, cov_path, cold_path, interview_path)

    # 12. Save seen URLs
    seen.update(new_urls)
    save_seen(seen)

    print("\n" + "=" * 65)
    print("  ✅ ALL DONE!")
    print(f"  ATS Resume      : {res_path}")
    print(f"  Cover Letter    : {cov_path}")
    print(f"  Cold Message    : {cold_path}")
    print(f"  Interview Prep  : {interview_path}")
    print(f"  Sent to         : {RECEIVER_EMAIL}")
    print(f"  Cost            : Rs.0!")
    print("=" * 65)
    print("\n  📅 Run again tomorrow for fresh internships!")
    print("  💡 Automate it — run daily at 9am:")
    print("     Linux/Mac: crontab -e  →  0 9 * * * python internship_pipeline.py")
    print("     Windows  : Task Scheduler → trigger daily at 9:00 AM")