class WorldState:
    def __init__(self):
        self.scene_description = "A quiet forest campfire at dusk."
        self.conversation_log = []

    def add_message(self, speaker, text):
        self.conversation_log.append({"speaker": speaker, "text": text})
        if len(self.conversation_log) > 20:
            self.conversation_log.pop(0)  # to keep it lightweight

    def get_recent_dialogue(self, n=5):
        return self.conversation_log[-n:]

    def get_scene_summary(self):
        return self.scene_description
    