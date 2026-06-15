"""Configuration loader."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Memory
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(DATA_DIR / "chroma"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Voice
TTS_RATE = int(os.getenv("TTS_RATE", "175"))
STT_ENGINE = os.getenv("STT_ENGINE", "whisper").lower()
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WAKE_WORD = os.getenv("WAKE_WORD", "hey assistant").lower()

# API
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_KEY = os.getenv("API_KEY", "change-this-secret")

PERSONALITY_FILE = DATA_DIR / "personality.json"
