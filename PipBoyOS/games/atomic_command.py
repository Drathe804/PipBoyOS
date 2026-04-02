# games/atomic_command.py
import pygame
from config import GREEN, BLACK, WIDTH, HEIGHT

class AtomicCommand:
    def __init__(self):
        self.small_font = pygame.font.Font("fallout.ttf", 24)
        
        self.cross_x = WIDTH // 2
        self.cross_y = HEIGHT // 2
        self.cross_speed = 6
        
        self.lasers = [] 
        self.explosions = [] # NEW: Holds our expanding fireballs!

    def update(self, events): # NEW: We now accept the events list!
        # 1. MOVEMENT (Keep using polling for smooth movement)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: self.cross_y -= self.cross_speed
        if keys[pygame.K_DOWN]: self.cross_y += self.cross_speed
        if keys[pygame.K_LEFT]: self.cross_x -= self.cross_speed
        if keys[pygame.K_RIGHT]: self.cross_x += self.cross_speed
            
        self.cross_x = max(30, min(self.cross_x, WIDTH - 30))
        self.cross_y = max(30, min(self.cross_y, HEIGHT - 60))

        # 2. FIRING (Use the Event Inbox so taps/encoders never drop!)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Fire instantly on tap! No cooldown needed for single taps.
                    new_laser = {
                        "start_x": WIDTH // 2,
                        "start_y": HEIGHT - 60,
                        "target_x": self.cross_x,
                        "target_y": self.cross_y,
                        "progress": 0.0 
                    }
                    self.lasers.append(new_laser)

        # 3. UPDATE LASERS & SPAWN EXPLOSIONS
        for laser in self.lasers:
            laser["progress"] += 0.05 
            
            # If the laser reaches the crosshair...
            if laser["progress"] >= 1.0:
                # Spawn an explosion at the target coordinates!
                self.explosions.append({
                    "x": laser["target_x"],
                    "y": laser["target_y"],
                    "radius": 1,      # Starts tiny
                    "max_radius": 35  # Grows to this size
                })
                
        # Remove finished lasers
        self.lasers = [l for l in self.lasers if l["progress"] < 1.0]

        # 4. UPDATE EXPLOSIONS
        for exp in self.explosions:
            exp["radius"] += 1.5 # The circle expands every frame!
            
        # Remove explosions that have reached their max size
        self.explosions = [e for e in self.explosions if e["radius"] < e["max_radius"]]

    def draw(self, screen):
        screen.fill(BLACK)
        pygame.draw.rect(screen, GREEN, (20, 20, WIDTH - 40, HEIGHT - 40), 2)
        
        # 1. Skyline 
        pygame.draw.rect(screen, GREEN, (WIDTH // 2 - 20, HEIGHT - 60, 40, 40)) 
        pygame.draw.rect(screen, GREEN, (80, HEIGHT - 40, 60, 20))              
        pygame.draw.rect(screen, GREEN, (WIDTH - 140, HEIGHT - 40, 60, 20))     
        
        # 2. Draw Active Lasers
        for laser in self.lasers:
            current_x = laser["start_x"] + (laser["target_x"] - laser["start_x"]) * laser["progress"]
            current_y = laser["start_y"] + (laser["target_y"] - laser["start_y"]) * laser["progress"]
            pygame.draw.line(screen, GREEN, (laser["start_x"], laser["start_y"]), (current_x, current_y), 3)

        # 3. Draw Expanding Explosions!
        for exp in self.explosions:
            # Draw a solid green circle that grows over time
            pygame.draw.circle(screen, GREEN, (int(exp["x"]), int(exp["y"])), int(exp["radius"]))

        # 4. Draw Crosshair
        pygame.draw.rect(screen, GREEN, (self.cross_x - 1, self.cross_y - 1, 2, 2))
        pygame.draw.circle(screen, GREEN, (self.cross_x, self.cross_y), 8, 1)
        pygame.draw.line(screen, GREEN, (self.cross_x, self.cross_y - 8), (self.cross_x, self.cross_y - 16), 1) 
        pygame.draw.line(screen, GREEN, (self.cross_x, self.cross_y + 8), (self.cross_x, self.cross_y + 16), 1) 
        pygame.draw.line(screen, GREEN, (self.cross_x - 8, self.cross_y), (self.cross_x - 16, self.cross_y), 1) 
        pygame.draw.line(screen, GREEN, (self.cross_x + 8, self.cross_y), (self.cross_x + 16, self.cross_y), 1) 

        prompt_surf = self.small_font.render("TAB TO EJECT", True, GREEN)
        screen.blit(prompt_surf, (30, 30))
