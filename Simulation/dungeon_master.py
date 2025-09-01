import json
from Simulation.llm_api import call_local_llm
from Simulation.prompt_templates import build_dm_prompt

#define an helper funtion to determine if the last dialogue was a question and who is the recipient
def analyze_last_dialogue(last_dialogue, all_agents):
    is_question = False
    recipient = "the group"
    if last_dialogue and last_dialogue.endswith("?"):
        is_question = True
        words = last_dialogue.split()
        for i, word in enumerate(words):
            if word.endswith(",") and word[:-1] in [a.name for a in all_agents]:
                recipient = word[:-1]
                break
            elif word in [a.name for a in all_agents] and i +1 < len(words) and words[i+1].startswith(('what', 'where', 'when', 'who', 'why', 'how', 'do', 'are', 'is', 'can', 'will')):
                recipient = word
                break
    return is_question, recipient

class Master:
    def __init__(self, model="mistral"):
        self.model = model
        self.dm_goal = "Facilitate compelling interactions between characters, ensuring all agents have a chance to contribute and driving the narrative forward. Occasionally introduce plot twists or environmental changes."
        self.turn_number = 0 # To track global turns

    def decide_next_action(self, world_state, all_agents, memory_manager):
        self.turn_number += 1
        print(f"\n--- DM Turn {self.turn_number} ---")

        # Gather context for the DM
        recent_dialogue = world_state.get_recent_dialogue(n=5)
        # DM's own internal memory (optional but good for consistency)
        dm_personal_memories = memory_manager.retrieve_personal_memories("DungeonMaster", f"Current turn {self.turn_number}. Conversation so far: {recent_dialogue}", n_results=2)

        if recent_dialogue:
            last_dialogue_text = recent_dialogue[-1]['text']

        is_last_a_question, question_recipient = analyze_last_dialogue(last_dialogue_text, all_agents) if recent_dialogue else (False, all_agents)
        #convert True or False to a string 
        is_last_a_question = "Yes" if is_last_a_question else "No"
        
        # Build the DM's prompt
        prompt = build_dm_prompt(self.dm_goal, 
                                 world_state,
                                all_agents, 
                                recent_dialogue, 
                                dm_personal_memories,
                                is_last_a_question,
                                question_recipient
                                )

        # Call the LLM for DM's decision
        response_json_str = call_local_llm(prompt, model=self.model)
        print(f"DM LLM Response:\n{response_json_str}")

        # Parse DM's decision
        try:
            dm_decision = json.loads(response_json_str)
            dm_thought = dm_decision.get("thought", "The DM ponders the scene.")
            dm_action = dm_decision.get("action", {})
            dm_narration = dm_decision.get("narration", "")

            # Add DM's thought to its own long-term memory
            memory_manager.add_memory("DungeonMaster", dm_thought, self.turn_number)

            if dm_narration:
                world_state.add_message("Narrator", dm_narration)

            return dm_action

        except json.JSONDecodeError:
            print(f"ERROR: DM failed to decode JSON. Response was:\n{response_json_str}")
            # Fallback for parsing errors
            world_state.add_message("Narrator", "The DM is lost in thought, and the story pauses with an unresolved tension.") # Modified fallback
            return {"command": "WAIT"} # A safe default action to prevent further errors
        except Exception as e:
            print(f"ERROR: An error occurred during DM decision-making: {e}")
            world_state.add_message("Narrator", f"The story seems to pause due to a DM error: {e}")
            return {"command": "WAIT"}