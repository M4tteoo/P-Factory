class Agent():
    def __init__(self, name, role, personality, goal):
        self.name = name
        self.role = role
        self.personality = personality
        self.goal = goal
        self.turn_count = 0
        self.memory = []
    
    def add_memory(self, memory_item):
        self.memory.append(memory_item)
    
    def get_memory(self):
        return "\n".join(self.memory)

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "traits": self.personality,
            "goal": self.goal,
            "turn_count": self.turn_count
        }

        
