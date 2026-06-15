"""In-memory conversation history."""
from collections import deque


class ConversationMemory:
    def __init__(self, max_turns=20):
        self.max_turns = max_turns
        self.history = deque(maxlen=max_turns * 2)

    def add(self, role, content):
        self.history.append({"role": role, "content": content})

    def get(self):
        return list(self.history)

    def clear(self):
        self.history.clear()
