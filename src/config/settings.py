import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email Configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "adithyaadi104@gmail.com")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "adithyaadi104@gmail.com")

# LLM Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Scraping Preferences
LOCATIONS = ["Hyderabad", "Remote", "Bangalore"]
MIN_STIPEND = 5000

# ML/AI Keywords and Core Matching Config
ML_ENGINEER_KEYWORDS = [
    ("machine-learning-engineer",   "Python, PyTorch, Scikit-learn, ML Pipelines"),
    ("llm-engineer",                "Python, LangChain, LangGraph, RAG, LLMs"),
    ("generative-ai",               "Python, LLMs, RAG, Pinecone, LangGraph"),
    ("mlops",                       "Docker, MLflow, CI/CD, Python, FastAPI"),
    ("deep-learning",               "Python, PyTorch, Neural Networks, GPU"),
    ("nlp-engineer",                "Python, NLP, Transformers, HuggingFace"),
    ("machine-learning",            "Python, ML, Scikit-learn, TensorFlow"),
    ("artificial-intelligence",     "Python, TensorFlow, PyTorch, Deep Learning"),
    ("computer-vision",             "Python, OpenCV, PyTorch, Deep Learning"),
    ("data-science",                "Python, Pandas, SQL, Scikit-learn"),
]

# Standard request headers to emulate a browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Directories setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# Ensure required directories exist
for directory in [DATA_DIR, OUTPUTS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# File Paths (with root fallback logic)
def get_resume_path() -> str:
    """Gets the path to the resume, checking data/ and falling back to root."""
    data_path = os.path.join(DATA_DIR, "resume.pdf")
    root_path = os.path.join(PROJECT_ROOT, "resume.pdf")
    if os.path.exists(data_path):
        return data_path
    if os.path.exists(root_path):
        return root_path
    return data_path  # Default to data/ if none exists yet

def get_seen_file_path() -> str:
    """Gets the path to the seen tracking file, checking data/ and falling back to root."""
    data_path = os.path.join(DATA_DIR, "seen_internships.json")
    root_path = os.path.join(PROJECT_ROOT, "seen_internships.json")
    if os.path.exists(data_path):
        return data_path
    if os.path.exists(root_path):
        return root_path
    return data_path  # Default to data/ if none exists yet
