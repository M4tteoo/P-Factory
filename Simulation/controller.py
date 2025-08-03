from Simulation.llm_engine import simulate_agent_turn

def run_simulation(agents, world_state, turns=10):
    for i in range(turns):
        current_agent = agents[i % len(agents)]
        simulate_agent_turn(current_agent, world_state, agents)