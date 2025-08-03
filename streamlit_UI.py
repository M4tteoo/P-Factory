# --- START OF FILE streamlit_UI.py ---

# streamlit_app.py

import streamlit as st
from Agents.agent_loader import load_agents_from_config
from Simulation.world_state import WorldState
from Simulation.llm_engine import simulate_agent_turn

st.set_page_config(page_title="AI Persona Factory", layout="wide")

# --- Initialize session state ---
if "agents" not in st.session_state:
    st.session_state.agents = load_agents_from_config()
    st.session_state.world = WorldState()
    st.session_state.turn = 0

agents = st.session_state.agents
world = st.session_state.world

# --- Sidebar: Agent info ---
st.sidebar.title("Agent Profiles")
for agent in agents:
    with st.sidebar.expander(agent.name):
        st.markdown(f"**Role:** {agent.role}")
        st.markdown(f"**Traits:** {', '.join(agent.personality)}") 
        st.markdown(f"**Goal:** {agent.goal}")
        st.markdown(f"**Turns Spoken:** {agent.turn_count}") 

# --- Main display ---
st.title("AI Persona Simulation")

# Conversation log
st.subheader("💬 Conversation")
# To prevent errors on the first run, check if the log exists
if hasattr(world, 'conversation_log'):
    for msg in world.conversation_log:
        st.markdown(f"**{msg['speaker']}**: {msg['text']}")

# --- Buttons ---
st.markdown("### Controls")
if st.button("▶️ Advance 1 Turn"):
    current_agent = agents[st.session_state.turn % len(agents)]
    simulate_agent_turn(current_agent, world, agents)
    current_agent.turn_count += 1 
    st.session_state.turn += 1
    st.rerun()

if st.button("🔄 Reset Simulation"):
    # Pass the correct path on reset as well
    st.session_state.agents = load_agents_from_config()
    st.session_state.world = WorldState()
    st.session_state.turn = 0
    st.rerun()