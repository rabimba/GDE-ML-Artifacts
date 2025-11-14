# -*- coding: utf-8 -*-
import streamlit as st
import asyncio
import re
from core import configure_api_key, run_agent_query, session_service, my_user_id
from agents import router_agent_ultimate, worker_agents, foodie_agent, transportation_agent

st.set_page_config(page_title="ADK Learning Tool", page_icon="🚀")

st.title("🚀 Welcome to Your ADK Adventure - MultiAgents!")

st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your Google API Key", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

async def run_app(query):
    if not api_key:
        st.error("Please enter your Google API Key in the sidebar.")
        return

    configure_api_key(api_key)

    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})


    # 1. Ask the Router Agent to choose the right agent or workflow
    router_session = await session_service.create_session(app_name=router_agent_ultimate.name, user_id=my_user_id)
    
    with st.spinner("🧠 Asking the router agent to make a decision..."):
        chosen_route = await run_agent_query(router_agent_ultimate, query, router_session, my_user_id, is_router=True, verbose=False)
    chosen_route = chosen_route.strip().replace("'", "")
    st.info(f"🚦 Router has selected route: '{chosen_route}'")


    # 2. Execute the chosen route
    if chosen_route == 'find_and_navigate_combo':
        with st.spinner("--- Starting Find and Navigate Combo Workflow ---"):
            # STEP 2a: Run the foodie_agent first
            foodie_session = await session_service.create_session(app_name=foodie_agent.name, user_id=my_user_id)
            foodie_response = await run_agent_query(foodie_agent, query, foodie_session, my_user_id, verbose=False)

            # STEP 2b: Extract the destination from the first agent's response
            match = re.search(r'\*\*(.*?)\*\*', foodie_response)
            if not match:
                st.error("🚨 Could not determine the restaurant name from the response.")
                return
            destination = match.group(1)
            st.info(f"💡 Extracted Destination: {destination}")

            # STEP 2c: Create a new query and run the transportation_agent
            directions_query = f"Give me directions to {destination} from the Palo Alto Caltrain station."
            transport_session = await session_service.create_session(app_name=transportation_agent.name, user_id=my_user_id)
            final_response = await run_agent_query(transportation_agent, directions_query, transport_session, my_user_id, verbose=False)
            st.success("--- Combo Workflow Complete ---")

    elif chosen_route in worker_agents:
        # This is a simple, single-agent route
        worker_agent = worker_agents[chosen_route]
        with st.spinner(f"--- Handing off to {worker_agent.name} ---"):
            worker_session = await session_service.create_session(app_name=worker_agent.name, user_id=my_user_id)
            final_response = await run_agent_query(worker_agent, query, worker_session, my_user_id, verbose=False)
        st.success(f"--- {worker_agent.name} Complete ---")
    else:
        final_response = f"🚨 Error: Router chose an unknown route: '{chosen_route}'"

    with st.chat_message("assistant"):
        st.markdown(final_response)
    st.session_state.messages.append({"role": "assistant", "content": final_response})


if prompt := st.chat_input("What is your query?"):
    asyncio.run(run_app(prompt))
