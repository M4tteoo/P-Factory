# --- START OF FILE llm_engine.py (Modified) ---
import json
from Simulation.prompt_templates import build_agent_prompt
from Simulation.llm_api import call_local_llm

#helper funtion to determine if the last dialogue was a question to the activated agent 
def analyze_last_dialogue_for_agent(last_dialogue,agent_name):
    if last_dialogue and last_dialogue.endswith("?"):
        #established if it is a question check if it is to the activated agent
        words = last_dialogue.split()
        for i, word in enumerate(words):
            if word.endswith(",") and word[:-1] == agent_name:
                return True
            elif word == agent_name and i +1 < len(words) and words[i+1].startswith(('what', 'where', 'when', 'who', 'why', 'how', 'do', 'are', 'is', 'can', 'will')):
                return True
        if "you" in last_dialogue.lower() or "anyone" in last_dialogue.lower() or "friends" in last_dialogue.lower():
            return True
            

    return False

def simulate_agent_turn(agent, world_state, all_agents, memory_manager, turn_number):
    print(f"\n--- Turn {turn_number}: {agent.name}'s Turn ---")

    # 1. DEFINE the context for memory retrieval
    last_dialogue = world_state.get_recent_dialogue(n=1)
    query_context = agent.goal
    if last_dialogue:
        query_context += ". In response to: " + last_dialogue[0]['text']

    # 2. RETRIEVE both public and personal memories
    public_memories = memory_manager.retrieve_public_memories(query_context)
    personal_memories = memory_manager.retrieve_personal_memories(agent.name, query_context)
    
    print(f"Retrieved Public Memories (for awareness): {public_memories}")
    print(f"Retrieved Personal Memories (for reflection): {personal_memories}")


    is_last_a_question_for_agent = analyze_last_dialogue_for_agent(last_dialogue[0]['text'], agent.name)
    is_last_a_question_for_agent_str = "Yes" if is_last_a_question_for_agent else "No"

    prompt = build_agent_prompt(agent, 
                                world_state, 
                                all_agents, 
                                public_memories, 
                                personal_memories,
                                is_last_a_question_for_agent_str
                                )

    # 3. CALL the LLM to get the agent's plan (in JSON)
    response_json_str = call_local_llm(prompt)
    print(f"LLM Response for {agent.name}:\n{response_json_str}")

    # 4. PARSE and EXECUTE the plan
    try:
        plan = json.loads(response_json_str)
        thought = plan.get("thought", "I had no thought.")
        dialogue = plan.get("dialogue", "[says nothing]") # Directly get dialogue

        # Add the agent's thought to its long-term memory
        memory_manager.add_memory(agent.name, thought, turn_number)

        # Execute the action: always SPEAK if the DM activated them to speak
        if dialogue != "[says nothing]": # Only add if they actually said something
            world_state.add_message(agent.name, dialogue)
        else:
            # If the agent returned empty dialogue, you might still want to log it
            # or have the DM interject. For now, we'll assume they always try to speak.
            world_state.add_message(agent.name, "[struggles to find words]") 

    except json.JSONDecodeError:
        print(f"ERROR: Failed to decode JSON from LLM for {agent.name}. Response was:\n{response_json_str}")
        world_state.add_message(agent.name, "[is confused and says nothing]")
    except Exception as e:
        print(f"ERROR: An error occurred during plan execution for {agent.name}: {e}")