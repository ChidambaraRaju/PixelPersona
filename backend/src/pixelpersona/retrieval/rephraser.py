"""Query rephrasing using GroqCloud llama-3.1-8b-instant."""
from langchain_groq import ChatGroq
from pixelpersona.config import GROQ_API_KEY, REPHRASER_MODEL, REPHRASER_SYSTEM_PROMPT

class QueryRephraser:
    """Rephrases user queries to improve retrieval."""

    def __init__(self):
        self.llm = ChatGroq(
            model=REPHRASER_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.3,
            max_tokens=100
        )
        self.system_prompt = REPHRASER_SYSTEM_PROMPT

    async def rephrase(self, query: str) -> str:
        """Rephrase a user query to improve semantic search retrieval."""
        response = await self.llm.ainvoke(
            f"{self.system_prompt}\n\nQuery: {query}"
        )
        return response.content.strip()