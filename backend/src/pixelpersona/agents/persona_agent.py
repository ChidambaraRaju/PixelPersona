"""LangGraph ReAct agent per persona with SummarizationMiddleware."""
from typing import List, Dict, Any, Optional
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from pixelpersona.retrieval.retriever import PersonaRetriever
from pixelpersona.config import (
    GROQ_API_KEY,
    GPT_OSS_MODEL,
    REPHRASER_MODEL,
    PERSONA_AGENT_PROMPT_TEMPLATE
)

@tool
def retrieve_context(query: str, persona: str) -> str:
    """Retrieve relevant context from Chroma for the given query and persona."""
    # Note: This tool is available to the agent but we also retrieve context
    # before calling the agent for better control
    return f"Context for '{query}' about {persona}"

class PersonaAgent:
    """ReAct agent for a specific persona with memory summarization."""

    def __init__(
        self,
        persona_name: str,
        persona_description: str = "famous historical figure"
    ):
        self.persona_name = persona_name
        self.persona_description = persona_description
        self.llm = ChatGroq(
            model=GPT_OSS_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.7,
            max_tokens=500
        )
        self.checkpointer = InMemorySaver()
        self.retriever = PersonaRetriever()
        self.agent = self._create_agent()

    def _create_agent(self):
        """Create a ReAct agent with SummarizationMiddleware for memory management."""
        prompt = PERSONA_AGENT_PROMPT_TEMPLATE.format(
            persona_name=self.persona_name,
            persona_description=self.persona_description,
            context="{context}"
        )

        # Summarization middleware to prevent context explosion
        # Uses smaller/faster model to summarize conversation history
        summarization_middleware = SummarizationMiddleware(
            model=ChatGroq(
                model=REPHRASER_MODEL,
                api_key=GROQ_API_KEY,
                temperature=0.3,
                max_tokens=200
            ),
            trigger=("tokens", 2500),  # Trigger when history exceeds 2500 tokens
            keep=("messages", 10)  # Keep last 10 messages after summarization
        )

        return create_agent(
            model=self.llm,
            tools=[retrieve_context],
            system_prompt=prompt,
            checkpointer=self.checkpointer,
            middleware=[summarization_middleware]
        )

    async def chat(self, query: str, thread_id: str = "default") -> str:
        """Chat with the persona agent."""
        config = {"configurable": {"thread_id": thread_id}}

        # First retrieve context
        context_results = await self.retriever.retrieve(
            persona_name=self.persona_name,
            query=query
        )

        context = "\n\n".join([
            f"- {r['content']}" for r in context_results
        ])

        # Format prompt with context
        prompt = PERSONA_AGENT_PROMPT_TEMPLATE.format(
            persona_name=self.persona_name,
            persona_description=self.persona_description,
            context=context
        )

        # Run agent
        response = await self.agent.ainvoke(
            {"messages": [("user", f"{prompt}\n\nUser: {query}")]},
            config=config
        )

        # Extract response
        return response["messages"][-1].content