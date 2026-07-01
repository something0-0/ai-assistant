import config
from groq import Groq

class LLM:
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        if self.provider == "groq":
            self._client = Groq(api_key=config.GROQ_API_KEY)
            self._model = config.GROQ_MODEL
            print(f"[LLM] Using Groq: {self._model}")
        else:
            raise ValueError("Only groq supported in this build")

    def chat(self, messages, temperature=0.7, max_tokens=512):
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
