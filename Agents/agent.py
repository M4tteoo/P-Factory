class Agent():
    def __init__(self, name, role, personality, goal):
        self.name = name
        self.role = role
        self.personality = personality
        self.goal = goal
        self.turn_count = 0
        

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "personality": self.personality,
            "goal": self.goal,
            "turn_count": self.turn_count
        }

        
