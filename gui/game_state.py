class GameState():
    def __init__(self):
        self.states = {}

    def reset(self):
        self.states["sleeping"] = False
        self.states["feeding_time"] = False
        self.states["cancel"] = False
        self.states["unwell"] = False
        self.states["health"] = 10
        self.states["happiness"] = 10
        self.states["sleepiness"] = 10
        self.states["tired"] = False

    def __str__(self):
        """ shows the current game state """
        message = "Game State: "
#         for state in self.states:
#             message += ", ".join(f"{key}: {value}" for key, value in self.states.items())
        message += ", ".join(f"{key}: {value}" for key, value in self.states.items())
        message += "."
        return message
