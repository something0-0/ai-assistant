"""Main AI Assistant that ties everything together."""
from core.llm import LLM
from core.personality import Personality
from memory.vector_store import VectorMemory
from memory.conversation import ConversationMemory


class AIAssistant:
    def __init__(self):
        print("[Assistant] Booting...")
        self.personality = Personality()
        self.llm = LLM()
        self.long_term = VectorMemory()
        self.short_term = ConversationMemory()
        print(f"[Assistant] Ready. I'm {self.personality.name}.")

    def ask(self, user_message, use_memory=True):
        recalled = []
        if use_memory:
            recalled = self.long_term.query(user_message, n_results=3)

        messages = [{"role": "system", "content": self.personality.system_prompt}]
        if recalled:
            context = "\n".join(f"- {m}" for m in recalled)
            messages.append({"role": "system",
                             "content": f"Relevant past context:\n{context}"})
        messages.extend(self.short_term.get())
        messages.append({"role": "user", "content": user_message})

        reply = self.llm.chat(messages)

        self.short_term.add("user", user_message)
        self.short_term.add("assistant", reply)
        return reply

    def remember(self, fact):
        return self.long_term.add(fact, metadata={"type": "fact"})

    def recall(self, query, n=5):
        return self.long_term.query(query, n_results=n)

    def clear_memory(self, scope="short"):
        if scope in ("short", "all"):
            self.short_term.clear()
        if scope in ("long", "all"):
            self.long_term.clear()

    def status(self):
        return {
            "name": self.personality.name,
            "llm_provider": self.llm.provider,
            "short_term_messages": len(self.short_term.get()),
            "long_term_memories": self.long_term.count(),
        }
