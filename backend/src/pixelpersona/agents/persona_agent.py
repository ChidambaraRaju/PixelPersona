"""LangGraph ReAct agent per persona with SummarizationMiddleware."""
from typing import List, Dict, Any
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from pixelpersona.retrieval.retriever import PersonaRetriever
from pixelpersona.config import (
    GROQ_API_KEY,
    GPT_OSS_MODEL,
    REPHRASER_MODEL,
    PERSONA_AGENT_PROMPT_TEMPLATE
)

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

    def _create_retrieval_tool(self):
        """Create a retrieval tool that queries Chroma for the persona."""

        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str) -> str:
            """Retrieve relevant context about the persona from the knowledge base.

            Use this tool to find relevant information from Wikipedia, Wikiquotes,
            and other sources about the persona before answering questions.

            Args:
                query: A search query to find relevant context about the persona.
                       Include specific names, concepts, or topics you want to look up.

            Returns:
                A string containing the retrieved context with source information.
                If no relevant context is found, returns a message indicating that.
            """
            import asyncio

            # Run the async retriever in sync context
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            results = loop.run_until_complete(
                self.retriever.retrieve(
                    persona_name=self.persona_name,
                    query=query,
                    top_k=5
                )
            )

            if not results:
                return "No relevant context found for this query."

            # Format context with sources
            formatted = []
            for r in results:
                content = r.get("content", "")
                metadata = r.get("metadata", {})
                source = metadata.get("source_type", "unknown")
                formatted.append(f"Source: {source}\nContent: {content}")

            return "\n\n---\n\n".join(formatted)

        return retrieve_context

    def _create_agent(self):
        """Create a ReAct agent with retrieval tool and SummarizationMiddleware."""

        # System prompt instructing the agent to use retrieval
        system_prompt = f"""You are {self.persona_name}, {self.persona_description}.

You have access to a retrieval tool that searches a knowledge base containing
information about this persona from Wikipedia, Wikiquotes, and other sources.

IMPORTANT: Before answering questions about this persona's life, work, views,
or any factual information, ALWAYS use the retrieve_context tool to get
relevant information from the knowledge base.

Your response must:
1. Use the retrieve_context tool to find relevant information first
2. Be grounded ONLY in the provided context from the retrieval tool
3. Match {self.persona_name}'s tone, style, and knowledge
4. Never fabricate facts outside the provided context
5. If the context doesn't contain enough information, say so clearly

Remember: Always use retrieve_context to find information before answering."""

        # Create the retrieval tool
        retrieval_tool = self._create_retrieval_tool()

        # Summarization middleware to prevent context explosion
        summarization_middleware = SummarizationMiddleware(
            model=ChatGroq(
                model=REPHRASER_MODEL,
                api_key=GROQ_API_KEY,
                temperature=0.3,
                max_tokens=200
            ),
            trigger=("tokens", 2500),
            keep=("messages", 10)
        )

        return create_agent(
            model=self.llm,
            tools=[retrieval_tool],
            system_prompt=system_prompt,
            checkpointer=self.checkpointer,
            middleware=[summarization_middleware]
        )

    async def chat(self, query: str, thread_id: str = "default") -> str:
        """Chat with the persona agent."""
        config = {"configurable": {"thread_id": thread_id}}

        # Run agent - it will use retrieve_context tool as needed
        response = await self.agent.ainvoke(
            {"messages": [("user", query)]},
            config=config
        )

        # Extract response
        return response["messages"][-1].content