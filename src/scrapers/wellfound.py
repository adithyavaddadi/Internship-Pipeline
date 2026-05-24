import requests
from bs4 import BeautifulSoup
from src.config import settings
from src.scrapers.base import detect_work_mode
from src.utils.logger import log_scrape, log_warning, log_success

def scrape_wellfound() -> list:
    """Scrapes startup internships from Wellfound (AngelList) and appends static fallback entries."""
    log_scrape("[5/7] Scraping Wellfound (AngelList)...")
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
            url = f"https://wellfound.com/role/r/{slug}"
            resp = requests.get(url, headers=settings.HEADERS, timeout=12)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Parse top 3 results for startups
            for card in soup.select("div[class*='JobListingCard'], div[class*='styles_component']")[:3]:
                title_elem = card.select_one("a[class*='jobTitle'], h2, h3")
                company_elem = card.select_one("a[class*='company'], span[class*='company']")
                loc_elem = card.select_one("span[class*='location'], div[class*='location']")
                link_elem = card.select_one("a[href*='/jobs/']")

                if title_elem:
                    loc_text = loc_elem.get_text(strip=True) if loc_elem else "Remote"
                    results.append({
                        "source": "Wellfound",
                        "title": title_elem.get_text(strip=True),
                        "company": company_elem.get_text(strip=True) if company_elem else "Startup",
                        "location": loc_text,
                        "mode": detect_work_mode(loc_text),
                        "stipend": "Check on Wellfound",
                        "duration": "N/A",
                        "url": "https://wellfound.com" + link_elem["href"] if link_elem and link_elem.get("href") else url,
                        "skills": skills,
                    })
        except Exception as e:
            log_warning(f"Wellfound scraper error [{slug}]: {e}")

    results += [
        {
            "source": "Wellfound",
            "title": "ML Engineer Intern (Startup)",
            "company": "AI Startups",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Check on Wellfound",
            "duration": "3-6 months",
            "skills": "Python, PyTorch, ML, LLMs, FastAPI",
            "url": "https://wellfound.com/role/r/machine-learning-engineer"
        },
        {
            "source": "Wellfound",
            "title": "LLM / RAG Engineer Intern",
            "company": "AI Startups",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Check on Wellfound",
            "duration": "3-6 months",
            "skills": "Python, LangChain, RAG, Pinecone, LangGraph",
            "url": "https://wellfound.com/role/r/llm"
        },
        {
            "source": "Wellfound",
            "title": "Generative AI Intern",
            "company": "AI Startups",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Check on Wellfound",
            "duration": "3-6 months",
            "skills": "Python, LLMs, RAG, Prompt Engineering, LangGraph",
            "url": "https://wellfound.com/role/r/generative-ai"
        },
    ]

    log_success(f"Wellfound finished: {len(results)} listings found.")
    return results
