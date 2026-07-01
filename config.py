import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# LLM Provider - hardcoded Groq
LLM_PROVIDER = "groq"
GROQ_API_KEY = "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"
GROQ_MODEL = "llama-3.1-8b-instant"

# Memory
CHROMA_PERSIST_DIR = str(DATA_DIR / "chroma")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# API Server
API_HOST = "0.0.0.0"
API_PORT = 8000

# Personality
PERSONALITY_FILE = DATA_DIR / "personality.json"
