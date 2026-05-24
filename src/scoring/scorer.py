import re
from src.config.settings import MIN_STIPEND
from src.utils.logger import log_success, log_info

def score_internship(job: dict) -> int:
    """Calculates matching scores for internships based on ML/AI engineer target keywords."""
    score = 0
    title = job.get("title", "").lower()
    skills = job.get("skills", "").lower()
    mode = job.get("mode", job.get("location", "")).lower()
    location = job.get("location", "").lower()
    source = job.get("source", "").lower()

    # Job Title Keywords Scoring
    if "ml engineer" in title:
        score += 10
    if "machine learning" in title:
        score += 8
    if "llm" in title:
        score += 8
    if "generative ai" in title:
        score += 8
    if "mlops" in title:
        score += 7
    if "deep learning" in title:
        score += 6
    if "nlp" in title:
        score += 6
    if "computer vision" in title:
        score += 6
    if "ai engineer" in title:
        score += 6
    if "data science" in title:
        score += 4

    # Technical Skills Keywords Scoring
    if "pytorch" in skills:
        score += 4
    if "langchain" in skills:
        score += 4
    if "langgraph" in skills:
        score += 4
    if "rag" in skills:
        score += 4
    if "mlflow" in skills:
        score += 3
    if "docker" in skills:
        score += 3
    if "python" in skills:
        score += 2

    # Location / Work Mode Compatibility Scoring
    if "remote" in mode:
        score += 3
    if "hyderabad" in location:
        score += 2
    if "bangalore" in location:
        score += 2

    # Platform/Sourcing Specific Bonus
    if "wellfound" in source:
        score += 3

    return score

def deduplicate(internships: list) -> list:
    """Filters duplicate listings using combined (title + company) unique keys."""
    seen_keys = set()
    unique = []
    
    for item in internships:
        title_norm = item.get("title", "").lower().strip()
        company_norm = item.get("company", "").lower().strip()
        key = f"{title_norm}|{company_norm}"
        
        if key not in seen_keys:
            seen_keys.add(key)
            unique.append(item)
            
    log_success(f"Deduplication completed: {len(unique)} unique listings remain out of {len(internships)}")
    return unique

def filter_stipend(internships: list) -> list:
    """Filters listings ensuring stipend matches minimum expectations, or allows unstated stipends."""
    log_info(f"Filtering internships for stipend >= Rs.{MIN_STIPEND}/month (unspecified are allowed)...")
    passed_filters = []
    
    for item in internships:
        stipend_raw = str(item.get("stipend", "")).lower().replace(",", "")
        numbers = re.findall(r"\d+", stipend_raw)
        
        if not numbers or int(numbers[0]) >= MIN_STIPEND:
            passed_filters.append(item)
            
    log_success(f"{len(passed_filters)} listings passed stipend filter.")
    return passed_filters
