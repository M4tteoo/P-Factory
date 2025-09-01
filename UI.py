import streamlit as st
from Agents.agent_loader import load_agents_from_config
from Simulation.world_state import WorldState
from Simulation.llm_engine import simulate_agent_turn
from Memory.memory_manager import MemoryManager
from Simulation.dungeon_master import Master # New import

st.set_page_config(page_title="AI Persona Factory", layout="wide")

# --- Initialize session state ---
if "agents" not in st.session_state:
    st.session_state.agents = load_agents_from_config()
    st.session_state.world = WorldState()
    st.session_state.memory_manager = MemoryManager()
    st.session_state.memory_manager.clear_all_memories()
    st.session_state.dm = Master() 
    st.session_state.turn = 0
    # Add an initial narration to kick things off
    st.session_state.world.add_message("Narrator", "The simulation begins. Four travelers gather around a crackling campfire as dusk settles over the forest.")


agents = st.session_state.agents
world = st.session_state.world
memory_manager = st.session_state.memory_manager
dm = st.session_state.dm

# --- Sidebar: Agent info ---
st.sidebar.title("Agent Profiles")
for agent in agents:
    with st.sidebar.expander(agent.name):
        st.markdown(f"**Role:** {agent.role}")
        # FIX: Use agent.personality here
        st.markdown(f"**Traits:** {', '.join(agent.personality)}") 
        st.markdown(f"**Goal:** {agent.goal}")
        st.markdown(f"**Turns Spoken:** {agent.turn_count}")

# --- Main display ---
st.title("AI Persona Simulation")

# Conversation log
st.subheader("💬 Conversation")
if hasattr(world, 'conversation_log'):
    for msg in world.conversation_log:
        st.markdown(f"**{msg['speaker']}**: {msg['text']}")

# --- Buttons ---
st.markdown("### Controls")
if st.button("▶️ Advance 1 Turn"):
    # DM decides what happens next!
    dm_action = dm.decide_next_action(world, agents, memory_manager)

    command = dm_action.get("command")

    if command == "ACTIVATE_AGENT":
        agent_name_to_activate = dm_action.get("agent_name")
        active_agent = next((a for a in agents if a.name == agent_name_to_activate), None)
        
        if active_agent:
            simulate_agent_turn(active_agent, world, agents, memory_manager, dm.turn_number)
            active_agent.turn_count += 1
        else:
            world.add_message("Narrator", f"DM tried to activate non-existent agent '{agent_name_to_activate}'.")
            print(f"ERROR: DM tried to activate non-existent agent '{agent_name_to_activate}'.")
    elif command == "NARRATE_ONLY": 
        narration_text = dm_action.get("narration", "The narrative subtly shifts.")
        world.add_message("Narrator", narration_text)
    elif command == "WAIT":
        world.add_message("Narrator", "The moment hangs, as if awaiting a sign. No one speaks.")
    else:
        world.add_message("Narrator", f"DM issued an unknown command: {command}")
        print(f"WARNING: DM issued an unknown command: {command}")

    st.session_state.turn = dm.turn_number # Keep UI turn in sync with DM's turn
    st.rerun()

if st.button("🔄 Reset Simulation"):
    st.session_state.agents = load_agents_from_config()
    st.session_state.world = WorldState()
    st.session_state.memory_manager.clear_all_memories()
    st.session_state.dm = Master() # Re-initialize DM
    st.session_state.turn = 0
    # Add initial narration again
    st.session_state.world.add_message("Narrator", "The simulation begins. Four travelers gather around a crackling campfire as dusk settles over the forest.")
    st.rerun()