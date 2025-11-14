# -*- coding: utf-8 -*-
import os
import asyncio
import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai.types import Content, Part

def configure_api_key(api_key: str):
    """Configures the generative AI library and environment variable."""
    genai.configure(api_key=api_key)
    os.environ['GOOGLE_API_KEY'] = api_key
    print("✅ API Key configured successfully!")

async def run_agent_query(agent: Agent, query: str, session: Session, user_id: str, is_router: bool = False, verbose: bool = True):
    """Initializes a runner and executes a query for a given agent and session."""
    if verbose:
        print(f"\n🚀 Running query for agent: '{agent.name}' in session: '{session.id}'...")

    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name=agent.name
    )

    final_response = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=Content(parts=[Part(text=query)], role="user")
        ):
            if verbose and not is_router:
                print(f"EVENT: {event}")
            if event.is_final_response():
                final_response = event.content.parts[0].text
    except Exception as e:
        final_response = f"An error occurred: {e}"

    if verbose and not is_router:
     print("\n" + "-"*50)
     print("✅ Final Response:")
     print(final_response)
     print("-"*50 + "\n")

    return final_response

# --- Initialize our Session Service ---
session_service = InMemorySessionService()
my_user_id = "adk_adventurer_001"
