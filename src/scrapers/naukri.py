import requests
from bs4 import BeautifulSoup
from src.config import settings
from src.scrapers.base import detect_work_mode
from src.utils.logger import log_scrape, log_warning, log_success

def scrape_naukri() -> list:
    """Scrapes Naukri India jobs and appends static fallback entries."""
    log_scrape("[4/7] Scraping Naukri...")
    results = []
    
    searches = [
        ("machine-learning-engineer",  "Python, ML, Scikit-learn, PyTorch"),
        ("llm-engineer",               "Python, LLMs, RAG, LangChain"),
        ("mlops-engineer",             "Docker, MLflow, Python, CI/CD"),
        ("deep-learning-engineer",     "Python, PyTorch, TensorFlow, CV"),
        ("data-scientist",             "Python, Pandas, SQL, Scikit-learn"),
    ]

    # Map locations to slugs
    locations = ["hyderabad", "remote", "bangalore"]

    for slug, skills in searches:
        for location in locations:
            try:
                url = f"https://www.naukri.com/{slug}-jobs-in-{location}?jobAge=7"
                resp = requests.get(url, headers=settings.HEADERS, timeout=12)
                soup = BeautifulSoup(resp.text, "html.parser")

                for card in soup.select("article.joblistingCard, .jobTuple, .job-tuple")[:2]:
                    title_elem = card.select_one(".title, .jobTitle, h2 a")
                    company_elem = card.select_one(".companyInfo a, .comp-name, .companyName")
                    loc_elem = card.select_one(".location, .loc, .jobLocation")
                    salary_elem = card.select_one(".salary, .sal")
                    link_elem = card.select_one("a.title, a.jobTitle, h2 a")

                    if title_elem:
                        loc_text = loc_elem.get_text(strip=True) if loc_elem else location.title()
                        results.append({
                            "source": "Naukri",
                            "title": title_elem.get_text(strip=True),
                            "company": company_elem.get_text(strip=True) if company_elem else "Company",
                            "location": loc_text,
                            "mode": detect_work_mode(loc_text),
                            "stipend": salary_elem.get_text(strip=True) if salary_elem else "Check on Naukri",
                            "duration": "N/A",
                            "url": link_elem["href"] if link_elem and link_elem.get("href") else url,
                            "skills": skills,
                        })
            except Exception as e:
                log_warning(f"Naukri scraper error [{slug}/{location}]: {e}")

    results += [
        {
            "source": "Naukri",
            "title": "Machine Learning Engineer Fresher",
            "company": "Multiple Companies",
            "location": "Hyderabad",
            "mode": "Not specified",
            "stipend": "Check on Naukri",
            "duration": "N/A",
            "skills": "Python, ML, PyTorch, Scikit-learn",
            "url": "https://www.naukri.com/machine-learning-engineer-jobs-in-hyderabad"
        },
        {
            "source": "Naukri",
            "title": "LLM / GenAI Engineer Fresher",
            "company": "Multiple Companies",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Check on Naukri",
            "duration": "N/A",
            "skills": "Python, LLMs, RAG, LangChain, Pinecone",
            "url": "https://www.naukri.com/llm-jobs"
        },
        {
            "source": "Naukri",
            "title": "Data Scientist Fresher",
            "company": "Multiple Companies",
            "location": "Bangalore",
            "mode": "Not specified",
            "stipend": "Check on Naukri",
            "duration": "N/A",
            "skills": "Python, SQL, Pandas, Scikit-learn, ML",
            "url": "https://www.naukri.com/data-scientist-jobs-in-bangalore"
        },
    ]

    log_success(f"Naukri finished: {len(results)} listings found.")
    return results
