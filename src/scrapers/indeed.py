import requests
from bs4 import BeautifulSoup
from src.config import settings
from src.scrapers.base import detect_work_mode
from src.utils.logger import log_scrape, log_warning, log_success

def scrape_indeed() -> list:
    """Scrapes Indeed India internships and appends static fallback entries."""
    log_scrape("[3/7] Scraping Indeed...")
    results = []
    
    searches = [
        ("machine+learning+engineer+intern", "Python, PyTorch, ML Pipelines"),
        ("llm+engineer+intern",              "Python, LangChain, RAG, LLMs"),
        ("mlops+intern",                     "Docker, MLflow, Python, FastAPI"),
        ("deep+learning+intern",             "Python, PyTorch, Neural Networks"),
        ("data+science+intern",              "Python, Pandas, SQL, Scikit-learn"),
    ]

    for query, skills in searches:
        for location in settings.LOCATIONS:
            try:
                url = f"https://in.indeed.com/jobs?q={query}&l={location}&fromage=7&jt=internship"
                resp = requests.get(url, headers=settings.HEADERS, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")

                for card in soup.select(".job_seen_beacon")[:2]:
                    title_elem = card.select_one(".jobTitle span")
                    company_elem = card.select_one(".companyName") or card.select_one(".company_name") or card.select_one("span[data-testid='company-name']")
                    loc_elem = card.select_one(".companyLocation") or card.select_one("div[data-testid='text-location']")
                    salary_elem = card.select_one(".salary-snippet-container") or card.select_one(".estimated-salary-container")
                    link_elem = card.select_one(".jcs-JobTitle")

                    if title_elem:
                        job_id = link_elem.get("data-jk", "") if link_elem else ""
                        loc_text = loc_elem.get_text(strip=True) if loc_elem else location
                        results.append({
                            "source": "Indeed",
                            "title": title_elem.get_text(strip=True),
                            "company": company_elem.get_text(strip=True) if company_elem else "Company",
                            "location": loc_text,
                            "mode": detect_work_mode(loc_text),
                            "stipend": salary_elem.get_text(strip=True) if salary_elem else "Check on Indeed",
                            "duration": "N/A",
                            "url": f"https://in.indeed.com/viewjob?jk={job_id}" if job_id else url,
                            "skills": skills,
                        })
            except Exception as e:
                log_warning(f"Indeed scraper error [{query}/{location}]: {e}")

    results += [
        {
            "source": "Indeed",
            "title": "ML Engineer Intern",
            "company": "Multiple Companies",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Check on Indeed",
            "duration": "N/A",
            "skills": "Python, PyTorch, ML Pipelines",
            "url": "https://in.indeed.com/jobs?q=machine+learning+engineer+intern&jt=internship"
        },
    ]

    log_success(f"Indeed finished: {len(results)} listings found.")
    return results
