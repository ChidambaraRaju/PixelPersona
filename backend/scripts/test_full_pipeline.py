#!/usr/bin/env python3
"""Debug script to trace the full pipeline including LLM response."""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pixelpersona.retrieval.rephraser import QueryRephraser
from pixelpersona.retrieval.retriever import PersonaRetriever
from pixelpersona.agents.persona_agent import PersonaAgent


async def trace_full_pipeline(persona_name: str, query: str):
    """Trace the full retrieval + response pipeline."""
    print("=" * 70)
    print("FULL PIPELINE TRACER")
    print("=" * 70)

    # Step 1: Original Query
    print(f"\n[1] ORIGINAL QUERY: {query}")

    # Step 2: Rephrase
    print("\n[2] REPHASING QUERY...")
    rephraser = QueryRephraser()
    rephrased = await rephraser.rephrase(query)
    print(f"    Rephrased: {rephrased}")

    # Step 3: Retrieve chunks
    print("\n[3] RETRIEVING CHUNKS FROM CHROMA...")
    retriever = PersonaRetriever()
    results = await retriever.retrieve(persona_name, query, top_k=5)

    print(f"    Retrieved {len(results)} chunks:")
    for i, r in enumerate(results, 1):
        src = r['metadata'].get('source_type', 'unknown')
        title = r['metadata'].get('title', 'unknown')
        content = r['content']
        print(f"    Chunk {i}: [{src}] {title} ({len(content)} chars)")

    # Step 4: Context formatting
    print("\n[4] CONTEXT FORMATTED FOR AGENT:")
    print("-" * 50)
    formatted = []
    for r in results:
        content = r.get("content", "")
        metadata = r.get("metadata", {})
        source = metadata.get("source_type", "unknown")
        formatted.append(f"Source: {source}\nContent: {content}")
    context = "\n\n---\n\n".join(formatted)
    # Show first 800 chars of context
    print(context[:800] + "..." if len(context) > 800 else context)

    # Step 5: Persona Agent Response
    print("\n\n[5] PERSONA AGENT RESPONSE:")
    print("-" * 50)

    # Get persona descriptions
    persona_descriptions = {
        "Albert Einstein": "German-born theoretical physicist who developed the theory of relativity",
        "Nikola Tesla": "Serbian-American inventor and engineer",
        "A. P. J. Abdul Kalam": "Indian aerospace scientist and politician",
        "Mahatma Gandhi": "Indian lawyer and anti-colonial nationalist"
    }
    desc = persona_descriptions.get(persona_name, "famous historical figure")

    agent = PersonaAgent(persona_name, desc)
    response = await agent.chat(query)

    print(response)

    print("\n" + "=" * 70)
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace full pipeline")
    parser.add_argument("persona_name", help="Name of the persona")
    parser.add_argument("query", help="Question to ask")
    args = parser.parse_args()

    asyncio.run(trace_full_pipeline(args.persona_name, args.query))
