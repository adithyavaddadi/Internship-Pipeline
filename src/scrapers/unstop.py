import requests
from bs4 import BeautifulSoup
from src.config import settings
from src.scrapers.base import detect_work_mode
from src.utils.logger import log_scrape, log_warning, log_success

def scrape_unstop() -> list:
    """Scrapes internships from Unstop platform and appends static fallback entries."""
    log_scrape("[6/7] Scraping Unstop...")
    results = []
    
    searches = [
        ("machine-learning", "Python, ML, Scikit-learn"),
        ("data-science",     "Python, Pandas, SQL"),
        ("ai-ml",            "Python, TensorFlow, Deep Learning"),
    ]

    for slug, skills in searches:
        try:
            url = f"https://unstop.com/internships?search={slug}&opportunity=internship"
            resp = requests.get(url, headers=settings.HEADERS, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            for card in soup.select(".opportunity-card, div[class*='card']")[:2]:
                title_elem = card.select_one("h2, h3, .title, a[class*='title']")
                company_elem = card.select_one(".comp-name, .company, span[class*='company']")
                loc_elem = card.select_one(".location, span[class*='location']")
                link_elem = card.select_one("a[href*='/internship'], a[href*='/opportunity']")

                if title_elem:
                    loc_text = loc_elem.get_text(strip=True) if loc_elem else "India"
                    results.append({
                        "source": "Unstop",
                        "title": title_elem.get_text(strip=True),
                        "company": company_elem.get_text(strip=True) if company_elem else "Company",
                        "location": loc_text,
                        "mode": detect_work_mode(loc_text),
                        "stipend": "Check on Unstop",
                        "duration": "N/A",
                        "url": "https://unstop.com" + link_elem["href"] if link_elem and link_elem.get("href") else url,
                        "skills": skills,
                    })
        except Exception as e:
            log_warning(f"Unstop scraper error [{slug}]: {e}")

    results += [
        {
            "source": "Unstop",
            "title": "ML / AI Intern",
            "company": "Multiple Companies",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Check on Unstop",
            "duration": "N/A",
            "skills": "Python, ML, TensorFlow, Scikit-learn",
            "url": "https://unstop.com/internships?search=machine+learning&opportunity=internship"
        },
    ]

    log_success(f"Unstop finished: {len(results)} listings found.")
    return results
