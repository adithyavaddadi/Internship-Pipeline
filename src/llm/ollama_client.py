import ollama
from src.config import settings
from src.scoring.scorer import score_internship
from src.utils.logger import log_ai, log_warning, log_info, log_msg

def ask_ollama(prompt: str) -> str:
    """Interacts with the local running Ollama instance, sending the prompt to the selected model."""
    try:
        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        log_warning(f"Ollama connection error: {e}")
        log_info("Troubleshooting: Ensure Ollama is running in the background. Command: 'ollama serve'")
        return "Ollama not available — please check if it's running."

def rank_internships(internships: list, seen_urls: set, resume_text: str) -> tuple:
    """Uses Ollama to compare all fresh listings and select the top 3 matches for Adithya's resume profile."""
    log_ai("Ollama is ranking the best ML Engineer internships...")

    # Sort all internships using score_internship
    sorted_internships = sorted(internships, key=score_internship, reverse=True)
    
    # Filter for new ones that haven't been applied to / seen yet
    new_ones = [item for item in sorted_internships if item["url"] not in seen_urls]
    if not new_ones:
        return None, [], []

    # Compile the top 15 candidates into a text block to feed into the prompt
    listing_summary = "\n".join([
        f"{idx+1}. [{item['source']}] {item['title']} at {item['company']} | "
        f"Location: {item['location']} | Stipend: {item['stipend']} | "
        f"Skills: {item['skills']} | URL: {item['url']}"
        for idx, item in enumerate(new_ones[:15])
    ])

    prompt = f"""
I am Adithya Vaddadi, a B.Tech AI/ML student targeting ML Engineer roles.
Skills: Python, TensorFlow, Scikit-learn, Pandas, LangGraph, Pinecone, RAG, NLP
Experience: ML Intern at Infosys Springboard (Dec 2025 - Feb 2026)
Projects: ClauseAI (multi-agent RAG), Food Classification (87% accuracy)
Target: ML Engineer / GenAI Engineer / LLM Engineer

Listings from 7 platforms (Internshala, LinkedIn, Indeed, Naukri, Wellfound, Unstop, HackerEarth):
{listing_summary}

Please:
1. Pick TOP 3 best matches for my ML Engineer profile
   — Prioritize startups and product companies over service companies
2. For each give:
   - Platform + Role + Company + Location
   - Why it matches my skills (1-2 lines)
   - Stipend
   - Chance of getting it: High/Medium/Low with reason
   - Direct URL
3. Give 3 specific action tips to crack these applications THIS WEEK

Be direct, honest, and encouraging!
"""
    ranked_text = ask_ollama(prompt)
    
    # Return: formatted ranked text, top 3 URLs, and the top 3 dictionary objects
    return ranked_text, [item["url"] for item in new_ones[:3]], new_ones[:3]

def generate_resume_content(resume_text: str, job: dict) -> str:
    """Prompts Ollama to output single-page tailored ATS optimization bullet points for the resume."""
    log_ai(f"Tailoring ATS resume for {job.get('title', 'Target Role')} at {job.get('company', 'Target Company')}...")
    
    prompt = f"""
You are an expert ATS resume optimizer for ML Engineer roles.

ORIGINAL RESUME:
{resume_text}

TARGET ROLE: {job.get('title', '')} at {job.get('company', '')}
REQUIRED SKILLS: {job.get('skills', '')}

Generate an ATS-optimized resume with EXACTLY these sections:

PROFESSIONAL SUMMARY:
3 sentences. Use exact keywords from the job title and required skills. Include a metric.

TECHNICAL SKILLS:
8-10 most relevant skills matching this specific role. Comma-separated.

EXPERIENCE:
ML Intern — Infosys Springboard | Dec 2025 - Feb 2026
3 bullet points. Each starts with action verb. Each includes a metric or outcome.
Focus bullets on skills matching this role.

KEY PROJECTS:
2 projects most relevant to this role.
Format: Project Name | Tech stack | One-line impact/result

CERTIFICATIONS:
Only certifications from original resume relevant to this role.

STRICT ATS RULES:
- Use exact keywords from job title and required skills naturally
- No tables, columns, graphics, special formatting
- Standard section headers only
- Every bullet starts with: Developed / Built / Implemented / Optimized / Deployed / Designed
- Do NOT invent skills or experience not in the original resume
"""
    return ask_ollama(prompt)

def generate_cover_letter(resume_text: str, job: dict) -> str:
    """Prompts Ollama to write a personalized, high-conviction cover letter for the job opportunity."""
    log_msg(f"Writing tailored cover letter for {job.get('title', '')}...")
    
    prompt = f"""
Write a professional cover letter for this ML Engineer internship.

MY PROFILE:
Name: Adithya Vaddadi
Degree: B.Tech AI/ML, Sphoorthy Engineering College Hyderabad (2027), CGPA 7.4
Experience: ML Intern at Infosys Springboard (Dec 2025 - Feb 2026)
Skills: Python, TensorFlow, Scikit-learn, LangGraph, Pinecone, RAG, NLP
Projects: ClauseAI (multi-agent RAG system), Food Classification (87% accuracy)

ROLE: {job.get('title', '')} at {job.get('company', '')}
PLATFORM: {job.get('source', '')}
SKILLS NEEDED: {job.get('skills', '')}

Rules:
- Under 200 words
- Sound like a real student, not a template
- Mention 2 specific skills or projects matching this role
- Start with: Dear Hiring Manager,
- End with: Warm regards,\nAdithya Vaddadi
- No clichés: avoid "passionate about", "team player", "quick learner"
- Show you understand what this role does
"""
    return ask_ollama(prompt)

def generate_cold_message(job: dict) -> str:
    """Prompts Ollama to formulate a short, non-templated LinkedIn outreach message to send to recruiters."""
    log_msg(f"Writing custom cold message for {job.get('title', '')} at {job.get('company', '')}...")
    
    prompt = f"""
Write a short LinkedIn cold message from a student to a recruiter at {job.get('company', '')}.

Student profile:
- Name: Adithya Vaddadi
- Degree: B.Tech AI/ML (2027), Hyderabad
- Experience: ML Intern at Infosys Springboard
- Key project: ClauseAI (multi-agent RAG system using LangGraph + Pinecone)
- Skills: Python, Machine Learning, TensorFlow, LangGraph, RAG, NLP

Role applying for: {job.get('title', '')} at {job.get('company', '')}

Rules:
- Under 80 words
- Friendly and professional tone
- Mention ClauseAI briefly with one concrete detail
- End with a polite ask for consideration
- Do NOT use "I hope this message finds you well"
- Do NOT use "passionate about"
- Sound human, not templated

Output ONLY the message text, nothing else.
"""
    return ask_ollama(prompt)

def prepare_interview(job: dict) -> str:
    """Prompts Ollama to generate a structured technical/behavioral interview preparation cheat sheet."""
    log_ai(f"Preparing targeted interview prep material for {job.get('title', '')}...")
    
    prompt = f"""
Generate targeted interview preparation for this ML Engineer internship.

Role: {job.get('title', '')}
Company: {job.get('company', '')}
Required Skills: {job.get('skills', '')}

Provide:
1. 5 technical questions with brief model answers
2. 2 Python coding questions (describe problem + approach, no full code)
3. 2 machine learning theory questions with model answers
4. 1 behavioral question about Adithya's ClauseAI RAG project
5. A 30-second elevator pitch for Adithya to introduce himself

Be specific and practical. Focus on ML Engineer skills.
"""
    return ask_ollama(prompt)
