#!/usr/bin/env python3
"""Direct chat with persona agent - shows ReAct pipeline with logging."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pixelpersona.agents.persona_agent import PersonaAgent


async def main():
    persona = "Nikola Tesla"
    desc = "Inventor and electrical engineer known for AC power systems"
    query = "What are you known for?"

    print("="*70)
    print("PERSONA AGENT - ReAct Pipeline Demo")
    print("="*70)
    print(f"\n[USER] {query}\n")

    agent = PersonaAgent(persona, desc)
    response = await agent.chat(query)

    print("\n" + "="*70)
    print("[AGENT RESPONSE]")
    print("="*70)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
