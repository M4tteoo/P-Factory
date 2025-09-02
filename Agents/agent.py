class Agent():
    def __init__(self, name, role, personality, goal, backstory, current_state, relationships):
        self.name = name
        self.role = role
        self.personality = personality
        self.goal = goal
        self.backstory = backstory
        self.current_state = current_state
        self.relationships = relationships
        self.turn_count = 0
        

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "personality": self.personality,
            "goal": self.goal,
            "backstory": self.backstory,
            "current_state": self.current_state,
            "relationships": self.relationships,
            "turn_count": self.turn_count
        }

        
