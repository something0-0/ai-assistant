"""Unified LLM interface: OpenAI or local."""
import config

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class LLM:
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self._client = None
        self._init_backend()

    def _init_backend(self):
        if self.provider == "openai":
            if OpenAI is None:
                raise ImportError("openai not installed")
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY missing in .env")
            self._client = OpenAI(api_key=config.OPENAI_API_KEY)
        else:
            raise ValueError(f"Provider '{self.provider}' not supported in this build")

    def chat(self, messages, temperature=0.7, max_tokens=512):
        if self.provider == "openai":
            resp = self._client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()
        return "Error: No LLM provider configured."
