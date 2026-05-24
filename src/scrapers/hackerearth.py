import requests
from bs4 import BeautifulSoup
from src.config import settings
from src.scrapers.base import detect_work_mode
from src.utils.logger import log_scrape, log_warning, log_success

def scrape_hackerearth() -> list:
    """Scrapes internships from HackerEarth Jobs filter page and appends static fallback entries."""
    log_scrape("[7/7] Scraping HackerEarth Jobs...")
    results = []

    try:
        url = "https://www.hackerearth.com/jobs/filter/?role=machine-learning-engineer&location=remote&location=hyderabad&location=bangalore"
        resp = requests.get(url, headers=settings.HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        for card in soup.select(".job-card, div[class*='job']")[:5]:
            title_elem = card.select_one("h2, h3, .job-title, a[class*='title']")
            company_elem = card.select_one(".company-name, .company")
            loc_elem = card.select_one(".location, .job-location")
            link_elem = card.select_one("a[href*='/jobs/']")

            if title_elem:
                loc_text = loc_elem.get_text(strip=True) if loc_elem else "Remote"
                results.append({
                    "source": "HackerEarth",
                    "title": title_elem.get_text(strip=True),
                    "company": company_elem.get_text(strip=True) if company_elem else "Company",
                    "location": loc_text,
                    "mode": detect_work_mode(loc_text),
                    "stipend": "Check on HackerEarth",
                    "duration": "N/A",
                    "url": "https://www.hackerearth.com" + link_elem["href"] if link_elem and link_elem.get("href") else url,
                    "skills": "Python, ML, Data Science",
                })
    except Exception as e:
        log_warning(f"HackerEarth scraper error: {e}")

    results += [
        {
            "source": "HackerEarth",
            "title": "ML Engineer / Data Scientist",
            "company": "Multiple Companies",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Check on HackerEarth",
            "duration": "N/A",
            "skills": "Python, ML, PyTorch, SQL",
            "url": "https://www.hackerearth.com/jobs/filter/?role=machine-learning-engineer"
        },
    ]

    log_success(f"HackerEarth finished: {len(results)} listings found.")
    return results
