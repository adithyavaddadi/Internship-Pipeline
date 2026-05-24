def find_hr(job: dict) -> dict:
    """Generates search links on LinkedIn to discover HR and decision-makers for a given job's company."""
    company = job.get("company", "Unknown")
    encoded_company = company.replace(" ", "+")
    
    return {
        "company": company,
        "hr_search": f"https://www.linkedin.com/search/results/people/?keywords=HR+Recruiter+{encoded_company}",
        "talent_search": f"https://www.linkedin.com/search/results/people/?keywords=Talent+Acquisition+{encoded_company}",
        "founder_search": f"https://www.linkedin.com/search/results/people/?keywords=Founder+CTO+{encoded_company}",
        "suggested_roles": ["HR Manager", "Technical Recruiter", "Talent Acquisition", "CTO", "Founder"],
    }
