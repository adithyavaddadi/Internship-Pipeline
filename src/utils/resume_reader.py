import pdfplumber
from src.config.settings import get_resume_path
from src.utils.logger import log_pdf, log_success, log_warning

DEFAULT_RESUME_PROFILE = """
Adithya Vaddadi | Hyderabad | adithyaadi104@gmail.com | +91-7075615349
B.Tech AI/ML — Sphoorthy Engineering College (2027) | CGPA: 7.4
ML Intern — Infosys Springboard (Dec 2025 - Feb 2026)
Skills: Python, TensorFlow, Scikit-learn, Pandas, LangGraph, Pinecone, RAG, NLP
Projects: ClauseAI (multi-agent RAG), Food Classification (87% accuracy)
Certifications: IBM AI (Coursera), HackerRank Python & Java
"""

def read_resume() -> str:
    """Reads the local resume PDF, extracting text with a fallback profile if unreadable."""
    resume_path = get_resume_path()
    log_pdf(f"Reading resume from: {resume_path}...")
    
    try:
        with pdfplumber.open(resume_path) as pdf:
            text = "".join(page.extract_text() or "" for page in pdf.pages)
        
        if not text.strip():
            raise ValueError("Extracted text is empty")
            
        log_success("Resume read successfully!")
        return text
        
    except Exception as e:
        log_warning(f"PDF read failed ({e}), using default B.Tech AI/ML profile...")
        return DEFAULT_RESUME_PROFILE
