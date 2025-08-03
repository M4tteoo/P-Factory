import json
from Agents.agent import Agent

def load_agents_from_config(path="Config/agents.json"):
    with open(path, "r") as f:
        data = json.load(f)
    return [Agent(**a) for a in data]

