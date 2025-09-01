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

Last thing said to you, or the main topic: {last_dialogue_summary}
Was the last statement a question directed at you or the group? {is_last_a_question_for_agent}

== RELEVANT MEMORIES OF THE CONVERSATION (What you've heard) ==
{public_memories}

== YOUR OWN RELEVANT THOUGHTS (What you've thought before) ==
{personal_memories}

== YOUR TASK ==
Based on your character, goal, and the current situation, you have been prompted to speak. Formulate your response.
If the last statement was a direct question directed at you or the group, your first priority is to answer it, even if it means momentarily deferring your personal goal. Otherwise, proceed with your goal or react naturally to the conversation.
You MUST respond with a JSON object with two keys: "thought" and "dialogue".
•⁠  ⁠"thought": A brief, private thought about your reasoning. This will become a memory.
•⁠  ⁠"dialogue": The exact words *you, {name},* say to the other characters.
**YOUR DIALOGUE MUST BE IN THE FIRST PERSON AND SPOKEN AS YOUR CHARACTER, {name}. DO NOT IMPERSONATE OTHER CHARACTERS.**

== EXAMPLE of a GOOD RESPONSE ==
{{
    "thought": "Lina asked about mapping, and it aligns with my explorer nature. I should agree to help.",
    "dialogue": "That's a fantastic idea, Lina! I'd be happy to help you map this intriguing forest."
}}

== YOUR RESPONSE (JSON ONLY) ==
"""

def build_agent_prompt(agent, world_state, all_agents, public_memories, personal_memories, is_last_a_question_for_agent_str):
    other_agents = [a.name for a in all_agents if a.name != agent.name]
    recent_dialogue = world_state.get_recent_dialogue()

    if not recent_dialogue:
        dialogue_str = "[The conversation has not started yet.]"
    else:
        dialogue_str = "\n".join([f"{line['speaker']}: {line['text']}" for line in recent_dialogue])

    # Format public memories
    if not public_memories:
        public_memories_str = "[No relevant public memories.]"
    else:
        public_memories_str = "\n".join([f"- {m}" for m in public_memories])
    # Format personal memories
    if not personal_memories:
        personal_memories_str = "[You have no relevant personal memories on this topic.]"
    else:
        personal_memories_str = "\n".join([f"- {m}" for m in personal_memories])

    last_dialogue_summary = "[No recent direct statement.]"
    last_speaker = 'Narrator'
    if recent_dialogue:
        last_speaker = recent_dialogue[-1]['speaker']
        last_text = recent_dialogue[-1]['text']
        if last_speaker != agent.name: # Only if someone else spoke
            last_dialogue_summary = f"{last_speaker} said: '{last_text}'"
        else: # If the agent itself spoke last, summarize the topic
            last_dialogue_summary = f"The last topic was: '{last_text}'"

    prompt = AGENT_PROMPT_TEMPLATE.format(
        name=agent.name,
        personality=", ".join(agent.personality),
        goal=agent.goal,
        scene_description=world_state.get_scene_summary(),
        other_agents=", ".join(other_agents) if other_agents else "no one else",
        recent_dialogue=dialogue_str,
        public_memories=public_memories_str,   
        personal_memories=personal_memories_str,
        last_dialogue_summary= last_dialogue_summary,
        is_last_a_question_for_agent=is_last_a_question_for_agent_str 
    )
    return prompt


MASTER_PROMPT_TEMPLATE = """
You are the Dungeon Master (DM) for an AI simulation. Your role is to guide the narrative and decide which character should speak next, or if an external event should occur. Avoid beeing overly verbose in the narration.

== YOUR GOAL ==
{dm_goal}
A primary aspect of your goal is to ensure natural and coherent conversation flow. This includes ensuring direct questions are answered and topics are addressed appropriately.

== CURRENT SCENE ==
Location: {scene_description}
Characters Present:
{all_agents_summary}

Recent Conversation:
{recent_dialogue}

Last Agent to Speak: {last_speaker_name}
Was the last statement a question? {is_last_a_question}
If so, who was it directed to? {question_recipient}

== YOUR OWN RELEVANT THOUGHTS (What you've thought before as DM) ==
{dm_personal_memories}

== YOUR TASK ==
Based on the current situation, your goal (especially conversational coherence), and the characters' personalities and goals, decide what should happen next.
IT IS ABSOLUTELY CRITICAL THAT THE 'agent_name' IN YOUR 'ACTIVATE_AGENT' COMMAND IS DIFFERENT FROM '{last_speaker_name}', UNLESS THERE IS A VERY COMPELLING NARRATIVE REASON TO HAVE THE SAME AGENT SPEAK AGAIN IMMEDIATELY (e.g., they were directly asked a follow-up question). You should strive to involve different agents in the conversation.
YOUR ENTIRE RESPONSE MUST BE A SINGLE, VALID JSON OBJECT. DO NOT INCLUDE ANY OTHER TEXT, COMMENTS, OR MULTIPLE JSON OBJECTS BEFORE OR AFTER IT.
**UNDER NO CIRCUMSTANCES SHOULD YOU GENERATE CHARACTER DIALOGUE FOR AN ACTIVATED AGENT OR INCLUDE IT IN YOUR 'narration' FIELD. CHARACTER DIALOGUE IS SOLELY GENERATED BY THE ACTIVATED AGENT.**
You MUST respond with a JSON object with two keys: "thought", "action", and optionally "narration".
•⁠  ⁠"thought": A brief, private thought about your reasoning. This will become a memory for the DM.
•⁠  ⁠"action": A dictionary describing what you decide. It MUST have a "command" key.
•⁠  ⁠"narration": (Optional) A string containing any *environmental description, scene-setting, or events that the DM observes or introduces*. THIS FIELD IS FOR THE DM'S VOICE ONLY, NOT CHARACTER DIALOGUE.

Possible commands for the "action" key:

1.  "ACTIVATE_AGENT": Make a specific agent speak.
    •⁠  ⁠Requires a "agent_name" key (must be one of the names of present agents).
    •⁠  ⁠Remember: This agent_name should ideally NOT be '{last_speaker_name}'. The activated agent will then generate their OWN dialogue.
    •⁠  ⁠If '{last_speaker_name}' asked a question directed at '{question_recipient}', prioritize activating '{question_recipient}' or another suitable agent to answer it.
    •⁠  ⁠Example: {{"command": "ACTIVATE_AGENT", "agent_name": "Lina"}}

2.  "NARRATE_ONLY": To introduce a narrative event *without* activating an agent.
    •⁠  ⁠Requires a "narration" key (what the narrator says).
    •⁠  ⁠**This 'narration' field in the 'action' dict is for the DM's voice only, not character dialogue.**
    •⁠  ⁠Example: {{"command": "NARRATE_ONLY", "narration": "A chilling gust of wind sweeps through the clearing, making the campfire flicker wildly."}}
    **(Note: If using NARRATE_ONLY, the top-level 'narration' key should typically be empty or omitted as the narrative content is already in the 'action'.)**

3.  "WAIT": To do nothing for this turn, allowing the situation to simmer. (Use sparingly)
    •⁠  ⁠Example: {{"command": "WAIT"}}

== EXAMPLE of a GOOD RESPONSE (Activating an Agent with preceding narration, NO CHARACTER DIALOGUE in narration) ==
{{
    "thought": "The group is quiet, so I'll set the scene and then have Eldrin offer some wisdom.",
    "narration": "A long silence stretches between the travelers, broken only by the crackling fire. Eldrin seems deep in thought.",
    "action": {{
        "command": "ACTIVATE_AGENT",
        "agent_name": "Eldrin"
    }}
}}

== EXAMPLE of a GOOD RESPONSE (Only Narration from DM, NO CHARACTER DIALOGUE) ==
{{
    "thought": "The conversation is getting too calm, it's time to introduce a small complication to keep things interesting.",
    "action": {{
        "command": "NARRATE_ONLY",
        "narration": "From the shadowy depths of the forest, a low, guttural growl echoes, sending shivers down everyone's spines."
    }}
}}

== YOUR RESPONSE (JSON ONLY) ==
"""

def build_dm_prompt(dm_goal, world_state, all_agents, recent_dialogue, dm_personal_memories, is_last_a_question, question_recipient):
    all_agents_summary = "\n".join([
        f"- {a.name} ({a.role}): {', '.join(a.personality)}. Goal: {a.goal}"
        for a in all_agents
    ])

    if not recent_dialogue:
        dialogue_str = "[The conversation has not started yet.]"
    else:
        dialogue_str = "\n".join([f"{line['speaker']}: {line['text']}" for line in recent_dialogue])

    if not dm_personal_memories:
        dm_personal_memories_str = "[The DM has no relevant previous thoughts.]"
    else:
        dm_personal_memories_str = "\n".join([f"- {m}" for m in dm_personal_memories])

    last_speaker_name = recent_dialogue[-1]['speaker'] if recent_dialogue else "No one yet"

    prompt = MASTER_PROMPT_TEMPLATE.format(
        dm_goal=dm_goal,
        scene_description=world_state.get_scene_summary(),
        all_agents_summary=all_agents_summary,
        recent_dialogue=dialogue_str,
        dm_personal_memories=dm_personal_memories_str,
        last_speaker_name=last_speaker_name,
        is_last_a_question=is_last_a_question,
        question_recipient=question_recipient
    )
    return prompt