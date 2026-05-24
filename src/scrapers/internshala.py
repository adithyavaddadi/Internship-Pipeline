import requests
from bs4 import BeautifulSoup
from src.config import settings
from src.scrapers.base import detect_work_mode
from src.utils.logger import log_scrape, log_warning, log_success

def scrape_internshala() -> list:
    """Scrapes ML Engineer internships from Internshala and appends static mock data fallbacks."""
    log_scrape("[1/7] Scraping Internshala...")
    results = []

    for location in settings.LOCATIONS:
        # Limit to the top 5 ML engineer keywords
        for slug, skills in settings.ML_ENGINEER_KEYWORDS[:5]:
            try:
                url = f"https://internshala.com/internships/keywords-{slug},location-{location.lower()}"
                resp = requests.get(url, headers=settings.HEADERS, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")

                # Parse the top 2 cards for this category to prevent rate-limiting and bloating
                for card in soup.select(".individual_internship")[:2]:
                    title_elem = card.select_one(".profile a")
                    company_elem = card.select_one(".company_name a")
                    stipend_elem = card.select_one(".stipend")
                    duration_elem = card.select_one(".duration-mobile")
                    link_elem = card.select_one(".profile a")

                    results.append({
                        "source": "Internshala",
                        "title": title_elem.get_text(strip=True) if title_elem else f"{slug.replace('-', ' ').title()} Intern",
                        "company": company_elem.get_text(strip=True) if company_elem else "Unknown",
                        "location": location,
                        "mode": detect_work_mode(card.text),
                        "stipend": stipend_elem.get_text(strip=True) if stipend_elem else "Not mentioned",
                        "duration": duration_elem.get_text(strip=True) if duration_elem else "2-6 months",
                        "skills": skills,
                        "url": "https://internshala.com" + link_elem["href"] if link_elem else url,
                    })
            except Exception as e:
                log_warning(f"Internshala scraper error [{slug}/{location}]: {e}")

    # Retain the exact mock/static fallback listings requested by the user
    results += [
        {
            "source": "Internshala",
            "title": "Machine Learning Engineer Intern",
            "company": "Multiple Companies",
            "location": "Hyderabad",
            "mode": "Not specified",
            "stipend": "Rs.8,000-Rs.25,000/month",
            "duration": "2-6 months",
            "skills": "Python, PyTorch, Scikit-learn, ML Pipelines",
            "url": "https://internshala.com/internships/machine-learning-internship-in-hyderabad/"
        },
        {
            "source": "Internshala",
            "title": "Generative AI / LLM Intern",
            "company": "Multiple Companies",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Rs.10,000-Rs.30,000/month",
            "duration": "2-6 months",
            "skills": "Python, LangChain, RAG, LLMs, Pinecone",
            "url": "https://internshala.com/internships/artificial-intelligence-internship/"
        },
        {
            "source": "Internshala",
            "title": "MLOps Intern",
            "company": "Multiple Companies",
            "location": "Remote",
            "mode": "Remote",
            "stipend": "Rs.10,000-Rs.20,000/month",
            "duration": "2-6 months",
            "skills": "Docker, MLflow, Python, CI/CD, FastAPI",
            "url": "https://internshala.com/internships/keywords-mlops/"
        },
    ]

    log_success(f"Internshala finished: {len(results)} listings found.")
    return results
