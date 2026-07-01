import config
import base64
from pathlib import Path
from groq import Groq


class LLM:
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self._client = None
        self._model = None
        self._vision_model = "llama-3.2-90b-vision-preview"
        self._init_backend()

    def _init_backend(self):
        if self.provider == "groq":
            self._client = Groq(api_key=config.GROQ_API_KEY)
            self._model = config.GROQ_MODEL
            print(f"[LLM] Using Groq: {self._model}")
            print(f"[LLM] Vision model: {self._vision_model}")
        else:
            raise ValueError("Only groq supported")

    def chat(self, messages, temperature=0.7, max_tokens=512):
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()

    def chat_with_image(self, text, image_data, image_type="image/jpeg",
                        temperature=0.7, max_tokens=1024):
        """Chat with an image attached."""
        # Convert image to base64
        if isinstance(image_data, bytes):
            b64_image = base64.b64encode(image_data).decode('utf-8')
        else:
            b64_image = image_data

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text or "What's in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{image_type};base64,{b64_image}"
                        }
                    }
                ]
            }
        ]

        resp = self._client.chat.completions.create(
            model=self._vision_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()

    def chat_with_file(self, text, file_data, file_type="text/plain",
                       temperature=0.7, max_tokens=2048):
        """Chat with a text file attached."""
        # For text files, include the content directly
        try:
            content = file_data.decode('utf-8', errors='ignore')
        except:
            content = str(file_data)

        # Truncate if too long
        if len(content) > 50000:
            content = content[:50000] + "\n\n[File truncated...]"

        combined = f"{text or 'Please analyze this file:'}\n\n---FILE CONTENT---\n{content}\n---END FILE---"
        return self.chat(
            [{"role": "user", "content": combined}],
            temperature=temperature,
            max_tokens=max_tokens
        )
