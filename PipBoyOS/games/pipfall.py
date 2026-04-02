# Example skeleton for games/atomic_command.py
class PipFall:
    def __init__(self):
        # Setup the missiles, bases, and score here
        self.score = 0
        
    def handle_input(self, event):
        # Move the crosshairs, fire lasers
        pass
        
    def update(self):
        # Move missiles down the screen, check for explosions
        pass
        
    def draw(self, screen):
        # Draw the cities, lasers, and score to the screen
        pass
