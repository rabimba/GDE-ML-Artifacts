# -*- coding: utf-8 -*-
import argparse
import asyncio
import re
from core import configure_api_key, run_agent_query, session_service, my_user_id
from agents import router_agent_ultimate, worker_agents, foodie_agent, transportation_agent

async def main():
    parser = argparse.ArgumentParser(description="Run the ADK Learning Tool from the command line.")
    parser.add_argument("--api-key", required=True, help="Your Google API Key.")
    parser.add_argument("--query", required=True, help="The query to send to the agent.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()

    configure_api_key(args.api_key)

    query = args.query
    print(f"\n{'='*60}\n🗣️ Processing New Query: '{query}'\n{'='*60}")

    # 1. Ask the Router Agent to choose the right agent or workflow
    router_session = await session_service.create_session(app_name=router_agent_ultimate.name, user_id=my_user_id)
    if args.verbose:
        print("🧠 Asking the router agent to make a decision...")
    chosen_route = await run_agent_query(router_agent_ultimate, query, router_session, my_user_id, is_router=True, verbose=args.verbose)
    chosen_route = chosen_route.strip().replace("'", "")
    if args.verbose:
        print(f"🚦 Router has selected route: '{chosen_route}'")

    # 2. Execute the chosen route
    if chosen_route == 'find_and_navigate_combo':
        if args.verbose:
            print("\n--- Starting Find and Navigate Combo Workflow ---")

        # STEP 2a: Run the foodie_agent first
        foodie_session = await session_service.create_session(app_name=foodie_agent.name, user_id=my_user_id)
        foodie_response = await run_agent_query(foodie_agent, query, foodie_session, my_user_id, verbose=args.verbose)

        # STEP 2b: Extract the destination from the first agent's response
        match = re.search(r'\*\*(.*?)\*\*', foodie_response)
        if not match:
            print("🚨 Could not determine the restaurant name from the response.")
            return
        destination = match.group(1)
        if args.verbose:
            print(f"💡 Extracted Destination: {destination}")

        # STEP 2c: Create a new query and run the transportation_agent
        directions_query = f"Give me directions to {destination} from the Palo Alto Caltrain station."
        if args.verbose:
            print(f"\n🗣️ New Query for Transport Agent: '{directions_query}'")
        transport_session = await session_service.create_session(app_name=transportation_agent.name, user_id=my_user_id)
        await run_agent_query(transportation_agent, directions_query, transport_session, my_user_id, verbose=args.verbose)

        if args.verbose:
            print("--- Combo Workflow Complete ---")

    elif chosen_route in worker_agents:
        # This is a simple, single-agent route
        worker_agent = worker_agents[chosen_route]
        if args.verbose:
            print(f"--- Handing off to {worker_agent.name} ---")
        worker_session = await session_service.create_session(app_name=worker_agent.name, user_id=my_user_id)
        await run_agent_query(worker_agent, query, worker_session, my_user_id, verbose=args.verbose)
        if args.verbose:
            print(f"--- {worker_agent.name} Complete ---")
    else:
        print(f"🚨 Error: Router chose an unknown route: '{chosen_route}'")

if __name__ == "__main__":
    asyncio.run(main())
