# --- START OF FILE prompt_templates.py ---

AGENT_PROMPT_TEMPLATE = """
You are an AI actor playing the role of a character in a simulation.

== YOUR CHARACTER ==
Name: {name}
Personality: {personality}
Current Goal: {goal}

== THE SCENE ==
Location: {scene_description}
Others Present: {other_agents}
Recent Conversation:
{recent_dialogue}

== YOUR TASK ==
Based on your character and goal, write your next line of dialogue.
You MUST follow these rules:
1.  **ONLY** output the words your character speaks. Nothing else.
2.  **DO NOT** write descriptions of actions, thoughts, or emotions (e.g., do not write 'she says with a smile' or 'he looks at the fire').
3.  **DO NOT** put your character's name at the start of your response (e.g., 'Lina: ...'). The simulation will add the name.
4.  Keep your response concise and natural, like real speech.
5. Do not use a too complex lexicon.

== EXAMPLE of a GOOD RESPONSE ==
"While we have a moment of quiet, has anyone here ventured deep into these woods before? I'm hoping to chart them."

== YOUR RESPONSE (DIALOGUE ONLY) ==
"""

def build_agent_prompt(agent, world_state, all_agents):
    other_agents = [a.name for a in all_agents if a.name != agent.name]
    recent_dialogue = world_state.get_recent_dialogue()

    # Format recent dialogue into a string. Add a placeholder if the convo is empty.
    if not recent_dialogue:
        dialogue_str = "[The conversation has not started yet.]"
    else:
        dialogue_str = "\n".join([f"{line['speaker']}: {line['text']}" for line in recent_dialogue])

    prompt = AGENT_PROMPT_TEMPLATE.format(
        name=agent.name,
        personality=", ".join(agent.personality),
        goal=agent.goal,
        scene_description=world_state.get_scene_summary(),
        other_agents=", ".join(other_agents) if other_agents else "no one else",
        recent_dialogue=dialogue_str
    )

    return prompt