"""AI personality loader."""
import json
from pathlib import Path
from config import PERSONALITY_FILE

DEFAULT = {
    "name": "Aria",
    "description": "A helpful AI assistant.",
    "system_prompt": "You are a helpful AI assistant.",
    "greeting": "Hello! How can I help?",
    "farewell": "Goodbye!",
    "traits": ["helpful"],
}

class Personality:
    def __init__(self, path=PERSONALITY_FILE):
        self.path = path
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return {**DEFAULT, **json.load(f)}
            except Exception:
                return DEFAULT
        return DEFAULT

    @property
    def system_prompt(self):
        return self.data["system_prompt"]

    @property
    def name(self):
        return self.data["name"]

    @property
    def greeting(self):
        return self.data["greeting"]

    @property
    def farewell(self):
        return self.data["farewell"]
