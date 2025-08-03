from Simulation.prompt_templates import build_agent_prompt
from Simulation.llm_api import call_local_llm

def simulate_agent_turn(agent, world_state, all_agents):
    prompt = build_agent_prompt(agent, world_state, all_agents)  # READS from world_state
    response = call_local_llm(prompt)
    world_state.add_message(agent.name, response)               # WRITES to world_state
    agent.add_memory(response)