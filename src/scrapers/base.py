def detect_work_mode(text: str) -> str:
    """Classifies the work mode of an internship based on keywords in the description or location text."""
    if not text:
        return "Not specified"
        
    text = text.lower()
    if "remote" in text or "work from home" in text:
        return "Remote"
    if "hybrid" in text:
        return "Hybrid"
    if "onsite" in text or "office" in text:
        return "Onsite"
    return "Not specified"
