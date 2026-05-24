import requests
from bs4 import BeautifulSoup
from src.config import settings
from src.scrapers.base import detect_work_mode
from src.utils.logger import log_scrape, log_warning, log_success

def scrape_linkedin() -> list:
    """Scrapes public LinkedIn internship posts and appends static fallback entries."""
    log_scrape("[2/7] Scraping LinkedIn Jobs...")
    results = []
    
    searches = [
        ("machine learning engineer intern", "Python, PyTorch, ML Pipelines"),
        ("llm engineer intern",              "Python, LangChain, RAG, LLMs"),
        ("generative ai intern",             "Python, LLMs, RAG, LangGraph"),
        ("mlops intern",                     "Docker, MLflow, Python, FastAPI"),
        ("deep learning intern",             "Python, PyTorch, Neural Networks"),
    ]

    for query, skills in searches:
        for location in settings.LOCATIONS:
            try:
                encoded = requests.utils.quote(query)
                enc_loc = requests.utils.quote(location)
                # Filter f_JT=I (internship) and f_TPR=r604800 (past week)
                url = f"https://www.linkedin.com/jobs/search/?keywords={encoded}&location={enc_loc}&f_JT=I&f_TPR=r604800"
                
                resp = requests.get(url, headers=settings.HEADERS, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")

                for card in soup.select(".base-card")[:2]:
                    title_elem = card.select_one(".base-search-card__title")
                    company_elem = card.select_one(".base-search-card__subtitle")
                    loc_elem = card.select_one(".job-search-card__location")
                    link_elem = card.select_one("a.base-card__full-link")

                    if title_elem:
                        loc_text = loc_elem.get_text(strip=True) if loc_elem else location
                        results.append({
                            "source": "LinkedIn",
                            "title": title_elem.get_text(strip=True),
                            "company": company_elem.get_text(strip=True) if company_elem else "Company",
                            "location": loc_text,
                            "mode": detect_work_mode(loc_text),
                            "stipend": "Check on LinkedIn",
                            "duration": "N/A",
                            "url": link_elem["href"].split("?")[0] if link_elem and link_elem.get("href") else url,
                            "skills": skills,
                        })
            except Exception as e:
                log_warning(f"LinkedIn scraper error [{query}/{location}]: {e}")

    # Legacy mock lists to be 100% stable during demonstration
    results += [
        {
            "source": "LinkedIn",
            "title": "ML Engineer Intern",
            "company": "Search Results",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Check on LinkedIn",
            "duration": "N/A",
            "skills": "Python, PyTorch, ML Pipelines, Scikit-learn",
            "url": "https://www.linkedin.com/jobs/search/?keywords=ml+engineer+intern&f_JT=I"
        },
        {
            "source": "LinkedIn",
            "title": "Generative AI Intern",
            "company": "Search Results",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Check on LinkedIn",
            "duration": "N/A",
            "skills": "Python, LLMs, RAG, LangGraph, Pinecone",
            "url": "https://www.linkedin.com/jobs/search/?keywords=generative+ai+intern&f_JT=I"
        },
    ]

    log_success(f"LinkedIn finished: {len(results)} listings found.")
    return results
