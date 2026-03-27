#!/usr/bin/env python3
"""Debug script to trace the full retrieval pipeline for a persona."""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pixelpersona.retrieval.rephraser import QueryRephraser
from pixelpersona.retrieval.retriever import PersonaRetriever
from pixelpersona.storage.chroma_client import ChromaCollectionManager
from pixelpersona.processing.embedder import LocalEmbedder


async def trace_retrieval(persona_name: str, query: str):
    """Trace the retrieval pipeline and print all steps."""
    print("=" * 60)
    print("RETRIEVAL PIPELINE TRACER")
    print("=" * 60)
    print(f"\n[1] ORIGINAL QUERY: {query}")

    # Step 1: Rephrase
    print("\n[2] REPHASING QUERY...")
    rephraser = QueryRephraser()
    rephrased = await rephraser.rephrase(query)
    print(f"    Rephrased query: {rephrased}")

    # Step 2: Retrieve chunks
    print("\n[3] RETRIEVING CHUNKS FROM CHROMA...")
    retriever = PersonaRetriever()
    results = await retriever.retrieve(persona_name, query, top_k=5)

    print(f"    Found {len(results)} chunks:\n")
    for i, r in enumerate(results, 1):
        print(f"  --- Chunk {i} ---")
        print(f"  Source: {r['metadata'].get('source_type', 'unknown')}")
        print(f"  Title: {r['metadata'].get('title', 'unknown')}")
        content = r['content']
        print(f"  Content preview ({len(content)} chars): {content[:300]}...")
        print()

    # Step 3: Show what the persona agent would see
    print("\n[4] CONTEXT PROVIDED TO PERSONA AGENT:")
    print("-" * 40)
    formatted = []
    for r in results:
        content = r.get("content", "")
        metadata = r.get("metadata", {})
        source = metadata.get("source_type", "unknown")
        formatted.append(f"Source: {source}\nContent: {content}")
    context = "\n\n---\n\n".join(formatted)
    print(context[:1500] + "..." if len(context) > 1500 else context)

    print("\n" + "=" * 60)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace retrieval pipeline")
    parser.add_argument("persona_name", help="Name of the persona")
    parser.add_argument("query", help="Question to trace")
    args = parser.parse_args()

    asyncio.run(trace_retrieval(args.persona_name, args.query))
